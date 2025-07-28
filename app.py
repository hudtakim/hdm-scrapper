from flask import Flask, request, jsonify, send_file, after_this_request
from scraper import scrape_reviews
from flask_cors import CORS
from query import create_user, update_quota, delete_expired_users, get_user, get_users, login_user
from datetime import datetime, timedelta, date
import pandas as pd
import json
import os
import uuid
import threading
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

CORS(app) 

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

def get_future_date(days=30) -> str:
    future_date = datetime.now().date() + timedelta(days=days)
    return future_date.isoformat()  # hasil: '2025-08-27'

@app.route('/api/update_token', methods=['GET'])
def update_token():
    new_token = request.args.get("newToken")
    if not new_token:
        return jsonify({"error": "new_token is required"}), 400
    set_stored_token(new_token)
    return jsonify({"message": "Token updated successfully", "new_token": new_token})

@app.route('/api/reviews', methods=['GET'])
def api_reviews():
    user_token = request.args.get("requestToken")
    user_email = request.args.get("userEmail")
    app_id = request.args.get("app_id")

    try:
        count = int(request.args.get("count", 10))
    except ValueError:
        return jsonify({"error": "Invalid count value"}), 400

    save_csv = request.args.get("save_csv", "false").lower() == "true"
    save_excel = request.args.get("save_excel", "false").lower() == "true"

    # Cek token
    valid_token = get_stored_token()
    if not user_token or user_token != valid_token:
        return jsonify({"error": "Invalid or missing requestToken"}), 403

    # Cek app_id
    if not app_id:
        return jsonify({"error": "Missing app_id parameter"}), 400

    # Proses scraping berdasarkan email user (jika ada)
    if user_email != 'empty':
        print('Masukkan');
        user_response = get_user(email=user_email)
        if user_response.data:
            user_quota = user_response.data.get("quota", 0)
            if user_quota > 0:
                new_quota = user_quota - 1
                update_quota(email=user_email, new_quota=new_quota)
                reviews = scrape_reviews(app_id, count=count)
            else:
                return jsonify({"error": "Scrape quota empty, please top up quota first"}), 400
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        # Jika tidak pakai email, batas maksimal adalah 100
        count = min(count, 100)
        reviews = scrape_reviews(app_id, count=count)

    df = pd.DataFrame(reviews)

    # Simpan sebagai file jika diminta
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
            threading.Timer(2.0, delayed_remove).start()
            return response

        return send_file(filename, as_attachment=True)

    # Jika tidak minta file, kembalikan data dalam bentuk JSON
    return jsonify(df.to_dict(orient="records"))
#query --- start

@app.route('/api/reviews', methods=['POST'])
def api_create_user():
    try:
        data = request.get_json()

        # Validasi input
        required_fields = ["email", "password"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Hash the password
        hashed_password = generate_password_hash(data["password"])

        response = create_user(
            email=data["email"],
            password=hashed_password,
            expired_date=get_future_date(120),
            quota=5,
            is_trial=True
        )

        return jsonify({"message": "User created", "data": response.data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/reviews/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()

        # Validasi input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400

        email = data['email']
        password = data['password']

        # Ambil user dari Supabase
        response = login_user(email=email)

        if not response.data:
            return jsonify({"error": "User not found"}), 404


        user = response.data

        # Cek password
        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Jika login berhasil, bisa generate token atau hanya kirim info user
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "quota": user["quota"],
                "expired_date": user["expired_date"],
                "is_trial": user["is_trial"]
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#query --- end

if __name__ == '__main__':
    app.run(debug=True)
