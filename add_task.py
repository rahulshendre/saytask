#!/usr/bin/env python3
import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/tasks']
DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(DIR, 'credentials.json')
TOKEN_FILE = os.path.join(DIR, 'token.json')

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('tasks', 'v1', credentials=creds)

def add_task(title, notes=None):
    service = get_service()
    task = {'title': title}
    if notes:
        task['notes'] = notes
    result = service.tasks().insert(tasklist='@default', body=task).execute()
    print(f"Task added: {result['title']} (id: {result['id']})")
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_task.py 'Task title'")
        sys.exit(1)
    title = ' '.join(sys.argv[1:])
    add_task(title)
