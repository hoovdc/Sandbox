#google sheet connection based on this tutorial: https://skills.ai/blog/ultimate-api-tutorial-for-google-sheets-users/
#some code based on official gspread library docs: https://docs.gspread.org/en/latest/user-guide.html
'''	Note that the "updating cells" portion seems to be wrong in official docs on gspread.org as of 2024 06. 
	Syntax has changed in recent gspread versions
	In particular, the sequence of arguments passed to the update() function
	Use these docs instead:
	https://pypi.org/project/gspread/
'''

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
#import datetime
#import numpy as np

def get_gsheet_data():
    #use credentials to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('my-dashboard-426016-058763d93d8e.json', scope)
    client = gspread.authorize(creds)

    #open a sheet
    mydash_sheet = client.open('My Dashboard Data')

    #select tabs in sheet
    habits_tab = mydash_sheet.worksheet("Habits")
    #time_tab = mydash_sheet.worksheet("Time")
    finmkts_tab = mydash_sheet.worksheet("Financial_Markets")
    quotes_tab = mydash_sheet.worksheet("Quotes")

    #get data from tabs, store as a list of lists
    habits_tab_data_headers = habits_tab.get("A2:AK2") #columns headers only
    habits_tab_data = habits_tab.get("A3:AK") #data without headers
    #habits_tab_data_full = habits_tab.get("A2:AK") # both headers and data
    #time_tab_data = time_tab.get("B2")
    finmkts_tab_data = finmkts_tab.get("A3:E")
    quote_data = quotes_tab.get("B5:B6")
    #print("\n" , quote_data , "\n")
   
    #if the 2nd cell (quote author) in quote data is empty, assign a blank string to resolve errors
    if quote_data[0] == []:
        quote_data[0] = [" "]

    text_quotes = "\n\n\n\n\n" + quote_data[1][0] + "\n" + quote_data[0][0]

    return habits_tab_data_headers,habits_tab_data, text_quotes, finmkts_tab_data

    #print("\n",finmkts_tab_data, "\n",)

#PROCESS HABITS DATA INTO DASH-FRIENDLY FORMAT

def process_habits(habits_tab_data_headers, habits_tab_data):
    # Function to convert percentage strings to floats
    def convert_percentage(percentage_str):
        return float(percentage_str.strip('%')) / 100.0

    # Select the required columns 
    habit_data_heat_noheaders = []
    habit_data_bars_noheaders = []
    habits_tab_line_noheaders = []
    for row in habits_tab_data:
        try:
            day_in_month = int(row[6])
            month_in_year = int(row[5])
            day_in_year = int(row[3])
            win_rate = convert_percentage(row[10])
            win_rate_YTD = convert_percentage(row[14])
            loss_rate = float(1.00 - win_rate)
            habit_data_heat_noheaders.append([day_in_month, month_in_year, win_rate])
            habit_data_bars_noheaders.append([day_in_year, win_rate, loss_rate])
            habits_tab_line_noheaders.append([day_in_year, win_rate, win_rate_YTD])
        except (ValueError, IndexError) as e:
            print(f"Skipping row due to error: {e}")

    # Convert the list to a DataFrame
    df_habit_data_heat = pd.DataFrame(habit_data_heat_noheaders, 
                                      columns=["  Day in Mo", "  Mo in Yr", "  Win %"])
    df_habit_data_bars = pd.DataFrame(habit_data_bars_noheaders, columns=["Day in Year", "Win %", "Loss %"])
    df_habit_data_line = pd.DataFrame(habits_tab_line_noheaders, columns=["Day in Year", "Win %", "Win % YTD"])

    # Pivot the heatmap data to create a 2D array and fill NULL values with 0
    z_data_heat = df_habit_data_heat.pivot(index="  Mo in Yr", columns="  Day in Mo", values="  Win %").fillna(0)
   
    #Take only the last 45 rows of the line dataframe
    df_habit_data_line_LxD = df_habit_data_line.tail(45)

    # Ensure the DataFrame matches the dimensions for the heatmap
  
    df_heatmap = pd.DataFrame(z_data_heat, index=df_habit_data_heat["  Mo in Yr"].unique(), columns=df_habit_data_heat["  Day in Mo"].unique()).fillna(0)
    #print ("df_heatmap \n", df_heatmap[:10])
    return df_heatmap, df_habit_data_bars, df_habit_data_line_LxD

#print(sheet.worksheets(),  end = "\n\n" ) #print list of all tabs in sheet

#Write data to gsheet tab
#weather_tab.update_cell(7, 4 , '3x')

#weather_tab.update([["Overriding2_D12"]], "D12")

#PROCESS FINANCIAL MARKETS DATA INTO DASH-FRIENDLY FORMAT

#read dates from the 2nd column and stock price from the 3rd column of the financial markets tab
def process_finmkts(finmkts_tab_data):
    # Select the required columns 
    finmkts_data_noheaders = []
    for row in finmkts_tab_data:
        try:
            date = row[1]
            price = row[2] #reading from column 3 (NASDAQ in this case)
            finmkts_data_noheaders.append([date, price])
        except (ValueError, IndexError) as e:
            print(f"Skipping row due to error: {e}")

    #remove headers from the data
    finmkts_data_noheaders = finmkts_data_noheaders[1:]

    #converting data types to datetime and float
    for row in finmkts_data_noheaders:
        row[0] = pd.to_datetime(row[0])
        row[1] = float(row[1])

    # Convert the list to a DataFrame
    df_finmkts_data = pd.DataFrame(finmkts_data_noheaders, columns=["Date", "Price"])

    return df_finmkts_data