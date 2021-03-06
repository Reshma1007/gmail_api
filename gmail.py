from __future__ import print_function
import base64
import email
import json
import os.path
import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, VARCHAR, engine
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
   Column('mail_to', String),
   Column('mail_from', VARCHAR),
   Column('mail_subject' , String),
   Column('mail_date', String)
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
    results = service.users().messages().list(userId='me',maxResults=5).execute()
    return results.get('messages',[])

def get_email_service(msg_id):
    service = get_gmail_service()
    results = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(results['raw'])
    min_msg = email.message_from_bytes(msg_str)
    data = {'to': min_msg['To'], 'from': min_msg['From'], 'date': min_msg['Date'], 'subject': min_msg['Subject']}
    return data

def store():
    engine = db.create_engine('sqlite:///gmail.db', echo=True)
    conn = engine.connect()
    results = get_email_service('17a50e49f6e74e09')
    conn.execute('INSERT INTO mail(mail_from,mail_to,mail_subject,mail_date) VALUES(:mail_from,:mail_to,:mail_subject,:mail_date)',
                 results['from'], results['to'], results['subject'], results ['date'])
    print("entered successfully")
    conn.close()

def mark_as_unread():
    engine = db.create_engine('sqlite:///gmail.db', echo=True)
    engine.connect()
    rules = json.load(open('rules.json'))
    for rule in rules["1"]["content"]:
        print(rule['name'], rule['value'])
        service = get_gmail_service()
        service.users().messages().modify(userId='me', id='17a50e49f6e74e09',body={'addLabelIds': ['UNREAD']}).execute()

def mark_as_read():
    rules = json.load(open('rules.json'))
    for rule in rules["rule1"]["content"]:
        print(rule['name'], rule['value'])
        service = get_gmail_service()
        service.users().messages().modify(userId='me', id='17a50e49f6e74e09',body={'removeLabelIds': ['READ']}).execute()

def starred():
    engine = db.create_engine('sqlite:///gmail.db', echo=True)
    engine.connect()
    rules = json.load(open('rules.json'))
    for rule in rules["1"]["content"]:
        print(rule['name'], rule['value'])
        service = get_gmail_service()
        service.users().messages().modify(userId='me', id='17a50e49f6e74e09', body={'addLabelIds': ['STARRED']}).execute()

def archive():
    engine = db.create_engine('sqlite:///gmail.db', echo=True)
    engine.connect()
    rules = json.load(open('rules.json'))
    for rule in rules["1"]["content"]:
        print(rule['name'], rule['value'])
        service = get_gmail_service()
        service.users().messages().modify(userId='me', id='17a50e49f6e74e09', body={'addLabelIds': ['INBOX']}).execute()

def add_label():
    service = get_gmail_service()
    label={
        "labelListVisibility":"labelShow",
        "messageListVisibility":"show",
        "name":"lab"
    }
    result=service.users().labels().create(userId='me', body=label).execute()
    print(result)

if __name__ == '__main__':
      store()
    # mark_as_unread()
    # mark_as_read()
    # starred()
    # archive()
    # add_label()
