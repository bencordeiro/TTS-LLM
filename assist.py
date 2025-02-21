import speech_recognition as sr
import requests
import pyttsx3

# Initialize recognizer and speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set properties for the speech engine (optional)
engine.setProperty('rate', 170)  # Speed of speech (default is 200)
engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)

# Adjust microphone sensitivity
recognizer.energy_threshold = 200  # Adjust if needed
recognizer.dynamic_energy_threshold = True  # Auto-adjusts for background noise
recognizer.pause_threshold = 1.5  # Waits for a slightly longer pause

# Initialize conversation history
conversation_history = [{"role": "system", "content": "You are a helpful text to speech assistant. Please keep responses clear and short"}]

# Define function to continuously listen and transcribe speech
def listen_continuous():
    with sr.Microphone() as source:
        print("Listening for commands... (Press Ctrl+C to stop)")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise

        while True:
            try:
                audio = recognizer.listen(source, timeout=None)  # No timeout, listens indefinitely
                command = recognizer.recognize_google(audio)
                print("You said:", command)
                return command
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand that.")
                continue  # Keep listening if nothing is understood
            except sr.RequestError as e:
                print(f"Error connecting to speech recognition service: {e}")
                return None

# Define function to send requests to the assistant model
def ask_assistant(prompt):
    global conversation_history
    url = 'http://127.0.0.1:1234/v1/chat/completions'
    headers = {'Content-Type': 'application/json'}

    conversation_history.append({"role": "user", "content": prompt})

    data = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": conversation_history
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()

    if response.status_code == 200 and "choices" in response_json:
        assistant_response = response_json["choices"][0]["message"]["content"]
        print("Assistant says:", assistant_response)

        # Append assistant's response to maintain conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})

        return assistant_response
    else:
        print("Error with response:", response_json)
        return None

# Define function to speak the assistant's response
def speak_response(response):
    engine.say(response)
    engine.runAndWait()

# Main loop: Listen, process command, and respond
while True:
    command = listen_continuous()  # Keeps listening until a full sentence is spoken
    if command:
        assistant_response = ask_assistant(command)  # Get response from LLM
        if assistant_response:
            speak_response(assistant_response)  # Speak the response

