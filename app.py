import streamlit as st
from st_audiorecorder import st_audiorecorder
import whisper
from gtts import gTTS
import tempfile
import os

# Optionally, use dotenv and openai import here if you use GPT later

st.title('NongChuai AI Healthcare Assistant')

# --- 1. Let users type symptoms
text_input = st.text_input("พิมพ์อาการของคุณ (Type your symptoms):")

# --- 2. Or record their voice
st.write("หรือกดปุ่มเพื่อบันทึกเสียง (Or click to record voice):")
audio = st_audiorecorder()

user_symptom = None

# Use typed text if available
if text_input:
    user_symptom = text_input
# Else, use audio if recorded
elif audio is not None:
    st.audio(audio, format='audio/wav')
    # Save audio to temp file for Whisper
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio)
        audio_path = tmp_file.name
    # Load Whisper model
    whisper_model = whisper.load_model("base")
    result = whisper_model.transcribe(audio_path, language='th')
    user_symptom = result['text']
    st.markdown(f"**ข้อความจากเสียง:** {user_symptom}")

# If there's symptom text, generate a sample response (replace with OpenAI call if you want)
if user_symptom:
    st.markdown(f"**อาการของคุณ:** {user_symptom}")
    health_advice = "นี่เป็นคำแนะนำตัวอย่าง: โปรดดื่มน้ำและพักผ่อน หากอาการไม่ดีขึ้นควรไปพบแพทย์"
    st.markdown(f"**คำแนะนำ:** {health_advice}")
    tts = gTTS(text=health_advice, lang='th')
    audio_response_path = "health_advice.mp3"
    tts.save(audio_response_path)
    st.audio(audio_response_path, format='audio/mp3')

st.info("คุณสามารถพิมพ์อาการ หรือกดปุ่มเพื่อบันทึกเสียง แล้วรอรับคำแนะนำเสียง")
