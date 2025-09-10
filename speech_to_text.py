import speech_recognition as sr

def speech_to_text():
    # Convert microphone input into urdu text 
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak ...")
        r.adjust_for_ambient_noise(source,duration=1)
        try:
            audio_text = r.listen(source,timeout=20)
            print("Recording Finished")
            spoken_text = r.recognize_google(audio_text)
            print("You said ",spoken_text)
            return spoken_text
        except sr.UnknownValueError:
            print("I could not understand the voice")
        except sr.RequestError:
            print("Could not connect with google speech service")
        except sr.WaitTimeoutError:
            print("Timeout, Please Speak Again")
        return None