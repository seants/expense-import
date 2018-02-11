from string import capwords

AMOUNT_THRESHOLD = 5


class Category(object):
    DRINKS = 'Dining/Drinks'
    ENTERTAINMENT = 'Entertainment'
    FAST_FOOD = 'Dining/Fast Food'
    FINANCIAL_MANAGEMENT = 'Financial Management'
    GROCERY = 'Grocery'
    GYM = 'Sports/Gym'
    TAXI = 'Transportation/Taxi'
    TOILETRIES = 'Appearance/Toiletries'

    class Housing(object):
        CABLE = 'Housing/Cable'


class Merchant(object):
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category


class Merchants(object):
    BLINK = Merchant("Blink Fitness", Category.GYM)
    CLASSPASS = Merchant("Classpass", Category.GYM)
    COINBASE = Merchant("Coinbase", Category.FINANCIAL_MANAGEMENT)
    VERIZON = Merchant("Verizon Wireless", Category.Housing.CABLE)
    NETFLIX = Merchant("Netflix", Category.Housing.CABLE)


RECURRING_MERCHANTS = {
    # Also, coned and Spectrum
    Merchants.BLINK,
    Merchants.CLASSPASS,
    Merchants.COINBASE,
    Merchants.VERIZON,
    Merchants.NETFLIX,
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
    "you should be": Merchant("You Should Be Dancing", Category.ENTERTAINMENT),
    "verizon": Merchants.VERIZON,
    "vzwrlss": Merchants.VERIZON,
    "netflix": Merchants.NETFLIX,
}


class Transaction(object):
    CARD_NAME = NotImplemented

    @property
    def formatted_date(self):
        return self.date.strftime('%m/%d/%Y')

    @property
    def meets_threshold(self):
        return self.amount > AMOUNT_THRESHOLD

    @property
    def recurring_ignored(self):
        return self.merchant in RECURRING_MERCHANTS

    @property
    def should_include(self):
        return self.meets_threshold and not self.recurring_ignored and self.is_charge

    @staticmethod
    def _parse_merchant(raw, parsed):
        lower_name = raw.lower()
        for key, val in NAME_CONVERSIONS.items():
            if key in lower_name:
                return val
        return Merchant(parsed, '')

    def __init__(self, date, merchant, amount, is_charge):
        self.date = date
        self.merchant = merchant
        self.amount = amount
        self.is_charge = is_charge

    @property
    def formatted(self) -> str:
        return ','.join([
            self.formatted_date,
            self.merchant.name,
            self.merchant.category,
            str(self.amount),
            self.CARD_NAME,
        ])

    def __str__(self):
        return self.formatted


class TransactionList(list):
    def __str__(self):
        out = ''
        for transaction in self:
            if transaction.should_include:
                out += transaction.formatted + '\n'
        return out
