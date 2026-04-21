"""
Optional microphone-based voice transcription helper.

This module uses SpeechRecognition when available. If dependency or
microphone access is unavailable, it returns a clear error message.
"""

try:
    import speech_recognition as sr
except ModuleNotFoundError:  # pragma: no cover
    sr = None


def transcribe_from_microphone(timeout=8, phrase_time_limit=10):
    """
    Capture one utterance from microphone and transcribe to text.

    Returns: (success: bool, text_or_error: str)
    """
    if sr is None:
        return False, "SpeechRecognition not installed. Run: pip install SpeechRecognition"

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )
        text = recognizer.recognize_google(audio)
        return True, text
    except sr.WaitTimeoutError:
        return False, "No speech detected within timeout."
    except sr.UnknownValueError:
        return False, "Speech was not understood."
    except sr.RequestError as exc:
        return False, f"Speech service error: {exc}"
    except Exception as exc:  # pragma: no cover
        return False, f"Microphone error: {exc}"
