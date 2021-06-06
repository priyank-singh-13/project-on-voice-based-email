import pyttsx3

engine = pyttsx3.init()

def talk(text):
    engine.say(text)
    engine.runAndWait()


x= "hello"

talk("this is me"+x)
print("this is me"+x)