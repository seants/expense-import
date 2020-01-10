import csv
import os
from decimal import Decimal

import datetime
from string import capwords

from sanitizer import Transaction, TransactionList
from util import find_file


class QuicksilverTransaction(Transaction):
    CARD_NAME = 'CapitalOne Quicksilver'

    @staticmethod
    def _parsed_description(description):
        description = capwords(description)
        description = description.strip()
        description = description.replace(',', '')
        return description

    def __init__(self, card, date, description, debit, credit):
        if card != '7299' or (debit and credit):
            raise ValueError
        super(QuicksilverTransaction, self).__init__(
            date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
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
                card=row['Card No.'],
                date=row['Transaction Date'],
                description=row['Description'],
                debit=row['Debit'],
                credit=row['Credit'],
            ))
    return transaction_list


def main():
    transactions = process(find_file("/Users/seanscott/Downloads/", "", "_transaction_download.csv"))
    print(transactions)


if __name__ == '__main__':
    main()
