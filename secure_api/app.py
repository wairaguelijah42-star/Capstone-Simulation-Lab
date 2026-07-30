from flask import Flask, request,jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_talisman import Talisman
from flask_limiter.util import get_remote_address
import bcrypt
import sqlite3
import jwt
import os
from dotenv import load_dotenv
import re
import os

from functools import wraps

def verify_jwt():

    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload

    except Exception:
        return None
def admin_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        payload = verify_jwt()

        if not payload:
            return jsonify({
                "message": "Authentication required"
            }),401

        if payload["role"] != "admin":
            return jsonify({
                "message": "Access denied"
            }),403

        return f(*args, **kwargs)

    return decorated
app = Flask(__name__)
app.config["TESTING"] = True
if not app.config.get("TESTING"):
    Talisman(app, force_https=True)
else:
    Talisman(app, force_https=False)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["https://localhost:3000"]
        }
    }
)
@app.errorhandler(Exception)
def handle_exception(error):

    print("SERVER ERROR:", error)

    return jsonify({
        "message": "An internal server error occurred."
    }), 500
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ACTIVE_API_KEY = os.getenv("ACTIVE_API_KEY")
OLD_API_KEY = os.getenv("OLD_API_KEY")

print("SECRET:", SECRET_KEY)
print("ACTIVE API:", ACTIVE_API_KEY)
print("OLD API:", OLD_API_KEY)
print(">>> LOADED UPDATED APP.PY <<<")

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
def verify_api_key():

    api_key = request.headers.get("X-API-Key")

    if api_key not in [ACTIVE_API_KEY, OLD_API_KEY]:

        return False

    return True
def valid_username(username):
    return re.fullmatch(r"[A-Za-z0-9_]{3,20}", username) is not None


def valid_amount(amount):
    try:
        amount = float(amount)
        return amount > 0
    except:
        return False


def valid_account(account):
    try:
        return int(account) > 0
    except:
        return False


@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    username = request.form["username"]
    password = request.form["password"]

    if not valid_username(username):
        return jsonify({
            "message": "Invalid username format"
        }), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must be at least 8 characters"
        }), 400

    print(f"Login attempt: {username}")

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    print("Username received:", repr(username))
    print("Password received:", repr(password))
    print("User found:", user is not None)

    if user:
        print("DB username:", user["username"])
        print("DB hash:", repr(user["password"]))
        print(
            "Password matches:",
            bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8")
        )
    )
    if not user:
        return jsonify({
            "status": "failed",
            "message": "Invalid username or password"
        }), 401

    if not bcrypt.checkpw(
        password.encode(),
        user["password"].encode()
    ):
        return jsonify({
            "status": "failed",
            "message": "Invalid username or password"
        }), 401

    print("Username received:", repr(username))
    print("User found:", user is not None)
    print("Password matches:",
          bcrypt.checkpw(password.encode(), user["password"].encode()))
    payload = {
        "user_id": user["user_id"],
        "role": user["role"]
    }
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user_id": user["user_id"],
        "role": user["role"]
    })
@app.route("/admin/users", methods=["GET"])
@admin_required
def admin_users():

    db = get_db()

    users = db.execute(
        "SELECT user_id, username, role FROM users"
    ).fetchall()

    results = []

    for user in users:
        results.append({
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"]
       })
    return jsonify(results)

@app.route("/accounts", methods=["GET"])
def accounts():

    account_id = request.args.get("account_id")

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE account_id=?",
        (account_id,)
    ).fetchone()

    if account:
        return jsonify(dict(account))

    return jsonify({
        "message": "Account not found"
    }), 404
    return jsonify(results)
@app.route("/transactions", methods=["GET"])
def transactions():

    account_id = request.args.get("account_id")

    db = get_db()

    rows = db.execute(
        """
        SELECT*
        FROM transactions
        WHERE from_account =?
            OR to_account = ?
        """,
        (account_id,account_id)
    ).fetchall()

    results = []

    for row in rows:
        results.append(dict(row))

    return jsonify(results)
@app.route("/profile/update", methods=["POST"])
def update_profile():

    data = request.get_json()

    db = get_db()

    db.execute(
        """
        UPDATE users
        SET username=?,
            role=?
        WHERE user_id=?
        """,
        (
            data["username"],
            data["role"],
            data["user_id"]
        )
    )

    db.commit()

    return jsonify({
        "message": "Profile updated"
    })
@app.route("/transfer", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("10 per minute")
def transfer():
    
    if not verify_api_key():
        return jsonify({
            "message": "Invalid API Key"
        }), 401

    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    required = [
        "from_account",
        "to_account",
        "amount"
    ]

    for field in required:
        if field not in data:
            return jsonify({
                "message": f"Missing field: {field}"
            }), 400

    from_account = int(data["from_account"])
    to_account = int(data["to_account"])
    amount = float(data["amount"])

    if not valid_account(from_account):
        return jsonify({
            "message": "Invalid source account"
        }), 400

    if not valid_account(to_account):
        return jsonify({
            "message": "Invalid destination account"
        }), 400

    if not valid_amount(amount):
        return jsonify({
            "message": "Amount must be greater than zero"
        }), 400

    if from_account == to_account:
        return jsonify({
            "message": "Source and destination accounts cannot be the same"
        }), 400

    db = get_db()

    db.execute(
        """
        UPDATE accounts
        SET balance = balance + ?
        WHERE account_id = ?
        """,
        (amount, to_account)
    )

    db.commit()

    return jsonify({
        "message":"Transfer completed"
    })
@app.route("/owasp-mapping", methods=["GET"])
def owasp_mapping():

    return jsonify([
        {
            "vulnerability": "SQL Injection",
            "endpoint": "/login",
            "owasp": "API8:2023 - Security Misconfiguration"
        },
        {
            "vulnerability": "Broken Authentication",
            "endpoint": "/login",
            "owasp": "API2:2023 - Broken Authentication"
        },
        {
            "vulnerability": "Broken Object Level Authorization (IDOR)",
            "endpoint": "/accounts, /transactions",
            "owasp": "API1:2023 - Broken Object Level Authorization"
        },
        {
            "vulnerability": "Parameter Tampering",
            "endpoint": "/profile/update",
            "owasp": "API3:2023 - Broken Object Property Level Authorization"
        },
        {
            "vulnerability": "Excessive Data Exposure",
            "endpoint": "/admin/users",
            "owasp": "API3:2023 - Broken Object Property Level Authorization"
        },
        {
            "vulnerability": "Business Logic Abuse",
            "endpoint": "/transfer",
            "owasp": "API6:2023 - Unrestricted Access to Sensitive Business Flows"
        },
        {
            "vulnerability": "Improper HTTP Methods",
            "endpoint": "/transfer",
            "owasp": "API8:2023 - Security Misconfiguration"
        }
    ])
if __name__ == "__main__":
    print(app.url_map)
    app.run(
        host="0.0.0.0",  # nosec B104
        port=5000,
        ssl_context=("cert.pem", "key.pem"),
        debug=False
    )
