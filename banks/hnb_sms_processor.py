import re
from datetime import datetime
from zoneinfo import ZoneInfo


def process_common_pattern(sms_message: str, date_time: str, bank: str):
    try:
        # Set the timezone to Sri Lanka
        sri_lanka_tz = ZoneInfo('Asia/Colombo')
        added_timestamp = datetime.now(
            sri_lanka_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Patterns for different HNB SMS formats
        # Debit card internet txn
        internet_txn_pattern = r"HNB SMS ALERT:(\w+), Account:(\S+),Location:(.+?),Amount\(Approx\.\):(\d+\.\d+)\s(\w+),.*Date:(\d{2}\.\d{2}\.\d{2}),Time:(\d{2}:\d{2})"
        # Debit card POS txn
        pos_txn_pattern = r"HNB SMS ALERT:\s*(\w+),\s*Debit account:(\S+),\s*Location:(.+?),\s*Amount\(Approx\.\):(\d+\.\d+)\s(\w+),.*Date:(\d{2}\.\d{2}\.\d{2}),Time:(\d{2}:\d{2})"
        # ATM Withdrawal
        atm_withdrawal_pattern = r"HNB ATM Withdrawal e-Receipt.*?Amt\(Approx\.\):\s*([\d,.]+)\s*(\w+).*?A/C:\s*(\S+).*?Location:\s*(.+?),.*?Date:\s*(\d{2}\.\d{2}\.\d{2})\s*Time:(\d{2}:\d{2}).*?Txn No:\s*(\d+)"
        # Credited/debited txn
        credited_debited_pattern = r"(\w+)\s([\d,]+\.\d{2})\s(credited|debited)\s+to\s+Ac No:(\S+)\s+on\s+(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})\s+Reason:(.+?)\s+Bal:"
        # Credit card txn
        credit_card_purchase_pattern = r"HNB SMS Alert VC : \*\*\d{4} :(?P<description>.+) \S+ (?P<location>.+)\s*(?:\(Apprx\))? (?P<currency>[A-Z]{3}) (?P<amount>[,\d]+(?:\.\d+)?) \((?P<date>\d{2}-\w{3}-\d{4}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<meridian>[AP]M)\) Av\.Bal : [A-Z]{3} [\d,.]+ Hot Line: \d+"

        # Attempt to match each pattern
        match1 = re.search(internet_txn_pattern, sms_message)
        match2 = re.search(pos_txn_pattern, sms_message)
        match3 = re.search(atm_withdrawal_pattern, sms_message, re.DOTALL)
        match4 = re.search(credited_debited_pattern, sms_message)
        match5 = re.search(credit_card_purchase_pattern, sms_message)

        # Debit card internet txn
        if match1:
            alert_type, account, location, amount, currency, date, time = match1.groups()
            date_time_str = f"{date} {time}"

            return {
                "bank": bank,
                "account": account,
                "location": location,
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "card_internet",
                "date_time": date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp

            }
        # Debit card POS txn
        elif match2:
            alert_type, account, location, amount, currency, date, time = match2.groups()
            date_time_str = f"{date} {time}"
            return {
                "bank": bank,
                "account": account,
                "location": location,
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "card_pos",
                "date_time": date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # ATM Withdrawal
        elif match3:
            amount, currency, account, location, date, time, txn_no = match3.groups()
            date_time_str = f"{date} {time}"
            return {
                "bank": bank,
                "account": account,
                "location": location,
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "atm_withdrawal",
                "date_time": date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # Credited/debited txn
        elif match4:
            currency, amount, action, account, date, time, reason = match4.groups()
            date_time_str = f"{date} {time}"

            # Further split the "Reason" field into two parts
            reason_parts = reason.split('/', 1)
            reason_main = reason_parts[0].strip() if len(
                reason_parts) > 0 else None
            reason_details = reason_parts[1].strip() if len(
                reason_parts) > 1 else None

            if (reason_main == 'CASH DEP'):
                transaction_type = 'cash_deposit'
            else:
                transaction_type = 'bank_transfer'
            return {
                "bank": bank,
                "account": account,
                "location": reason_details if transaction_type == "cash_deposit" else reason_main,
                "description": reason_main,
                "amount": amount,
                "currency": currency,
                "flow": "income" if action == "credited" else "expense",
                "transactionType": transaction_type,
                "date_time": date_time_str,
                "sms_message": sms_message,
                "added_timestamp": added_timestamp
            }
        # Credit card txn
        elif match5:
            alert_type, card_number, location, currency, amount, date_time_str = match5.groups()
            return {
                "bank": bank,
                "account": card_number,
                "location": location,
                "description": "",
                "amount": amount,
                "currency": currency,
                "flow": "expense",
                "transactionType": "credit_card",
                "date_time": date_time_str,
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
