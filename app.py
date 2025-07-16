import streamlit as st
from supabase import create_client
from PIL import Image
import openai
import os
from dotenv import load_dotenv

# --- CONFIG ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()

# --- SUPABASE SETUP ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- OPENAI SETUP ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- AUTH ---
st.title("🔐 เข้าสู่ระบบ / สมัครสมาชิก")
if "user" not in st.session_state:
    mode = st.radio("เลือกเมนู", ["เข้าสู่ระบบ", "สมัครสมาชิก"])

    email = st.text_input("อีเมล")
    password = st.text_input("รหัสผ่าน", type="password")

    if mode == "สมัครสมาชิก":
        if st.button("สมัครสมาชิก"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("✅ สมัครแล้ว กรุณาเข้าสู่ระบบ")
            except Exception as e:
                st.error(f"❌ สมัครไม่สำเร็จ: {e}")
    else:
        if st.button("เข้าสู่ระบบ"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = user
                st.rerun()
            except Exception as e:
                st.error("❌ เข้าสู่ระบบไม่สำเร็จ")

# --- CHATBOT ---
if "user" in st.session_state:
    st.sidebar.success(f"ยินดีต้อนรับ {st.session_state.user.user.email}")
    if st.sidebar.button("ออกจากระบบ"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    st.image("logo.png", width=200)

    user_id = st.session_state.user.user.id

    # Load chat history from Supabase
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน")}
        ]

        # Fetch past messages
        data = supabase.table("symptom_history").select("*").eq("user_id", user_id).order("timestamp").execute()
        for row in data.data:
            st.session_state.messages.append({"role": "user", "content": row["question"]})
            st.session_state.messages.append({"role": "assistant", "content": row["response"]})

    # Show history
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("พิมพ์อาการของคุณ...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"เกิดข้อผิดพลาด: {e}"

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Save to Supabase
        supabase.table("symptom_history").insert({
            "user_id": user_id,
            "question": user_input,
            "response": reply
        }).execute()
