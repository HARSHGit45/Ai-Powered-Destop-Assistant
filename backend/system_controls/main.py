import os
import sys
import subprocess
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import re
import psutil
import pywifi
from pywifi import const
import time
import asyncio
from bleak import BleakScanner
from groq import Groq
from dotenv import load_dotenv
import ctypes
import win32com.shell.shell as shell
import pythoncom
from typing import Dict
load_dotenv()

class SystemControls:
    def __init__(self):
        # Initialize Groq client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Initialize COM for Windows
        pythoncom.CoInitialize()
        
        # Initialize volume control
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def __del__(self):
        # Cleanup COM when the object is destroyed
        pythoncom.CoUninitialize()

    def generate_code(self, command: str) -> str:
        """Generate Python code using LLM based on the command"""
        system_prompt = """You are a Python code generator for system controls. Generate ONLY the Python code that should be executed, with no explanations or markdown formatting.

Available functions:
1. Brightness Control:
   - sbc.get_brightness()[0] -> Get current brightness (0-100)
   - sbc.set_brightness(value) -> Set brightness (0-100)

2. Volume Control:
   - self.volume.GetMasterVolumeLevelScalar() -> Get current volume (0-1)
   - self.volume.SetMasterVolumeLevelScalar(value, None) -> Set volume (0-1)

3. Battery Status:
   - psutil.sensors_battery() -> Returns battery information
     - .percent -> Battery percentage
     - .power_plugged -> True if plugged in, False if not

4. WiFi Control:
   - wifi = pywifi.PyWiFi()
   - iface = wifi.interfaces()[0]
   - iface.scan()  # Scan for networks
   - scan_results = iface.scan_results()  # Get scan results
   - iface.status()  # Get connection status
   - iface.disconnect()  # Disconnect from current network
   - const.IFACE_CONNECTED  # Check if connected

5. Bluetooth Control:
   - async with BleakScanner() as scanner:
       devices = await scanner.discover()  # Scan for devices
   - device.name  # Get device name
   - device.address  # Get device address
   - device.is_connected  # Check connection status

Example commands and their code:

1. For "what's the brightness?":
current_brightness = sbc.get_brightness()[0]
print(f'Current brightness is {current_brightness}%')

2. For "make it louder":
current_volume = self.volume.GetMasterVolumeLevelScalar()
new_volume = min(1.0, current_volume + 0.1)
self.volume.SetMasterVolumeLevelScalar(new_volume, None)
print(f'Volume increased to {int(new_volume * 100)}%')

3. For "dim the screen":
current_brightness = sbc.get_brightness()[0]
new_brightness = max(0, current_brightness - 10)
sbc.set_brightness(new_brightness)
print(f'Brightness decreased to {new_brightness}%')

4. For "get battery status" or "what's my battery":
battery = psutil.sensors_battery()
if battery:
    percent = battery.percent
    plugged = battery.power_plugged
    status = "Plugged In" if plugged else "Not Plugged In"
    print(f"Battery Percentage: {percent}%")
    print(f"Power Status: {status}")
else:
    print("No battery detected")

4. For "show wifi networks":
wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[0]
iface.scan()
time.sleep(2)
scan_results = iface.scan_results()
if not scan_results:
    print("No WiFi networks found.")
else:
    print("Available WiFi Networks:")
    for idx, network in enumerate(scan_results, start=1):
        print(f"{idx}. {network.ssid} (Signal Strength: {network.signal} dBm)")

5. For "show connected wifi":
wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[0]
iface.scan()
profile = iface.status()
if profile == const.IFACE_CONNECTED:
    print(f"Currently connected to WiFi: {iface.network_profiles()[0].ssid}")
else:
    print("Not connected to any WiFi network.")

6. For "show bluetooth devices":
async def scan_bluetooth():
    print("Scanning for Bluetooth devices...")
    async with BleakScanner() as scanner:
        devices = await scanner.discover()
        if not devices:
            print("No Bluetooth devices found.")
        else:
            print("\\nFound Bluetooth Devices:")
            for idx, device in enumerate(devices, start=1):
                print(f"{idx}. {device.name or 'Unknown'} - {device.address}")
asyncio.run(scan_bluetooth())

7. For "turn bluetooth on":
if run_as_admin("bluetooth"):
    try:
        subprocess.run(["powershell", "Enable-PnpDevice -InstanceId (Get-PnpDevice -Class Bluetooth | Select-Object -ExpandProperty InstanceId) -Confirm:$false"], shell=True)
        print("✅ Bluetooth turned ON.")
    except Exception as e:
        print(f"❌ Failed to turn Bluetooth ON: {str(e)}")

8. For "turn bluetooth off":
if run_as_admin("bluetooth"):
    try:
        subprocess.run(["powershell", "Disable-PnpDevice -InstanceId (Get-PnpDevice -Class Bluetooth | Select-Object -ExpandProperty InstanceId) -Confirm:$false"], shell=True)
        print("✅ Bluetooth turned OFF.")
    except Exception as e:
        print(f"❌ Failed to turn Bluetooth OFF: {str(e)}")

9. For "turn wifi on":
if run_as_admin("wifi"):
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "name=\"Wi-Fi\"", "admin=enabled"], shell=True)
        print("✅ WiFi turned ON.")
    except Exception as e:
        print(f"❌ Failed to turn WiFi ON: {str(e)}")

10. For "turn wifi off":
if run_as_admin("wifi"):
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "name=\"Wi-Fi\"", "admin=disabled"], shell=True)
        print("✅ WiFi turned OFF.")
    except Exception as e:
        print(f"❌ Failed to turn WiFi OFF: {str(e)}")

Important:
1. Generate ONLY the Python code, no explanations
2. No markdown formatting or code blocks
3. No imports (they are already available)
4. Use print() statements for output
5. Use proper Python syntax"""

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": command}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extract the code from the response
            raw_response = completion.choices[0].message.content.strip()
            
            # Clean up the code
            code = re.sub(r'```python|```', '', raw_response)  # Remove markdown code blocks
            code = re.sub(r'^\s*import.*$', '', code, flags=re.MULTILINE)  # Remove import statements
            code = re.sub(r'^\s*#.*$', '', code, flags=re.MULTILINE)  # Remove comments
            code = '\n'.join(line for line in code.split('\n') if line.strip())  # Remove empty lines
            
            # Indent each line of the code with 4 spaces
            indented_code = '\n'.join('    ' + line for line in code.split('\n'))
            
            # Add error handling with proper indentation
            final_code = f"""try:
{indented_code}
except Exception as e:
    print(f'Error: {{str(e)}}')"""
            
            return final_code
        except Exception as e:
            print(f"Error generating code: {e}")
            return None

    def execute_code(self, code: str) -> None:
        """Execute the generated Python code"""
        try:
            namespace = {
                'sbc': sbc,
                'AudioUtilities': AudioUtilities,
                'IAudioEndpointVolume': IAudioEndpointVolume,
                'CLSCTX_ALL': CLSCTX_ALL,
                'cast': cast,
                'POINTER': POINTER,
                'subprocess': subprocess,
                'psutil': psutil,
                'pywifi': pywifi,
                'const': const,
                'BleakScanner': BleakScanner,
                'asyncio': asyncio,
                'time': time,
                'os': os,
                'self': self,
                'run_as_admin': run_as_admin
            }
            
            exec(code, namespace)
            
        except Exception as e:
            print(f'Error executing code: {str(e)}')

def run_as_admin():
    """Check if running as admin and restart with admin privileges if not"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Re-run the program with admin rights
        script = os.path.abspath(sys.argv[0])
        params = ' '.join(sys.argv[1:])
        try:
            shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=f'"{script}" {params}')
            print("Please run the new window that opened with administrator privileges.")
            return False
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            return False
    return True

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_admin_required(command: str) -> bool:
    """Check if the command requires admin privileges"""
    admin_commands = ['wifi', 'bluetooth', 'network', 'interface']
    return any(cmd in command.lower() for cmd in admin_commands)

def process_command(command: str) -> Dict:
    """Process a system control command"""
    try:
        controls = SystemControls()
        code = controls.generate_code(command)
        if code:
            controls.execute_code(code)
            return {
                "success": True,
                "result": "Command executed successfully"  # LLM's response will be printed directly
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

def main():
    print("\nSystem Controls Assistant is ready! Type 'exit' to quit.")
    print("\nYou can use natural language commands like:")
    print("- 'what's the brightness?' or 'show me the brightness'")
    print("- 'make it louder' or 'turn up the volume'")
    print("- 'dim the screen' or 'lower the brightness'")
    print("- 'show system info' or 'what's running?'")
    print("- 'get battery status' or 'how's the battery?'")
    print("- 'show wifi networks' or 'what networks are available?'")
    print("- 'show connected wifi' or 'what's my current wifi?'")
    print("- 'show bluetooth devices' or 'what devices are connected?'")
    print("- 'show connected bluetooth' or 'what devices are connected?'")
    print("- 'turn bluetooth on' or 'turn bluetooth off'")
    print("- 'turn wifi on' or 'turn wifi off'")
    print("\nNote: WiFi and Bluetooth controls will automatically request administrator privileges when needed.")
    print("\nJust type what you want in any way you want!")
    
    while True:
        try:
            command = input("\nEnter your command: ").strip()
            if command.lower() == 'exit':
                break
            if command:
                process_command(command)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()