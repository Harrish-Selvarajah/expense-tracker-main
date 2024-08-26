from banks import hnb_sms_processor
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe


def process_sms(sms_message, bank, date_time, sheet_name):
    try:
        # Define the scope
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "serious-form-432917-a0-2c4f7e9f87a2.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).sheet1
        if bank == 'hnb':
            extracted_data = []

            # Load the existing data to find the next available row
            existing_data = get_as_dataframe(
                sheet, evaluate_formulas=True, skipinitialspace=False)
            next_row = len(existing_data) + 2

            details = hnb_sms_processor.process_common_pattern(
                sms_message, date_time, bank)

            # Append the details to the extracted_data list
            extracted_data.append(details)

            df = pd.DataFrame(extracted_data)

            # Append the DataFrame to the next available row
            set_with_dataframe(sheet, df, row=next_row,
                               include_index=False, include_column_header=False, resize=False)

            # Export to Excel
            # df.to_excel("{bank}_transaction_details.xlsx", index=False)
            print("Transaction details exported to 'transaction_details.xlsx'")

            return {"status": "success", "message": "SMS processed and added to Google Sheet"}
        else:
            return {"status": "error", "message": "Bank not supported - {bank}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def process_sms_bulk(sms_message, bank):
    if bank == 'hnb':
        extracted_data = []

        for sms in sms_message:
            details = hnb_sms_processor.process_common_pattern(
                sms, "", bank)
            extracted_data.append(details)

        df = pd.DataFrame(extracted_data)

        # Export to Excel
        file_name = f"{bank}_transaction_details.xlsx"
        df.to_excel(file_name, index=False)
        print("Transaction details exported to 'file_name'")

        return {"status": "success", "message": "SMS processed and added to Google Sheet"}
    else:
        return {"status": "error", "message": "Bank not supported - {bank}"}
