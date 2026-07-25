# Secrets Management Report

## Objective

The objective of this task was to improve the security of the application by removing hardcoded secrets and replacing them with secure environment variables.

---

## Changes Made

### 1. Removed Hardcoded Secrets

Sensitive values such as:

- SECRET_KEY
- Database credentials
- API keys

were removed from the application source code.

---

### 2. Created Environment Variables

A `.env` file was created to securely store:

- SECRET_KEY
- ACTIVE_API_KEY
- OLD_API_KEY
- Database configuration

---

### 3. Updated the Application

The application now loads configuration using the `python-dotenv` package.

Example:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
```

---

### 4. Protected Sensitive Files

The following entries were added to `.gitignore`:

```
.env
*.pem
database.db
__pycache__/
logs/
venv/
```

This prevents sensitive files from being committed to GitHub.

---

### 5. Rotated Exposed Secrets

Previously exposed API keys were replaced with new values stored in `.env`.

Old credentials should be considered compromised and no longer used.

---

## Result

The application now:

- stores secrets securely
- keeps credentials outside source code
- prevents accidental exposure through Git
- follows secure development best practices
