import json
import os
from typing import Dict
from groq import Groq
import psutil
import subprocess
import win32gui
import win32con
import winreg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class AppController:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.apps_data = self.load_apps_data()

    def load_apps_data(self):
        json_file = "found_apps.json"
        
        if not os.path.exists(json_file):
            print("Scanning for applications...")
            return self.discover_applications()
            
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading apps data: {e}")
            print("Falling back to application discovery...")
            return self.discover_applications()

    def discover_applications(self):
        preferred_apps = {
            "VS Code": "code.exe",
            "Google Chrome": "chrome.exe",
            "Cursor": "cursor.exe",
            "WhatsApp": "WhatsApp.exe",
            "Microsoft Edge": "msedge.exe",
            "Firefox": "firefox.exe",
            "XAMPP": "xampp-control.exe",
            "MySQL Workbench": "MySQLWorkbench.exe",
            "Jupyter Notebook": "jupyter-notebook.exe",
            "Notepad": "notepad.exe",
            "Microsoft Word": "WINWORD.EXE",
            "Microsoft Excel": "EXCEL.EXE",
            "Microsoft PowerPoint": "POWERPNT.EXE",
            "Microsoft Paint": "mspaint.exe"
        }

        search_dirs = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming"),
            "C:\\Windows\\System32",
            "C:\\Users\\Public\\Desktop",
            os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code"),
            "C:\\Program Files\\Microsoft VS Code"
        ]

        found_apps = {}
        
        # Find Office apps in registry
        reg_paths = {
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WINWORD.EXE": "Microsoft Word",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\EXCEL.EXE": "Microsoft Excel",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\POWERPNT.EXE": "Microsoft PowerPoint"
        }

        for reg_path, app_name in reg_paths.items():
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    app_path, _ = winreg.QueryValueEx(key, "")
                    found_apps[app_name] = app_path
            except Exception:
                continue

        # Search directories for other apps
        for directory in search_dirs:
            if os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for app_name, exe_name in preferred_apps.items():
                        if exe_name in files and app_name not in found_apps:
                            found_apps[app_name] = os.path.join(root, exe_name)

        with open("found_apps.json", "w") as f:
            json.dump(found_apps, f, indent=4)

        return found_apps

    def process_command(self, command: str):
        try:
            generated_command = self.generate_command(command)
            if generated_command.get("operation") == "ERROR":
                return generated_command
            
            return self.execute_command(generated_command)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_command(self, user_query: str):
        system_prompt = f"""Match user's intent for application control.
        Available apps: {', '.join(self.apps_data.keys())}
        
        Return JSON with:
        - operation: OPEN/CLOSE/SWITCH/LIST
        - app_name: exact app name from available list
        - confidence: 0-100"""

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this to JSON: {user_query}"}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            try:
                return json.loads(completion.choices[0].message.content)
            except json.JSONDecodeError:
                return self.fallback_command_parser(user_query)

        except Exception:
            return self.fallback_command_parser(user_query)

    def fallback_command_parser(self, query):
        query = query.lower().strip()
        
        def find_app_match(query):
            for app_name in self.apps_data.keys():
                app_lower = app_name.lower()
                variations = [
                    app_lower,
                    app_lower.replace(" ", ""),
                    app_lower.split()[-1],
                    ''.join(word[0] for word in app_lower.split())
                ]
                if any(var in query or query in var for var in variations):
                    return app_name
            return None

        operation_keywords = {
            "OPEN": ['open', 'start', 'run', 'launch'],
            "CLOSE": ['close', 'exit', 'quit', 'kill'],
            "SWITCH": ['switch', 'goto', 'show', 'change'],
            "LIST": ['list', 'running', 'what', 'show all']
        }

        for op, keywords in operation_keywords.items():
            if any(word in query for word in keywords):
                if op == "LIST":
                    return {"operation": "LIST", "app_name": "", "confidence": 85}
                
                app_name = find_app_match(query)
                if app_name:
                    return {"operation": op, "app_name": app_name, "confidence": 75}

        return {"operation": "LIST", "app_name": "", "confidence": 60}

    def execute_command(self, command):
        try:
            operation = command["operation"]
            
            if operation == "LIST":
                running_apps = self.list_running_apps()
                return {"success": True, "result": f"Running: {', '.join(running_apps)}"}

            app_name = command["app_name"]
            app_path = self.apps_data.get(app_name)
            
            if not app_path:
                return {"success": False, "error": f"App '{app_name}' not found"}

            operations = {
                "OPEN": lambda: subprocess.Popen([app_path]),
                "CLOSE": lambda: self.close_app(app_name),
                "SWITCH": lambda: self.switch_to_app(app_name)
            }

            if operation in operations:
                operations[operation]()
                return {"success": True, "result": f"{operation.capitalize()}ed {app_name}"}

            return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_running_apps(self):
        running_apps = []
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                proc_path = proc.info['exe']
                if proc_path:
                    for app_name, app_path in self.apps_data.items():
                        if proc_path.lower() == app_path.lower():
                            running_apps.append(app_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return running_apps

    def close_app(self, app_name):
        app_path = self.apps_data[app_name]
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['exe'] and proc.info['exe'].lower() == app_path.lower():
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def switch_to_app(self, app_name):
        def window_enum_handler(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if app_name.lower() in window_title.lower():
                    windows.append(hwnd)

        windows = []
        win32gui.EnumWindows(window_enum_handler, windows)
        
        if windows:
            hwnd = windows[0]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)

def main():
    controller = AppController()
    print("\nApp Controller Ready")
    print("\nCommands:")
    print("- open [app]")
    print("- close [app]")
    print("- switch [app]")
    print("- list apps")
    print("\nAvailable apps:")
    for app in controller.apps_data.keys():
        print(f"- {app}")
    
    while True:
        try:
            command = input("\nCommand: ").strip()
            if command.lower() == 'exit':
                print("Goodbye!")
                break
            if command:
                result = controller.process_command(command)
                print(json.dumps(result))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main() 