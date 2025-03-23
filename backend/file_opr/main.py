import json
import sys
import os
from .file_operations.embeddings_manager import EmbeddingsManager
from .file_operations.file_manager import FileManager
from .file_operations.llm_manager import LLMManager

from typing import Dict, Any
import platform
from pathlib import Path

GROQ_API_KEY="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"

class FileAssistant:
    def __init__(self, silent=False):
        self.silent = silent
        self.file_manager = FileManager()
        self.embeddings_manager = EmbeddingsManager()
        self.llm_manager = LLMManager()
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the system by loading existing embeddings or creating new ones if they don't exist"""
        if self.embeddings_manager.load_embeddings():
            return True
        else:
            # Create new embeddings only if they don't exist
            directory_tree = self.file_manager.scan_system()
            self.file_manager.save_directory_tree(directory_tree)
            self.embeddings_manager.create_embeddings(directory_tree)
            return True

    def process_command(self, command: str) -> Dict:
        """Process a user command"""
        try:
            similar_paths = self.embeddings_manager.search_paths(command)
            result = self.llm_manager.process_query(command, similar_paths)
            
            if result["command"]:
                success = self.execute_command(result["command"])
                if success:
                    return {
                        "success": True,
                        "result": result["explanation"]  # Return user-friendly explanation
                    }
                return {
                    "success": False,
                    "error": "Failed to execute command"
                }
            return {
                "success": False,
                "error": "Could not understand command"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute_command(self, command: str) -> bool:
        """Execute a Python command safely"""
        try:
            # Create a new namespace for execution
            namespace = {}
            
            # Add required imports
            if "os" in command:
                namespace["os"] = os
            if "shutil" in command:
                import shutil
                namespace["shutil"] = shutil
            
            # Execute the command
            exec(command, namespace)
            return True
        except Exception as e:
            return False

def main():
    assistant = FileAssistant()
    print("\nFile Assistant is ready! Type 'exit' to quit.")
    
    while True:
        try:
            command = input("\nEnter your command: ").strip()
            if command.lower() == 'exit':
                break
            if command:
                result = assistant.process_command(command)
                print(json.dumps(result))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main() 