from __future__ import print_function
import os.path
import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String
from requests import Session
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

engine = db.create_engine('sqlite:///gmail.db', echo=True)
meta = db.MetaData()


mail = Table(
   'mail', meta,
   Column('id', Integer, primary_key=True),
   Column('description', String),
   Column('thID', String),
)
session = Session()
meta.create_all(engine)


def get_gmail_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_email_list():
    service = get_gmail_service()
    results=service.users().messages().list(userId='me',maxResults=5).execute()
    return results.get('messages',[])

def get_email_content(message_id):
    service=get_gmail_service()
    results = service.users().messages().get(userId='me', id=message_id).execute()
    data = {'snippet': results['snippet'],'threadId': results['threadId']}
    return data

def store():
    engine = db.create_engine('sqlite:///gmail.db', echo=True)
    conn = engine.connect()
    result = get_email_content('17a50ab54502b678')
    conn.execute('INSERT INTO mail(description,thId) VALUES(:description,:thId)',
                 (result['snippet']), result['threadId'])
    print("entered successfully")
    conn.close()


if __name__ == '__main__':
    store()
