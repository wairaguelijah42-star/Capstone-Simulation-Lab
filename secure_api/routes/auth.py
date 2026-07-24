from flask import Flask, request

app = Flask(__name__)

class DummyDB:
    def execute(self, query):
        print(query)
        return None

db = DummyDB()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    query = (
        "SELECT * FROM users WHERE username = '" + username + "' "
        "AND password = '" + password + "'"
    )

    result = db.execute(query)

    return {"status": "ok"}
