import speech_recognition as sr


class SpeechRecognitionClient:
    def transcribe_wav(self, wav_path: str, language: str) -> str:
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio, language=language)
        except Exception:
            return ""
