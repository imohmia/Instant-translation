from fastapi import FastAPI, UploadFile, File
import openai
import io
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import tempfile
from fastapi.responses import FileResponse

app = FastAPI()
translator = Translator()
recognizer = sr.Recognizer()

@app.post("/translate_speech/")
async def translate_speech(file: UploadFile = File(...), target_language: str = "en"):
    try:
        # Read audio file
        audio_data = await file.read()
        audio_file = io.BytesIO(audio_data)

        # Recognize speech
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

        # Translate text
        translated_text = translator.translate(text, dest=target_language).text

        # Convert translated text to speech
        tts = gTTS(translated_text, lang=target_language)
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)

        return FileResponse(temp_audio.name, media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
