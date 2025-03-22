import json
import sys
import os
from file_operations.embeddings_manager import EmbeddingsManager
from file_operations.file_manager import FileManager
from file_operations.llm_manager import LLMManager
from typing import Dict, Any
import platform
from pathlib import Path

GROQ_API_KEY="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"

class FileAssistant:
    def __init__(self):
        self.file_manager = FileManager()
        self.embeddings_manager = EmbeddingsManager()
        self.llm_manager = LLMManager()
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the system by scanning directories and creating embeddings"""
        print("🔄 Checking system state...")
        
        # Check if embeddings and directory tree already exist
        if self.embeddings_manager.load_embeddings():
            print("✅ Found existing embeddings")
            # Update embeddings with any new paths
            self._update_embeddings()
        else:
            print("⚠️ No existing embeddings found. Performing initial scan...")
            # Scan system for directory structure
            directory_tree = self.file_manager.scan_system()
            
            # Save directory tree
            self.file_manager.save_directory_tree(directory_tree)
            
            # Create embeddings for paths
            self.embeddings_manager.create_embeddings(directory_tree)
            
            print("✅ System initialized successfully!")

    def process_command(self, command: str) -> Dict:
        """Process a user command"""
        print(f"\n🔍 Processing command: {command}")
        
        try:
            # Search for similar paths
            similar_paths = self.embeddings_manager.search_paths(command)
            
            # Process command with LLM
            result = self.llm_manager.process_query(command, similar_paths)
            
            if result["command"]:
                # Handle file operation command
                print(f"📝 Generated command: {result['command']}")
                print(f"ℹ️ Explanation: {result['explanation']}")
                
                try:
                    # Execute the command
                    success = self.execute_command(result["command"])
                    if success:
                        print("✅ Command executed successfully!")
                        # Update embeddings with any new paths
                        self._update_embeddings()
                    else:
                        print("❌ Command execution failed")
                    
                    return {
                        "success": success,
                        "command": result["command"],
                        "explanation": result["explanation"]
                    }
                except Exception as e:
                    print(f"❌ Error executing command: {str(e)}")
                    return {
                        "success": False,
                        "message": f"Error executing command: {str(e)}"
                    }
            else:
                print("❌ No command generated")
                return {
                    "success": False,
                    "message": "No command generated"
                }
            
        except Exception as e:
            print(f"❌ Error processing command: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing command: {str(e)}"
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
            print("\n🔄 Checking for directory structure changes...")
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
    print("\n🤖 File Assistant is ready! Type 'exit' to quit.")
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