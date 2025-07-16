import streamlit as st
from PIL import Image
import openai
import os
from dotenv import load_dotenv
from supabase_client import supabase, sign_up, sign_in  # you already have this file
from datetime import datetime

# --- App Config ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# --- Sidebar Authentication ---
st.sidebar.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.auth_mode == "login":
    st.sidebar.subheader("เข้าสู่ระบบ")
    email = st.sidebar.text_input("อีเมล", key="login_email")
    password = st.sidebar.text_input("รหัสผ่าน", type="password", key="login_password")
    if st.sidebar.button("เข้าสู่ระบบ"):
        try:
            result = sign_in(email, password)
            if result.user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("✅ เข้าสู่ระบบสำเร็จ")
            else:
                st.error("❌ อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
    st.sidebar.markdown("ยังไม่มีบัญชี? 👉 [สมัครสมาชิก](#)", unsafe_allow_html=True)
    if st.sidebar.button("เปลี่ยนไปสมัครสมาชิก"):
        st.session_state.auth_mode = "register"

elif st.session_state.auth_mode == "register":
    st.sidebar.subheader("สมัครสมาชิก")
    email = st.sidebar.text_input("อีเมลใหม่", key="signup_email")
    password = st.sidebar.text_input("รหัสผ่านใหม่", type="password", key="signup_password")
    if st.sidebar.button("สมัครสมาชิก"):
        try:
            result = sign_up(email, password)
            st.success("✅ สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")
            st.session_state.auth_mode = "login"
        except Exception as e:
            st.error(f"สมัครไม่สำเร็จ: {e}")
    if st.sidebar.button("กลับไปเข้าสู่ระบบ"):
        st.session_state.auth_mode = "login"

# --- MAIN APP UI ---
if st.session_state.get("logged_in"):
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    logo = Image.open("logo.png")
    st.image(logo, width=200)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน")}
        ]

    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("พิมพ์อาการของคุณหรือสอบถามสิ่งที่ต้องการได้ที่นี่...")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_reply = f"ขออภัย เกิดข้อผิดพลาด: {e}"

        with st.chat_message("assistant", avatar="logo.png"):
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        # Save to Supabase
        try:
            supabase.table("symptom_logs").insert({
                "user_email": st.session_state["user_email"],
                "symptom": user_input,
                "response": assistant_reply,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            st.warning(f"⚠️ ไม่สามารถบันทึกประวัติ: {e}")
