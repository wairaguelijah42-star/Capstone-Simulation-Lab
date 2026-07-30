from flask import Flask, request,jsonify
import sqlite3
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = "CapstoneSecretKey2026"

app = Flask(__name__)
print(">>> LOADED UPDATED APP.PY <<<")

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    print(f"Login attempt: {username}")

    db = get_db()

    query = (
        "SELECT * FROM users WHERE username = '" + username + "' "
        "AND password = '" + password + "'"
    )
    print(query)
    user = db.execute(query).fetchone()
    print("User:", user)
    if user:
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

    return jsonify({
        "status": "failed",
        "message": "Invalid username or password"
    }), 401
@app.route("/admin/users", methods=["GET"])
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
def transfer():
    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json()

    from_account = int(data["from_account"])
    to_account = int(data["to_account"])
    amount = float(data["amount"])
    

    

    db = get_db()

    db.execute(
        """
        UPDATE accounts
        SET balance = balance - ?
        WHERE account_id = ?
        """,
        (amount, from_account)
    )

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
    app.run(debug=True)
