import streamlit as st
from PIL import Image
import openai
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()

# Supabase credentials
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# --- Login/Register UI ---
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def login(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def register(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

st.sidebar.title("🔐 ระบบผู้ใช้")

if st.session_state.auth_mode == "login":
    st.sidebar.subheader("เข้าสู่ระบบ")
    email = st.sidebar.text_input("อีเมล")
    password = st.sidebar.text_input("รหัสผ่าน", type="password")
    if st.sidebar.button("เข้าสู่ระบบ"):
        try:
            user = login(email, password)
            st.session_state.logged_in = True
            st.session_state.user = user.user
            st.rerun()
        except Exception as e:
            st.error(f"❌ เข้าสู่ระบบล้มเหลว: {e}")
    if st.sidebar.button("สมัครสมาชิก"):
        st.session_state.auth_mode = "register"

elif st.session_state.auth_mode == "register":
    st.sidebar.subheader("สมัครสมาชิก")
    email = st.sidebar.text_input("อีเมลใหม่")
    password = st.sidebar.text_input("รหัสผ่านใหม่", type="password")
    if st.sidebar.button("สมัครสมาชิก"):
        try:
            register(email, password)
            st.success("✅ สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
            st.session_state.auth_mode = "login"
        except Exception as e:
            st.error(f"❌ สมัครไม่สำเร็จ: {e}")
    if st.sidebar.button("กลับไปเข้าสู่ระบบ"):
        st.session_state.auth_mode = "login"

# --- If logged in ---
if st.session_state.get("logged_in"):
    user_id = st.session_state.user.id
    st.success(f"✅ สวัสดีคุณ {st.session_state.user.email}")

    # --- Chat UI ---
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    logo = Image.open("logo.png")
    st.image(logo, width=200)

    # Load chat history from Supabase
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน")}
        ]
        # Load previous history from Supabase
        res = supabase.table("symptom_history").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        for row in res.data:
            st.session_state.messages.append({"role": "user", "content": row["user_input"]})
            st.session_state.messages.append({"role": "assistant", "content": row["bot_response"]})

    # Display chat messages
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
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
        supabase.table("symptom_history").insert({
            "user_id": user_id,
            "user_input": user_input,
            "bot_response": assistant_reply,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
