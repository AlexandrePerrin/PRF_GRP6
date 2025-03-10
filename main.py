import pyaudio
import wave
import speech_recognition as sr

def record_audio(filename, duration=5):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    frames = []

    try:
        #print("Enregistrement en cours...")
        for _ in range(int(44100 / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    audio.terminate()

    sound_file = wave.open(filename, "wb")
    sound_file.setnchannels(1)
    sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    sound_file.setframerate(44100)
    sound_file.writeframes(b''.join(frames))
    sound_file.close()

    #print(f"Enregistrement terminé. Fichier audio enregistré sous : {filename}")

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        #print("Transcription en cours...")
        text = recognizer.recognize_whisper(audio_data)
        return text
    except sr.UnknownValueError:
        print("Whisper n'a pas pu comprendre l'audio")
    except sr.RequestError as e:
        print(f"Erreur lors de la requête à l'API Whisper; {e}")

def get_phrase():
    audio_file = "enregistrement.wav"
    record_audio(audio_file)
    return transcribe_audio(audio_file)

if __name__ == "__main__":
    phrase = get_phrase()
    print(phrase)
