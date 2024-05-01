import os
import speech_recognition as sr
import subprocess
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
import re  # Import regular expressions library
import getpass


# Configure Gemini API key (replace with your actual key)
load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def listen_and_respond(keyword='stop'):
    """
    Listens for microphone input, converts it to text, generates a response
    using Gemini, removes all asterisks from the response, and speaks it back.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=1)  # Use microphone device index 3

    try:
        while True:
            with microphone as source:
                print("Adjusting noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Speak now to Gemini...")
                audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio)
            print("You said:", text)

            if keyword in text.lower():
                print("Keyword detected. Stopping listening.")
                break  # Exit the loop if the keyword is detected

            response = model.generate_content(text)
            print("Gemini:", response.text)

            # Remove all occurrences of asterisks using regular expressions
            clean_response = re.sub(r'\*', '', response.text)  # Replace all * with an empty string

            speech = gTTS(clean_response, lang='en')
            speech.save('output.mp3')

            # Play audio using subprocess
            process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', 'output.mp3'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            # Wait for the process to finish or until the keyword is detected
            while True:
                if process.poll() is not None:
                    break  # Break the loop if the subprocess has finished
                recognized_keyword = listen_and_stop(recognizer, microphone)
                if recognized_keyword and keyword in recognized_keyword:
                    print("Stopping audio playback.")
                    process.terminate()  # Terminate the audio subprocess
                    break  # Exit the loop if the keyword is detected during playback

    except KeyboardInterrupt:
        print("Program stopped by user.")

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))


def listen_and_stop(recognizer, microphone, keyword='stop'):
    """
    Listens for a specific keyword and returns the recognized text if the keyword is detected.
    """
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)

        if keyword in text.lower():
            print("Keyword detected.")
            return text
        else:
            return None

    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None


while True:
    listen_and_respond()

    # Prompt to continue
    continue_talking = getpass.getpass("Would you like to talk to Gemini again? (y/n): ").lower()
    if continue_talking != 'y':
        break

print("Thank you for talking to Gemini!")