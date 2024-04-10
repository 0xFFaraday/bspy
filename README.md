# bspy - Browser Spy
_Uh oh, they got phished again!_ Name inspired from the wonderful tool [pspy](https://github.com/DominicBreuker/pspy)!

## Overview
Provide security researchers or security analysts the ability to provide insight to browser history files in a more accessible manner without the use of a SQLite GUI. At the current stage of this tool, Microsoft Edge and Google Chrome history files have been validated.

## Usage 

```
git clone https://github.com/0xFFaraday/bspy.git
cd bspy && pip install -r requirements.txt

python ./main.py
```

## Features
- Automatic extraction of potential IoCs
- Pulls latest SQLite file from the home's downloads directory
- [Chainsaw](https://github.com/WithSecureLabs/chainsaw)-inspired output for console

### References
https://jacobnarayan.com/blogs/how-to-find-the-most-recent-file-in-a-directory-in-python
https://docs.nxlog.co/integrate/browser-history.html
