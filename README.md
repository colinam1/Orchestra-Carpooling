# Orchestra-Carpooling
Purdue Orchestras Carpooling Repo

This YouTube video explains how to properly authenticate your gmail account with the library used in the Python script, gspread:
https://www.youtube.com/watch?v=bu5wXjz2KvU

Python script should take in the form responses from the Google Form, not mess with the sheet they came from (raw data stays the same) but should create a new sheet for each orchestra with the drivers and riders allocated properly without emailing everybody in the sheet.

If email functionality is set up, there DEFINITELY should be safeties set up to make it hard to accidentally email everybody all at once. There should be one email per car with everybody's contact info listed so it only takes one of the members to setup a group and contact their driver.
