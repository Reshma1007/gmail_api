from __future__ import print_function
import base64
import email
import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def get_gmail_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_email_list():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me',maxResults=5).execute()
    return results.get('messages',[])

def get_email_service(msg_id):
    service = get_gmail_service()
    results = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(results['raw'])
    min_msg = email.message_from_bytes(msg_str)
    data = {'to': min_msg['To'], 'from': min_msg['From'], 'date': min_msg['Date'], 'subject': min_msg['Subject']}
    return data


if __name__ == '__main__':
    get_email_list('17a50e49f6e74e09')




