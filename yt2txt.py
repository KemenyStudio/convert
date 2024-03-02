import streamlit as st
import os
import sys
import time
import ffmpeg
from tqdm import tqdm
from pytube import YouTube
from dotenv import load_dotenv
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason
from azure.cognitiveservices.speech import CancellationReason
import azure.cognitiveservices.speech as speechsdk

load_dotenv()

API_KEY = os.getenv("API_KEY")
REGION = os.getenv("REGION")
LANGUAGE = os.getenv("LANGUAGE")

class AzureSpeechService:
    def __init__(self, speech_key, service_region):
        self.speech_key = speech_key
        self.service_region = service_region
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    def validate_speech_service(self):
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)
        result = speech_recognizer.recognize_once_async().get()
        if result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == CancellationReason.Error:
                if "401" in cancellation_details.error_details:
                    print("Invalid subscription key or region.")
                    return False
                else:
                    print("Error: " + cancellation_details.error_details)
                    return False
        print("Subscription key and region are valid.")
        return True

    def recognize(self, speech_recognizer: speechsdk.SpeechRecognizer) -> list:
        print("Starting speech recognition ...\n")
        done = False
        all_results = list()

        def stop_cb(evt):
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

            if evt.result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = evt.result.cancellation_details
                cancellation_reason = cancellation_details.reason
                print()
                if cancellation_reason == speechsdk.CancellationReason.Error:
                    print(RED + "=== ERROR ===" + ENDC)
                    print(f"Error code: {cancellation_details.error_code}")
                    print(f"Error details: {cancellation_details.error_details}")
                elif cancellation_reason == speechsdk.CancellationReason.CancelledByUser:
                    print(RED + "=== CANCELED BY USER ===" + ENDC)
                elif cancellation_reason == speechsdk.CancellationReason.EndOfStream:
                    print(GREEN + "=== SUCCESS ===" + ENDC)

        def handle_final_result(evt):
            nonlocal all_results
            all_results.append(evt.result.text)

        # connect callbacks to the events fired by the speech recognizer
        speech_recognizer.recognized.connect(handle_final_result)
        speech_recognizer.recognizing.connect(lambda evt: print(f"RECOGNIZING: {evt}"))
        speech_recognizer.recognized.connect(lambda evt: print(f"RECOGNIZED: {evt}"))
        speech_recognizer.session_started.connect(lambda evt: print(f"SESSION STARTED: {evt}"))
        speech_recognizer.session_stopped.connect(lambda evt: print(f"SESSION STOPPED: {evt}"))
        speech_recognizer.canceled.connect(lambda evt: print(f"CANCELED: {evt}"))

        # stop continuous recognition on either session stopped or canceled events
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # start continuous speech recognition
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(5)

        return all_results

    def transcribe_audio(self, audio_file, language=LANGUAGE):
        self.speech_config.speech_recognition_language = language
        self.speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, '120000')  # 2 minute
        audio_config = AudioConfig(filename=audio_file)
        speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        all_results = self.recognize(speech_recognizer)

        if all_results:
            return " ".join(all_results)
        else:
            return "No speech could be recognized."

def progress_function(stream, chunk, bytes_remaining):
    current = ((stream.filesize - bytes_remaining)/stream.filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    sys.stdout.write('\rFile Downloading ' + '[' + '#' * progress + '-' * (50 - progress) + ']'+percent+'% complete')
    sys.stdout.flush()

def download_youtube_audio(youtube_url):
    youtube_id = youtube_url.split('=')[-1]
    audio_file = f'audio_files/{youtube_id}.mp4'
    wav_file = f'audio_files/{youtube_id}.wav'

    # Check if the wav file already exists
    if os.path.exists(wav_file):
        print(f'File {wav_file} already exists, skipping download and conversion.')
        return wav_file

    # Download the YouTube video
    print(f'Downloading YouTube video {youtube_url}...')
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(output_path='audio_files', filename=f'{youtube_id}.mp4')
    print(f'Download complete. Saved as {audio_file}.')

    # Check if the audio file exists
    if not os.path.exists(audio_file):
        print(f'File {audio_file} does not exist. Download may have failed.')
        return None

    # Convert the audio to wav
    print(f'Converting {audio_file} to wav...')
    stream = ffmpeg.input(audio_file)
    stream = ffmpeg.output(stream, wav_file)
    ffmpeg.run(stream)
    print(f'Conversion complete. Saved as {wav_file}.')

    return wav_file

def convert_audio_to_wav(input_file):
    output_file = input_file.rsplit(".", 1)[0] + ".wav"
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.output(stream, output_file, ac=1, ar=16000)
    ffmpeg.run(stream)
    return output_file

def write_transcription_to_file(transcription, filename):
    output_dir = 'transcriptions'
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, filename + '.txt'), 'w') as f:
        f.write(transcription)

def main():
    st.title('YouTube Audio to Text Converter')

    youtube_url = st.text_input('Enter YouTube URL:')
    if youtube_url:
        video_id = youtube_url.split('=')[-1]
        audio_file = download_youtube_audio(youtube_url)
        azure_speech_service = AzureSpeechService(speech_key=API_KEY, service_region=REGION)
        transcription = azure_speech_service.transcribe_audio(audio_file)
        write_transcription_to_file(transcription, video_id)
        st.text("Transcription:")
        st.write(transcription)

if __name__ == "__main__":
    main()