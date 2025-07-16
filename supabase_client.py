from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["https://tdqepmunuwfaqmsmusry.supabase.co/"]
SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkcWVwbXVudXdmYXFtc211c3J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2NTgyNjgsImV4cCI6MjA2ODIzNDI2OH0.xyPdUcWmBfzkF1zGp3lkM7HVzCQ7GWA9s17fDg3G_UQ"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
