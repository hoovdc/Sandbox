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
import datetime
import numpy as np

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
    fit_run_tab = mydash_sheet.worksheet("Fit_Run")

    #get data from tabs, store as a list of lists
    habits_tab_data_headers = habits_tab.get("A2:BK2") #columns headers only
    habits_tab_data = habits_tab.get("A3:BK") #data without headers
    habits_tab_data_full = habits_tab.get("A2:BK") # both headers and data
    #time_tab_data = time_tab.get("B2")
    finmkts_tab_data = finmkts_tab.get("A3:E")
    quote_data = quotes_tab.get("B5:B6")
    fit_run_data = fit_run_tab.get("B2:H")
   
    #if the 2nd cell (quote author) in quote data is empty, assign a blank string to resolve errors
    if quote_data[0] == []:
        quote_data[0] = [" "]

    text_quotes = "\n" + quote_data[1][0] + "\n" + quote_data[0][0]

    return habits_tab_data_headers,habits_tab_data, habits_tab_data_full, text_quotes, finmkts_tab_data, fit_run_data

    #print("\n",finmkts_tab_data, "\n",)

#PROCESS HABITS DATA INTO DASH-FRIENDLY DATA FORMAT
def process_habits(habits_tab_data_headers, habits_tab_data, habits_tab_data_full):
    
    #create a class to contain all the dataframes
    class dfs_habits:
        def __init__(self):
            self.heatmap = None
            self.bars = None
            self.line_LxD = None
            self.perhabit_lines_LxD = None
            self.wkday_summary = None
            self.perhabit_summary = None

    # Create an instance of the class
    dfs_habits = dfs_habits()

    def convert_percentage(percentage_str):  # Function to convert percentage strings to floats
        return float(percentage_str.strip('%')) / 100.0

    #detailed metrics
    # Select the required columns 
    habit_data_heat_noheaders = []
    habit_data_bars_noheaders = []
    habits_tab_line_noheaders = []
    for row in habits_tab_data:
        try:
            #read next row for each individual variable 
            day_in_month = int(row[6])
            month_in_year = int(row[5])
            day_in_year = int(row[3])
            win_rate = convert_percentage(row[10])
            win_rate_YTD = convert_percentage(row[14])
            loss_rate = float(1.00 - win_rate)
            #update the full data set with the latest row's values for each variable
            habit_data_heat_noheaders.append([day_in_month, month_in_year, win_rate])
            habit_data_bars_noheaders.append([day_in_year, win_rate, loss_rate])
            habits_tab_line_noheaders.append([day_in_year, win_rate, win_rate_YTD])
        except (ValueError, IndexError) as e:
            print(f"Last Day-in-Year Read:  {day_in_year}    Current Time: {datetime.datetime.now()}")
            #print(f"Skipping habits row.  {e}")
            break

    #summary metrics
    habit_data_wkday_summary_noheaders = []
    habit_data_perhabit_summary_noheaders = []
    
    #wkday summary
    wkday_counter = 0
    for row in habits_tab_data:
        name_of_wkday = row[38]
        day_in_wk_total_winrate = convert_percentage(row[40])
        #print(f"Day of Week: {name_of_wkday}  Win Rate: {day_in_wk_total_winrate}")
        habit_data_wkday_summary_noheaders.append([name_of_wkday, day_in_wk_total_winrate])
        wkday_counter += 1
        if wkday_counter == 7:
            break
   
    #per-habit summary
    for row in habits_tab_data:
        try:
            name_of_habit = row[42]
            habit_total_winrate = convert_percentage(row[43])
            habit_data_perhabit_summary_noheaders.append([name_of_habit, habit_total_winrate])
            #print(f"Habit: {name_of_habit}  Win Rate: {habit_total_winrate}")
        except (ValueError, IndexError):
            break
    #sort the per-habit summary by win rate, descending
    habit_data_perhabit_summary_noheaders.sort(key=lambda x: x[1], reverse=True)

    #select data for Per-habit LxD line graph
    #select all rows from columns 28 to 35 from the habits tab
    listdata_perhabit_lines_LxD = [row[28:35] for row in habits_tab_data_full]
    #print first 3 rows of the perhabit line data with a paragraph return at the end of each row
    # for row in listdata_perhabit_lines_LxD[0:2]:
    #     print(row)
    
    listdata_perhabit_lines_LxD_datanoheaders = listdata_perhabit_lines_LxD[1:]
    listdata_perhabit_lines_LxD_headers = listdata_perhabit_lines_LxD[0]

    #print("code row 118 | columns headers: " ,  listdata_perhabit_lines_LxD_headers)
    #print("code row 119 | columns data: " ,  listdata_perhabit_lines_LxD_datanoheaders[0])

     #convert the list data to numerical values with up to 2 decimal places
    listdata_perhabit_lines_LxD_datanoheaders = [
        [float(x.strip('%')) / 100 if x.strip() else np.nan for x in row]
        for row in listdata_perhabit_lines_LxD_datanoheaders
    ]
    
   # print("code row 127 | columns headers: " , listdata_perhabit_lines_LxD[0])
   # print("code row 128 | first 2 data rows: " , listdata_perhabit_lines_LxD[1:2])

    # Convert the lists to DataFrames
    df_habit_data_heat = pd.DataFrame(habit_data_heat_noheaders, 
                                      columns=["  Day in Mo", "  Mo in Yr", "  Win %"])
    df_habit_data_bars = pd.DataFrame(habit_data_bars_noheaders, columns=["Day in Year", "Win %", "Loss %"])
    df_habit_data_line = pd.DataFrame(habits_tab_line_noheaders, columns=["Day in Year", "Win %", "Win % YTD"])
    df_habit_data_wkday_summary = pd.DataFrame(habit_data_wkday_summary_noheaders, 
                                               columns=["Day of Week", "Win Rate"])
    df_habit_data_perhabit_summary = pd.DataFrame(habit_data_perhabit_summary_noheaders,
                                                  columns=["Habit", "Win Rate"])
    df_perhabit_lines_LxD = pd.DataFrame(listdata_perhabit_lines_LxD_datanoheaders, columns=listdata_perhabit_lines_LxD_headers)
    #print("[df] perhabit line columns: ", df_perhabit_lines_LxD.columns)
    #print the first 2 rows of the perhabit line data dataframe
    #print("perhabit line data: ", df_perhabit_lines_LxD.head(2))

    # Pivot the heatmap data to create a 2D array and fill NULL values with 0
    z_data_heat = df_habit_data_heat.pivot(index="  Mo in Yr", columns="  Day in Mo", values="  Win %").fillna(0)
   
    #Take only the last 45 rows of the line dataframe
    df_habit_data_line_LxD = df_habit_data_line.tail(45)

    # Ensure the DataFrame matches the dimensions for the heatmap
    df_heatmap = pd.DataFrame(z_data_heat, index=df_habit_data_heat["  Mo in Yr"].unique(), columns=df_habit_data_heat["  Day in Mo"].unique()).fillna(0)

    #assign the dataframes to the class instance
    dfs_habits.heatmap = df_heatmap
    dfs_habits.bars = df_habit_data_bars
    dfs_habits.line_LxD = df_habit_data_line_LxD
    dfs_habits.perhabit_lines_LxD = df_perhabit_lines_LxD
    dfs_habits.wkday_summary = df_habit_data_wkday_summary
    dfs_habits.perhabit_summary = df_habit_data_perhabit_summary

    return dfs_habits

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
            print(f"Skipping finmkts row due to error: {e}")

    #remove headers from the data
    finmkts_data_noheaders = finmkts_data_noheaders[1:]

    #converting data types to datetime and float
    for row in finmkts_data_noheaders:
        row[0] = pd.to_datetime(row[0])
        row[1] = float(row[1])

    # Convert the list to a DataFrame
    df_finmkts_data = pd.DataFrame(finmkts_data_noheaders, columns=["Date", "Price"])

    return df_finmkts_data

def process_fitness(fit_run_data):
    # Convert the data to a DataFrame, using the first row as the header
    df_fit_run = pd.DataFrame(fit_run_data[1:], columns=fit_run_data[0])

    # Convert Pace (min/mi) to numeric
    df_fit_run['Pace (min/mi)'] = pd.to_numeric(df_fit_run['Pace (min/mi)'], errors='coerce')

    # Ensure Date is in datetime format
    df_fit_run['Date'] = pd.to_datetime(df_fit_run['Date'], format='%Y-%m-%d', errors='coerce')

    # Drop rows with NaN values in critical columns
    df_fit_run.dropna(subset=['Date', 'Pace (min/mi)', 'Distance (mi)'], inplace=True)

    # Sort DataFrame by Date
    df_fit_run.sort_values('Date', inplace=True)

    return df_fit_run