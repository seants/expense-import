import csv
import os
import re
from decimal import Decimal

import datetime
from string import capwords

from sanitizer import Transaction, TransactionList


class AmazonTransaction(Transaction):
    CARD_NAME = 'Amazon Rewards'

    @staticmethod
    def _parsed_description(description):
        if description.startswith('SQ *') or description.startswith('TST* '):
            description = description[4:]
        description = re.sub(r'(\d{4,15})$', '', description)
        description = capwords(description)
        description = description.strip()
        description = description.replace(',', '')
        description = description.replace('`', "'")
        return description

    def __init__(self, date, description, type, amount):
        if type not in ('Sale', 'Payment', 'Return'):
            raise ValueError
        super(AmazonTransaction, self).__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description, self._parsed_description(description)),
            amount=-1 * Decimal(amount),
            is_charge=type == 'Sale',
            is_return=type == 'Return',
        )


def process(infile: str) -> list:
    transaction_list = TransactionList()
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): val for key, val in row.items()}
            lowered['date'] = lowered['transaction date']
            del lowered['transaction date']
            del lowered['post date']
            del lowered['category']
            transaction_list.insert(0, AmazonTransaction(**lowered))
    return transaction_list


def find_file():
    candidates = set()
    for file in os.listdir("/Users/seanscott/Downloads/"):
        if file.startswith("Chase") and file.endswith(".CSV"):
            candidates.add(os.path.join("/Users/seanscott/Downloads/", file))
    if len(candidates) != 1:
        print(candidates)
        raise ValueError
    else:
        return next(iter(candidates))


def main():
    transactions = process(find_file())
    print(transactions)


if __name__ == '__main__':
    main()
