import re
from datetime import datetime
from zoneinfo import ZoneInfo


def process_common_pattern(sms_message: str, date_time: str, bank: str):
    try:
        # Set the timezone to Sri Lanka
        sri_lanka_tz = ZoneInfo('Asia/Colombo')
        added_timestamp = datetime.now(
            sri_lanka_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Patterns for different Commercial SMS formats
        # Debit card internet/ POS purchase
        debit_purchase_txn_pattern = r"^Dear\sCardholder,\sPurchase\sat\s(?P<Location>.+?)\sfor\s(?P<Currency>\w+)\s(?P<Amount>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\son\s(?P<DateTime>.+?)\shas\sbeen\sauthorised\son\syour\s(?P<CardType>.+?)\sending\s#(?P<CardNo>\d+)\."
         # ATM Withdrawal
        atm_withdrawal_pattern = r"^Withdrawal\sat\s(?P<Location>.+?)\sfor\s(?P<Currency>\w+)\s(?P<Amount>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\son\s(?P<DateTime>\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}\s[APM]{2})\sfrom\scard\sending\s#(?P<Card>\d+)\."
        #ATM Deposit
        atm_deposit_pattern =r"^We\swish\sto\sconfirm\sa\sCRM\sDeposit\sat\s(?P<Time>\d{2}:\d{2})\sfor\s(?P<Currency>[A-Za-z]+)\.\s(?P<Amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\sthrough\s(?P<Location>.+?)\sto\syour\saccount\s(?P<Account>[*\d]+)"
        # Credit card internet/ POS purchase
        credit_purchase_txn_pattern=r"^Dear\sCardholder,\sPurchase\sat\s(?P<Location>.+?)\sfor\s(?P<Currency>\w+)\s(?P<Amount>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\son\s(?P<DateTime>\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}\s(?:AM|PM))\shas\sbeen\sauthorised\son\syour\s(?P<CardType>.+?)\scard\s#(?P<CardNo>\d+)\sCard\sAVL\sBAL\s(?P<AvailableBalance>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)"
        # Bank Transfer (Credit/Debit)
        # Utility Payment

        # Attempt to match each pattern
        match1 = re.search(debit_purchase_txn_pattern, sms_message)
        match2 = re.search(atm_withdrawal_pattern, sms_message,re.DOTALL)
        match3 = re.search(atm_deposit_pattern, sms_message)
        match4 = re.search(credit_purchase_txn_pattern, sms_message)
    
        # Debit card internet and pos purchase 
        if match1:
            location,currency,amount,date_time_str,card_type,card_no = match1.groups()
    
            return {
                "bank": bank,
                "account": card_no,
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow":  "expense",
                "transactionType": (card_type +" purchase"),
                "date_time":  date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # ATM Withdrawal
        elif match2:
            location,currency, amount, date_time_str, card_no  = match2.groups()

            return {
                "bank": bank,
                "account": card_no , 
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "atm_withdrawal",
                "date_time": date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # ATM Deposit
        elif match3:
            time_str,currency, amount,location,account  = match3.groups()

            return {
                "bank": bank,
                "account": account,
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "atm_deposit",
                "date_time": time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # Credit card Purchase internet and pos purchase
        elif match4:
            location,currency,amount,date_time_str,card_type,card_no,available_balance  = match4.groups()

            return {
                "bank": bank,
                "account": card_no,
                "location": location.strip(),
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow":  "expense",
                "transactionType": (card_type +" purchase"),
                "date_time":  date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
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
                "added_timestamp": added_timestamp
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
            "added_timestamp": added_timestamp,
            # Optionally include the error message for debugging
            "error": str(e)
        }

