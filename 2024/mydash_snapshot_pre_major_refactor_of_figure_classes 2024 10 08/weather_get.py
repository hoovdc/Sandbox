#API webpage link (general info page): https://open-meteo.com/

import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import gspread
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio #for style themes
import dash #for plot layouts
import numpy as np


def weather_get():

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
    # print('\n')
    # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation {response.Elevation()}m above sea level")
    # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} seconds") #seconds since 1970 01 01 (UNIX Epoch Time)

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()

    # print(f"Current time {current.Time()}")
    # print(f"Current temperature_2m {current_temperature_2m}")
    # print(f"current precipitation_2m {current_precipitation}")

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

    # print("DAILY SUNRISE")
    # print(response.Daily())
    # print("-")
    # print(daily_sunrise)

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset

    daily_dataframe = pd.DataFrame(data = daily_data)
    #print(daily_dataframe)

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

    #generate chart in Plotly
    #set default style template for plots
    pio.templates.default = "plotly_dark"



    # Create your figure.  Using Plotly Express because Plotly Graph Objects doesn't support continuous color scales for bar charts
    fig_temp_hr_bar = px.bar(hourly_dataframe,x='date',y='temperature_2m',
                            #rename vertical axis title to 'temp_2m_F'
                            labels={'temperature_2m':'temp_2m_F'},
                            color='temperature_2m',
                            #color_continuous_scale='Purples'
                            #set a continuous custom color scale where low values are white and high values 
                            #are the default plotly dark mode purple
                            color_continuous_scale= [
                                [0, 'rgba(255, 255, 255, 0.7)'],  # Semi-Transparent white
                                [0.25, 'rgba(255, 255, 255, 1)'],  # Solid white
                                [0.5, 'rgba(159, 157, 250, 0.5)'],  # Mid-purple
                                [0.75, 'rgba(99, 110, 250, 0.75)'],  # Darker purple
                                [1, 'rgba(99, 110, 250, 1)']  # Solid Plotly dark mode purple
                             ]
                           )

    fig_temp_hr_bar.update_layout(title="Hourly Temperature",
                                yaxis_title="Temperature (°F)",
                                yaxis2=dict(
                                    overlaying='y',
                                    side='right',
                                    showgrid=False,
                                    mirror=True
                                ))

    fig_temp_hr_bar.update_yaxes(dtick=10)  # Add grid lines every 10 units

    # fig_hr = go.line(hourly_dataframe, x = 'date', y = 'temperature_2m') #causes error
    # fig_hr = go.line(hourly_export, x = 0, y = 1, title = "dark mode bayyybayyyyyy")
    # fig_hr2 = go.Bar(hourly_export, x = 0, y = 1, title = "dark mode bayyybayyyyyy")
    # fig_day = go.Scatter(daily_dataframe, x = 'date', y = 'sunrise')

    #fig_temp_hr_bar.show()

    return fig_temp_hr_bar