import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['document']
    filename = f.filename

    f.save(os.path.join('/var/www/uploads/', filename))

    return {"status": "saved"}
