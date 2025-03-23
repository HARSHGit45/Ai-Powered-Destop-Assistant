import speech_recognition as sr
import json
from groq import Groq
import os
import sys
from dotenv import load_dotenv

load_dotenv()

class CommandClassifier:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Load embeddings at startup
        print("Initializing system...")

        # Import file operations
        from file_opr.main import FileAssistant
        self.file_assistant = FileAssistant(silent=True)

        # Import browser operations
        from browser_operations.main import BrowserAssistant
        self.browser_assistant = BrowserAssistant()

        # Import app control (new)
        from app_controls.main import AppController
        self.app_controller = AppController()

        print("Ready! Speak a command...")

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

Example command: "search for weather in New York"
Example response:
{
    "type": "BROWSER_OPERATION",
    "confidence": 95,
    "keywords": ["search", "browser", "weather"],
    "command": "search for weather in New York"
}

Classify commands into:
1. FILE_OPERATION - for file management tasks (create, delete, move, copy, search files)
2. SYSTEM_CONTROL - for system settings (brightness, volume, wifi, bluetooth, battery)
3. BROWSER_OPERATION - for browser tasks (open websites, search, email, YouTube, social media)
4. APP_CONTROL - for application control (open, close, switch between apps)
"""

    def listen_command(self):
        """Listen for voice command and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio).strip()
                print(f"Recognized: {text}")
                return text
        except Exception as e:
            print(f"❌ Error: Could not understand audio - {str(e)}")
            return None

    def classify_command(self, command: str):
        """Classify the command using LLM"""
        if not command:
            return None

        # Handle exit command specially
        if command.lower() in ['exit', 'quit', 'bye', 'thank you']:
            return {
                "type": "EXIT",
                "confidence": 100,
                "keywords": ["exit"],
                "command": command
            }

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": command}
                ],
                temperature=0.1,
                max_tokens=500
            )

            try:
                result = json.loads(completion.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # Fallback classification if LLM response fails
                return self.manual_classification(command)

        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            return self.manual_classification(command)

    def manual_classification(self, command: str):
        """Fallback method for classifying commands manually"""
        command_lower = command.lower()

        # ✅ Ensure "Open Chrome" works properly
        if any(word in command_lower for word in ['search', 'browser', 'website', 'youtube', 'google']):
            return {
                "type": "BROWSER_OPERATION",
                "confidence": 90,
                "keywords": ["browser", "search"],
                "command": command
            }

        elif any(word in command_lower for word in ['open', 'launch', 'start', 'run']):
            if any(browser in command_lower for browser in ['chrome', 'firefox', 'edge', 'opera', 'explorer']):
                return {
                    "type": "BROWSER_OPERATION",
                    "confidence": 95,
                    "keywords": ["open", "browser"],
                    "command": command
                }
            else:
                return {
                    "type": "APP_CONTROL",
                    "confidence": 85,
                    "keywords": ["application", "control"],
                    "command": command
                }

        elif any(word in command_lower for word in ['volume', 'brightness', 'wifi', 'bluetooth']):
            return {
                "type": "SYSTEM_CONTROL",
                "confidence": 90,
                "keywords": ["system", "settings"],
                "command": command
            }

        else:
            return {
                "type": "FILE_OPERATION",
                "confidence": 80,
                "keywords": ["file", "operation"],
                "command": command
            }

    def route_command(self, classification, original_command):
        """Route the command to the appropriate handler"""
        try:
            if classification["type"] == "FILE_OPERATION":
                return self.file_assistant.process_command(original_command)

            elif classification["type"] == "SYSTEM_CONTROL":
                from system_controls.main import process_command
                return process_command(original_command)

            elif classification["type"] == "BROWSER_OPERATION":
                return self.browser_assistant.process_command(original_command)

            elif classification["type"] == "APP_CONTROL":
                return self.app_controller.process_command(original_command)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def main_loop(self):
        """Main loop for voice command processing"""
        print("\n=== Voice Command Assistant ===")
        print("🎤 Control your system with voice commands.")
        print("Say 'exit' or 'quit' to end the session.\n")

        while True:
            command = self.listen_command()
            if not command:
                continue

            classification = self.classify_command(command)
            if classification["type"] == "EXIT":
                print(json.dumps({"success": True, "result": "Goodbye!"}))
                if hasattr(self, 'browser_assistant'):
                    self.browser_assistant.browser_ops.close()
                break
            elif classification["type"] == "ERROR":
                print(json.dumps({"success": False, "error": classification["error"]}))
                continue

            result = self.route_command(classification, command)
            if result is None:
                result = {"success": False, "error": "Command processing failed"}

            if result["success"]:
                print(f"✅ {result.get('message', 'Command executed successfully')}")
            else:
                print(f"❌ {result.get('error', 'Unknown error occurred')}")

    def __del__(self):
        """Clean up resources on object destruction"""
        if hasattr(self, 'browser_assistant') and hasattr(self.browser_assistant, 'browser_ops'):
            self.browser_assistant.browser_ops.close()

def main():
    try:
        classifier = CommandClassifier()
        classifier.main_loop()
    except KeyboardInterrupt:
        print("\n🔴 Detected Ctrl+C. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
