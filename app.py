from fastapi import FastAPI, Request
import psycopg2

app = FastAPI()

conn = psycopg2.connect(
    dbname="saas",
    user="ebrahimamini",
    password="",
    host="localhost"
)

cur = conn.cursor()


# ======================
# ثبت کاربر
# ======================
@app.post("/register")
async def register(req: Request):
    data = await req.json()

    name = data["name"]
    bale_id = data["bale_id"]

    cur.execute(
        "INSERT INTO users (name, bale_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (name, bale_id)
    )
    conn.commit()

    return {"ok": True}


# ======================
# ثبت پروژه (Google Sheet)
# ======================
@app.post("/add-sheet")
async def add_sheet(req: Request):
    data = await req.json()

    name = data["name"]
    sheet_id = data["sheet_id"]

    cur.execute(
        "INSERT INTO projects (user_name, sheet_id) VALUES (%s, %s)",
        (name, sheet_id)
    )
    conn.commit()

    return {"ok": True}
from fastapi import FastAPI, Request
import psycopg2
import gspread
from google.oauth2.service_account import Credentials
import requests

app = FastAPI()


# ======================
# DB
# ======================
conn = psycopg2.connect(
    dbname="saas",
    user="ebrahimamini",   # همون یوزر مک خودت
    host="localhost"
)

cur = conn.cursor()


# ======================
# GOOGLE SHEETS
# ======================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)


# ======================
# GET USER SHEET
# ======================
def get_sheet(name):
    cur.execute("SELECT sheet_id FROM projects WHERE user_name=%s", (name,))
    row = cur.fetchone()

    if not row:
        return None

    return client.open_by_key(row[0]).sheet1


# ======================
# BALE WEBHOOK
# ======================
@app.post("/bale-webhook")
async def bale_webhook(req: Request):
    data = await req.json()

    # پیام کاربر
    message = data.get("text", "").strip()
    chat_id = data.get("chat_id")

    print("MESSAGE:", message)

    # 1. فرض: پیام = نام کاربر
    sheet = get_sheet(message.lower())

    if not sheet:
        return {
            "ok": False,
            "msg": "user not found"
        }

    # 2. تست اتصال
    sheet.update("A1", "CONNECTED_FROM_BALE")

    return {
        "ok": True,
        "msg": "sheet updated"
    }
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
