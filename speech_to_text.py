import speech_recognition as sr
import streamlit as st

def speech_to_text():
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Speak ...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5)
            
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        st.error(f"Audio recording error: {e}")
        return None