import csv
import datetime

from decimal import Decimal

import re

CARD_NAME = 'Citi DoubleCash'
AMOUNT_THRESHOLD = 5


class Category(object):
    GROCERY = 'Grocery'
    TAXI = 'Transportation/Taxi'
    FAST_FOOD = 'Dining/Fast Food'
    TOILETRIES = 'Appearance/Toiletries'
    GYM = 'Sports/Gym'
    DRINKS = 'Dining/Drinks'
    FINANCIAL_MANAGEMENT = 'Financial Management'


def _sanitize_name(name):
    parts = name.split()
    if len(parts) > 1 and re.search('[0-9]{3}', parts[-1]):
        return ' '.join(parts[:-1])
    return name


class Merchant(object):
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category


class Merchants(object):
    BLINK = Merchant("Blink Fitness", Category.GYM)
    CLASSPASS = Merchant("Classpass", Category.GYM)
    COINBASE = Merchant("Coinbase", Category.FINANCIAL_MANAGEMENT)


RECURRING_MERCHANTS = {
    Merchants.BLINK,
    Merchants.CLASSPASS,
    Merchants.COINBASE,
}


NAME_CONVERSIONS = {
    "trader joe's": Merchant("Trader Joe's", Category.GROCERY),
    'uber': Merchant('Uber', Category.TAXI),
    'lyft': Merchant('Lyft', Category.TAXI),
    'target': Merchant('Target', Category.GROCERY),
    "mcdonald's": Merchant("McDonald's", Category.FAST_FOOD),
    "cvs/pharmacy": Merchant("CVS", Category.TOILETRIES),
    "dnkn donuts": Merchant("Dunkin Donuts", Category.FAST_FOOD),
    "brother jimmys": Merchant("Brother Jimmy's", Category.DRINKS),
    "blink moto": Merchants.BLINK,
    "classpass": Merchants.CLASSPASS,
    "coinbase": Merchants.COINBASE,
    "mortonwilliams": Merchant("Morton Williams", Category.GROCERY),
    "nyctaxi": Merchant("NYC Taxi", Category.TAXI),
}


def _lower(in_str):
    return in_str.group(0).lower()


class Transaction(object):
    class Description(object):
        def __init__(self, desc_string: str):
            self.name = desc_string[:23].strip()
            self.city = desc_string[23:37].strip()
            self.state = desc_string[37:41].strip()
            self.extra = desc_string[41:].strip() or None

        @property
        def merchant(self) -> Merchant:
            lower_name = self.name.lower()
            for key, val in NAME_CONVERSIONS.items():
                if key in lower_name:
                    return val
            name = self.name.title().replace("'S", "'s")
            name = re.sub(r'\d\w+', _lower, name)
            name = re.sub(r'(.{1,8}\*)', '', name, flags=re.IGNORECASE)
            name = name.strip()
            return Merchant(_sanitize_name(name), '')

    @staticmethod
    def _convert_amount(amount):
        return Decimal(amount.replace(',', '')) if amount else None

    @staticmethod
    def _convert_date(date_str):
        return datetime.datetime.strptime(date_str, '%m/%d/%Y').date()

    @property
    def is_charge(self):
        return self.debit is not None

    @property
    def formatted_date(self):
        return self.date.strftime('%m/%d/%Y')

    @property
    def amount(self):
        return self.debit or self.credit

    @property
    def meets_threshold(self):
        return self.amount > AMOUNT_THRESHOLD

    @property
    def recurring_ignored(self):
        return self.description.merchant in RECURRING_MERCHANTS

    @property
    def should_include(self):
        return self.meets_threshold and not self.recurring_ignored

    def __init__(self, status, date, description, debit, credit):
        self.status = status
        self.date = self._convert_date(date)
        self.description = self.Description(desc_string=description)
        self.debit = self._convert_amount(debit)
        self.credit = self._convert_amount(credit)

    @property
    def formatted(self) -> str:
        return ','.join([
            self.formatted_date,
            self.description.merchant.name,
            self.description.merchant.category,
            str(self.amount),
            CARD_NAME,
        ])
