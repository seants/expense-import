import csv
import os
import re
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
        description = re.sub(r'(\d{4,15})$', '', description)
        description = capwords(description)
        description = description.replace('`', "'")
        return Transaction._sanitize_description(description)

    def __init__(self, date, description, category, amount):
        super(UberTransaction, self).__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description, self._parsed_description(description)),
            amount=-1 * Decimal(amount),
            is_charge=category == 'DEBIT',
            is_return=(
                category == 'CREDIT'
                and not description.startswith('CASH BACK')
                and not description.startswith('Payment Received')
            ),
        )


def process(infile: str) -> TransactionList:
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


def find_file() -> str:
    candidates = set()
    for file in os.listdir("/Users/seanscott/Downloads/"):
        if file.startswith("CreditCard_") and file.endswith(".csv"):
            candidates.add(os.path.join("/Users/seanscott/Downloads/", file))
    if len(candidates) != 1:
        raise ValueError
    else:
        return next(iter(candidates))


def main():
    transactions: TransactionList = process(find_file())
    transactions.date_sort()
    transactions.glob_small_amounts()
    print(transactions)


if __name__ == '__main__':
    main()
