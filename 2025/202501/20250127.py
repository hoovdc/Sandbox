#Aggegregates Google Calendar event times and Notion task times
#Generated by Cursor using Claude 3.5 Sonnet
import os
import datetime
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import asyncio
import aiohttp
import sqlite3
import os.path
from pathlib import Path


# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_local_calendar_service():
    """Get calendar service using credentials from environment variables or secure storage."""
    # Load credentials from environment variables or secure storage
    creds = None
    token_path = os.getenv('GOOGLE_TOKEN_PATH', 'path/to/token.json')
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'path/to/credentials.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def adjust_overlapping_events(events):
    """Handle overlapping events within a single day."""
    sorted_events = sorted(events, key=lambda e: (e['start'], -e['duration']))
    adjusted_events = []
    last_end = None

    for event in sorted_events:
        if event['questionable']:
            adjusted_events.append(event)
            continue

        if last_end and event['start'] < last_end:
            if event['end'] <= last_end:
                continue  # Skip completely overlapped events
            event['start'] = last_end
            # Calculate duration in hours
            event['duration'] = (event['end'] - event['start']).total_seconds() / 3600

        adjusted_events.append(event)
        last_end = max(last_end, event['end']) if last_end else event['end']

    return adjusted_events

def calculate_event_hours(events, date):
    """Calculate total hours of events for a specific date, handling overlaps."""
    day_events = []
    central = pytz.timezone('US/Central')
    
    for event in events:
        if 'attendees' in event:
            if any(attendee.get('self') and attendee.get('responseStatus') == 'declined' 
                   for attendee in event['attendees']):
                continue

        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        
        if not start or not end:
            continue
            
        start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        start_time_central = start_time.astimezone(central)
        end_time_central = end_time.astimezone(central)
        
        if start_time_central.date() == date:
            summary = event.get('summary', '').lower()
            questionable = any(word in summary for word in ["?", "tbd", "canx", "//", "prev complete"])
            
            if not questionable:
                duration = (end_time_central - start_time_central).total_seconds() / 3600  # Convert to hours
                day_events.append({
                    'start': start_time_central,
                    'end': end_time_central,
                    'duration': duration,  # Store as float hours
                    'questionable': questionable
                })
    
    adjusted_events = adjust_overlapping_events(day_events)
    total_hours = sum(event['duration'] for event in adjusted_events)
    return total_hours

def get_notion_headers():
    """Get Notion headers from environment variables."""
    NOTION_SECRET_KEY = os.getenv('NOTION_SECRET_KEY')
    DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    if not NOTION_SECRET_KEY or not DATABASE_ID:
        raise ValueError("NOTION_SECRET_KEY or NOTION_DATABASE_ID environment variables are not set")

    return {
        "Authorization": f"Bearer {NOTION_SECRET_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }, DATABASE_ID

async def fetch_chunk(session, headers, DATABASE_ID, chunk_start, chunk_end, semaphore):
    """Fetch a chunk of tasks asynchronously with rate limiting."""
    async with semaphore:
        chunk_totals = {}
        has_more = True
        next_cursor = None
        
        while has_more:
            payload = {
                'filter': {
                    'and': [
                        {
                            'property': 'Done?',
                            'checkbox': {
                                'equals': True
                            }
                        },
                        {
                            'property': 'Due Date',
                            'date': {
                                'on_or_after': chunk_start.isoformat(),
                                'on_or_before': chunk_end.isoformat()
                            }
                        }
                    ]
                }
            }
            
            if next_cursor:
                payload['start_cursor'] = next_cursor
            
            try:
                async with session.post(
                    f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 1))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    for task in result.get('results', []):
                        due_date_prop = task['properties'].get('Due Date', {}).get('date')
                        if due_date_prop and due_date_prop.get('start'):
                            try:
                                date = datetime.datetime.fromisoformat(
                                    due_date_prop['start'].replace('Z', '+00:00')
                                ).date()
                                time_block = task['properties'].get('Time Block (Min)', {}).get('number', 0)
                                if time_block:
                                    chunk_totals[date] = chunk_totals.get(date, 0) + time_block
                            except ValueError:
                                continue
                    
                    has_more = result.get('has_more', False)
                    next_cursor = result.get('next_cursor')
                    
                    if has_more:
                        await asyncio.sleep(0.1)  # Small delay between pagination requests
                    
            except aiohttp.ClientError as e:
                print(f"Error fetching chunk {chunk_start} to {chunk_end}: {e}")
                break
        
        return chunk_totals

async def fetch_all_chunks(headers, DATABASE_ID, date_chunks):
    """Fetch all chunks concurrently with rate limiting."""
    semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_chunk(session, headers, DATABASE_ID, chunk_start, chunk_end, semaphore)
            for chunk_start, chunk_end in date_chunks
        ]
        results = await asyncio.gather(*tasks)
    
    daily_totals = {}
    for chunk_totals in results:
        daily_totals.update(chunk_totals)
    
    return daily_totals

def fetch_local_completed_tasks_by_date_range(start_date, end_date):
    """Fetch completed tasks for a date range and return daily totals."""
    headers, DATABASE_ID = get_notion_headers()
    
    # Split the date range into smaller chunks for more efficient requests
    date_chunks = []
    current_date = start_date
    while current_date < end_date:
        chunk_end = min(current_date + datetime.timedelta(days=30), end_date)  # Reduced chunk size
        date_chunks.append((current_date, chunk_end))
        current_date = chunk_end + datetime.timedelta(days=1)
    
    # Run the asynchronous fetching using asyncio.run
    daily_totals = asyncio.run(fetch_all_chunks(headers, DATABASE_ID, date_chunks))
    
    return daily_totals

def get_daily_summary(target_date):
    """Get combined summary for a specific date."""
    # Get calendar hours
    service = get_local_calendar_service()
    central = pytz.timezone('US/Central')
    
    # Query for the specific day
    start_time = datetime.datetime.combine(target_date, datetime.time.min, tzinfo=central).astimezone(datetime.timezone.utc)
    end_time = datetime.datetime.combine(target_date, datetime.time.max, tzinfo=central).astimezone(datetime.timezone.utc)
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime',
        maxResults=2500
    ).execute()
    
    events = events_result.get('items', [])
    calendar_hours = calculate_event_hours(events, target_date)
    calendar_minutes = int(calendar_hours * 60)
    
    # Get Notion tasks minutes
    target_datetime = datetime.datetime.combine(target_date, datetime.time.min)
    target_datetime = pytz.timezone('US/Central').localize(target_datetime)
    notion_minutes = fetch_local_completed_tasks_by_date_range(target_date, target_date)
    
    return calendar_minutes, notion_minutes

def process_calendar_events(events):
    """Process all calendar events and return daily totals."""
    daily_totals = {}  # Initialize the dictionary
    central = pytz.timezone('US/Central')
    
    for event in events:
        if 'attendees' in event:
            if any(attendee.get('self') and attendee.get('responseStatus') == 'declined' 
                   for attendee in event['attendees']):
                continue

        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        
        if not start or not end:
            continue
            
        start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        start_time_central = start_time.astimezone(central)
        end_time_central = end_time.astimezone(central)
        
        date = start_time_central.date()
        
        summary = event.get('summary', '').lower()
        questionable = any(word in summary for word in ["?", "tbd", "canx", "//", "prev complete"])
        
        if not questionable:  # Only include non-questionable events
            duration = (end_time_central - start_time_central).total_seconds() / 3600
            daily_totals[date] = daily_totals.get(date, 0) + duration * 60  # Convert to minutes
    
    return daily_totals

def adapt_date(date):
    """Convert date to string for SQLite storage."""
    return date.isoformat()

def convert_date(date_str):
    """Convert string from SQLite to date object."""
    return datetime.date.fromisoformat(date_str.decode())

# Register the adapters
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

def setup_database():
    """Setup SQLite database and tables."""
    # Use environment variable for database path or default to a local path
    db_path = os.getenv('DASHBOARD_DB_PATH', 'dashboard_data.db')
    
    # Add detect_types parameter to enable date conversion
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Explicitly specify DATE type in table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            date DATE PRIMARY KEY,
            minutes FLOAT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notion_tasks (
            date DATE PRIMARY KEY,
            minutes FLOAT
        )
    ''')
    
    conn.commit()
    return conn

def get_stored_data(conn, start_date, end_date):
    """Retrieve stored data from database for date range."""
    cursor = conn.cursor()
    
    # Get stored calendar data
    cursor.execute('''
        SELECT date, minutes FROM calendar_events 
        WHERE date BETWEEN ? AND ?
    ''', (start_date, end_date))
    calendar_stored = {date: minutes for date, minutes in cursor.fetchall()}
    
    # Get stored notion data
    cursor.execute('''
        SELECT date, minutes FROM notion_tasks 
        WHERE date BETWEEN ? AND ?
    ''', (start_date, end_date))
    notion_stored = {date: minutes for date, minutes in cursor.fetchall()}
    
    return calendar_stored, notion_stored

def store_calendar_data(conn, daily_totals):
    """Store calendar data in database."""
    cursor = conn.cursor()
    for date, minutes in daily_totals.items():
        cursor.execute('''
            INSERT OR REPLACE INTO calendar_events (date, minutes)
            VALUES (?, ?)
        ''', (date.isoformat(), minutes))
    conn.commit()

def store_notion_data(conn, daily_totals):
    """Store notion data in database."""
    cursor = conn.cursor()
    for date, minutes in daily_totals.items():
        cursor.execute('''
            INSERT OR REPLACE INTO notion_tasks (date, minutes)
            VALUES (?, ?)
        ''', (date.isoformat(), minutes))
    conn.commit()

def main():
    central = pytz.timezone('US/Central')
    today = datetime.datetime.now(central).date()
    start_date = datetime.date(2024, 8, 5)  # #first date of my Notion usage was 20240805. Migrated from Asana
    end_date = today - datetime.timedelta(days=1)
    
    print(f"Analyzing data from {start_date} to {end_date}")
    
    # Setup database connection
    conn = setup_database()
    
    # Get stored data
    calendar_stored, notion_stored = get_stored_data(conn, start_date, end_date)
    
    # Only fetch new calendar data for dates not in storage
    print("Fetching calendar data...")
    service = get_local_calendar_service()
    
    # Check if we need to fetch any calendar data
    dates_to_fetch = [date for date in (start_date + datetime.timedelta(days=x) 
                     for x in range((end_date - start_date).days + 1)) 
                     if date not in calendar_stored]
    
    if dates_to_fetch:  # Only proceed if there are dates to fetch
        calendar_fetch_start = min(dates_to_fetch)
        if calendar_fetch_start <= end_date:
            start_time_cal = datetime.datetime.combine(calendar_fetch_start, datetime.time.min, 
                                                     tzinfo=central).astimezone(datetime.timezone.utc)
            end_time_cal = datetime.datetime.combine(end_date, datetime.time.max, 
                                                   tzinfo=central).astimezone(datetime.timezone.utc)
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time_cal.isoformat(),
                timeMax=end_time_cal.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500
            ).execute()
            
            new_calendar_totals = process_calendar_events(events_result.get('items', []))
            store_calendar_data(conn, new_calendar_totals)
            calendar_stored.update(new_calendar_totals)
    
    # Only fetch new Notion data for dates not in storage
    print("Fetching and processing Notion tasks...")
    start_time = time.time()
    
    # Check if we need to fetch any Notion data
    dates_to_fetch = [date for date in (start_date + datetime.timedelta(days=x) 
                     for x in range((end_date - start_date).days + 1)) 
                     if date not in notion_stored]
    
    if dates_to_fetch:  # Only proceed if there are dates to fetch
        notion_fetch_start = min(dates_to_fetch)
        if notion_fetch_start <= end_date:
            new_notion_totals = fetch_local_completed_tasks_by_date_range(notion_fetch_start, end_date)
            store_notion_data(conn, new_notion_totals)
            notion_stored.update(new_notion_totals)
    
    end_time = time.time()
    print(f"Notion processing took {end_time - start_time:.2f} seconds")
    
    # Prepare visualization using stored data
    dates = []
    cal_minutes_list = []
    notion_minutes_list = []
    total_minutes_list = []
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        cal_minutes = calendar_stored.get(current_date, 0)
        notion_minutes = notion_stored.get(current_date, 0)
        
        cal_minutes_list.append(cal_minutes)
        notion_minutes_list.append(notion_minutes)
        total_minutes_list.append(cal_minutes + notion_minutes)
        
        current_date += datetime.timedelta(days=1)
    
    # Create visualization
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=cal_minutes_list,
        name='Calendar Events',
        marker_color='#636EFA'
    ))
    
    fig.add_trace(go.Bar(
        x=dates,
        y=notion_minutes_list,
        name='Notion Tasks',
        marker_color='white'
    ))
    
    # Calculate 14-day moving average
    window_size = 14
    moving_avg = []
    for i in range(len(total_minutes_list)):
        if i < window_size - 1:
            window = total_minutes_list[:i+1]
        else:
            window = total_minutes_list[i-window_size+1:i+1]
        moving_avg.append(sum(window) / len(window))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=moving_avg,
        name='14-Day Moving Average',
        line=dict(color='gray', width=5),
        mode='lines'
    ))
    
    fig.update_layout(
        title='Daily Time Distribution',
        barmode='stack',
        template='plotly_dark',
        yaxis_title='Minutes',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(t=30, l=60, r=20, b=60)
    )
    
    fig.update_xaxes(tickangle=45)
    
    conn.close()
    return fig  # Return the figure instead of showing it

if __name__ == '__main__':
    fig = main()
    fig.show()  # Only show if run directly
