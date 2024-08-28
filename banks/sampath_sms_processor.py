import re
from datetime import datetime


def process_common_pattern(sms_message: str, date_time: str, bank: str):
    try:
        # Patterns for different Sampath SMS formats
        # Debit card internet txn
        internet_txn_pattern = r"([A-Z]{3})\s([\d,]+\.\d{2})\s(debited|credited)\s(?:to|from)\sAC\s\*\*(\d{4})\sfor\s((?:eCom|eCom/REV)[^\s]*)\s([A-Z]+\s[A-Z]+\s\d+|[A-Z]+\s\d+|[A-Z]+)"
        # Debit card POS txn
        pos_txn_pattern = r"([A-Z]{3})\s([\d,]+\.\d{2})\s(debited|credited)\sfrom\sAC\s\*\*(\d{4})\s(?:via|at)\sPOS\sat\s(.+?)-"
        # ATM Withdrawal
        atm_withdrawal_pattern = r"([A-Z]{3})\s([\d,]+\.\d{2})\s(debited|credited)\sfrom\sAC\s\*\*(\d{4})\s(via\sATM)\sat\s(.+?)\s*-\s*For"
        # Credited/debited txn
        credited_debited_pattern = r"([A-Z]{3})\s([\d,]+\.\d{2})\s(debited|credited)\s(?:from|to)\sAC\s\*\*(\d{4})\sfor\s(.+?)(?:-For|$)"
        # Credit card txn/ web card txn
        credit_card_purchase_pattern = r"(Cr Crd)\sno\.\.(\d+)\s(Auth|Recvd)\sPmt\s([A-Z]{3})?\s?([\d,]+\.\d{2})\s?(?:at\s([\w\s.-]+))?.*?(\d{2}-[A-Za-z]+)$"

        # Attempt to match each pattern
        match1 = re.search(internet_txn_pattern, sms_message)
        match2 = re.search(pos_txn_pattern, sms_message)
        match3 = re.search(atm_withdrawal_pattern, sms_message, re.DOTALL)
        match4 = re.search(credited_debited_pattern, sms_message)
        match5 = re.search(credit_card_purchase_pattern, sms_message)

        # Debit card internet txn
        if match1:
            currency, amount, action, account, description, location = match1.groups()

            return {
                "bank": bank,
                "account": account,
                "location": location.strip(),
                "description": description.strip(),
                "amount": amount,
                "currency": currency,
                "flow": "income" if action == "credited" else "expense",
                "transactionType": "card_internet",
                "date_time":  date_time,
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        # Debit card POS txn
        elif match2:
            currency, amount, action, account, location = match2.groups()

            return {
                "bank": bank,
                "account": account,
                "location": location,
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "card_pos",
                "date_time": date_time,
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        # ATM Withdrawal
        elif match3:
            currency, amount, action, account, atm, location = match3.groups()

            return {
                "bank": bank,
                "account": account,
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "atm_withdrawal",
                "date_time": date_time,
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        # Credited/debited txn
        elif match4:
            currency, amount, action, account, description = match4.groups()

            return {
                "bank": bank,
                "account": account,
                "location": "",
                "description": description.strip(),
                "amount": amount,
                "currency": currency,
                "flow": "income" if action == "credited" else "expense",
                "transactionType": 'bank_transfer',
                "date_time": date_time,
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        # Credit card txn/ web card txn
        elif match5:
            cr_crd, card_number, action, currency, amount, location, date = match5.groups()
            return {
                "bank": bank,
                "account": card_number,
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "income" if action == "Recvd" else "expense",
                "transactionType": "credit_card",
                "date_time": date,
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            return {
                "bank": bank,
                "account": "NO_MATCH",
                "location": "NO_MATCH",
                "description": "NO_MATCH",
                "amount": "NO_MATCH",
                "currency": "NO_MATCH",
                "flow": "NO_MATCH",
                "transactionType": "NO_MATCH",
                "date_time": "NO_MATCH",
                "sms_message": sms_message,
                "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    except Exception as e:
        # Return the "NO_MATCH" result if an error is caught
        return {
            "bank": bank,
            "account": "NO_MATCH",
            "location": "NO_MATCH",
            "description": "NO_MATCH",
            "amount": "NO_MATCH",
            "currency": "NO_MATCH",
            "flow": "NO_MATCH",
            "transactionType": "NO_MATCH",
            "date_time": "NO_MATCH",
            "sms_message": sms_message,
            "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # Optionally include the error message for debugging
            "error": str(e)
        }
