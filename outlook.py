import imaplib
import email
from email.header import decode_header

def get_unread_emails(user, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")

    result, data = mail.uid('search', None, "(UNSEEN)") # search and return uids of unread emails
    if result == 'OK':
        for num in data[0].split():
            result, data = mail.uid('fetch', num, '(BODY.PEEK[])') # don't mark the email as read
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            print(decode_header(email_message['Subject'])[0])
    else:
        print("No new emails.")

    mail.logout()

get_unread_emails("")

