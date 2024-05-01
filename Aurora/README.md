# Aurora

Gemini provides a multimodal model (gemini-pro-vision) that accepts both text and images and inputs. The GenerativeModel.generate_content API is designed handle multi-media prompts and returns a text output.

This sample will read from your webcam you can type requests to the ai model in the text field and send them when you are ready.  

You can also access information using voice commands and object recognition.



# to run this.

Obtain API_KEY [HERE](https://aistudio.google.com/app/apikey)

Create a service account key, GOOGLE_APPLICATION_CREDENTIALS [HERE](https://developers.google.com/workspace/guides/create-credentials)  

## Select a microphone

    python device.py

## Speak with Aurora

    python gemini_voice.py

## for the main ui

    python gemini_voice_webcam.py

## to just play with gemini text and image based you can run

    python gemini.py

Upload your image and share link from Google Drive.

After that generate direct link for the image stored in your Google Drive [HERE](https://www.labnol.org/embed/google/drive/) 

## to just run chat

    python gemini_chat.py

## WIP tuning models

Its broken on googles end

    python create_tuned_model.py

## Required

TODO: update after the beta library has been released as a pip.

```
pip install PyQt5
pip install opencv-python
pip install python-dotenv
pip install google-generativeai
pip install google-ai-generativelanguage

pip install SpeechRecognition
pip install gTTS

```

Install ffmpeg [HERE](https://www.hostinger.com/tutorials/how-to-install-ffmpeg)

```
python3 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

```


## Settings

The format of the .env file is

GOOGLE_APPLICATION_CREDENTIALS is path to the service account key file only needed for tuning

```
API_KEY=[readacted]
TEXT_MODEL_NAME=models/gemini-pro
IMAGE_MODEL_NAME=models/gemini-pro-vision
CHAT_MODEL_NAME=gemini-pro
GOOGLE_APPLICATION_CREDENTIALS='\path\key.json' 
```

## error 

If you see the following error try running a vpn.

>400 User location is not supported for the API use.


Text based chat conversation calls must go as user, model, user, model.  This error occurs if you dont send it in that format

> # 400 Please ensure that multiturn requests ends with a user role or a function response. 

 
