from typing import Optional, Dict
from .db import supabase, exec_data, USERS_TABLE

PublicUser = Dict

def row_to_public_user(row: dict) -> Optional[PublicUser]:
    if not row:
        return None
    return {
        "userId": row.get("userId"),
        "email": row.get("email"),
        "username": row.get("username"),
        "mobile": row.get("mobile"),
    }

def get_user_by_email(email: str) -> Optional[dict]:
    try:
        resp = supabase.table(USERS_TABLE).select("*").eq("email", email).limit(1).execute()
        data = exec_data(resp)
        return data[0] if data else None
    except Exception:
        return None

def get_user_by_username(username: str) -> Optional[dict]:
    try:
        resp = supabase.table(USERS_TABLE).select("*").eq("username", username).limit(1).execute()
        data = exec_data(resp)
        return data[0] if data else None
    except Exception:
        return None

def get_user_by_id(user_id: str) -> Optional[dict]:
    try:
        resp = supabase.table(USERS_TABLE).select("*").eq("userId", user_id).limit(1).execute()
        data = exec_data(resp)
        return data[0] if data else None
    except Exception:
        return None

def create_user(email: str, password: str, username: str | None = None, mobile: str | None = None) -> Optional[dict]:
    payload = {
        "email": email,
        "password": password,  # TODO: hash in production
        "username": username,
        "mobile": mobile,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    resp = supabase.table(USERS_TABLE).insert(payload).execute()
    data = exec_data(resp)
    return data[0] if data else None

def update_user_fields_by_id(user_id: str, fields: dict) -> Optional[dict]:
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return None
    resp = supabase.table(USERS_TABLE).update(fields).eq("userId", user_id).execute()
    data = exec_data(resp)
    return data[0] if data else None
