from flask import Flask, request, jsonify, send_file, after_this_request
from scraper import scrape_reviews
import pandas as pd
import json
import os
import uuid
import threading

app = Flask(__name__)

TOKEN_FILE = "token_store.json"

def get_stored_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data.get("token")
    return None

def set_stored_token(new_token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": new_token}, f)

@app.route('/api/update_token', methods=['POST'])
def update_token():
    data = request.get_json()
    new_token = data.get("new_token")
    if not new_token:
        return jsonify({"error": "new_token is required"}), 400
    set_stored_token(new_token)
    return jsonify({"message": "Token updated successfully", "new_token": new_token})

@app.route('/api/reviews', methods=['GET'])
def api_reviews():
    user_token = request.args.get("requestToken")
    valid_token = get_stored_token()
    if user_token != valid_token:
        return jsonify({"error": "Invalid or missing requestToken"}), 403

    app_id = request.args.get("app_id")

    try:
        count = int(request.args.get("count", 10))
    except ValueError:
        return jsonify({"error": "Invalid count value"}), 400

    save_csv = request.args.get("save_csv", "false").lower() == "true"
    save_excel = request.args.get("save_excel", "false").lower() == "true"

    if not app_id:
        return jsonify({"error": "Missing app_id parameter"}), 400

    reviews = scrape_reviews(app_id, count = count)
    df = pd.DataFrame(reviews)

    if save_csv or save_excel:
        extension = "csv" if save_csv else "xlsx"
        filename = f"reviews_{uuid.uuid4().hex}.{extension}"

        if extension == "csv":
            df.to_csv(filename, index=False)
        else:
            df.to_excel(filename, index=False)

        @after_this_request
        def cleanup(response):
            def delayed_remove():
                try:
                    os.remove(filename)
                except Exception as e:
                    print(f"Failed to delete file {filename}: {e}")

            threading.Timer(2.0, delayed_remove).start()  # Delay 2 detik
            return response

        return send_file(filename, as_attachment=True)

    return df.to_dict(orient="records")

if __name__ == '__main__':
    app.run(debug=True)
