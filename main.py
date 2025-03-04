from fastapi import FastAPI, UploadFile, File
import io
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import tempfile
from fastapi.responses import FileResponse
from pydub import AudioSegment
import os

app = FastAPI()
translator = Translator()
recognizer = sr.Recognizer()

@app.post("/translate_speech/")
async def translate_speech(file: UploadFile = File(...), target_language: str = "en"):
    try:
        # Save the uploaded file temporarily
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_input.write(await file.read())
        temp_input.close()
        
        # Convert to WAV if necessary
        audio_format = file.filename.split(".")[-1].lower()
        if audio_format != "wav":
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio = AudioSegment.from_file(temp_input.name)
            audio.export(temp_wav.name, format="wav")
            temp_input.name = temp_wav.name
        
        # Recognize speech (Detect Language Dynamically)
        with sr.AudioFile(temp_input.name) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)  # Removed hardcoded "fa"

        # Translate text
        translated_text = translator.translate(text, dest=target_language).text

        # Convert translated text to speech
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        if target_language == "fa":
            # Use gTTS workaround for Farsi
            tts = gTTS(translated_text, lang="fa")
            tts.save(temp_audio.name)
        else:
            # Use gTTS for all other languages
            tts = gTTS(translated_text, lang=target_language)
            tts.save(temp_audio.name)

        # Convert MP3 to ensure compatibility
        final_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        sound = AudioSegment.from_file(temp_audio.name, format="mp3")
        sound.export(final_audio.name, format="mp3", bitrate="192k")  # Fixed incorrect variable name

        # Clean up temp files
        os.remove(temp_input.name)
        if 'temp_wav' in locals():
            os.remove(temp_wav.name)

        return FileResponse(final_audio.name, media_type="audio/mpeg", filename="translated_audio.mp3")

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
