from string import capwords

AMOUNT_THRESHOLD = 5


class Category(object):
    HAIRCUT = 'Appearance/Haircut'
    DRINKS = 'Dining/Drinks'
    ENTERTAINMENT = 'Entertainment'
    FAST_FOOD = 'Dining/Fast Food'
    FINANCIAL_MANAGEMENT = 'Financial Management'
    GROCERY = 'Grocery'
    GYM = 'Sports/Gym'
    TOILETRIES = 'Appearance/Toiletries'

    class Housing(object):
        CABLE = 'Housing/Cable'

    class Health(object):
        MEDICAL = 'Health/Medical'

    class Transportation(object):
        TAXI = 'Transportation/Taxi'
        CAR = 'Transportation/Car Rental or Gas'


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
    TWC = Merchant('Time Warner Cable', Category.Housing.CABLE)
    ZOMATO = Merchant('Zomato', Category.FAST_FOOD)
    MC_DONALDS = Merchant("McDonald's", Category.FAST_FOOD)
    GEO_BLUE = Merchant("Geoblue Insurance", Category.Health.MEDICAL)
    CARREFOUR = Merchant("Carrefour", Category.GROCERY)
    EKAR = Merchant("Ekar", Category.Transportation.CAR)
    DUBAI_TAXI = Merchant("Dubai Taxi", Category.Transportation.TAXI)
    UDRIVE = Merchant("Udrive", Category.Transportation.CAR)
    AMAZON = Merchant("Amazon", "")
    AMAZON_AE = Merchant("Amazon AE", "")
    AMAZON_MKT = Merchant("Amazon Marketplace", "")
    WHOLE_FOODS = Merchant("Whole Foods", Category.GROCERY)


RECURRING_MERCHANTS = {
    Merchants.VERIZON,
    Merchants.NETFLIX,
    Merchants.GEO_BLUE,
}

HALF_CHARGE = {
    # Also ConEd but goes to debit acct
    Merchants.TWC,
}


NAME_CONVERSIONS = {
    'mcdonalds': Merchants.MC_DONALDS,
    'zomato order': Merchants.ZOMATO,
    "trader joe's": Merchant("Trader Joe's", Category.GROCERY),
    "whos next gents salon": Merchant("Who's Next Salon", Category.HAIRCUT),
    "zoom site no. 6523": Merchant('Zoom Majan', Category.GROCERY),
    'uber   trip': Merchant('Uber', Category.Transportation.TAXI),
    'uber   eats': Merchant('UberEats', Category.FAST_FOOD),
    'lyft': Merchant('Lyft', Category.Transportation.TAXI),
    'target': Merchant('Target', Category.GROCERY),
    "mcdonald's": Merchant("McDonald's", Category.FAST_FOOD),
    "cvs/pharmacy": Merchant("CVS", Category.TOILETRIES),
    "dnkn donuts": Merchant("Dunkin Donuts", Category.FAST_FOOD),
    "brother jimmys": Merchant("Brother Jimmy's", Category.DRINKS),
    "blink moto": Merchants.BLINK,
    "classpass": Merchants.CLASSPASS,
    "coinbase": Merchants.COINBASE,
    "mortonwilliams": Merchant("Morton Williams", Category.GROCERY),
    "nyctaxi": Merchant("NYC Taxi", Category.Transportation.TAXI),
    "you should be": Merchant("You Should Be Dancing", Category.ENTERTAINMENT),
    "verizon": Merchants.VERIZON,
    "vzwrlss": Merchants.VERIZON,
    "netflix": Merchants.NETFLIX,
    "twc*time warner nyc": Merchants.TWC,
    "mighty bowl": Merchant("Mighty Bowl", Category.FAST_FOOD),
    "worldwide insurance": Merchants.GEO_BLUE,
    "carrefour": Merchants.CARREFOUR,
    "www ekar ae": Merchants.EKAR,
    "cars taxi service": Merchants.DUBAI_TAXI,
    "arabia taxi": Merchants.DUBAI_TAXI,
    "u drive rent a": Merchants.UDRIVE,
    "amazon.com": Merchants.AMAZON,
    "amazon.ae": Merchants.AMAZON_AE,
    "amzn mktp": Merchants.AMAZON_MKT,
    "wholefds": Merchants.WHOLE_FOODS,
}


class Transaction(object):
    CARD_NAME = NotImplemented

    @property
    def formatted_date(self):
        return self.date.strftime('%m/%d/%Y')

    @property
    def meets_threshold(self):
        return abs(self.amount) > AMOUNT_THRESHOLD

    @property
    def recurring_ignored(self):
        return self.merchant in RECURRING_MERCHANTS

    @property
    def half_charge(self):
        return self.merchant in HALF_CHARGE

    @property
    def should_include(self):
        return self.meets_threshold and not self.recurring_ignored and (self.is_charge or self.is_return)

    @staticmethod
    def _parse_merchant(raw, parsed):
        lower_name = raw.lower()
        for key, val in NAME_CONVERSIONS.items():
            if key in lower_name:
                return val
        return Merchant(parsed, '')

    @property
    def final_amount(self):
        return round(self.amount / 2 if self.half_charge else self.amount, 2)

    def __init__(self, date, merchant, amount, is_charge, is_return=False):
        self.date = date
        self.merchant = merchant
        self.amount = amount
        self.is_charge = is_charge
        self.is_return = is_return

    @property
    def formatted(self) -> str:
        return ','.join([
            self.formatted_date,
            self.merchant.name,
            self.merchant.category,
            str(self.final_amount),
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
