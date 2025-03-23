import speech_recognition as sr
import json
from groq import Groq
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class CommandClassifier:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Load embeddings at startup
        print("Initializing system...")
        from file_opr.main import FileAssistant
        self.file_assistant = FileAssistant(silent=True)  # Add silent mode
        print("Ready!")
        
        self.system_prompt = """You are a command classifier. Analyze the user's command and determine if it's:
        1. FILE_OPERATION - for file management tasks (create, delete, move, copy, search files)
        2. SYSTEM_CONTROL - for system settings (brightness, volume, wifi, bluetooth, battery)
        3. APP_CONTROL - for application control (open, close, switch between apps)
        
        Return ONLY a JSON with these fields:
        {
            "type": "FILE_OPERATION or SYSTEM_CONTROL or APP_CONTROL",
            "confidence": "0-100",
            "keywords": ["list of relevant keywords"],
            "command": "original command"
        }"""

    def listen_command(self):
        """Listen for voice command and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            print("Error: Could not understand audio")
            return None

    def classify_command(self, command: str):
        """Classify the command using LLM"""
        # Handle exit command specially
        if command.lower() in ['exit', 'quit', 'bye', 'thank you']:
            return {
                "type": "EXIT",
                "confidence": 100,
                "keywords": ["exit"],
                "command": command
            }

        try:
            # Make the system prompt more explicit about JSON formatting
            system_prompt = """You are a command classifier. Return ONLY valid JSON, no other text.

Example commands and responses:
Input: "open chrome"
{
    "type": "APP_CONTROL",
    "confidence": 95,
    "keywords": ["open", "launch", "chrome", "browser"],
    "command": "open chrome"
}

Input: "increase volume"
{
    "type": "SYSTEM_CONTROL",
    "confidence": 90,
    "keywords": ["volume", "increase", "audio"],
    "command": "increase volume"
}

Input: "delete file from desktop"
{
    "type": "FILE_OPERATION",
    "confidence": 85,
    "keywords": ["delete", "remove", "file", "desktop"],
    "command": "delete file from desktop"
}

Rules:
1. ONLY return valid JSON
2. No explanations or additional text
3. Type must be one of: FILE_OPERATION, SYSTEM_CONTROL, APP_CONTROL
4. Confidence must be a number between 0-100
5. Keywords must be relevant to the command
6. Command must be the original input"""

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this command: {command}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            try:
                result = json.loads(completion.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # Fallback classification based on keywords
                command_lower = command.lower()
                if any(word in command_lower for word in ['open', 'launch', 'start', 'run', 'close', 'switch']):
                    return {
                        "type": "APP_CONTROL",
                        "confidence": 70,
                        "keywords": ["application", "control"],
                        "command": command
                    }
                elif any(word in command_lower for word in ['volume', 'brightness', 'wifi', 'bluetooth']):
                    return {
                        "type": "SYSTEM_CONTROL",
                        "confidence": 70,
                        "keywords": ["system", "settings"],
                        "command": command
                    }
                else:
                    return {
                        "type": "FILE_OPERATION",
                        "confidence": 70,
                        "keywords": ["file", "operation"],
                        "command": command
                    }
        except Exception as e:
            return {
                "type": "ERROR",
                "confidence": 0,
                "keywords": ["error"],
                "command": command,
                "error": str(e)
            }

    def route_command(self, classification, original_command):
        """Route the command to appropriate handler"""
        try:
            if classification["type"] == "FILE_OPERATION":
                from file_opr.main import FileAssistant
                assistant = FileAssistant()
                return assistant.process_command(original_command)
                
            elif classification["type"] == "SYSTEM_CONTROL":
                from system_controls.main import process_command
                return process_command(original_command)
                
            elif classification["type"] == "APP_CONTROL":
                from app_controls.main import AppController
                controller = AppController()
                return controller.process_command(original_command)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def main_loop(self):
        while True:
            command = self.listen_command()
            if not command:
                continue
                
            classification = self.classify_command(command)
            if classification["type"] == "EXIT":
                print(json.dumps({"success": True, "result": "Goodbye!"}))
                break
            elif classification["type"] == "ERROR":
                print(json.dumps({"success": False, "error": classification["error"]}))
                continue
            
            result = self.route_command(classification, command)
            # Ensure result is always JSON
            if result is None:
                result = {"success": False, "error": "Command processing failed"}
            print(json.dumps(result))

def main():
    classifier = CommandClassifier()
    classifier.main_loop()

if __name__ == "__main__":
    main() 