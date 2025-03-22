import speech_recognition as sr
import sys
import json
import threading
import queue

# Global variables for control
should_stop = False
command_queue = queue.Queue()

def listen_and_convert():
    global should_stop
    should_stop = False
    recognizer = sr.Recognizer()
    
    # Configure recognition settings for better sensitivity
    recognizer.dynamic_energy_threshold = True  # Enable dynamic adjustment
    recognizer.energy_threshold = 1000  # Higher initial threshold
    recognizer.dynamic_energy_adjustment_damping = 0.15  # Make it adjust faster
    recognizer.dynamic_energy_ratio = 1.5  # More sensitive to changes
    recognizer.pause_threshold = 0.5  # Shorter pause between phrases
    recognizer.operation_timeout = None  # No timeout
    recognizer.phrase_threshold = 0.3  # Shorter phrases allowed
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...", file=sys.stderr)
            # Quick ambient noise adjustment
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...", file=sys.stderr)
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
                
        if should_stop:
            return "Listening stopped"
            
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results; {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def process_commands():
    global should_stop
    while True:
        try:
            command = input().strip()
            if command == "START_LISTENING":
                should_stop = False
                text = listen_and_convert()
                response = json.dumps({"text": text})
                print(response)
                sys.stdout.flush()
            elif command == "STOP_LISTENING":
                should_stop = True
        except EOFError:
            break
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    process_commands() 