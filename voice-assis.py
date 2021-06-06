import speech_recognition as sr
import smtplib
#import pyaudio
import pyttsx3
import gc
import imaplib
import email
import os
from email.message import EmailMessage

listener = sr.Recognizer()
engine = pyttsx3.init()
host ='imap.gmail.com'

your_password = "water is blue"
your_name = "Anivesh"
sender_Email="a##########333@gmail.com"
sender_Email_pass="##################"

email_list = {
    'mayank' : 'mayan$##########@gmail.com',
    'anivesh' : 'ani$$$$$$$%%%%%%%@gmail.com'
}

def talk(text):
    engine.say(text)
    engine.runAndWait()

def get_info():
    try:
        with sr.Microphone() as source:
            print('listening...')
            listener.adjust_for_ambient_noise(source)
            # listener.dynamic_energy_threshold = False
            voice = listener.listen(source, phrase_time_limit=7, timeout=8)
            print("ok.......")
            info = listener.recognize_google(voice)    #Google API to convert voice to text
            print(info)
            return info.lower()
    except:
        print('Try Again')

def get_inbox():
    mail = imaplib.IMAP4_SSL(host)
    mail.login(sender_Email, sender_Email_pass)
    mail.select("inbox")
    _, search_data = mail.search(None, 'UNSEEN')
    my_message = []
    for num in search_data[0].split():
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')
        # print(data[0])
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        for header in ['subject', 'to', 'from', 'date']:
            print("{}: {}".format(header, email_message[header]))
            email_data[header] = email_message[header]
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                email_data['body'] = body.decode()
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True)
                email_data['html_body'] = html_body.decode()
        my_message.append(email_data)
    return my_message

def send_email(receiver,subject,message):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    #make sure to give app acess in google account
    server.login(sender_Email, sender_Email_pass)
    email = EmailMessage()
    email['From'] = sender_Email
    email['To'] = receiver
    email['Subject'] = subject
    email.set_content(message)
    server.send_message(email)

def get_email_info():
    print("To Whom you want to send email")
    talk('To Whom you want to send email')
    name = get_info() 
    receiver = email_list[name]
    receiver = email_list[name]
    print(receiver)
    talk('What is the subject of your email?')
    subject = get_info()
    talk('Tell me the text in your email')
    message = get_info()
    send_email(receiver, subject, message)
    talk('Hey , Your email is sent')
    talk('Do you want to send more email?')
    send_more = get_info()
    if 'yes' in send_more:
        get_email_info()


def auth(password):
    if password == your_password :
        return 0
    elif password == exit :
        return 2
    else :
        print("Your Password is in correct, Try again .. and if you don't know say EXIt ..")    
        talk("Your Password is in correct, Try again .. and if you don't know say EXIt ..")   
        x = get_info()
        auth(x)

def exit() :
    print("bye")        
    talk("bye")
     

os.system("cls")
print("*-"*10)    
print("Welcome to your personal assistance")
talk("Welcome to your personal assistance")
print("*-"*10)    

print("Please Identiye Yourself, say the secret code")
talk("Please Identiye Yourself, say the secret code")
password = get_info()
x= auth(password)
if x == 2 :
    exit()
    
else :
    talk("welcome, ")
    while True :
        gc.collect()
        talk("what can i do for you?")
        print("what can i do for you?")
        p=get_info()
        if (("send" in p) or ("write" in p)) and (("email" in p) or ("gmail" in p) or ("mail" in p)) :
            get_email_info()

        elif (("read" in p) or ("open" in p)) and (("email" in p) or ("gmail" in p)) :
            get_inbox()

        elif (("quit" in p) or("exit" in p) )   :
            break

exit()        

