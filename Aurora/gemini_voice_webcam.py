import os
import speech_recognition as sr
import subprocess
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
import re  # Import regular expressions library

import sys
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gemini import sample_generate_text_image_content, sample_generate_text_content
import asyncio
from qasync import QEventLoop, asyncSlot

cap = cv2.VideoCapture(0)  # 0 refers to the default webcam

# Configure Gemini API key (replace with your actual key)
load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')


class MainWindow(QWidget):

    def __init__(self, loop=None):
        super().__init__()
        self.initUI()

        # Start the timer in the constructor
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam_feed)
        self.timer.start(50)  # Update the webcam feed every 50 milliseconds
        self.loop = loop or asyncio.get_event_loop()
        self.screen_data = []
        self.previous_screen = ""

    def initUI(self):
        hbox = QHBoxLayout(self)

        # webcam frame
        webcam_frame = QFrame(self)
        webcam_frame.setFrameShape(QFrame.StyledPanel)

        # Create a QLabel to display the webcam feed
        self.label = QLabel(webcam_frame)
        self.label.setGeometry(0, 0, 640, 480)

        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)

        self.textedit = QTextEdit()
        self.textedit.setFontPointSize(16)
        # Create buttons
        button = QPushButton("Voice", self)
        button2 = QPushButton("Text", self)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(self.textedit)
        splitter2.addWidget(button)
        splitter2.addWidget(button2)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(webcam_frame)
        splitter1.addWidget(splitter2)
        splitter1.setSizes([400, 400])

        hbox.addWidget(splitter1)

        self.setLayout(hbox)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

        self.setGeometry(100, 100, 1280, 480)
        self.setWindowTitle('Aurora')

        # Connect button click events to functions
        button.clicked.connect(self.capture_voice_async)
        button2.clicked.connect(self.capture_text_async)

        # self.show()

    @asyncSlot()
    async def capture_text_async(self):
        # Read the text from the textedit
        text = self.textedit.toPlainText()

        # Replace everything from the previous screen with space to find what was changed.
        new_text = text.replace(self.previous_screen, "")
        print(new_text)

        # add this to the lines of data to send chatbot.
        self.screen_data.append(new_text)

        # send chat history to gemini
        response = await sample_generate_text_content(self.screen_data)

        format_response = f"\n\nGemini: {response}\n"
        # format response
        self.textedit.append(format_response)

        # Add response as screen data.
        self.screen_data.append(format_response)

        # read what the text area is now.
        text = self.textedit.toPlainText()

        # Text is now the new previous screen.
        self.previous_screen = text

        return response

    @asyncSlot()
    async def capture_voice_async(self):
        """
        Listens for microphone input, converts it to text, generates a response
        using Gemini, removes asterisks, speaks it back, and adds it to the chat history.
        """

        async def listen_and_respond():
            recognizer = sr.Recognizer()
            microphone = sr.Microphone(device_index=1)  # Use microphone device index 3

            with microphone as source:
                print("Adjusting noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Speak now to Gemini...")

                # Set a timeout for speech recognition (adjust as needed)
                try:
                    #  audio = await asyncio.wait_for(recognizer.listen(source, timeout=3), timeout=3)
                    audio = await self.loop.run_in_executor(None, lambda: recognizer.listen(source))
                except asyncio.TimeoutError:
                    print("Listening timed out.")
                    return

                text = recognizer.recognize_google(audio)

                print("You said:", text)

                # Update the chat history on the UI thread

                self.textedit.append(f"You: {text}")

                frames = []

                # read ten frames
                for i in range(10):
                    print("picture")
                    ret, frame = cap.read()
                    if ret:
                        frames.append(cv2.imencode('.jpg', frame)[1].tobytes())
                    await asyncio.sleep(.5)  # Delay for 1 second

                    # Read the text from the textedit
                    text = self.textedit.toPlainText()

                    # Split the text into lines
                    lines = text.splitlines()

                    # Get the last line
                    last_line = lines[-1]

                    response = await sample_generate_text_image_content(last_line, frames)

                    # Check the type of response
                    if isinstance(response, str):
                        response_text = response
                    else:
                        response_text = response.candidates[0].content.parts[0].text

                # Remove "Assistant:" from the response if present
                response_text = response_text.replace("Assistant: ", "")

                self.textedit.append(f"Gemini: {response_text}")

                # Speak the response using gTTS
                speech = gTTS(response_text, lang='en')
                speech.save('output.mp3')

                # Play audio using ffmpeg (assuming it's installed)
                process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', 'output.mp3'],
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                process.wait()

        # Run the asynchronous function within an event loop
        await listen_and_respond()

    def update_webcam_feed(self):
        ret, frame = cap.read()
        if ret:
            # Convert OpenCV frame to QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            # Display the QImage on the QLabel
            self.label.setPixmap(QPixmap.fromImage(frame))


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow(loop)
    window.update_webcam_feed()  # Call the update function once
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()