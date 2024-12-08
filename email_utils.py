import imaplib
import email

# Gmail settings
IMAP_SERVER = 'imap.gmail.com'
EMAIL = 'singh.priyank.13112003@gmail.com'
PASSWORD = 'eplw rffl lqvx ocjq'

def read_emails():
    # Connect to Gmail
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    # Search for emails
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()

    # Fetch emails
    for email_id in email_ids[-10:]:  # Fetch the first 10 emails
        status, data = mail.fetch(email_id, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                print(f"Subject: {msg['subject']}")
                print(f"From: {msg['from']}")
                print()

    mail.logout()

if __name__ == '__main__':
    read_emails()
