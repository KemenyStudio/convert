import os
import re
import ffmpeg
from pytube import YouTube
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason
from azure.cognitiveservices.speech import CancellationReason
import azure.cognitiveservices.speech as speechsdk
import tempfile

class AzureSpeechService:
    def __init__(self, speech_key, service_region):
        self.speech_key = speech_key
        self.service_region = service_region
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)  # Uses AZURE_SPEECH_KEY

    def transcribe_audio(self, audio_file_path, speech_key, service_region, language='en-US'):
        self.speech_config = SpeechConfig(subscription=speech_key, region=service_region)
        self.speech_config.speech_recognition_language = language
        audio_config = AudioConfig(filename=audio_file_path)
        speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        all_results = []

        def handle_final_result(evt):
            nonlocal all_results
            all_results.append(evt.result.text)

        speech_recognizer.recognized.connect(handle_final_result)
        speech_recognizer.start_continuous_recognition()
        while not all_results:
            pass

        return " ".join(all_results)

def transcribe_audio(file_storage, speech_key, service_region):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_storage.save(temp_file)
        temp_file_path = temp_file.name

    azure_speech_service = AzureSpeechService(
        speech_key=speech_key,
        service_region=service_region
    )
    transcription = azure_speech_service.transcribe_audio(temp_file_path)
    
    os.remove(temp_file_path)
    return transcription

def download_youtube_audio(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download()
        base, ext = os.path.splitext(output_file)
        new_file = base + '.mp3'
        os.rename(output_file, new_file)
        return new_file
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None