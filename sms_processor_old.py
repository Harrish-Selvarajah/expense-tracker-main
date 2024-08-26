import re

# Google Sheets setup (You'll need to handle this in your main app.py)
# ... (Assume 'sheet' is available from app.py)

# Patterns to match both HNB and Sampath Bank SMS formats
pattern_hnb = r"(\w+ SMS ALERT):(\w+), Account:(\d+).*Location:([^,]+),.*Amount\(Approx.\):([\d.]+) (\w+),Av\.Bal:([\d.]+) LKR,Date:(\d+\.\d+\.\d+),Time:(\d+:\d+),.*Reason:(.*) Bal"
pattern_sampath = r"LKR ([\d,.]+) (\w+) from AC \*\*(\d+) for eCom (\w+) (\d+)\n- For Inq Call 0112 303050, Sampath Bank"
pattern_sampath_credit = r"Cr Crd no\.\.(\d+) (\w+) Pmt LKR ([\d,.]+) at (\w+)  ;Avl Bal LKR ([\d,.]+) Enq Call 0112300604-Sampath Bank (\d+)-Aug"
pattern_sampath_received = r"Cr Crd no\.\.(\d+) Recvd Pmt LKR ([\d,.]+)  ;Avl Bal LKR ([\d,.]+) Enq Call 0112300604-Sampath Bank (\d+)-Aug"
pattern_transaction = r"A Transaction for LKR ([\d,.]+) has been (\w+) ed to Ac No:(\d+) on (\d+)\/(\d+)\/(\d+) \d+:\d+:\d+ \..*Remarks :(.*)Bal: LKR ([\d,.]+)"

# Function to categorize transactions


def categorize_transaction(bank, location, reason, merchant, description):
    location = location.lower() if location else ""
    reason = reason.lower() if reason else ""
    merchant = merchant.lower() if merchant else ""
    description = description.lower() if description else ""

    # Handle transaction reversals for both banks
    if "transaction reversal" in reason.lower():
        return "Transportation", "Uber" if "uber" in location.lower() else "", "Transaction Reversal"

    # Prioritize "credited" messages as Transfers (unless it's a reversal)
    if "credited" in reason.lower() and "transaction reversal" not in reason.lower():
        # Include reason in Note for clarity
        return "Transfer", "Incoming Transfer", reason

    if bank == "HNB":
        if "uber" in location or "pickme" in location:
            subcategory = location.split(",")[0].replace(" * PENDING", "")
            return "Transportation", subcategory, ""
        elif "billpmt" in reason or "dialog mobile" in reason:
            return "Bill Payment", "Dialog Mobile", reason
        elif "ceft" in reason or "fund transfer" in reason or "justpay" in reason or "transfer" in reason or "t" in reason:
            return "Transfer", "Incoming Transfer" if "credited" in reason else "Outgoing Transfer", reason
        elif "adidas" in location or "globe logistics" in location or "pvr inox" in location or "aroha hospitality" in location or "mc donalds" in location or "kaffa coffee" in location or "aviserv airport" in location or "daraz.lk" in location or "apple.com/bill" in location or "edrops" in location or "koko" in location:
            return "Shopping", location.split(",")[0], reason
        elif "cash dep" in reason:
            return "Deposit", "Cash Deposit", reason
        elif "ecom rev" in reason:
            return "E-commerce", "Refund", reason
        elif "fx markup" in reason:
            return "Adjustment", "FX Markup", reason
        elif "finacle alert charges" in reason:
            return "Fees & Charges", "Finacle Alert Charges", reason
        elif "mb:" in reason:
            return "Miscellaneous", reason[3:], reason  # Remove "MB:" prefix
        else:
            return "Uncategorized", "", reason

    elif bank == "Sampath Bank":
        if "uber" in merchant:
            return "Transportation", "Uber", description
        elif "uber eats" in merchant:
            return "Food & Dining", "Uber Eats", description
        elif "pickme" in merchant:
            return "Transportation", "PickMe", description
        elif "koko" in merchant:
            return "Shopping", "KOKO", description
        elif "prime video" in merchant:
            return "Entertainment", "Prime Video", description
        elif "dialog axiata plc" in description:
            return "Bill Payment", "Dialog", description
        elif "ecom/rev" in description:
            return "E-commerce", "Refund", description
        else:
            return "Uncategorized", "", description

    else:
        # Handle other banks or unknown formats if needed
        return "Uncategorized", "", reason


# INR to LKR exchange rate
exchange_rate = 4.5


def process_sms(sms_message):
    # Process HNB SMS
    match_hnb = re.match(pattern_hnb, sms_message)
    print(match_hnb)
    match_transaction = re.match(pattern_transaction, sms_message)

    # Process Sampath Bank SMS
    match_sampath = re.match(pattern_sampath, sms_message)
    match_sampath_credit = re.match(pattern_sampath_credit, sms_message)
    match_sampath_received = re.match(pattern_sampath_received, sms_message)

    if match_hnb:
        bank, transaction_type, account, location, amount, currency, available_balance, date, time, reason = match_hnb.groups()
        category, subcategory, note = categorize_transaction(
            bank, location, reason, None, None)
        amount_lkr = float(amount) if currency == "LKR" else float(
            amount) * exchange_rate
        date_time = f"{date.replace('.', '/')} {time}"
        income_expense = "Expense" if transaction_type in [
            "PURCHASE", "INTERNET"] else "Income"
        description = reason

    elif match_transaction:
        amount, transaction_type, account, date_day, date_month, date_year, remarks, available_balance = match_transaction.groups()
        category, subcategory, note = categorize_transaction(
            "HNB", None, remarks, None, None)
        amount_lkr = float(amount.replace(",", ""))
        date_time = f"{date_year}/{date_month}/{date_day} 00:00:00"
        bank = "HNB"
        income_expense = "Expense" if transaction_type == "debit" else "Income"
        description = remarks

    elif match_sampath:
        amount, transaction_type, account, merchant, date = match_sampath.groups()
        category, subcategory, note = categorize_transaction(
            "Sampath Bank", None, None, merchant, None)
        amount_lkr = float(amount.replace(",", ""))
        # Assuming year 2023 based on provided data
        date_time = f"2023/08/{date} 00:00:00"
        bank = "Sampath Bank"
        income_expense = "Expense" if transaction_type == "debited" else "Income"
        description = f"eCom {merchant}"

    elif match_sampath_credit:
        card_no, transaction_type, amount, merchant, available_balance, date = match_sampath_credit.groups()
        category, subcategory, note = categorize_transaction(
            "Sampath Bank", merchant, None, None, None)
        amount_lkr = float(amount.replace(",", ""))
        # Assuming year 2023 based on provided data
        date_time = f"2023/08/{date} 00:00:00"
        bank = "Sampath Bank"
        income_expense = "Expense" if transaction_type == "Card" else "Income"
        description = f"Card Payment at {merchant}"

    elif match_sampath_received:
        card_no, amount, available_balance, date = match_sampath_received.groups()
        category, subcategory, note = categorize_transaction(
            "Sampath Bank", None, "Received Payment", None, None)
        amount_lkr = float(amount.replace(",", ""))
        date_time = f"2023/08/{date} 00:00:00"
        bank = "Sampath Bank"
        income_expense = "Income"
        description = "Received Payment"

    else:
        return {"status": "error", "message": "Unmatched SMS format"}

    if any([match_hnb, match_transaction, match_sampath, match_sampath_credit, match_sampath_received]):
        return {"status": "success", "data": [date_time, bank, account, category, subcategory, note, amount_lkr, income_expense, description, ""]}

    #  sms_array = [
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):64.94 INR,Av.Bal:37184.88 LKR,Date:31.07.24,Time:10:12, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):64.72 INR,Av.Bal:36941.12 LKR,Date:31.07.24,Time:10:17, Hot Line:0112462462",
    #         "LKR 244.60 credited to Ac No:09702XXXXX67 on 31/07/24 10:18:38 Reason:ECOM REV/383442/ID:113007 Bal:LKR 40,185.72 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "TRANSACTION REVERSAL, Credit account:0970***4667,Location:UBER * PENDING, NL,Amount:64.94 INR,Av.Bal:37185.72 LKR,Date:31.07.24,Time:10:18, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:GLOBE LOGISTICS, IN,Amount(Approx.):935.00 INR,Av.Bal:20891.32 LKR,Date:01.08.24,Time:12:48, Hot Line:0112462462",
    #         "LKR 1,200.00 debited to Ac No:09702XXXXX67 on 01/08/24 14:38:33 Reason:MB BillPmt/Dialog Mobile/0764389437/0764389437 Bal:LKR 22,691.32 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "LKR 30,000.00 credited to Ac No:09702XXXXX67 on 01/08/24 15:38:45 Reason:CEFT-FUND TRANSFER TO HATTON NATIONAL... Bal:LKR 52,691.32 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:ADIDAS GD RETAIL CG RO, IN,Amount(Approx.):7999.00 INR,Av.Bal:19545.27 LKR,Date:01.08.24,Time:16:16, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):57.35 INR,Av.Bal:19329.14 LKR,Date:01.08.24,Time:16:40, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):119.97 INR,Av.Bal:18877.01 LKR,Date:01.08.24,Time:17:09, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:PVR INOX LIMITED, IN,Amount(Approx.):800.00 INR,Av.Bal:15862.03 LKR,Date:01.08.24,Time:17:45, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:AROHA HOSPITALITY, IN,Amount(Approx.):974.00 INR,Av.Bal:12191.29 LKR,Date:01.08.24,Time:18:14, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:MC DONALDS, IN,Amount(Approx.):49.01 INR,Av.Bal:12006.58 LKR,Date:01.08.24,Time:18:26, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:PVR INOX LIMITED, IN,Amount(Approx.):400.00 INR,Av.Bal:10499.09 LKR,Date:01.08.24,Time:18:36, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):90.13 INR,Av.Bal:10159.41 LKR,Date:01.08.24,Time:20:32, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):48.39 INR,Av.Bal:9977.05 LKR,Date:01.08.24,Time:22:23, Hot Line:0112462462",
    #         "LKR 15,030.00 debited to Ac No:09702XXXXX75 on 02/08/24 00:36:33 Reason:MB:harrish bday pizza Bal:LKR 626.27 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER * PENDING, NL,Amount(Approx.):279.90 INR,Av.Bal:8922.18 LKR,Date:02.08.24,Time:02:22, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:KAFFA COFFEE ROASTERS, IN,Amount(Approx.):682.50 INR,Av.Bal:6350.02 LKR,Date:02.08.24,Time:03:14, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:AVISERV AIRPORT SERVIC, IN,Amount(Approx.):500.00 INR,Av.Bal:4466.64 LKR,Date:02.08.24,Time:07:53, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:MC DONALDS, IN,Amount(Approx.):324.00 INR,Av.Bal:3246.21 LKR,Date:02.08.24,Time:08:14, Hot Line:0112462462",
    #         "HNB SMS ALERT: PURCHASE, Debit account:0970***4667,Location:AVISERV AIRPORT SERVIC, IN,Amount(Approx.):300.00 INR,Av.Bal:2116.19 LKR,Date:02.08.24,Time:08:15, Hot Line:0112462462",
    #         "LKR 3,000.00 debited to Ac No:09702XXXXX36 on 02/08/24 12:07:21 Reason:MB:t Bal:LKR 9,764.68 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "LKR 3,000.00 credited to Ac No:09702XXXXX67 on 02/08/24 12:07:21 Reason:t Bal:LKR 8,116.19 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER, LK,Amount(Approx.):4045.63 LKR,Av.Bal:1070.56 LKR,Date:02.08.24,Time:12:07, Hot Line:0112462462",
    #         "HNB SMS ALERT:INTERNET, Account:0970***4667,Location:UBER, LK,Amount(Approx.):400.00 LKR,Av.Bal:670.56 LKR,Date:02.08.24,Time:12:52, Hot Line:0112462462",
    #         "LKR 5,000.00 debited to Ac No:09702XXXXX36 on 02/08/24 18:40:46 Reason:MB:uber Bal:LKR 4,764.68 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462",
    #         "LKR 5,000.00 credited to Ac No:09702XXXXX67 on 02/08/24 18:40:46 Reason:uber Bal:LKR 8,670.56 Protect from scams *DO NOT SHARE ACCOUNT DETAILS /OTP* Hotline 0112462462"
    #     ]
