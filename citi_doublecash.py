import csv

from sanitizer import Transaction


def process(infile: str) -> list:
    transaction_list = []
    with open(infile) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lowered = {key.lower(): value for key, value in row.items()}
            transaction_list.append(Transaction(**lowered))
    return transaction_list


def main():
    transactions = process('/Users/seanscott/Downloads/MC_954_CURRENT_VIEW.CSV')
    charges = [transaction for transaction in transactions if transaction.is_charge]
    credits_list = [transaction for transaction in transactions if not transaction.is_charge]
    thresh_charges = [charge for charge in charges if charge.should_include]
    print(len(charges), len(credits_list), len(thresh_charges))
    # for charge in thresh_charges:
    #     if not charge.description.merchant.category:
    #         print(charge.formatted)
    for charge in thresh_charges:
        print(charge.formatted)


if __name__ == '__main__':
    main()
