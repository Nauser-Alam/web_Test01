from flask import Flask, render_template, jsonify
import pyttsx3
import speech_recognition as sr
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Initialize the TTS engine
engine = pyttsx3.init()

# Function to speak text with a selected voice
def speak_text(text, voice_index):
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech input
def listen_for_command(timeout=0.8, pause_duration=2):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        last_command_time = time.time()

        while True:
            try:
                audio = recognizer.listen(source, timeout=timeout)
                command = recognizer.recognize_google(audio).lower()
                last_command_time = time.time()
                return command
            except sr.WaitTimeoutError:
                current_time = time.time()
                if current_time - last_command_time > pause_duration:
                    return "pause"
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def recognition_thread():
    texts = [
        "okay Nauser, Explain me about CSS model",
        "okay Nauser, Explain me about HTML model",
        "okay Nauser, Explain me about JavaScript model",
        "okay Nauser, Explain me about PHP model"
    ]
    current_text_index = 0

    while current_text_index < len(texts):
        if current_text_index % 2 == 0:
            voice_index = 0
        else:
            voice_index = 1

        command = listen_for_command()  # Keep listening for commands
        if command == "pause" and current_text_index == len(texts):
            speak_text("Thank you Nauser", voice_index)
            current_text_index += 1
        else:
            if command == "start":
                speak_text(texts[current_text_index], voice_index)
                current_text_index += 1
            elif command == "pause":
                if current_text_index < len(texts):
                    speak_text(texts[current_text_index], voice_index)
                    current_text_index += 1
            elif command == "exit":
                return  # Exit the loop and stop recognition

        # Reset temp variables and continue listening for commands
        command = None

executor = ThreadPoolExecutor(max_workers=3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-recognition', methods=['POST'])
def start_recognition():
    executor.submit(recognition_thread)  # Start recognition in a new thread
    return jsonify({"status": "recognition started"})

