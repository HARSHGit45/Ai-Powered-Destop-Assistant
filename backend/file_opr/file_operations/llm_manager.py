# Modified llm_manager.py to include browser operations prompting
import os
from groq import Groq
from dotenv import load_dotenv
import json
import re

load_dotenv()

class LLMManager:
    def __init__(self):
       
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.api_key)
        self.system_prompt = """You are an AI assistant that helps users with file operations.
Your task is to analyze user requests and generate appropriate Python commands for file operations.

For file operations, you should:
1. Use the provided similar paths to find relevant locations
2. Generate Python commands using os, shutil, or other file operation libraries
3. Return a JSON object with:
   - command: The Python command to execute
   - explanation: A clear explanation of what the command does
   - imports: List of required Python imports

Example response:
{
    "command": "os.makedirs('C:/Users/username/Documents/NewFolder', exist_ok=True)",
    "explanation": "Creates a new folder named 'NewFolder' in the Documents directory",
    "imports": ["os"]
}

IMPORTANT: 
1. Return ONLY a valid JSON object. Do not include any additional text, markdown formatting, or code blocks.
2. Always use absolute paths based on the similar paths provided.
3. Include proper error handling in the commands."""

        self.browser_system_prompt = """You are an AI assistant that helps users with browser operations.
Your task is to analyze user requests and generate appropriate instructions for browser automation.

For browser operations, you should:
1. Identify the specific action the user wants to perform (search, navigate, email, etc.)
2. Extract important parameters like search queries, URLs, email details, etc.
3. Return a JSON object with the necessary information to execute the browser command.

Return a JSON object with:
   - action_type: The type of browser action (search, navigate, email, youtube, social_media, open_browser)
   - browser: Browser to use (chrome, firefox, edge, opera) if specified
   - Additional parameters based on the action type

Example response for search:
{
    "action_type": "search",
    "browser": "chrome",
    "query": "weather in New York",
    "search_engine": "google"
}

Example response for email:
{
    "action_type": "email",
    "browser": "chrome",
    "email_action": "compose",
    "recipient": "example@example.com",
    "subject": "Meeting tomorrow",
    "body": "Hi, let's meet tomorrow at 2pm."
}

IMPORTANT: 
1. Return ONLY a valid JSON object. Do not include any additional text, markdown formatting, or code blocks.
2. Include all necessary parameters for the specific action type."""

    def process_query(self, query: str, similar_paths: list = None) -> dict:
        """Process a user query and generate appropriate commands"""
        try:
            # Prepare context for the LLM
            context = "User Query: " + query + "\n\n"
            
            if similar_paths:
                context += "Relevant Paths:\n"
                for path in similar_paths:
                    context += f"- {path}\n"
                context += "\n"
            
           
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            
            content = response.choices[0].message.content.strip()
            
          
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Parse JSON response
            result = json.loads(content)
            
            # Validate response format
            required_fields = ["command", "explanation", "imports"]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in response")
            
            return result
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print(f"Raw response: {content if 'content' in locals() else 'No response'}")
            return {
                "command": "",
                "explanation": f"Error processing query: {str(e)}",
                "imports": []
            }
            
    def process_browser_query(self, query: str) -> dict:
            """Process a browser-related query and generate appropriate commands"""
            try:
                # Ensure query is a string before sending to LLM
                if not isinstance(query, str):
                    query = json.dumps(query)  # Convert dict to string safely
                
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": self.browser_system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )

                # Check if response contains valid choices
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Invalid LLM response: No content returned")

                content = response.choices[0].message.content.strip()

                # Ensure content is valid before processing
                if not content:
                    raise ValueError("Empty response from LLM")

                # Clean up any code blocks
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*', '', content)

                # Parse JSON response safely
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    raise ValueError("LLM returned invalid JSON format")

                # Validate response structure
                if "action_type" not in result:
                    raise ValueError("Missing 'action_type' in response")

                return result

            except Exception as e:
                print(f"Error processing browser query: {e}")
                print(f"Raw response: {content if 'content' in locals() else 'No response'}")
                return {
                    "action_type": "error",
                    "error": f"Error processing query: {str(e)}"
                }
