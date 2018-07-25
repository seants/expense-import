import csv
import re

import datetime
from decimal import Decimal
from string import capwords

from sanitizer import Transaction, TransactionList

CARD_NAME = 'Discover Credit Card'


def _lower(in_str):
    return in_str.group(0).lower()


def _sanitize_name(name):
    # For street numbers
    name = re.sub(r'\d\w+', _lower, name)
    name = re.sub(r'(#? ?\d{1,8}\*?)', '', name, flags=re.IGNORECASE)
    name = name.strip()
    name = capwords(name)
    parts = name.split()
    if len(parts) > 1 and re.search('[0-9]{3}', parts[-1]):
        return ' '.join(parts[:-1])
    return name


def _convert_amount(amount):
    return Decimal(amount.replace(',', '')) if amount else None


class DiscoverTransaction(Transaction):
    CARD_NAME = CARD_NAME

    def __init__(self, date, category, description, amount):
        amount = _convert_amount(amount)
        is_charge = amount > 0
        super().__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description, _sanitize_name(description)),
            amount=amount,
            is_charge=is_charge,
        )


def process(infile: str) -> list:
    transaction_list = TransactionList()
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): val for key, val in row.items()}
            lowered['date'] = lowered['trans. date']
            del lowered['trans. date']
            del lowered['post date']
            transaction_list.append(DiscoverTransaction(**lowered))
    return transaction_list


def main():
    transactions = process('/Users/seanscott/Downloads/Discover-2018-YearToDateSummary.csv')
    print(transactions)


if __name__ == '__main__':
    main()
