import streamlit as st
from supabase import create_client
from PIL import Image
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# --- Page Config ---
st.set_page_config(page_title="น้องช่วย", layout="wide")

# --- Load Environment Variables ---
load_dotenv()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_SECRET_KEY = st.secrets["SUPABASE_SECRET_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# --- Connect to Supabase ---
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

# --- Auth state ---
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if not st.session_state.get("logged_in"):
    st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")
    email = st.text_input("อีเมล")
    password = st.text_input("รหัสผ่าน", type="password")

    if st.session_state.auth_mode == "login":
        if st.button("เข้าสู่ระบบ"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if user.user:
                    st.session_state.user = user.user
                    st.session_state.logged_in = True
                    st.success("✅ เข้าสู่ระบบสำเร็จ")
                    st.rerun()
                else:
                    st.error("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
            except Exception as e:
                st.error(f"เข้าสู่ระบบล้มเหลว: {e}")

        if st.button("ยังไม่มีบัญชี? 👉 สมัครสมาชิก"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    elif st.session_state.auth_mode == "signup":
        if st.button("สมัครสมาชิก"):
            try:
                user = supabase.auth.sign_up({"email": email, "password": password})
                st.success("✅ สมัครสำเร็จ! ไปยืนยันอีเมล แล้วกลับมาเข้าสู่ระบบได้เลยค่ะ")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

        if st.button("มีบัญชีอยู่แล้ว? 👉 เข้าสู่ระบบ"):
            st.session_state.auth_mode = "login"
            st.rerun()

# --- Chat UI ---
if st.session_state.get("logged_in"):
    user_id = st.session_state.user.id

    # --- Header ---
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)

    # Center logo and logout button using HTML
    st.markdown("""
        <div style='text-align: center; margin-top: 1em; margin-bottom: 1em;'>
            <img src='https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/logo.png' width='120'/>
            <br>
            <button onclick="fetch('/_stcore/logout', {method: 'POST'}).then(() => location.reload())"
                style='margin-top:10px; padding:8px 16px; font-size:14px;'>🚪 ออกจากระบบ</button>
        </div>
    """, unsafe_allow_html=True)

    # Optional backup logout (Streamlit native button)
    if st.button("🚪 ออกจากระบบ"):
        st.session_state.clear()
        st.rerun()

    # --- Load chat history ---
    if "messages" not in st.session_state:
        try:
            response = supabase.table("symptom_history").select("message, reply").eq("user_id", user_id).order("timestamp").execute()
            st.session_state.messages = [{"role": "system", "content": "คุณคือน้องช่วย..."}]
            for row in response.data:
                st.session_state.messages.append({"role": "user", "content": row["message"]})
                st.session_state.messages.append({"role": "assistant", "content": row["reply"]})
        except Exception as e:
            st.session_state.messages = [{"role": "system", "content": "คุณคือน้องช่วย..."}]
            st.error(f"ไม่สามารถโหลดประวัติได้: {e}")

    # --- Display chat ---
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Input & Response ---
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

        try:
            supabase.table("symptom_history").insert({
                "user_id": user_id,
                "message": user_input,
                "reply": assistant_reply
            }).execute()
        except Exception as e:
            st.error(f"บันทึกประวัติล้มเหลว: {e}")

