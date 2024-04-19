import sqlite3
import os
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table, Column
from datetime import datetime

console = Console()

def printBanner():
    banner = """
    ____                                    _____            
   / __ )_________ _      __________  _____/ ___/____  __  __
  / __  / ___/ __ \ | /| / / ___/ _ \/ ___/\__ \/ __ \/ / / /
 / /_/ / /  / /_/ / |/ |/ (__  )  __/ /   ___/ / /_/ / /_/ / 
/_____/_/   \____/|__/|__/____/\___/_/   /____/ .___/\__, /  
                                             /_/    /____/ 
"""
    print(banner)

def getNewestFile():
    directory_path = str(Path.home()) + "/Downloads"
    most_recent_file = None
    most_recent_time = 0

    # iterate over the files in the directory
    for entry in os.scandir(directory_path):
        if entry.name.endswith(".sqlite"):
            mod_time = entry.stat().st_mtime_ns
            if mod_time > most_recent_time:
                # update the most recent file and its modification time
                most_recent_file = entry.name
                most_recent_time = mod_time

    return os.path.join(directory_path, most_recent_file)


def dbConnection(database):
    con = sqlite3.connect(database)
    cur = con.cursor()
    return cur, con

def dbCleanup(con):
    con.close()


def queryBuilder(connection, table, rows):
    # The result of a "cursor.execute" can be iterated over by row
    
    #queryResults = connection.execute(f"SELECT id, current_path, DATETIME(ROUND(start_time / 1000000-11644473600), 'unixepoch', 'localtime') AS EventTime, referrer, site_url, tab_url, tab_referrer_url, mime_type, original_mime_type FROM {table} LIMIT {rows};")
    queryResults = connection.execute(f"SELECT * FROM (SELECT * FROM {table} ORDER BY ID DESC LIMIT {rows}) ORDER BY ID ASC;")
    columnNames = list(map(lambda x: x[0], connection.description))
    #print(columnNames)
    # for result in queryResults:
    #     print(result)
    #print(queryResults)

    return {
        "columnNames": columnNames,
        "tableName": table,
        "queryResults": queryResults
        }

def printOutput(queryResults: dict, minimal: bool):

    resultsTable = None
    columns = []

    if minimal:
        if queryResults["tableName"] == "downloads":
            resultsTable = Table(title="Downloads Table", show_lines=True)
            columns = ["File Path", "Date", "Referrer", "Site URL", "Tab URL", "Tab Referrer URL"]
        
        elif queryResults["tableName"] == "urls":
            resultsTable = Table(title="URLs Table", show_lines=True)
            columns = ["URL", "Title", "Visit Count", "Typed Count", "Last Visit Time"]

    else:
        if queryResults["tableName"] == "downloads":
            resultsTable = Table(title="Downloads Table", show_lines=True)
        elif queryResults["tableName"] == "urls":
            resultsTable = Table(title="URLs Table", show_lines=True)
        
        columns = queryResults["columnNames"]

        # if queryResults["tableName"] == "downloads":
        #     resultsTable = Table("ID", "File Path", "Date", "Referrer", "Site URL", "Tab URL", "Tab Referrer URL", "mime_type", "original_mime_type")
        # elif queryResults["tableName"] == "urls":
        #     resultsTable = Table("ID", "File Path", "Date", "Referrer", "Site URL", "Tab URL", "Tab Referrer URL", "mime_type", "original_mime_type")
    
    for column in columns:
            # create columns
            resultsTable.add_column(column)

    for result in queryResults["queryResults"]:
        dataNormalized = None
        
        if queryResults["tableName"] == "downloads":
            dataNormalized = {
                "ID": str(result[0]),
                "File_Path": str(result[2]),
                "Date": str(convertTime(result[4])),
                "Referrer": str(result[15]),
                "Site_URL": str(result[16]),
                "Tab_URL": str(result[18]),
                "Tab_Referrer_URL": str(result[19])
            }

        elif queryResults["tableName"] == "urls":
            dataNormalized = {
                "URL": str(result[1]),
                "Title": str(result[2]),
                "Visit_Count": str(result[3]),
                "Typed_Count": str(result[4]),
                "Last_Visit_Time": str(convertTime(result[5]))
            }
        
        if minimal:
            if queryResults["tableName"] == "downloads":
                resultsTable.add_row(dataNormalized["File_Path"], dataNormalized["Date"], dataNormalized["Referrer"], dataNormalized["Site_URL"], dataNormalized["Tab_URL"], dataNormalized["Tab_Referrer_URL"])
            elif queryResults["tableName"] == "urls":
                resultsTable.add_row(dataNormalized["URL"], dataNormalized["Title"], dataNormalized["Visit_Count"], dataNormalized["Typed_Count"], dataNormalized["Last_Visit_Time"])
        else:
            resultsTable.add_row(result)

    if resultsTable.rows:
        console.print(resultsTable)
    else:
        console.print("[i]No data for table...[/i]")

def convertTime(time):
    seconds = time / 1000000-11644473600
    converted = datetime.fromtimestamp(seconds)
    return converted.strftime('%Y-%m-%dT%H:%M:%S.%f')

    

def main(all: bool = False, minimal: bool = True, rows: int = 10):
    printBanner()
    databaseHistory = getNewestFile()
    
    cursor, con = dbConnection(databaseHistory)
    console.print(f"Reading file - {databaseHistory}", style="white on blue")
    
    queryResults = None

    tables = ["downloads", "urls"]

    if all:
        for table in tables:
            queryResults = queryBuilder(cursor, table, rows)
            printOutput(queryResults, minimal)
    else:
        queryResults = queryBuilder(cursor, tables[0], rows)
        printOutput(queryResults, minimal)

    
    dbCleanup(con)
    console.print("Database connection closed...", style="white on blue")

if __name__ == "__main__":
    typer.run(main)