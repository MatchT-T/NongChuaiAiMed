import streamlit as st
import openai
from gtts import gTTS
import os

# If you use dotenv to load your key
from dotenv import load_dotenv
load_dotenv()

# Read API key from Streamlit secrets (if running on Cloud)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

st.title('NongChuai AI Healthcare Assistant')

# --- 1. Let users type symptoms
text_input = st.text_input("พิมพ์อาการของคุณ (Type your symptoms):")

if text_input:
    st.markdown(f"**อาการของคุณ:** {text_input}")

    # --- 2. Call OpenAI (replace with your own OpenAI logic as needed)
    prompt = f"คุณคือผู้ช่วยแพทย์: ให้คำแนะนำเบื้องต้นแก่ผู้ป่วยจากอาการต่อไปนี้:\n\nอาการ: {text_input}\n\nคำแนะนำ:"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "คุณคือผู้ช่วยแพทย์ที่ให้คำแนะนำเบื้องต้นเป็นภาษาไทย"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        health_advice = response.choices[0].message.content.strip()
    except Exception as e:
        health_advice = f"ขออภัย เกิดข้อผิดพลาด: {e}"

    st.markdown(f"**คำแนะนำ:** {health_advice}")

    # --- 3. Text-to-speech with gTTS
    tts = gTTS(text=health_advice, lang='th')
    audio_response_path = "health_advice.mp3"
    tts.save(audio_response_path)
    st.audio(audio_response_path, format='audio/mp3')

st.info("กรุณาพิมพ์อาการของคุณ แล้วรอรับคำแนะนำเสียง")
