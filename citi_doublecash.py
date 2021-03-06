import csv
import os
import re

import datetime
from decimal import Decimal
from string import capwords

from sanitizer import Transaction, TransactionList

CARD_NAME = 'Citi DoubleCash'


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
    return Decimal(amount.replace(',', '')) if amount else 0


class CitiDescription(object):
    def __init__(self, desc_string: str):
        self.name = desc_string[:23].strip()
        self.city = desc_string[23:37].strip()
        self.state = desc_string[37:41].strip()
        self.extra = desc_string[41:].strip() or None


class CitiTransaction(Transaction):
    CARD_NAME = CARD_NAME

    def __init__(self, date, status, description, debit, credit):
        if debit and credit:
            raise ValueError
        if status != 'Cleared':
            raise ValueError
        description = CitiDescription(description)
        amount = _convert_amount(debit or credit)
        is_charge = bool(debit)
        super().__init__(
            date=datetime.datetime.strptime(date, '%m/%d/%Y').date(),
            merchant=self._parse_merchant(description.name, _sanitize_name(description.name)),
            amount=amount,
            is_charge=is_charge,
        )


def process(infile: str) -> TransactionList:
    transaction_list = TransactionList()
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): val for key, val in row.items()}
            transaction_list.append(CitiTransaction(**lowered))
    return transaction_list


def find_file() -> str:
    candidates = set()
    for file in os.listdir("/Users/seanscott/Downloads/"):
        if file.startswith("From ") and file.endswith(".CSV"):
            candidates.add(os.path.join("/Users/seanscott/Downloads/", file))
    if len(candidates) != 1:
        raise ValueError
    else:
        return next(iter(candidates))


def main():
    transactions = process(find_file())
    transactions.date_sort()
    transactions.glob_small_amounts()
    print(transactions)


if __name__ == '__main__':
    main()
