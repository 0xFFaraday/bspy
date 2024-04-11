import sqlite3
import os
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table, Column

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


def queryDownloads(connection):
    # The result of a "cursor.execute" can be iterated over by row
    downloads = connection.execute("SELECT id, current_path, DATETIME(ROUND(start_time / 1000000-11644473600), 'unixepoch', 'localtime') AS EventTime, referrer, site_url, tab_url, tab_referrer_url, mime_type, original_mime_type FROM downloads;")
    #columnNames = list(map(lambda x: x[0], connection.description))
    #print(columnNames)

    return downloads

def printOutput(downloads: tuple, minimal: bool):

    downloadsTable = None
    if minimal:
        downloadsTable = Table("File Path", "Date", "Referrer", "Site URL", "Tab URL", "Tab Referrer URL", show_lines=True)
    else:
        downloadsTable = Table("ID", "File Path", "Date", "Referrer", "Site URL", "Tab URL", "Tab Referrer URL", "mime_type", "original_mime_type", show_lines=True)
    
    for download in downloads:
        dataNormalized = {
            "ID": str(download[0]),
            "File_Path": str(download[1]),
            "Date": str(download[2]),
            "Referrer": str(download[3]),
            "Site_URL": str(download[4]),
            "Tab_URL": str(download[5]),
            "Tab_Referrer_URL": str(download[6]),
            "Mime_Type": str(download[7]),
            "Original_Mime_Type": str(download[8])
    }
        
        if minimal:
            downloadsTable.add_row(dataNormalized["File_Path"], dataNormalized["Date"], dataNormalized["Referrer"], dataNormalized["Site_URL"], dataNormalized["Tab_URL"], dataNormalized["Tab_Referrer_URL"])
        else:
            downloadsTable.add_row(dataNormalized["ID"], dataNormalized["File_Path"], dataNormalized["Date"], dataNormalized["Referrer"], dataNormalized["Site_URL"], dataNormalized["Tab_URL"], dataNormalized["Tab_Referrer_URL"], dataNormalized["Mime_Type"], dataNormalized["Original_Mime_Type"])

    if downloadsTable.columns:
        console.print(downloadsTable)
    else:
        console.print("[i]No data...[/i]")

def main():
    printBanner()
    databaseHistory = getNewestFile()
    
    cursor, con = dbConnection(databaseHistory)
    console.print(f"Reading file - {databaseHistory}", style="white on blue")
    
    downloads = queryDownloads(cursor)
    printOutput(downloads, True)
    
    dbCleanup(con)
    console.print("Database connection closed...", style="white on blue")

if __name__ == "__main__":
    typer.run(main)