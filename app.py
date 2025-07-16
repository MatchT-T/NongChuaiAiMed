import streamlit as st
from PIL import Image
import openai
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# --- Load environment ---
load_dotenv()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Page setup ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")
st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
st.image("logo.png", width=150)

# --- State init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Auth UI ---
menu = st.radio("เลือกเมนู", ["เข้าสู่ระบบ", "สมัครสมาชิก"])

if not st.session_state.logged_in:
    email = st.text_input("อีเมล")
    password = st.text_input("รหัสผ่าน", type="password")

    if menu == "สมัครสมาชิก":
        if st.button("สมัครสมาชิก"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("✅ สมัครสำเร็จ! กรุณายืนยันอีเมลแล้วเข้าสู่ระบบ")
            except Exception as e:
                st.error(f"❌ สมัครไม่สำเร็จ: {e}")

    elif menu == "เข้าสู่ระบบ":
        if st.button("เข้าสู่ระบบ"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.logged_in = True
                st.session_state.user_id = user.user.id
                st.success("✅ เข้าสู่ระบบสำเร็จ")
            except Exception as e:
                st.error(f"❌ เข้าสู่ระบบล้มเหลว: {e}")
                st.stop()

# --- Chat UI ---
if st.session_state.logged_in:
    # Load past history
    if not st.session_state.messages:
        try:
            response = supabase.table("symptom_history")\
                .select("message, role")\
                .eq("user_id", st.session_state.user_id)\
                .order("timestamp")\
                .execute()
            records = response.data
            st.session_state.messages = [{"role": r["role"], "content": r["message"]} for r in records]
        except Exception as e:
            st.warning("⚠️ โหลดประวัติไม่สำเร็จ")

    # System prompt
    if not any(msg["role"] == "system" for msg in st.session_state.messages):
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน"
            )
        })

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

        st.chat_message("assistant", avatar="logo.png").markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        # Save to Supabase
        try:
            supabase.table("symptom_history").insert([
                {"user_id": st.session_state.user_id, "role": "user", "message": user_input, "timestamp": datetime.utcnow()},
                {"user_id": st.session_state.user_id, "role": "assistant", "message": assistant_reply, "timestamp": datetime.utcnow()}
            ]).execute()
        except Exception as e:
            st.warning(f"⚠️ ไม่สามารถบันทึกประวัติได้: {e}")
