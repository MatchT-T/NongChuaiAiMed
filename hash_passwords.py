import streamlit_authenticator as stauth

# Replace with your real passwords
passwords = ['123', '456']
hashed_passwords = stauth.Hasher(passwords).generate()

for i, hashed in enumerate(hashed_passwords):
    print(f"user{i+1} hashed password: {hashed}")
