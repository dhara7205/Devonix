import os
import json
import base64
import hmac
import hashlib
from datetime import datetime


LICENSE_FILE = os.path.expanduser("~/.codexpro.license")
SECRET_KEY = "your-secret-key"  # 🔒 Only you know this (keep secret, especially before .exe packaging)


class LicenseManager:
    def __init__(self, license_path: str = LICENSE_FILE):
        self.license_path = license_path
        self.raw_key = None
        self.data = None
        self.valid = False

        self._load_and_verify()

    def _load_and_verify(self):
        if not os.path.exists(self.license_path):
            return

        with open(self.license_path, 'r') as f:
            self.raw_key = f.read().strip()

        if '.' not in self.raw_key:
            return

        payload_b64, signature = self.raw_key.split('.', 1)

        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, signature):
            return

        try:
            payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            self.data = json.loads(payload_json)

            # Check expiry
            expiry_date = datetime.strptime(self.data.get("expiry", "1970-01-01"), "%Y-%m-%d")
            self.valid = expiry_date >= datetime.utcnow()
        except Exception:
            self.valid = False

    def is_valid(self):
        return self.valid

    def get_plan(self):
        return self.data.get("plan", "community") if self.valid else None

    def is_enterprise(self):
        return self.get_plan() == "enterprise"

    def get_summary(self):
        if not self.valid:
            return "❌ Invalid or expired license"
        return (
            f"✅ License Info:\n"
            f"  Name: {self.data.get('name')}\n"
            f"  Email: {self.data.get('email')}\n"
            f"  Plan: {self.data.get('plan')}\n"
            f"  Expiry: {self.data.get('expiry')}"
        )
