# YNAB reporter

Gets stuff from ynab

# Install

```
python3 -m venv .venv
source .venv/bin/activate

.venv/bin/pip3 install -r requirements.txt

deactivate
```

# Create a Google sheet

Set up a sheet for this project to update

# Create a google project and get creds

Google project per https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/

**Share that google sheet with the email from your google creds file!!!**

# Config

Copy config.ini.example to config.ini, and fill in your details.

Copy mappings.json.example to mappings.json, and fill in your name mappings.

# Running

```
python3 -m venv .venv
source .venv/bin/activate

python ynab.py -h
# -h outputs the help:
# usage: ynab.py [-h] [--since_date SINCE_DATE] [--output OUTPUT]

python ynab.py
# Runs using the first of the month as the first entry,
# and updates google sheet.

deactivate
```

# Thanks

to https://github.com/danaimone/ynab_pandas_demo/blob/master/ynab.py for the starting point.