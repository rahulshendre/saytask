#!/usr/bin/env python3
import os
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


def list_tasks(show_completed=False):
    service = get_service()
    result = service.tasks().list(
        tasklist='@default',
        showCompleted=show_completed,
        showHidden=show_completed,
        maxResults=100,
    ).execute()
    items = result.get('items', [])
    if not items:
        print("No tasks. You're all caught up.")
        return

    pending = [t for t in items if t.get('status') != 'completed']
    done = [t for t in items if t.get('status') == 'completed']

    if pending:
        print(f"\n  Tasks ({len(pending)}):")
        for i, t in enumerate(pending, 1):
            due = t.get('due', '')
            due_str = f"  (due {due[:10]})" if due else ""
            print(f"  {i}. {t['title']}{due_str}")
    if show_completed and done:
        print(f"\n  Done ({len(done)}):")
        for t in done:
            print(f"  x {t['title']}")
    print()


if __name__ == '__main__':
    import sys
    show_all = len(sys.argv) > 1 and sys.argv[1] in ('-a', '--all', 'all')
    list_tasks(show_completed=show_all)
