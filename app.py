from flask import Flask, request, jsonify
import sms_processor

app = Flask(__name__)


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})


@app.route('/process_sms', methods=['POST'])
def process_sms():
    sms_message = request.json.get('message')
    bank = request.json.get('bank')
    date_time = request.json.get('dateTime')
    sheet_name = request.json.get('sheetName')

    if len(sms_message) <= 1:
        return jsonify({"status": "error", "message": "SMS message is missing"})

    if len(bank) <= 1:
        return jsonify({"status": "error", "message": "Bank name is missing"})

    if len(date_time) <= 1:
        return jsonify({"status": "error", "message": "Date/time is missing"})

    if len(sheet_name) <= 1:
        return jsonify({"status": "error", "message": "Sheet name is missing"})

    # Process the SMS if all conditions are met
    result = sms_processor.process_sms(
        sms_message, bank, date_time, sheet_name)
    return jsonify(result)


@app.route('/process_sms_bulk', methods=['POST'])
def process_sms_bulk():
    sms_message_array = request.json.get('sms_message_array')
    bank = request.json.get('bank')

    if len(sms_message_array) < 1:
        return jsonify({"status": "error", "message": "SMS message is missing"})

    if len(bank) <= 1:
        return jsonify({"status": "error", "message": "Bank name is missing"})

    # Process the SMS if all conditions are met
    result = sms_processor.process_sms_bulk(
        sms_message_array, bank)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
