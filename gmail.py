from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import base64
import re
import time
import dateutil.parser as parser
from base64 import urlsafe_b64decode
import json
import pickle
import binascii

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def retrieve_unread_emails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API to fetch unread emails
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No new messages.')
    else:
            emails = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = msg['payload']['headers']
                from_name, subject = None, None
                for values in email_data:
                    if values['name'] == 'From':
                        from_name = values['value']
                    if values['name'] == 'Subject':
                        subject = values['value']

                if msg['payload']['mimeType'] == 'text/plain':
                    try:
                        data = msg['payload']['body']['data']
                        byte_code = base64.urlsafe_b64decode(data)
                        text = byte_code.decode("utf-8")
                        emails.append((from_name, subject, text))
                    except binascii.Error:
                        pass
                elif 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            try:
                                data = part['body']['data']
                                byte_code = base64.urlsafe_b64decode(data)
                                text = byte_code.decode("utf-8")
                                emails.append((from_name, subject, text))
                            except binascii.Error:
                                pass
            return emails
    # Call the Gmail API to fetch unread emails
    # results = service.users().messages().list(userId='me', q='is:unread label:inbox').execute()
unread_emails=retrieve_unread_emails()

for email in unread_emails:
    sender, subject, body = email
    print(f"Sender: {sender}, Subject: {subject}")
    