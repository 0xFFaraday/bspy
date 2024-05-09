import sqlite3
import os
import typer
import csv
from pathlib import Path
from typing_extensions import Annotated
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
                                            Created By: 0xFFaraday
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


def queryBuilder(connection, table, rows: int, verbose: bool):
    if not verbose:
        if table == "urls":
            queryResults = connection.execute(f"SELECT * FROM (SELECT * FROM {table} ORDER BY ID DESC LIMIT {rows}) ORDER BY ID ASC;")
        elif table == "downloads":
            queryResults = connection.execute(f"SELECT id, current_path, start_time, referrer, site_url, tab_url, tab_referrer_url FROM(SELECT id, current_path, start_time, referrer, site_url, tab_url, tab_referrer_url FROM {table} ORDER BY ID DESC LIMIT {rows}) ORDER BY ID ASC;")
    else:
        queryResults = connection.execute(f"SELECT * FROM (SELECT * FROM {table} ORDER BY ID DESC LIMIT {rows}) ORDER BY ID ASC;")
        
    # iterate through table's column names
    columnNames = list(map(lambda x: x[0], connection.description))
    
    return {
        "columnNames": columnNames,
        "tableName": table,
        "queryResults": queryResults
        }

def printOutput(queryResults: dict, output: bool):

    resultsTable = None
    columns = queryResults["columnNames"]
    timeColumns = []

    # parse all columns that have time within it
    for col in columns:
        if "time" in col:
            timeColumns.append(columns.index(col))

    if queryResults["tableName"] == "downloads":
        resultsTable = Table(title="Downloads Table", show_lines=True)
    
    elif queryResults["tableName"] == "urls":
        resultsTable = Table(title="URLs Table", show_lines=True)
        
    for column in queryResults["columnNames"]:
            # create columns
            resultsTable.add_column(column)

    normalizedResults = []

    for result in queryResults["queryResults"]:

        # convert time to human format, temp way to do it
        tmpList = list(result)
        for timeCol in timeColumns:
            tmpList[timeCol] = str(convertTime(result[timeCol]))

        result = tuple(tmpList)
        normalizedResults.append(result)
        
        #tuple unpack - creates column data
        resultsTable.add_row(*[str(item) for item in result])

    if resultsTable.rows:
        console.print(resultsTable)
    else:
        console.print(f"[i]No data for " + queryResults["tableName"] + " table...[/i]")

    #will fix later, currently works
    if output:
        write_to_csv(queryResults["tableName"] + ".csv", queryResults["columnNames"], normalizedResults)
        console.print("[i]"+ "Created CSV File:  " + queryResults["tableName"] + ".csv" + "[/i]")

def convertTime(time):
    seconds = time / 1000000-11644473600
    converted = datetime.fromtimestamp(seconds)
    return converted.strftime('%Y-%m-%dT%H:%M:%S.%f')

def write_to_csv(filename, columns, data):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(data)

def main(
    all: Annotated[bool, typer.Option("--all", "-a", help="Show both URL and Download tables")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show verbose output from tables")] = False,
    rows: Annotated[int, typer.Option("--rows", "-r", min = 0, max=50, help="Limit number of rows that each table generates")] = 10,
    output: Annotated[bool, typer.Option("--output", "-o", help="Output table contents to a CSV (not implemented)")] = False,
    ):
    
    printBanner()
    databaseHistory = getNewestFile()
    
    cursor, con = dbConnection(databaseHistory)
    console.print(f"Reading file - {databaseHistory}", style="white on blue")
    
    queryResults = None

    tables = ["downloads", "urls"]

    if all:
        for table in tables:
            queryResults = queryBuilder(cursor, table, rows, verbose)
            printOutput(queryResults, output)
    else:
        queryResults = queryBuilder(cursor, tables[0], rows, verbose)
        printOutput(queryResults, output)

    
    dbCleanup(con)
    console.print("Database connection closed...", style="white on blue")

if __name__ == "__main__":
    typer.run(main)