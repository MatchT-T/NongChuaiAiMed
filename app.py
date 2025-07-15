import streamlit as st
from PIL import Image
import openai
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

# App setup
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()

# OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Load logo and convert to base64
logo = Image.open("logo.png")
buffered = BytesIO()
logo.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Centered title and logo
st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align: center;'><img src='data:image/png;base64,{img_str}' width='200'/></div>",
    unsafe_allow_html=True
)

# Input symptom
text_input = st.text_input("พิมพ์อาการของคุณ (Type your symptoms):")

# Handle response
if text_input:
    st.markdown(f"**อาการของคุณ:** {text_input}")

    prompt = f"คุณคือผู้ช่วยแพทย์: ให้คำแนะนำเบื้องต้นแก่ผู้ป่วยจากอาการต่อไปนี้:\n\nอาการ: {text_input}\n\nคำแนะนำ:"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "คุณคือผู้ช่วยด้านสุขภาพที่พูดภาษาไทยและให้คำแนะนำเบื้องต้นเกี่ยวกับอาการเจ็บป่วยทั่วไป "
                        "คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา แต่สามารถแนะนำแนวทางเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการพบแพทย์เมื่อจำเป็น "
                        "ให้คำตอบที่สุภาพ ชัดเจน และเข้าใจง่ายสำหรับคนทั่วไป และควรใช้ภาษาที่อบอุ่นเป็นกันเอง"
                    )
                },
                {
                    "role": "user",
                    "content": f"อาการของฉันคือ: {text_input}"
                }
            ],
            max_tokens=4000,
            temperature=0.7,
        )
        health_advice = response.choices[0].message.content.strip()
    except Exception as e:
        health_advice = f"ขออภัย เกิดข้อผิดพลาด: {e}"

    st.markdown(f"**คำแนะนำ:** {health_advice}")

# Info footer
st.info("กรุณาพิมพ์อาการของคุณ แล้วรอรับคำแนะนำเป็นข้อความ")

