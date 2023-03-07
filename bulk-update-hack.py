import configparser
import requests
import argparse
import pandas as pd
import json
import sys
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_transactions(config, args):

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

    def needs_memo(t):
        sought = 'AMZ*DasMarine-1        WWW.AMAZON.CA ON'
        return t['payee_name'] == sought and t['memo'] == ''

    txns = response["data"]["transactions"]

    patchdata = [
        {
            'id': t['id'],
            'account_id': t['account_id'],
            'date': t['date'],
            'amount': t['amount'],
            'memo': t['payee_name']
        }
        for t in txns
        if needs_memo(t)
    ]
    # print(patchdata)
    payload = {
        'transactions': patchdata
    }

    patchurl = f'https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions'
    print(patchurl)
    print(json.dumps(params, indent=4, sort_keys=True))

    if len(patchdata) > 0:
        print('posting...')
        response = session.patch(patchurl, json = payload)
        data = response.json()
        print('\n\nresponse:')
        print(data)
    else:
        print('nothing to update')


def main(config, args):
    get_transactions(config, args)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    now = datetime.now()
    first_of_month = now.strftime("%Y-%m-1")
    parser.add_argument(
        "--since_date",
        help=f"Start date of transactions, YYYY-mm-dd, default = {first_of_month}",
        default = first_of_month)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    main(config, args)
