import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


class LicenseManager:
    def __init__(self, license_file_path=None, public_key_path=None):
        self.license_file_path = license_file_path or os.path.expanduser("~/.codexpro.license")
        self.public_key_path = public_key_path or os.path.join(
            os.path.dirname(__file__), "public_key.pem"
        )
        self.license_data = None
        self.valid = False

        if os.path.exists(self.license_file_path):
            with open(self.license_file_path, "r") as f:
                license_str = f.read().strip()
                self.valid = self._validate_license(license_str)
        else:
            print(f"[CodexPro] License file not found at {self.license_file_path}")

    def _validate_license(self, license_str):
        try:
            payload_b64, signature_b64 = license_str.split(".")
            payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            self.license_data = json.loads(payload_json)

            # Load public key
            with open(self.public_key_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())

            # Verify signature
            signature = base64.urlsafe_b64decode(signature_b64.encode())
            public_key.verify(
                signature,
                payload_b64.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            # Check expiry
            expiry = datetime.strptime(self.license_data.get("expiry", "1970-01-01"), "%Y-%m-%d")
            if expiry < datetime.utcnow():
                print("[CodexPro] License has expired.")
                return False

            return True
        except Exception as e:
            print(f"[CodexPro] License validation error: {e}")
            return False

    def is_valid(self):
        return self.valid

    def get_plan(self):
        return self.license_data.get("plan") if self.valid else None

    def is_enterprise(self):
        return self.get_plan() == "enterprise"

    def get_summary(self):
        if not self.valid:
            return "❌ Invalid or expired license"
        return (
            f"✅ License Info:\n"
            f"  Name: {self.license_data.get('name')}\n"
            f"  Email: {self.license_data.get('email')}\n"
            f"  Plan: {self.license_data.get('plan')}\n"
            f"  Expiry: {self.license_data.get('expiry')}"
        )
