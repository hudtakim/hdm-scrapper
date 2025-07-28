from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# CREATE USER
def create_user(email, password, expired_date, quota, is_trial):
    data = {
        "email": email,
        "password": password,
        "expired_date": expired_date,
        "quota": quota,
        "is_trial": is_trial
    }
    return supabase.table("users").insert(data).execute()

# UPDATE QUOTA
def update_quota(email, new_quota):
    return supabase.table("users").update({"quota": new_quota}).eq("email", email).execute()

# DELETE USER YANG SUDAH EXPIRED
def delete_expired_users():
    today = str(date.today())
    return supabase.table("users").delete().lt("expired_date", today).execute()

# GET USER BY EMAIL
def get_user(email):
    return supabase.table("users").select("*").eq("email", email).single().execute()

# GET USERS WITH LIMIT AND OFFSET
def get_users(limit=1000, offset=0):
    return supabase.table("users").select("*").range(offset, offset + limit - 1).execute()
