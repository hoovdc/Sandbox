#google sheet connection based on this tutorial: https://skills.ai/blog/ultimate-api-tutorial-for-google-sheets-users/
#some code based on official gspread library docs: https://docs.gspread.org/en/latest/user-guide.html
'''	Note that the "updating cells" portion seems to be wrong in official docs on gspread.org as of 2024 06. 
	Syntax has changed in recent gspread versions
	In particular, the sequence of arguments passed to the update() function
	Use these docs instead:
	https://pypi.org/project/gspread/
'''

#code edited to present in screenshot for Upwork portfolio

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np

def get_gsheet():
    #use credentials to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('my-dashboard-426016-058763d93d8e.json', scope)
    client = gspread.authorize(creds)

    #open a sheet
    mydash_sheet = client.open('My Dashboard Data')

    #select tabs in sheet
    sales_tab = mydash_sheet.worksheet("Sales")
    time_tab = mydash_sheet.worksheet("Time")
    finmkts_tab = mydash_sheet.worksheet("Financial_Markets")

    #get data from tabs, store as a list of lists
    sales_tab_data = sales_tab.get("A3:AK")
    time_tab_data = time_tab.get("B2")
    finmkts_tab_data = finmkts_tab.get("A3:E")

    return(sales_tab_data)

#PROCESS SALES DATA INTO DASH-FRIENDLY FORMAT

def process_sales_data(sales_tab_data):
  
    # convert percentage strings to floats
    def convert_percentage(percentage_str):
        return float(percentage_str.strip('%')) / 100.0

    # Select the required columns for the heatmap data
    sales_data_heat_noheaders = []
    for row in sales_tab_data:
        try:
            day = int(row[6])
            month = int(row[5])
            win_rate = convert_percentage(row[10])
            sales_data_heat_noheaders.append([day, month, win_rate])
        except (ValueError, IndexError) as e:
            print(f"Skipping row due to error: {e}")

    # Convert the list to a DataFrame
    df_sales_data_heat = pd.DataFrame(sales_data_heat_noheaders, columns=["Day in Mo", "Mo in Year", "Win %"])

    # Pivot the data to create a 2D array
    z_data = df_sales_data_heat.pivot(index="Day in Mo", columns="Mo in Year", values="Win %").fillna(0) # Fill NaN values with 0

    # Ensure the DataFrame matches the dimensions for the heatmap
    df_heatmap = pd.DataFrame(z_data, index=day, columns=month).fillna(0) # Fill NaN values with 0


#print(sheet.worksheets(),  end = "\n\n" ) #print list of all tabs in sheet

#Write data to gsheet tab
#weather_tab.update_cell(7, 4 , '3x')

#weather_tab.update([["Overriding2_D12"]], "D12")

'''
WAYS TO WRITE TO GSHEET THAT DON'T WORK [DEPRECATED]
This syntax no longer works with current gspread version as of 2024 06
Updating Cells
Using A1 notation:
    worksheet.update('B1', 'Bingo!')
Or row and column coordinates:
    worksheet.update_cell(1, 2, 'Bingo!')
Update a range
    worksheet.update('A1:B2', [[1, 2], [3, 4]])
weather_tab.update([
    ['C9', 'C9x'],
    ['E2', 'E2x'],
    ['A14', 'A14x'],
    ['B3', 'B3x']
])
weather_tab.update([ ['D10', 'Overriding1'] ])

#Have gotten this warning:
#DeprecationWarning: The order of arguments in worksheet.update() has changed. Please pass values first and range_name secondor used named arguments (range_name=, values=)
#  weather_tab.update('D10', [['Overriding1_D10']])
# my original code causing this warning: weather_tab.update( [['Overriding1_D10']],'D10')
'''