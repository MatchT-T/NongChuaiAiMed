import streamlit as st
from supabase import create_client
from PIL import Image
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Auth State Management ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# --- Auth Interface ---
st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")

auth_mode = st.radio("เลือกเมนู", ["เข้าสู่ระบบ", "สมัครสมาชิก"])

if auth_mode == "สมัครสมาชิก":
    email = st.text_input("อีเมล", key="signup_email")
    password = st.text_input("รหัสผ่าน", type="password", key="signup_password")
    if st.button("สมัครสมาชิก"):
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            st.success("✅ สมัครสมาชิกสำเร็จ! ไปยืนยันอีเมลก่อนใช้งาน")
        except Exception as e:
            st.error(f"❌ สมัครไม่สำเร็จ: {e}")

elif auth_mode == "เข้าสู่ระบบ":
    email = st.text_input("อีเมล", key="login_email")
    password = st.text_input("รหัสผ่าน", type="password", key="login_password")
    if st.button("เข้าสู่ระบบ"):
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if result.user:
                st.session_state.logged_in = True
                st.session_state.user_id = result.user.id
                st.success("✅ เข้าสู่ระบบสำเร็จ")
            else:
                st.error("❌ อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        except Exception as e:
            st.error(f"❌ เข้าสู่ระบบล้มเหลว: {e}")

# --- Main Chat App ---
if st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    st.image("logo.png", width=200)

    # Load previous history
    if "messages" not in st.session_state:
        user_id = st.session_state.user_id
        data = supabase.table("symptom_history").select("role, content").eq("user_id", user_id).order("timestamp").execute()
        st.session_state.messages = data.data if data.data else [
            {"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน")}
        ]

    # Display chat history
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("พิมพ์อาการของคุณหรือสอบถามสิ่งที่ต้องการได้ที่นี่...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        supabase.table("symptom_history").insert({
            "user_id": st.session_state.user_id,
            "role": "user",
            "content": user_input,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_reply = f"ขออภัย เกิดข้อผิดพลาด: {e}"

        st.chat_message("assistant", avatar="logo.png").markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        supabase.table("symptom_history").insert({
            "user_id": st.session_state.user_id,
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
