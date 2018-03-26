import csv
import re

import datetime
from decimal import Decimal
from string import capwords

from sanitizer import Transaction, Merchant, NAME_CONVERSIONS, TransactionList

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
    return Decimal(amount.replace(',', '')) if amount else None


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


def process(infile: str) -> list:
    transaction_list = TransactionList()
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): val for key, val in row.items()}
            transaction_list.append(CitiTransaction(**lowered))
    return transaction_list


def main():
    transactions = process('/Users/seanscott/Downloads/MC_954_CURRENT_VIEW.CSV')
    print(transactions)


if __name__ == '__main__':
    main()
