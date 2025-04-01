import os
import wave
from datetime import datetime

import pyaudio
import speech_recognition as sr


class AudioRecorder:
    def __init__(self, filename="enregistrement.wav"):
        self.filename = filename
        self.frames = []
        self.recording = False

        self.p = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        self.frames = []
        self.recording = True
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                  input=True, frames_per_buffer=1024)
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop(self):
        self.recording = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        self._save_to_file()

    def _save_to_file(self):
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

def transcribe_audio(audio_file="enregistrement.wav"):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_whisper(audio_data)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"Erreur Whisper : {e}"

def save_to_file(text, folder="transcriptions"):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"transcription_{timestamp}.txt"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    return filepath
