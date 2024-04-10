import sqlite3
import os
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

console = Console()

def getNewestFile():
    directory_path = str(Path.home()) + "\\Downloads"
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
    downloads = connection.execute("SELECT id, current_path, DATETIME(ROUND(start_time / 1000000-11644473600), 'unixepoch', 'localtime') AS EventTime, referrer, site_url, tab_url, tab_referrer_url, mime_type, original_mime_type, total_bytes FROM downloads;")
    #columnNames = list(map(lambda x: x[0], cursor.description))
    #print(columnNames)

    for download in downloads:
        print(download)


def main():
    databaseHistory = getNewestFile()
    
    cursor, con = dbConnection(databaseHistory)
    
    queryDownloads(cursor)
    dbCleanup(con)
    print(f"Read file: {databaseHistory}")
    print("Database connection closed...")

if __name__ == "__main__":
    typer.run(main())