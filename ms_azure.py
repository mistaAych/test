
import os
import base64
from random import sample
import random
import azure.cognitiveservices.speech as speechsdk
from fastapi import HTTPException
import requests

SUBSCRIPTION_KEY = os.environ.get("SUBSCRIPTION_KEY")
SPEECH_REGION = os.environ.get("REGION")
VOICE_NAME = os.environ.get("VOICE_NAME")


def save_audio(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SUBSCRIPTION_KEY, region=SPEECH_REGION)
    filename = f'az_axxa{random.randint(0,1000)}.wav'
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=filename)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = VOICE_NAME
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

    print(filename)
    speech_synthesis_result = speech_synthesizer.speak_text_async(
        text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    return filename


def get_azure_token():
    url = 'https://swedencentral.api.cognitive.microsoft.com/sts/v1.0/issuetoken'
    headers = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type': 'text/plain; charset=utf-8',
        'Accept': 'text/html: application/xhtml+xml, */*',
    }
    try:
        print('Azure token created!')
        return requests.post(url, headers=headers).text
    except Exception as e:
        print(f"An error occurred while creating the azure token: {e}")
        return HTTPException(status_code=400, detail='Credentials could not be retrieved!')
