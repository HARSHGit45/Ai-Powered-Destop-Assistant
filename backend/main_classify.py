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
        
        self.system_prompt = """You are a command classifier. Analyze the user's command and return ONLY a valid JSON object.

Rules:
1. Always return valid JSON
2. No explanations or additional text
3. Only return the JSON object

Example command: "volume 100%"
Example response:
{
    "type": "SYSTEM_CONTROL",
    "confidence": 95,
    "keywords": ["volume", "audio", "sound"],
    "command": "volume 100%"
}

Example command: "delete my documents"
Example response:
{
    "type": "FILE_OPERATION",
    "confidence": 90,
    "keywords": ["delete", "remove", "documents"],
    "command": "delete my documents"
}

Classify commands into:
1. FILE_OPERATION - for file management tasks (create, delete, move, copy, search files)
2. SYSTEM_CONTROL - for system settings (brightness, volume, wifi, bluetooth, battery)"""

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
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Classify this command: {command}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(completion.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error classifying command: {e}")
            print(f"Raw LLM response: {completion.choices[0].message.content}")  # Debug line
            return None

    def route_command(self, classification, original_command):
        """Route the command to appropriate handler"""
        try:
            if classification["type"] == "FILE_OPERATION":
                return self.file_assistant.process_command(original_command)
                
            elif classification["type"] == "SYSTEM_CONTROL":
                from system_controls.main import process_command
                return process_command(original_command)
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def main_loop(self):
        while True:
            command = self.listen_command()
            if not command:
                continue
                
            classification = self.classify_command(command)
            if not classification:
                print("Failed to process command")
                continue
            
            result = self.route_command(classification, command)
            if result and result.get("success"):
                print(result.get("result", "Command executed successfully"))
            else:
                print(result.get("error", "Failed to execute command"))

def main():
    classifier = CommandClassifier()
    classifier.main_loop()

if __name__ == "__main__":
    main() 