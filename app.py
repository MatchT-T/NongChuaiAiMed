import streamlit as st
from supabase import create_client, Client
from PIL import Image
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# --- Page Config ---
st.set_page_config(page_title="น้องช่วย", layout="wide")

# --- Load Secrets ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# --- Connect to Supabase ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Auth Mode Switch ---
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# --- Login/Register ---
st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")
menu = st.radio("เลือกเมนู", ["เข้าสู่ระบบ", "สมัครสมาชิก"])
email = st.text_input("อีเมล")
password = st.text_input("รหัสผ่าน", type="password")

if menu == "สมัครสมาชิก":
    if st.button("สมัครสมาชิก"):
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            st.success("✅ สมัครสำเร็จ! ไปยืนยันอีเมล แล้วกลับมาเข้าสู่ระบบนะคะ")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
elif menu == "เข้าสู่ระบบ":
    if st.button("เข้าสู่ระบบ"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user.user:
                st.session_state.logged_in = True
                st.session_state.user = user.user
                st.session_state.token = user.session.access_token
                st.success("✅ เข้าสู่ระบบสำเร็จ")
            else:
                st.error("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        except Exception as e:
            st.error(f"เข้าสู่ระบบล้มเหลว: {e}")

# --- Chat Section ---
if st.session_state.get("logged_in"):
    user_id = st.session_state.user.id
    token = st.session_state.token
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    st.image("logo.png", width=200)

    # --- Load past history ---
    if "messages" not in st.session_state:
        try:
            data = supabase.table("symptom_history")\
                .select("message, reply")\
                .eq("user_id", user_id)\
                .order("timestamp")\
                .execute(headers={"Authorization": f"Bearer {token}"})
            st.session_state.messages = [{"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย..."  # your system prompt here
            )}]
            for row in data.data:
                st.session_state.messages.append({"role": "user", "content": row["message"]})
                st.session_state.messages.append({"role": "assistant", "content": row["reply"]})
        except Exception as e:
            st.session_state.messages = [{"role": "system", "content": "คุณคือน้องช่วย..."}]
            st.error(f"โหลดประวัติไม่สำเร็จ: {e}")

    # --- Chat UI ---
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

        # --- Save to Supabase with Token ---
        try:
            supabase.table("symptom_history").insert({
                "user_id": user_id,
                "message": user_input,
                "reply": assistant_reply
            }).execute(headers={"Authorization": f"Bearer {token}"})
        except Exception as e:
            st.error(f"บันทึกประวัติล้มเหลว: {e}")

