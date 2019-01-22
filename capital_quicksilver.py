import csv
import os
from decimal import Decimal

import datetime
from string import capwords

from sanitizer import Transaction, TransactionList


class QuicksilverTransaction(Transaction):
    CARD_NAME = 'Capital One Quicksilver'

    @staticmethod
    def _parsed_description(description):
        description = capwords(description)
        description = description.strip()
        description = description.replace(',', '')
        return description

    def __init__(self, card, stage, date, description, debit, credit):
        if card != '7299' or stage != 'POSTED' or (debit and credit):
            raise ValueError
        super(QuicksilverTransaction, self).__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description, self._parsed_description(description)),
            amount=Decimal(debit or credit),
            is_charge=bool(debit),
        )


def process(infile: str) -> list:
    transaction_list = TransactionList()
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            transaction_list.insert(0, QuicksilverTransaction(
                card=row[' Card No.'],
                stage=row['Stage'],
                date=row[' Transaction Date'],
                description=row[' Description'],
                debit=row[' Debit'],
                credit=row[' Credit'],
            ))
    return transaction_list


def find_file():
    candidates = set()
    for file in os.listdir("/Users/seanscott/Downloads/"):
        if file.endswith("_transaction_download.csv"):
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
