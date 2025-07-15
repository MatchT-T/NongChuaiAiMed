import streamlit as st
st.set_page_config(layout="wide")
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Read OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

st.title('NongChuai AI Healthcare Assistant')

text_input = st.text_input("พิมพ์อาการของคุณ (Type your symptoms):")

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


st.info("กรุณาพิมพ์อาการของคุณ แล้วรอรับคำแนะนำเป็นข้อความ")
