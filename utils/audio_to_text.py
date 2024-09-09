import os
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason

class AzureSpeechService:
    def __init__(self, speech_key, service_region):
        self.speech_config = SpeechConfig(subscription=speech_key, region=service_region)  # Uses AZURE_SPEECH_KEY

    def transcribe_audio(self, audio_file, language='en-US'):
        self.speech_config.speech_recognition_language = language
        audio_config = AudioConfig(filename=audio_file)
        speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        all_results = []

        def handle_final_result(evt):
            if evt.result.reason == ResultReason.RecognizedSpeech:
                all_results.append(evt.result.text)

        speech_recognizer.recognized.connect(handle_final_result)
        speech_recognizer.start_continuous_recognition()
        speech_recognizer.session_stopped.connect(lambda evt: speech_recognizer.stop_continuous_recognition())

        while not all_results:
            pass

        return " ".join(all_results)

def transcribe_audio(audio_file, speech_key, service_region):
    azure_speech_service = AzureSpeechService(
        speech_key=speech_key,
        service_region=service_region
    )
    return azure_speech_service.transcribe_audio(audio_file)