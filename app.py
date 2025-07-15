import streamlit as st
import whisper
import openai
from gtts import gTTS
import tempfile
from dotenv import load_dotenv
import os

# Load your API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title('👵🏻 NongChuai AI Healthcare Assistant')

uploaded_file = st.file_uploader("เลือกไฟล์เสียงอธิบายอาการ (ไฟล์ WAV)", type=['wav'])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        audio_path = tmp_file.name

    with st.spinner('กำลังแปลงเสียงเป็นข้อความ...'):
        whisper_model = whisper.load_model("base")
        result = whisper_model.transcribe(audio_path, language='th')
        user_symptom = result['text']
        st.markdown(f"**ข้อความจากเสียงของคุณ:** {user_symptom}")

    with st.spinner('กำลังสร้างคำแนะนำทางการแพทย์...'):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "คุณเป็นผู้ช่วยทางการแพทย์สำหรับผู้สูงอายุไทย ตอบคำถามสั้น กระชับ เข้าใจง่าย และแนะนำแนวทางเบื้องต้นในการดูแลสุขภาพ"},
                {"role": "user", "content": user_symptom},
            ]
        )
        health_advice = response.choices[0].message.content
        st.markdown(f"**คำแนะนำ:** {health_advice}")

    with st.spinner('กำลังแปลงข้อความเป็นเสียง...'):
        tts = gTTS(text=health_advice, lang='th')
        audio_response_path = "health_advice.mp3"
        tts.save(audio_response_path)
        st.audio(audio_response_path, format='audio/mp3')
