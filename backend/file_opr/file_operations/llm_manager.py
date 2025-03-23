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