import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image
import openai
import os
from dotenv import load_dotenv

# --- App Config ---
st.set_page_config(page_title="น้องช่วย", layout="wide")
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# --- Dummy user login setup ---
names = ['สมชาย', 'สมหญิง']
usernames = ['user1', 'user2']
passwords = ['123', '456']  # Plaintext (for testing only!)

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "nongchuai_cookie", "some_random_key", cookie_expiry_days=30
)

# --- Login form ---
name, authentication_status, username = authenticator.login("เข้าสู่ระบบ", "main")

if authentication_status is False:
    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    st.stop()
elif authentication_status is None:
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนใช้งาน")
    st.stop()
else:
    authenticator.logout("ออกจากระบบ", "sidebar")
    st.success(f"✅ สวัสดีคุณ {name}!")

    # --- App Content ---
    st.markdown("<h1 style='text-align: center;'>น้องช่วย AI Healthcare Assistant</h1>", unsafe_allow_html=True)
    logo = Image.open("logo.png")
    st.image(logo, width=200)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": (
                "คุณคือน้องช่วย ผู้ช่วยด้านสุขภาพที่พูดภาษาไทย คุณไม่ใช่แพทย์และจะไม่วินิจฉัยโรคหรือสั่งยา "
                "แต่สามารถให้คำแนะนำเบื้องต้น เช่น การพักผ่อน การดื่มน้ำ หรือการไปพบแพทย์ "
                "คุณควรให้คำตอบที่สุภาพ อบอุ่น เป็นกันเอง และเข้าใจง่ายสำหรับทุกคน")}
        ]

    # Display previous chat messages
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box
    user_input = st.chat_input("พิมพ์อาการของคุณหรือสอบถามสิ่งที่ต้องการได้ที่นี่...")

    if user_input:
        # Show user message
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate response
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_reply = f"ขออภัย เกิดข้อผิดพลาด: {e}"

        # Show assistant message with custom logo
        with st.chat_message("assistant", avatar="logo.png"):
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

