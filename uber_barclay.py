import csv
import os
from decimal import Decimal

import datetime
from string import capwords

from sanitizer import Transaction, NAME_CONVERSIONS, TransactionList


class UberTransaction(Transaction):
    CARD_NAME = 'Uber Barclaycard'

    @staticmethod
    def _parsed_description(description):
        if description.startswith('SQ *') or description.startswith('TST* '):
            description = description[4:]
        description = capwords(description)
        description = description.strip()
        description = description.replace(',', '')
        description = description.replace('`', "'")
        return description

    def __init__(self, date, description, category, amount):
        super(UberTransaction, self).__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description, self._parsed_description(description)),
            amount=-1 * Decimal(amount),
            is_charge=category == 'DEBIT',
        )


def process(infile: str) -> list:
    transaction_list = TransactionList()
    with open(infile) as f:
        for _ in range(4):
            f.readline()
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): val for key, val in row.items()}
            lowered['date'] = lowered['transaction date']
            del lowered['transaction date']
            transaction_list.insert(0, UberTransaction(**lowered))
    return transaction_list


def find_file():
    candidates = set()
    for file in os.listdir("/Users/seanscott/Downloads/"):
        if file.startswith("CreditCard_") and file.endswith(".csv"):
            candidates.add(os.path.join("/Users/seanscott/Downloads/", file))
    if len(candidates) != 1:
        raise ValueError
    else:
        return next(iter(candidates))


def main():
    transactions = process(find_file())
    print(transactions)


if __name__ == '__main__':
    main()
