import base64
import os
from typing_extensions import Annotated
import wave
import requests
from fastapi import Depends, FastAPI, UploadFile, HTTPException, Request, File
from auth import AuthHandler
from ms_azure import get_azure_token, save_audio
from schemas import AuthDetails
from fastapi.middleware.cors import CORSMiddleware

from stt import speech_recognize_once_from_file
# import moviepy.editor as moviepy
# from ffmpy import FFmpeg


origins = [
    'http://localhost',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8100'
    'http://localhost:8000',
    'http://localhost:8100',
    'http://172.20.10.2',
    'http://172.20.10.3'
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUBSCRIPTION_KEY = os.environ.get("SUBSCRIPTION_KEY")
AZ_TOKEN = os.environ.get("AZ_TOKEN")

'''
@app.get("/api/login")
def login(auth_details: AuthDetails):
    """Handles user login."""
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(
            status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    get_azure_token()
    return {'token': token}
'''


@app.get("/api/login")
def login():
    return get_azure_token()


@app.post("/api/stt")
async def speech_to_text(language: str, file: UploadFile = File(...)):
    """
    Converts speech to text.
    """
    url = 'https://swedencentral.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'
    headers = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type': 'text/plain; charset=utf-8',
        'Authorization': AZ_TOKEN
    }

    params = {'language': language}
    # audio_base64 = await request.body()

    with open(file.filename, 'wb') as buffer:
        buffer.write(file.file.read())
    audio_output = open(file.filename, 'rb')

    try:
        data = requests.post(url, data=audio_output,
                             headers=headers, params=params).json()
        return {'data': data}
    except Exception as e:
        return f"An error occurred while text transcribed from the audio file: {e}"


@app.post("/api/tts")
async def text_to_speech(request: Request):
    """
    Converts text to speech.
    """
    text = await request.body()
    filename = save_audio(text.decode())

    try:
        with open(filename, "rb") as audio:
            encoded_audio = base64.b64encode(audio.read())
        # Med denna rad aktiv så raderas filen så fort den konverterats till base64-string
        # os.remove(filename)
        return encoded_audio
    except Exception as e:
        return f"An error occurred while opening the audio file for the provided text: {e}"


def write_to_file(base64_audio):
    import base64
    wav_file = open("temp.wav", "wb")
    decode_string = base64.b64decode(base64_audio)
    wav_file.write(decode_string)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000, host='0.0.0.0')
