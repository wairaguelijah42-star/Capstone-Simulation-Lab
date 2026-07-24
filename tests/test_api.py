import sys
import os

sys.path.append(os.path.abspath("secure_api"))

from app import app


client = app.test_client()


def test_owasp_mapping():
    response = client.get("/owasp-mapping")

    assert response.status_code == 200


def test_accounts_not_found():
    response = client.get("/accounts?account_id=999999")

    assert response.status_code == 404
