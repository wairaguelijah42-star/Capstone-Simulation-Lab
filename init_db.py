import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("database.db")

# Create a cursor
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY,
    owner_user_id INTEGER,
    balance REAL,
    account_type TEXT,
    FOREIGN KEY(owner_user_id) REFERENCES users(user_id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_account INTEGER,
    to_account INTEGER,
    amount REAL,
    transaction_date TEXT,
    FOREIGN KEY(from_account) REFERENCES accounts(account_id),
    FOREIGN KEY(to_account) REFERENCES accounts(account_id)
)
""")
cursor.executemany("""
INSERT INTO users (user_id, username, password, role)
VALUES (?, ?, ?, ?)
""", [
    (1, "admin", "Admin@123", "admin"),
    (42, "jkamau", "Passw0rd!", "user"),
    (43, "amuthoni", "Passw0rd!", "user"),
    (44, "partner_svc", "Fintech2024", "service")
])
cursor.executemany("""
INSERT INTO accounts (account_id, owner_user_id, balance, account_type)
VALUES (?, ?, ?, ?)
""", [
    (1042, 42, 184500.00, "Savings"),
    (1043, 43, 62300.00, "Savings"),
    (1099, 1, 0.00, "Internal")
])
cursor.executemany("""
INSERT INTO transactions
(from_account, to_account, amount, transaction_date)
VALUES (?, ?, ?, ?)
""", [
    (1042, 1043, 5000.00, "2026-07-18 09:30:00"),
    (1043, 1042, 2500.00, "2026-07-18 10:15:00"),
    (1042, 1099, 1500.00, "2026-07-18 11:00:00")
])
conn.commit()
conn.close()

print("Database created and seeded successfully.")
