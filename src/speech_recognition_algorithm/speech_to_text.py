import speech_recognition as sr  # type: ignore
import pyttsx3  # type: ignore

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
                speak_text("Je vous écoute")
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

# Initial message
speak_text("Je suis Yatra GPT. Je vais répéter tout ce que vous dites")

try:
    while True:
        text = record_text()
        if "arrête" in text.lower():
            speak_text("Programme interrompu")
            print("\nProgramme interrompu")
            break
        output_text(text)
        speak_text(f"Vous avez dit: {text}")
        print(f"Texte: {text}")

except KeyboardInterrupt:
    print("\nProgramme interrompu")
