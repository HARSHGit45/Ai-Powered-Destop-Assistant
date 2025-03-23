import json
import sys
import os



from typing import Dict, Any
import platform
from pathlib import Path

GROQ_API_KEY="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"
from .file_operations.llm_manager import LLMManager
from .file_operations.embeddings_manager import EmbeddingsManager
from .file_operations.file_manager import FileManager

class FileAssistant:
    def __init__(self, silent=False):
        self.silent = silent
        self.file_manager = FileManager()
        self.embeddings_manager = EmbeddingsManager()
        self.llm_manager = LLMManager()
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the system by scanning directories and creating embeddings"""
        if not self.silent:
            print("Checking system state...")
        
        if self.embeddings_manager.load_embeddings():
            self._update_embeddings()
        else:
            directory_tree = self.file_manager.scan_system()
            self.file_manager.save_directory_tree(directory_tree)
            self.embeddings_manager.create_embeddings(directory_tree)

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
            print(f"Error executing command: {e}")
            return False

    def _update_embeddings(self):
        """Update embeddings with any new paths"""
        try:
            print("\n Checking for directory structure changes...")
            # Scan for new paths
            directory_tree = self.file_manager.scan_system()
            
            # Save updated directory tree
            self.file_manager.save_directory_tree(directory_tree)
            
            # Create new embeddings
            self.embeddings_manager.create_embeddings(directory_tree)
            print("✅ Directory structure is up to date.")
        except Exception as e:
            print(f"❌ Error updating embeddings: {str(e)}")

def main():
    assistant = FileAssistant()
    print("\n File Assistant is ready! Type 'exit' to quit.")
    print("\nAvailable commands:")
    print("- File operations: create, move, copy, delete files and folders")
    
    while True:
        try:
            command = input("\nEnter your command: ").strip()
            if command.lower() == 'exit':
                break
            if command:
                assistant.process_command(command)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 