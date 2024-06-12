#API webpage link (general info page): https://open-meteo.com/
#Tutorial provided by API provider (with preset inputs entered by me): 
#https://open-meteo.com/en/docs#current=temperature_2m,precipitation&hourly=temperature_2m,precipitation_probability&daily=sunrise,sunset&location_mode=csv_coordinates&csv_coordinates=30.2666,+-97.7333+,+,+America%2FChicago&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&forecast_days=3
#Code from tutorial customized for my purposes, including interspersed with code to write to gsheet using gspread
#docs referenced for gsheet connection: https://docs.gspread.org/en/v6.0.0/oauth2.html#for-bots-using-service-account
'''	Note that the "updating cells" portion seems to be wrong in official docs on gspread.org as of 2024 06. 
	Syntax has changed in recent gspread versions
	In particular, the sequence of arguments passed to the update() function
	Use these docs instead:
	https://pypi.org/project/gspread/
'''

import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import gspread

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 30.2666,
	"longitude": -97.7333,
	"current": ["temperature_2m", "precipitation"],
	"hourly": ["temperature_2m", "precipitation_probability"],
	"daily": ["sunrise", "sunset"],
	"temperature_unit": "fahrenheit",
	"wind_speed_unit": "mph",
	"precipitation_unit": "inch",
	"timezone": "America/Chicago",
	"forecast_days": 3
}

responses = openmeteo.weather_api(url,params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print('\n')
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()}m above sea level")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} seconds") #seconds since 1970 01 01 (UNIX Epoch Time)

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_precipitation = current.Variables(1).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"current precipitation_2m {current_precipitation}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_precipitationprobability = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(hourly.Time(), unit = "s" , utc = True), 
    end = pd.to_datetime(hourly.TimeEnd(), unit = "s" , utc = True),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation_probability"] = hourly_precipitationprobability

hourly_dataframe = pd.DataFrame(data = hourly_data)
#print (hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_sunrise = daily.Variables(0).ValuesAsNumpy()
daily_sunset = daily.Variables(1).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)

#open gsheet connection and select desired tab
gcred = gspread.service_account(filename='my-dashboard-426016-058763d93d8e.json')
gsheetfile = gcred.open("My Dashboard Data")
gs_weathertab= gsheetfile.worksheet("Weather")

#Write data to gsheet tab.  

#The weather API time format needs a data type conversion for gspread to read it.
#Using a string format that at least resembles a date-time data type on the surface
hourly_dataframe_export = hourly_dataframe
hourly_dataframe_export['date'] = hourly_dataframe_export['date'].apply(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)
#Gspread needs Dataframe converted to list structure
#without header structure: hourly_export = hourly_dataframe.values.tolist()
#or for header structure: 
hourly_export = [hourly_dataframe_export.columns.values.tolist()] + hourly_dataframe_export.values.tolist()
gs_weathertab.update(hourly_export, "A2") 

'''
# Update multiple ranges at once
worksheet.batch_update([{
    'range': 'A1:B2',
    'values': [['A1', 'B1'], ['A2', 'B2']],
}, {
    'range': 'J42:K43',
    'values': [[1, 2], [3, 4]],
}])
'''


#Write data to gsheet tab
#weather_tab.update_cell(7, 4 , '3x')

#weather_tab.update([["Overriding2_D12"]], "D12")

#print(gs_weathertab.get('A1:F30'))