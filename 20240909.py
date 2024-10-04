#gcal_standalone.py
#This script exports events from your Google Calendar to a CSV file.
#Code originally generated by Cursor using Claude 3.5 Sonnet

import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import csv

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def main():
    service = get_calendar_service()
    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting events from your calendar...')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=100, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    # Prepare CSV file
    with open('calendar_events.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Event Title', 'Event Duration', 'Event Color'])

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse start and end times
            start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            # Calculate duration
            duration = end_time - start_time
            
            # Get event color
            color_id = event.get('colorId', 'default')
            
            writer.writerow([
                start_time.date(),
                event['summary'],
                str(duration),
                color_id
            ])

    print('Events exported to calendar_events.csv')

if __name__ == '__main__':
    main()