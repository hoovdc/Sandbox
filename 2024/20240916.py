#file: time_ingest.py
#code initially generated in chatgpt 4o

import pandas as pd

def get_time_data():
    # Load the CSV file
    file_path = 'Data/Time Data/Gcal Time Data/gcal_export_20240916_1201.csv'
    data = pd.read_csv(file_path)

    # Convert 'Date' to datetime and 'Event Duration' to handle times
    data['Date'] = pd.to_datetime(data['Date'])

    # Function to convert duration string to hours
    def duration_to_hours(duration):
        if duration == 'All day':  # Ignore all-day events
            return None
        try:
            # Split the duration and convert to total hours
            h, m, s = map(int, duration.split(':'))
            return h + m/60 + s/3600
        except:
            return 0

    # Apply the conversion to the 'Event Duration' column
    data['Event Hours'] = data['Event Duration'].apply(duration_to_hours)

    # Drop rows where 'Event Hours' is None (ignoring 'All day' events)
    data = data.dropna(subset=['Event Hours'])

    # Extract the month and the day from the 'Date' column
    data['Month'] = data['Date'].dt.month
    data['Day'] = data['Date'].dt.date

    # Group by both month and day to compute daily total hours
    daily_hours = data.groupby(['Month', 'Day'])['Event Hours'].sum().reset_index()

    # Group by month to calculate the average and median daily hours blocked
    monthly_stats = daily_hours.groupby('Month')['Event Hours'].agg(
        Average_Daily_Hours_Blocked='mean',
        Median_Daily_Hours_Blocked='median'
    ).reset_index()

    #print(monthly_stats)
    return monthly_stats
