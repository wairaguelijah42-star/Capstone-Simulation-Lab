import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "False") == "True"

SECRET_KEY = os.getenv("SECRET_KEY")

STRIPE_LIKE_GATEWAY_KEY = os.getenv("STRIPE_LIKE_GATEWAY_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
