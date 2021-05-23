# Book Scrapper
----------------------------------------
## Requirements:
altgraph==0.17
appdirs==1.4.4
asgiref==3.3.4
beautifulsoup4==4.9.3
certifi==2020.12.5
chardet==4.0.0
distlib==0.3.1
filelock==3.0.12
future==0.18.2
idna==2.10
pefile==2019.4.18
pyinstaller==4.3
pyinstaller-hooks-contrib==2021.1
pytz==2021.1
pywin32-ctypes==0.2.0
requests==2.25.1
six==1.15.0
soupsieve==2.2.1
sqlparse==0.4.1
urllib3==1.26.4
virtualenv==20.4.4
virtualenvwrapper-win==1.2.6




Book scrapper goes through various websites, where free books are available 
and allow user to download them.
Version 1: This version will go to z-lib and will look for the book titles, find the first match, and acquire its details
Version 2: It'll populate top 4 searches.
Version 3: Adds available formats, and their size from search page. (pdf if pdf is avail, otherwise others)
Version 4: goes to the url for the book and finds all the formats available