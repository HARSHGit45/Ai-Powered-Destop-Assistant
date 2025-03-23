import os
import json
from dotenv import load_dotenv
from groq import Groq
from browser_operations.browser_manager import BrowserOperations

# Load environment variables
load_dotenv()

class BrowserAssistant:
    def __init__(self):
        # Initialize Groq client for natural language processing if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        self.use_llm = bool(api_key)
        if self.use_llm:
            self.client = Groq(api_key=api_key)
        
        # Initialize BrowserOperations
        self.browser_ops = BrowserOperations()
        
    def __del__(self):
        # Clean up browser when object is destroyed
        if hasattr(self, 'browser_ops'):
            self.browser_ops.close()

    def generate_command(self, user_input: str) -> dict:
        """Generate structured browser command using LLM based on natural language input"""
        if not self.use_llm:
            # Use simple rule-based parsing if no API key
            return self.parse_command(user_input)
            
        system_prompt = """You are a Python code generator for web browser operations. Generate ONLY a JSON object that should be executed, with no explanations or formatting.

Available browser actions:
1. "action_type": "open_browser"
   - "browser": "chrome", "firefox", "edge", or "opera"

2. "action_type": "search" 
   - "query": "search term"
   - "search_engine": "google", "bing", "yahoo", or "duckduckgo"

3. "action_type": "navigate"
   - "url": "website.com"

4. "action_type": "youtube"
   - "query": "search term" 
   - "youtube_action": "search" or "play"

5. "action_type": "social_media"
   - "platform": "facebook", "twitter", "instagram", "linkedin", or "reddit"
   - "social_action": null (just open the site)

6. "action_type": "email"
   - "email_action": "compose", "send", or "open"
   - "recipient": "email@example.com" (optional)
   - "subject": "Email subject" (optional)
   - "body": "Email body" (optional)

Examples:
For "open chrome browser":
{"action_type":"open_browser","browser":"chrome"}

For "search for python tutorials":
{"action_type":"search","query":"python tutorials","search_engine":"google"}

For "go to github.com":
{"action_type":"navigate","url":"github.com"}

For "search YouTube for funny cats":
{"action_type":"youtube","query":"funny cats","youtube_action":"search"}

For "play music videos on YouTube":
{"action_type":"youtube","query":"music videos","youtube_action":"play"}

For "open Facebook":
{"action_type":"social_media","platform":"facebook"}

For "compose email to john@example.com":
{"action_type":"email","email_action":"compose","recipient":"john@example.com"}"""

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Using smaller model for speed
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract the JSON from the response
            raw_response = completion.choices[0].message.content.strip()
            
            # Try to parse the response as JSON
            try:
                # Clean up the response - remove any markdown code formatting
                clean_response = raw_response.replace("```json", "").replace("```", "").strip()
                command_data = json.loads(clean_response)
                return command_data
            except json.JSONDecodeError:
                print(f"Error: Could not parse LLM response as JSON. Using fallback parsing.")
                return self.parse_command(user_input)
                
        except Exception as e:
            print(f"LLM error: {e}")
            return self.parse_command(user_input)

    def parse_command(self, command_text):
        """Fallback method to parse text command into a structured command for BrowserOperations"""
        words = command_text.split()
        
        if not words:
            return None
        
        # Handle browser opening
        if words[0].lower() == "open":
            if len(words) > 1:
                if words[1].lower() in ["chrome", "firefox", "edge", "opera"]:
                    return {
                        "action_type": "open_browser",
                        "browser": words[1].lower()
                    }
                elif words[1].lower() in ["facebook", "twitter", "instagram", "linkedin", "reddit"]:
                    return {
                        "action_type": "social_media",
                        "platform": words[1].lower()
                    }
                elif words[1].lower() == "youtube":
                    if len(words) > 2:
                        return {
                            "action_type": "youtube",
                            "query": " ".join(words[2:]),
                            "youtube_action": "search"
                        }
                    else:
                        return {
                            "action_type": "navigate",
                            "url": "youtube.com"
                        }
                elif words[1].lower() == "gmail":
                    return {
                        "action_type": "navigate",
                        "url": "mail.google.com"
                    }
                else:
                    # Assume it's a website
                    return {
                        "action_type": "navigate",
                        "url": words[1]
                    }
        
        # Handle search
        elif words[0].lower() == "search":
            if len(words) > 1:
                # Check if searching on specific platform
                if len(words) > 2 and words[1].lower() in ["on", "in", "using", "with"]:
                    platform = words[2].lower() 
                    query = " ".join(words[3:])
                    
                    if platform in ["google", "bing", "yahoo", "duckduckgo"]:
                        return {
                            "action_type": "search",
                            "query": query,
                            "search_engine": platform
                        }
                    elif platform == "youtube":
                        return {
                            "action_type": "youtube",
                            "query": query,
                            "youtube_action": "search"
                        }
                else:
                    # Default search on Google
                    query = " ".join(words[1:])
                    return {
                        "action_type": "search",
                        "query": query,
                        "search_engine": "google"
                    }
        
        # Handle navigation
        elif words[0].lower() in ["navigate", "go", "visit"]:
            if len(words) > 1:
                # Skip "to" if present
                start_idx = 2 if words[1].lower() == "to" else 1
                url = " ".join(words[start_idx:])
                return {
                    "action_type": "navigate",
                    "url": url
                }
        
        # Handle YouTube
        elif words[0].lower() == "youtube":
            if len(words) > 1:
                query = " ".join(words[1:])
                return {
                    "action_type": "youtube",
                    "query": query,
                    "youtube_action": "search"
                }
        
        # Handle YouTube play
        elif words[0].lower() == "play" and len(words) > 1:
            if words[1].lower() == "youtube" and len(words) > 2:
                query = " ".join(words[2:])
            else:
                query = " ".join(words[1:])
                
            return {
                "action_type": "youtube",
                "query": query,
                "youtube_action": "play"
            }
        
        # Handle social media
        elif words[0].lower() in ["facebook", "twitter", "instagram", "linkedin", "reddit"]:
            return {
                "action_type": "social_media",
                "platform": words[0].lower()
            }
            
        # Handle email
        elif words[0].lower() in ["email", "mail", "gmail"]:
            if len(words) > 1:
                if words[1].lower() == "compose" and len(words) > 2:
                    # Try to extract recipient
                    recipient = None
                    for i, word in enumerate(words[2:]):
                        if "@" in word:
                            recipient = word
                            break
                            
                    return {
                        "action_type": "email",
                        "email_action": "compose",
                        "recipient": recipient
                    }
                elif words[1].lower() == "send":
                    return {
                        "action_type": "email",
                        "email_action": "send"
                    }
            else:
                # Just open Gmail
                return {
                    "action_type": "navigate",
                    "url": "mail.google.com"
                }
        
        # Default case - treat as URL
        if len(words) == 1 and "." in words[0]:
            return {
                "action_type": "navigate",
                "url": words[0]
            }
            
        # Default case - treat as search
        return {
            "action_type": "search",
            "query": command_text,
            "search_engine": "google"
        }

    def process_command(self, user_input: str) -> dict:
        """Process a user command"""
        try:
            # Generate structured command from natural language input
            command_data = self.generate_command(user_input)
            
            if command_data:
                # Execute the command
                result = self.browser_ops.process_command(command_data)
                return result
            else:
                return {"success": False, "error": "Could not understand command"}
        except Exception as e:
            return {"success": False, "error": f"Error processing command: {str(e)}"}


def main():
    print("\n=== Web Browser Assistant ===")
    print("Control your web browser with natural language commands.")
    print("Type 'exit' to quit.")
    print("\nExample commands:")
    print("- 'open chrome'")
    print("- 'search for python tutorials'")
    print("- 'go to github.com'")
    print("- 'youtube funny cats videos'")
    print("- 'play music videos on youtube'")
    print("- 'open facebook'")
    print("- 'gmail compose'")
    
    # Initialize the browser assistant
    assistant = BrowserAssistant()
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip()
            
            if user_input.lower() == 'exit':
                print("Closing browser and exiting...")
                assistant.browser_ops.close()
                break
                
            if user_input:
                result = assistant.process_command(user_input)
                if result["success"]:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['error']}")
                    
        except KeyboardInterrupt:
            print("\nDetected Ctrl+C. Closing browser and exiting...")
            assistant.browser_ops.close()
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("Goodbye!")


if __name__ == "__main__":
    main()