#file: time_ingest.py
#code initially generated in chatgpt 4o.  Rewritten with Claude 3.5 Sonnet using Cursor IDE

import pandas as pd
from datetime import timedelta

def get_time_data():
    # Load the CSV file
    file_path = 'Data/Time Data/Gcal Time Data/gcal_export_20240916_1201.csv'
    data = pd.read_csv(file_path)

    # Convert 'Date' to datetime and 'Start Time' to timedelta
    data['Date'] = pd.to_datetime(data['Date'])
    data['Start Time'] = pd.to_timedelta(data['Start Time'] + ':00')

    # Function to convert duration string to timedelta and calculate end time
    def duration_to_timedelta_and_end_time(duration, start_date, start_time):
        if duration == 'All day':  # Ignore all-day events
            return None, None
        try:
            h, m, s = map(int, duration.split(':'))
            duration_td = timedelta(hours=h, minutes=m, seconds=s)
            end_time = start_time + duration_td
            end_date = start_date
            if end_time >= timedelta(hours=24):
                end_date += timedelta(days=1)
                end_time -= timedelta(hours=24)
            return duration_td, (end_date, end_time)
        except:
            return timedelta(0), (start_date, start_time)
    
    # Apply the conversion to 'Event Duration' and 'Start Time'
    data[['Duration', 'End']] = data.apply(
        lambda row: duration_to_timedelta_and_end_time(row['Event Duration'], row['Date'], row['Start Time']),
        axis=1, result_type="expand"
    )

    # Drop rows where 'Duration' is None (ignoring 'All day' events)
    data = data.dropna(subset=['Duration'])

    # print("print the first 4 rows of the dataframe")
    # print(data[:4])

    # Helper function to calculate non-overlapping hours for a single day
    def calculate_daily_hours(events):
        events = events.sort_values('Start Time')
        total_hours = 0
        current_end = timedelta(0)

        for _, event in events.iterrows():
            start = event['Start Time']
            end = event['End'][1] if event['Date'] == event['End'][0] else timedelta(hours=24)
            
            if start > current_end:
                total_hours += (end - start).total_seconds() / 3600
                current_end = end
            elif end > current_end:
                total_hours += (end - current_end).total_seconds() / 3600
                current_end = end

        return total_hours  # Cap at 24 hours

    # Calculate daily hours
    daily_hours = data.groupby('Date').apply(calculate_daily_hours).reset_index(name='Total Event Hours')

    # Extract the month and day from the 'Date' column
    daily_hours['Month'] = daily_hours['Date'].dt.month
    daily_hours['Day'] = daily_hours['Date'].dt.date

    # Group by month to calculate the average, max, and median daily hours blocked
    monthly_stats = daily_hours.groupby('Month')['Total Event Hours'].agg(
        Average_Daily_Hours_Blocked='mean',
        Max_Daily_Hours_Blocked='max',
        Median_Daily_Hours_Blocked='median'
    ).reset_index()

    # Print the total hours for September 15, 2024
    #sept_14_hours = daily_hours[daily_hours['Date'] == pd.to_datetime('2024-09-14')]['Total Event Hours'].sum()
    #print(f"Total daily hours on Sept 14, 2024 with overlapping events de-duplicated: {sept_14_hours}")

    #print the max daily hours blocked for each month
    #print(monthly_stats[['Month', 'Max_Daily_Hours_Blocked']])

    return monthly_stats
