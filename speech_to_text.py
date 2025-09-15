import speech_recognition as sr
import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import io

def speech_to_text():
    """
    Records audio and converts it into text
    """
    
    st.subheader("🎤 Record your voice")
    
    # Audio recorder component
    wav_audio_data = st_audiorec()
    
    if wav_audio_data is not None:
        # Audio playback
        st.audio(wav_audio_data, format='audio/wav')
        
        if st.button("Convert Speech to Text", type="primary"):
            with st.spinner("Converting speech to text..."):
                try:
                    # Convert audio to text
                    recognized_text = convert_audio_to_text(wav_audio_data)
                    
                    if recognized_text:
                        st.success(f"Recognized Text: **{recognized_text}**")
                        return recognized_text
                    else:
                        st.error("Could not recognize speech")
                        return None
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    return None
    
    return None

def convert_audio_to_text(audio_bytes):
    """
    Converts audio bytes into text
    """
    try:
        # Save audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # For speech recognition
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(tmp_file.name) as source:
                audio_data = recognizer.record(source)
                
                # Use Google Web Speech API
                # For Urdu set language="ur-PK"
                text = recognizer.recognize_google(audio_data, language="ur-PK")
                return text
                
    except sr.UnknownValueError:
        st.error("Could not understand the audio. Please try again")
        return None
    except sr.RequestError as e:
        st.error(f"Could not connect to the service: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# For direct microphone recording (optional)
def record_from_microphone():
    """
    Records voice directly from microphone
    """
    if st.button("Record directly from Microphone"):
        try:
            r = sr.Recognizer()
            
            with sr.Microphone() as source:
                st.info("Start speaking...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5)
                
            text = r.recognize_google(audio, language="ur-PK")
            st.success(f"Recognized Text: **{text}**")
            return text
            
        except sr.UnknownValueError:
            st.error("Could not understand the speech")
            return None
        except sr.RequestError as e:
            st.error(f"Could not connect to the service: {e}")
            return None
        except Exception as e:
            st.error(f"Error in audio recording: {e}")
            return None

# Run directly for testing
if __name__ == "__main__":
    st.title("Speech to Text Converter")
    
    # Provide both options
    option = st.radio(
        "Select recording method:",
        ["With st_audiorec (recommended)", "Direct Microphone"]
    )
    
    if option == "With st_audiorec (recommended)":
        result = speech_to_text()
    else:
        result = record_from_microphone()
    
    if result:
        st.success(f"Final Result: {result}")
