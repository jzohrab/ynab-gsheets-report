import configparser
import requests
import argparse
import pandas as pd
import json
import sys
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

mappings = None
with open('mappings.json') as infile:
    mappings = json.load(infile)

def mapped_payee_name(s):
    return mappings.get(s, s)

def get_dataframe(config, args):

    session = requests.Session()
    header = {'Authorization': f"Bearer {config['CONFIG']['token']}"}
    session.headers.update(header)

    # Figuring out your budget ID
    response = session.get(f'https://api.youneedabudget.com/v1/budgets/')
    data = response.json()
    # print(json.dumps(data, indent=4, sort_keys=True))

    budgetName = config['CONFIG']['budgetName']
    budgets = [
        b for b in data["data"]["budgets"]
        if b["name"] == budgetName
    ]
    
    if (len(budgets) != 1):
        print(f"missing budget {budgetName}, or multiple with same name")
        sys.exit(1)
    
    budget = budgets[0]
    budget_id = budget.get("id")
    
    # Get all your transactions in your budget
    params = {
        'since_date': args.since_date
    }
    endpoint = f'https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions/'
    response = session.get(endpoint, params = params).json()
    
    # print(response)

    txns = response["data"]["transactions"]
    # for t in txns:
    #     print(t['amount'])

    def to_curr(a):
        pennies = int(int(a) / 10)
        return -1 * round(pennies / 100.0, 2)

    smalltxns = [
        {
            "amount": to_curr(t['amount']),
            "category_name": t['category_name'],
            "date": t['date'],
            "payee_name": t['payee_name'],
            "payee": mapped_payee_name(t['payee_name'])
        }
        for t in txns
    ]
    # print(json.dumps(smalltxns, indent=4, sort_keys=True))

    print("Unmapped:")
    unmapped = [
        t['payee_name']
        for t in smalltxns
        if t['payee'] == t['payee_name']
    ]
    unmapped = list(set(unmapped))
    unmapped.sort()
    for u in unmapped:
        orig = f"\"{u}\"".ljust(50)
        print(f"{orig}: \"{u}\",")
    print()

    def shorten(s, maxlen):
        ret = s
        if len(s) > maxlen:
            ret = f"{s[0:maxlen - 1]}..."
        return ret

    for t in smalltxns:
        t['payee'] = shorten(t['payee'], 40)

    df = pd.json_normalize(smalltxns)
    # print(df)

    cols = ['category_name', 'payee']
    ret = df.groupby(cols)['amount'].sum().reset_index()
    ret = ret.sort_values(by = ['category_name', 'amount'], ascending=[True,False])

    return ret


def upload_to_gsheets(config, args, df):

    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    jfile = config['CONFIG']['googleCreds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(jfile, scope)

    client = gspread.authorize(creds)

    sheetname = config['CONFIG']['sheetName']
    sheet = client.open(sheetname)

    sheet_instance = sheet.get_worksheet(0)
    sheet_instance.clear()

    df.reset_index()

    # For getting list plus headings for insert:
    # https://stackoverflow.com/questions/49176376/
    #   pandas-dataframe-to-lists-of-lists-including-headers
    a = df.columns.values.tolist()
    b = df.values.tolist()
    b.insert(0, a)

    sheet_instance.update(b)


def main(config, args):
    ret = get_dataframe(config, args)
    if (args.output):
        ret.to_csv(args.output, index=False)
    else:
        print(ret)
        print('Upload to gsheets...')
        upload_to_gsheets(config, args, ret)
        print('done upload')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    now = datetime.now()
    first_of_month = now.strftime("%Y-%m-1")
    parser.add_argument(
        "--since_date",
        help=f"Start date of transactions, YYYY-mm-dd, default = {first_of_month}",
        default = first_of_month)
    parser.add_argument(
        "--output",
        help="Path to output csv file.  If not present, upload to configured google sheet"
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    main(config, args)
