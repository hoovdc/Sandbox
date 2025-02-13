import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def refresh_or_get_new_token(token_path, credentials_path, scopes):
    """
    Attempts to refresh existing token or get new credentials if needed.
    
    Args:
        token_path: Path to token.json
        credentials_path: Path to credentials.json
        scopes: List of required API scopes
    
    Returns:
        google.oauth2.credentials.Credentials: Valid credentials object
    """
    creds = None
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
    except Exception as e:
        print(f"Error loading token: {e}")
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        
        # Save the valid token
        try:
            with open(token_path, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Warning: Failed to save token: {e}")
    
    return creds

def get_calendar_service():
    """Get authenticated Google Calendar service."""
    secrets_dir = os.path.join(os.path.dirname(__file__), '..', 'Secrets')
    credentials_path = os.path.join(secrets_dir, 'Google_calendar_credentials.json')
    token_path = os.path.join(secrets_dir, 'Google_calendar_token.json')
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    
    creds = refresh_or_get_new_token(token_path, credentials_path, scopes)
    return build('calendar', 'v3', credentials=creds)