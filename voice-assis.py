import speech_recognition as sr
import smtplib
import pyttsx3
import os
import imaplib
import email
import json
from email.message import EmailMessage
import datetime

# Initialize voice engine and listener
listener = sr.Recognizer()
engine = pyttsx3.init()

# User credentials (consider using environment variables)
your_password = os.getenv("YOUR_PASSWORD", "water is blue")
your_name = "Anivesh"
sender_email = os.getenv("SENDER_EMAIL", "********************@gmail.com") 
sender_email_pass = os.getenv("SENDER_EMAIL_PASS", "***********************") 

# File to store the email directory
email_directory_file = "mail_directory.json"

def talk(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_info():
    """Capture voice input and convert it to text."""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source, phrase_time_limit=7, timeout=8)
            print("Processing...")
            info = listener.recognize_google(voice)
            print(f"User said: {info}")
            return info.lower()
    except sr.UnknownValueError:
        print('Could not understand audio, please try again.')
        talk("Could not understand, please try again.")
        return get_info()
    except sr.RequestError:
        print('Could not request results, check your internet connection.')
        talk("Could not request results, check your internet connection.")
        return None
    except sr.WaitTimeoutError:
        print('Listening timed out while waiting for phrase to start.')
        talk("Listening timed out, please try again.")
        return None

def authenticate():
    """Authenticate the user based on voice input."""
    while True:
        talk("Please identify yourself by saying the secret code.")
        password = get_info()
        if password is None:
            continue
        if password == your_password:
            talk("Authentication successful.")
            return True
        elif password.lower() == 'exit':
            exit_program()
        else:
            talk("Incorrect password, please try again or say exit to quit.")

def exit_program():
    """Exit the program gracefully."""
    print("Goodbye")
    talk("Goodbye")
    exit()

def send_email(receiver, subject, message):
    """Send an email using SMTP."""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_email_pass)
            email_msg = EmailMessage()
            email_msg['From'] = sender_email
            email_msg['To'] = receiver
            email_msg['Subject'] = subject
            email_msg.set_content(message)
            server.send_message(email_msg)
        print("Email sent successfully.")
        talk("Your email has been sent.")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your email credentials.")
        talk("There was an authentication error. Please check your email settings.")
    except Exception as e:
        print(f"Error sending email: {e}")
        talk("There was an error sending your email.")

def get_email_info(email_list):
    """Gather information to send an email."""
    talk('To whom do you want to send an email?')
    name = get_info()

    if name in email_list:
        receiver = email_list[name]
    else:
        talk("Name not found in email directory.")
        print("Name not found in email directory.")
        return

    talk('What is the subject of your email?')
    subject = get_info()
    talk('Tell me the text in your email.')
    message = get_info()
    send_email(receiver, subject, message)

def get_inbox():
    """Read unread emails one by one, asking the user whether to continue after each."""
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(sender_email, sender_email_pass)
        mail.select('inbox')
        result, data = mail.search(None, 'UNSEEN')  # Only fetch unread (UNSEEN) emails

        if result != 'OK':
            print("No new emails found.")
            talk("No new emails found.")
            return

        email_uids = data[0].split()
        if not email_uids:
            print("No unread emails.")
            talk("You have no unread emails.")
            return

        for uid in email_uids:
            result, email_data = mail.fetch(uid, '(RFC822)')
            if result != 'OK':
                print(f"Failed to fetch email UID {uid}.")
                continue

            raw_email = email_data[0][1].decode('utf-8')
            email_message = email.message_from_string(raw_email)
            email_from = email.utils.parseaddr(email_message['From'])[1]
            subject = email_message['Subject']
            date = email_message['Date']
            print(f"From: {email_from}\nSubject: {subject}\nDate: {date}\n")

            # Displaying body if necessary
            body = ""
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
            if body:
                print(f"Body:\n{body}\n")
                talk(f"You have an email from {email_from} with the subject {subject}. The message is: {body}")
            else:
                talk(f"You have an email from {email_from} with the subject {subject}, but it has no text content.")

            # Ask the user if they want to continue to the next unread email
            talk("Do you want to read the next email? Say yes to continue or no to stop.")
            response = get_info()
            if response and 'no' in response:
                print("Stopped reading emails.")
                talk("Stopped reading emails.")
                break

        # Optionally, mark all fetched emails as seen (optional as IMAP fetch typically marks as seen)
        # mail.close()
        # mail.logout()

    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
        talk("There was an error accessing your inbox.")
    except Exception as e:
        print(f"Error reading inbox: {e}")
        talk("There was an unexpected error accessing your inbox.")

def load_email_directory():
    """Load the email directory from the JSON file. Create the file if it doesn't exist."""
    if not os.path.exists(email_directory_file):
        # Create an empty email directory
        with open(email_directory_file, 'w') as file:
            json.dump({}, file, indent=4)
        print(f"{email_directory_file} created as it did not exist.")
        talk("Email directory file created.")
        return {}
    else:
        try:
            with open(email_directory_file, 'r') as file:
                email_list = json.load(file)
                print(f"Loaded email directory from {email_directory_file}.")
                return email_list
        except json.JSONDecodeError:
            print(f"Error decoding {email_directory_file}. Starting with an empty directory.")
            talk("There was an error with the email directory file. Starting with an empty directory.")
            return {}
        except Exception as e:
            print(f"Error loading email directory: {e}")
            talk("There was an error loading your email directory.")
            return {}

def save_email_directory(email_list):
    """Save the email directory to the JSON file."""
    try:
        with open(email_directory_file, 'w') as file:
            json.dump(email_list, file, indent=4)
        print(f"Email directory saved to {email_directory_file}.")
    except Exception as e:
        print(f"Error saving email directory: {e}")
        talk("There was an error saving your email directory.")

def add_new_email(email_list):
    """Add a new email to the email directory."""
    talk("Please provide the nickname of the person.")
    nickname = get_info()

    while True:
        talk("Please provide the email address.")
        new_email = get_info()
        if not new_email or '@' not in new_email:
            talk("That doesn't seem to be a valid email address. Please try again.")
            continue

        talk(f"Is this the correct email: {new_email}? Say 'yes' to confirm or 'no' to retry.")
        confirmation = get_info()

        if 'yes' in confirmation.lower():
            email_list[nickname] = new_email
            save_email_directory(email_list)
            talk(f"{nickname} has been added to your email directory.")
            print(f"Added: {nickname} -> {new_email}")
            break
        else:
            talk("Let's try again.")

def remove_email(email_list):
    """Remove an email from the email directory."""
    talk("Please provide the nickname of the person you want to remove.")
    nickname = get_info()

    if nickname in email_list:
        del email_list[nickname]
        save_email_directory(email_list)
        talk(f"{nickname} has been removed from your email directory.")
        print(f"Removed: {nickname}")
    else:
        talk("That nickname was not found in your email directory.")
        print(f"Nickname '{nickname}' not found.")
        
def update_email(email_list):
    """Update an existing email in the email directory."""
    talk("Please provide the nickname of the person whose email you want to update.")
    nickname = get_info()

    if nickname in email_list:
        talk(f"The current email for {nickname} is {email_list[nickname]}.")
        talk("Please provide the new email address.")
        new_email = get_info()
        if not new_email or '@' not in new_email:
            talk("That doesn't seem to be a valid email address. Update canceled.")
            return

        talk(f"Is this the correct new email: {new_email}? Say 'yes' to confirm or 'no' to cancel.")
        confirmation = get_info()

        if 'yes' in confirmation.lower():
            email_list[nickname] = new_email
            save_email_directory(email_list)
            talk(f"{nickname}'s email has been updated.")
            print(f"Updated: {nickname} -> {new_email}")
        else:
            talk("Update canceled.")
    else:
        talk("That nickname was not found in your email directory.")
        print(f"Nickname '{nickname}' not found.")

def open_email_directory():
    """Open the email directory JSON file using the default text editor."""
    try:
        if os.name == 'nt':  # For Windows
            os.startfile(email_directory_file)
        elif os.name == 'posix':  # For Unix/Linux/Mac
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            os.system(f"{opener} {email_directory_file}")
        talk("Opening your email directory file.")
    except Exception as e:
        print(f"Error opening email directory file: {e}")
        talk("There was an error opening your email directory file.")

def modify_email_directory(email_list):
    """Provide options to modify the email directory."""
    while True:
        talk("What would you like to do? You can add, remove, update an email, or open the email directory.")
        print("Options: add, remove, update, open, done")
        command = get_info()

        if "add" in command:
            add_new_email(email_list)
        elif "remove" in command:
            remove_email(email_list)
        elif "update" in command:
            update_email(email_list)
        elif "open" in command:
            open_email_directory()
        elif "done" in command or "finish" in command:
            talk("Finished modifying email directory.")
            break
        else:
            talk("I did not understand that command. Please try again.")

def main():
    """Main function to run the personal assistant."""
    os.system("cls" if os.name == "nt" else "clear")
    print("*-"*10)    
    print("Welcome to your personal assistant")
    talk("Welcome to your personal assistant")
    print("*-"*10)

    if authenticate():
        talk("Welcome!")
        email_list = load_email_directory()

        while True:
            talk("What can I do for you?")
            command = get_info()

            if command:
                if ("send" in command or "write" in command) and ("email" in command):
                    get_email_info(email_list)
                elif ("read" in command or "open" in command) and ("email" in command):
                    get_inbox()
                elif ("add" in command or "remove" in command or "update" in command) and ("email" in command or "directory" in command):
                    modify_email_directory(email_list)
                elif ("open" in command) and ("directory" in command):
                    open_email_directory()
                elif ("quit" in command or "exit" in command):
                    exit_program()
                else:
                    talk("I did not understand that command. Please try again.")

if __name__ == "__main__":
    main()
