# bspy - Browser Spy
_Uh oh, they got phished again!_ Name inspired from the wonderful tool [pspy](https://github.com/DominicBreuker/pspy)!

## Overview
Provide security researchers or security analysts the ability to provide insight to browser history files in a more accessible manner without the use of a SQLite GUI. At the current stage of this tool, Microsoft Edge and Google Chrome history files have been validated.

## Prereq

Clone the repo and create the required config file for the tool to function
```
git clone https://github.com/0xFFaraday/bspy.git
cd bspy && pip install -r requirements.txt

# Create config reference for input & export of files
echo "$PWD/config.json" > .env
```

## Usage 

Before running, ensure you have a browser history SQLite file within your Downloads directory (Default Search Location). Tested on MacOS, Unix, and PowerShell on Windows. Your first run of bspy will prompt you for a directory to store your exported CSVs and the SQLite search directory.
```
# Help Usage
python ./main.py --help

# Example 1 - Pull both URLs and the downloads tables
python ./main.py --all

# Example 2 - Pull downloads table and limit output
python ./main.py --rows 5
```

## Features
- Automatic extraction of potential IoCs
- Pulls latest SQLite file from the home's downloads directory
- [Chainsaw](https://github.com/WithSecureLabs/chainsaw)-inspired output for console