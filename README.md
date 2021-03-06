# YNAB gsheets reporter

Gets transactions after a given start date, or defaults from the first
of the current month, "normalizes" the payees using a supplied
`mappings.json` file, and then exports a summary to a google sheet.

The "normalizing" was necessary for me, because different locations in
a chain will use their particular name as the "payee".  For example, Starbucks has

```
STARBUCKS 00122        VICTORIA      BC
STARBUCKS 00134        DUNCAN        BC
STARBUCKS COFFEE #2038 VICTORIA      BC
```

I only care about "Starbucks", so I do a manual map.

It's not a great solution, but it's good enough.

**NOTE: I just read a bit more about this, and apparently YNAB has a
feature that allows for automatic renaming based on some rules ... USE
THAT INSTEAD!  I'll update this code (perhaps) when I try out that
feature for myself.**


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

When it runs, it outputs a list of "Unmapped" entries so that you can
add them to your mappings.json.

# Cron job

If you have a mac, and are feeling adventursome, you could try setting up a cron job with the bash file in this repo:

`crontab -e` starts the editor, and add, e.g.:

```
0 8 * * * pushd /path/to/this/dir && ./update-gsheets.sh && popd >> /tmp/cron.out 2>&1
```

Then after a few days, when you're sure everything works, remove the `>> /tmp/cron.out 2>&1` and `rm /tmp/cron.out`

# Thanks ...

... to https://github.com/danaimone/ynab_pandas_demo for the starting
point.
