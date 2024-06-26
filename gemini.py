from google.ai import generativelanguage_v1beta
from gemini_chat import build_conversation_turn, get_conversation
import asyncio
from pathlib import Path
import google.api_core
import gemini_util
import os
import requests

def read_prompt():
    with open("prompt.txt", "r") as file:
        return file.read()


async def sample_generate_text_image_content(text, image):
    """
        This function sends a text and image reqeust to gemini.

        :param text: The text prompt from the user.
        :param image: The image from the user as a byte array
        :return: The response from gemini
        """

    # Create a client
    client = generativelanguage_v1beta.GenerativeServiceAsyncClient()

    request = generativelanguage_v1beta.GenerateContentRequest(
        model=gemini_util.IMAGE_MODEL_NAME,
        contents=[gemini_util.build_content("user", image, f'{read_prompt} {text}')],
        generation_config=gemini_util.generation_config,
        safety_settings=gemini_util.safety_settings
    )

    # Make the request
    response = await client.generate_content(request=request)

    # Handle the response
    return response.candidates[0].content.parts[0].text


async def sample_generate_text_content(text_list):
    """
        This function sends a text reqeust to gemini.

        :param text_list:
        :param text: The text prompt from the user.   
        :return: The response from gemini
        """
    # Create a client
    client = generativelanguage_v1beta.GenerativeServiceAsyncClient()

    contents = []
    for text in text_list:
        role = "user"
        if text.find("Gemini: ") != -1:
            text = text.replace("Gemini: ", "")
            role = "model"
        contents.append(gemini_util.build_content_text(role, text))

    # for obj in contents:
    #    print({"parts": obj.parts, "role": obj.role})

    try:
        # Initialize request argument(s)
        request = generativelanguage_v1beta.GenerateContentRequest(
            model=gemini_util.TEXT_MODEL_NAME,
            contents=contents,
            generation_config=gemini_util.generation_config,
            safety_settings=gemini_util.safety_settings
        )

        # Make the request
        response = await client.generate_content(request=request)

        # Handle the response
        return response.candidates[0].content.parts[0].text
    except google.api_core.exceptions.FailedPrecondition as e:
        # print('Failed precondition error:', e)
        return f'Error: {e}  Tip: use a VPN.'
    except Exception as e:
        # print('Unknown error:', e)
        return f'Error: {e}'


async def main():
    # Gemini provides a multimodal model (gemini-pro-vision) that accepts both text and images and inputs. The
    # GenerativeModel.generate_content API is designed handle multi-media prompts and returns a text output.

    # downloading an image to test with

    if not os.path.exists("image.jpg"):
        image_url = "https://lh3.googleusercontent.com/drive-viewer/AKGpihbQfOhXGcd7ld96NzkhrL6f59WAWIYDuMVrXEjWauXguQkl4772hkqhJ2JXpYxVobNwDwJSIjcazPiWBKg5dP2-wwe0LcgYjic=s1600-rw-v1"
        response = requests.get(image_url)
        if response.status_code == 200:
            print("Image downloaded successfully")

            with open("image.jpg", "wb") as f:
                f.write(response.content)

        else:
            print("Error downloading image:", response.status_code)

    image_bites = Path("image.jpg").read_bytes()
    response = await sample_generate_text_image_content('What do you see?', [image_bites])
    print(f'Text Image response: {response}')

    # for testing text based calls.
    response = await sample_generate_text_content(["Who is Sergei Korolev?"])
    print(f'Text response: {response}')


async def main_text(text):
    response = await sample_generate_text_content(text)
    return f'Gemini: {response}'


async def main_chat():
    try:
        # storing conversation data.
        conversation_history = []

        print("Test application for sending chat messages to Gemini ai.  To exit type Exit")
        print("To exit type Exit")

        while True:
            # Prompt the user to type something
            user_input = input(": ")

            # get conversation history
            convo = get_conversation(conversation_history)

            # send message with conversation history
            convo.send_message(user_input)

            if user_input.lower().strip() == "exit":
                print("Application shutting down.")
                break

            # This is for debugging the conversation history.  (Linda)
            if user_input.lower().strip() == "show history":
                print(conversation_history)
            else:
                # store user message as history
                conversation_history.append(build_conversation_turn("user", user_input))

                # store model response
                conversation_history.append(build_conversation_turn("model", convo.last.text))
                print(convo.last.text)

    except KeyboardInterrupt:
        print("Application shutting down. ")


# For testing text based chat.
if __name__ == "__main__":
    # test text based and image.
    asyncio.run(main())

    # test chat
    #asyncio.run(main_chat())



