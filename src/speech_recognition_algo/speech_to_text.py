import speech_recognition as sr 
import pyttsx3 

r = sr.Recognizer()
engine = pyttsx3.init()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def record_text():
    while True:
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.2)
                print("En écoute...")
                audio2 = r.listen(source2)
                MyText = r.recognize_google(audio2, language="fr-FR")
                return MyText
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.UnknownValueError:
            print("Unknown Speech Detected")
    return

def output_text(text):
    with open("output.txt", "a", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")
    return

try:
    while True:
        text = record_text()
        output_text(text)
        print(f"Texte: {text}")

except KeyboardInterrupt:
    print("\nProgramme interrompu")
