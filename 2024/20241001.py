#from https://github.com/FelixKohlhas/ScreenTime2CSV/tree/main
#modifying to address gaps in data
import os
import sqlite3
import csv
import datetime
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
#import argparse
#from io import StringIO

knowledge_db = os.path.expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")

def query_database():
    # Check if knowledgeC.db exists
    if not os.path.exists(knowledge_db):
        print("Could not find knowledgeC.db at %s." % (knowledge_db))
        exit(1)

    # Check if knowledgeC.db is readable
    if not os.access(knowledge_db, os.R_OK):
        print("The knowledgeC.db at %s is not readable.\nPlease grant full disk access to the application running the script (e.g. Terminal, iTerm, VSCode etc.)." % (knowledge_db))
        exit(1)

    # Connect to the SQLite database
    with sqlite3.connect(knowledge_db) as con:
        cur = con.cursor()
        
        # Execute the SQL query to fetch data
        # Modified from https://rud.is/b/2019/10/28/spelunking-macos-screentime-app-usage-with-r/
        # Modified further, beginning 2024 09 04, to address gaps in data, as proposed by ChatGPT
        query = """
        SELECT
            ZOBJECT.ZVALUESTRING AS "app", 
            (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "usage",
            (ZOBJECT.ZSTARTDATE + 978307200) as "start_time", 
            (ZOBJECT.ZENDDATE + 978307200) as "end_time",
            (ZOBJECT.ZCREATIONDATE + 978307200) as "created_at", 
            ZOBJECT.ZSECONDSFROMGMT AS "tz",
            ZSOURCE.ZDEVICEID AS "device_id",
            ZMODEL AS "device_model"
        FROM
            ZOBJECT 
            LEFT JOIN ZSTRUCTUREDMETADATA 
            ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
            LEFT JOIN ZSOURCE 
            ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
            LEFT JOIN ZSYNCPEER
            ON ZSOURCE.ZDEVICEID = ZSYNCPEER.ZDEVICEID
        WHERE
            ZSTREAMNAME LIKE "%usage%" -- Broaden this condition to capture any usage-related streams
        ORDER BY
            ZSTARTDATE DESC;
        """
        cur.execute(query)
        
        # Fetch ascreentime_data from the result set
        return cur.fetchall()

def write_to_csv(screentime_data, data_timestamp):
    csv_file_name = "screentime_%s.csv" % (data_timestamp)
    csv_delimiter = ','
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=csv_delimiter, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["app", "usage", "start_time", "end_time", "created_at", "tz", "device_id", "device_model"])
        writer.writerows(screentime_data)

#Access and authenticate Google Sheet
# def auth_gsheet():
#     #use credentials to create a client to interact with the Google Drive API
#     scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name('my-dashboard-426016-058763d93d8e.json', scope)
#     client = gspread.authorize(creds)

#     #open sheet(s)
#     active_sheet = client.open('My Dashboard Data')
#     archive_sheet = client.open('Screentime Data from Apple Devices')

#     #TO DO update these tab names as applicable for current naming.  read/write data from them    
#     #select tabs in sheet
#     active_tab = active_sheet.worksheet("Habits")
#     achive_tab = archive_sheet.worksheet("screentime")


#Write data to Google Sheet
# def write_to_gsheet(screentime_data, data_timestamp):
#     #TO DO:  write data to Google Sheet
#     x = 1 #placeholder

def main():
    # parser = argparse.ArgumentParser(description="Query knowledge database")
    # parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    # parser.add_argument("-d", "--delimiter", default=',', help="Delimiter for output file (default: comma)")
    # args = parser.parse_args()

    # Query the database and fetch tscreentime_data
    screentime_data = query_database()

    #print the first 10 lines of the output
    #print(screentime_data[:10])

    # Prepare output format
    # delimiter = args.delimiter.replace("\\t", "\t")

    data_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Write the output to a local csv file
    write_to_csv(screentime_data, data_timestamp)

    #write_to_gsheet(screentime_data, data_timestamp)
#     #TO DO:  write data to Google Sheet

if __name__ == "__main__":
    main()