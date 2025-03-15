import streamlit as st
import sqlite3
import speech_recognition as sr
import pyttsx3
import requests
import base64

# ------------------ App Config ------------------
st.set_page_config(page_title="Smart City Security", layout="wide")

# ------------------ Background Setup ------------------
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def set_background(png_file):
    bin_str = get_base64(png_file)
    if bin_str:
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{bin_str}");
                background-size: cover;
            }}
            </style>
        ''', unsafe_allow_html=True)

set_background("background/4.jpg")

# ------------------ Database Functions ------------------
def create_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

create_db()

# ------------------ TTS ------------------
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# ------------------ UI ------------------
st.title("Smart City Security Login")

option = st.sidebar.radio("Select Option", ["Login", "Register"])

if option == "Register":
    st.header("Register")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(user, pwd):
            st.success("User registered successfully! ✅")
        else:
            st.error("Username already exists. ❌")

elif option == "Login":
    st.header("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(user, pwd):
            st.success("Login successful! ✅")
            
            # ------------------ Voice Assistant ------------------
            st.subheader("Voice Assistant 🎙️")
            if st.button("Start Voice Command"):
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    st.write("Listening...")
                    audio = recognizer.listen(source)
                    try:
                        command = recognizer.recognize_google(audio)
                        st.success(f"You said: {command}")
                        speak(f"You said: {command}")
                    except:
                        st.error("Voice not recognized. ❌")

            # ------------------ URL Accessibility Checker ------------------
            st.subheader("Internet URL Check 🌐")
            url = st.text_input("Enter URL", "https://www.google.com")
            if st.button("Check URL"):
                try:
                    response = requests.get(url, timeout=5)
                    st.success(f"URL is reachable ✅ (Status {response.status_code})")
                except Exception as e:
                    st.error(f"Error: {e} ❌")
        else:
            st.error("Invalid login. ❌")
