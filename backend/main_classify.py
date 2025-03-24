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
        from file_opr.main import FileAssistant
        self.file_assistant = FileAssistant(silent=True)
        
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
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Set dynamic energy threshold
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 4000  # Initial threshold
                
             
                audio = self.recognizer.listen(
                    source,
                    timeout=5,  # Maximum time to wait for speech to start
                    phrase_time_limit=5,  # Maximum time for a single phrase
                    snowboy_configuration=None  # Disable snowboy for better phrase detection
                )
                
                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                return text
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
        except Exception:
            return None

    def accept_command(self, command: str = None):
        """Accept text command from user input"""
        try:
            if command:
                return command.strip()
            return None
        except Exception:
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
        """Main loop to process commands from stdin"""
        while True:
            try:
                # Read JSON input from stdin
                input_line = sys.stdin.readline()
                if not input_line:
                    continue
                    
                # Parse the JSON input
                input_data = json.loads(input_line)
                command_type = input_data.get('type')
                command = input_data.get('command')
                
                if not command:
                    continue
                
                # Process command based on type
                if command_type == 'text':
                    command_text = self.accept_command(command)
                elif command_type == 'voice':
                    command_text = self.listen_command()
                else:
                    print("Error: Invalid command type")
                    continue
                
                if not command_text:
                    continue
                    
                # Classify and route the command
                classification = self.classify_command(command_text)
                if classification["type"] == "EXIT":
                    print("Goodbye!")
                    break
                elif classification["type"] == "ERROR":
                    print(f"Error: {classification['error']}")
                    continue
                
                # Route the command and get result
                result = self.route_command(classification, command_text)
                
                # Print result to terminal
                if result.get("success"):
                    print(f"Success: {result.get('result', 'Command executed successfully')}")
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("Goodbye!")
                break
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON input - {str(e)}")
            except Exception as e:
                print(f"Error: {str(e)}")
            
            # Flush stdout to ensure output is sent
            sys.stdout.flush()

def main():
    classifier = CommandClassifier()
    classifier.main_loop()

if __name__ == "__main__":
    main() 