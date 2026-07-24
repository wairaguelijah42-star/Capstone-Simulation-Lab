import sqlite3
import bcrypt

db = sqlite3.connect("database.db")

users = db.execute(
    "SELECT user_id, password FROM users"
).fetchall()

for user_id, password in users:

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    db.execute(
        "UPDATE users SET password=? WHERE user_id=?",
        (hashed, user_id)
    )

db.commit()

print("Passwords hashed successfully.")
