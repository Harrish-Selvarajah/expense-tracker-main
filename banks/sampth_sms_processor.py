# def process sms (sms, bank, datetime)
# depending on the bank we will extract the location, Description, Amount, Currency, Income/Expense, transaction type (card, bank transfer, cash)

# def process sms category (location, description)
# creates the txn Category and subcategory.

import re


def process_sms(sms_message: str):

    # Patterns for different HNB SMS formats
    pattern1 = r"LKR ([\d,.]+) (credited|debited) to Ac No:\d+ on \d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} Reason:(.*?) Bal:LKR [\d,.]+ Protect from scams .* Hotline \d+"
    pattern2 = r"TRANSACTION REVERSAL, (Credit|Debit) account:\d+,Location:(.*?),Amount:([\d,.]+) LKR,Av.Bal:[\d,.]+ LKR,Date:\d{2}.\d{2}.\d{2},Time:\d{2}:\d{2}, Hot Line:\d+"
    pattern3 = r"HNB SMS ALERT:(.*?), Account:\d+,Location:(.*?),Amount\(Approx.\):([\d,.]+) LKR,Av.Bal:[\d,.]+ LKR,Date:\d{2}.\d{2}.\d{2},Time:\d{2}:\d{2}, Hot Line:\d+"

    # Attempt to match each pattern
    match1 = re.search(pattern1, sms_message)
    match2 = re.search(pattern2, sms_message)
    match3 = re.search(pattern3, sms_message)

    if match1:
        amount = float(match1.group(2).replace(",", ""))
        transaction_type = match1.group(3).lower()
        return {
            "location": "",
            "description": match1.group(4),
            "amount": amount if transaction_type == "credited" else -amount,
            "currency": match1.group(1),
            "income/expense": "income" if transaction_type == "credited" else "expense",
            "transaction_type": "bank_transfer",
        }
    elif match2:
        transaction_type = match2.group(1).lower()
        return {
            "location": match2.group(2),
            "description": "TRANSACTION REVERSAL",
            "amount": float(match2.group(3).replace(",", "")) if transaction_type == "credit" else -float(match2.group(3).replace(",", "")),
            "currency": match2.group(4),
            "income_expense": "income" if transaction_type == "credit" else "expense",
            "transaction_type": "transaction_reversal",
        }
    elif match3:
        description = match3.group(1).lower()
        transaction_type = "card" if description in [
            "purchase", "internet"] else "bank_transfer"
        return {
            "location": match3.group(2),
            "description": description,
            # Assuming HNB SMS ALERT is usually a debit/expense
            "amount": -float(match3.group(3).replace(",", "")),
            "currency": match3.group(4),
            "income_expense": "expense",
            "transaction_type": transaction_type,
        }
    else:
        return None
