import json
import base64
import hmac
import hashlib
from datetime import datetime


# 🔒 Your private key (keep this secret)
SECRET_KEY = "your-secret-key"


def generate_license(data: dict, secret: str):
    payload_json = json.dumps(data, separators=(',', ':'), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    signature = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def main():
    print("🔐 CodexPro License Generator\n")

    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip()

    while True:
        plan = input("Enter plan (community / enterprise): ").strip().lower()
        if plan in ("community", "enterprise"):
            break
        print("❌ Invalid plan. Must be 'community' or 'enterprise'.")

    while True:
        expiry = input("Enter expiry date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(expiry, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Invalid date format. Try again.")

    license_data = {
        "name": name,
        "email": email,
        "plan": plan,
        "expiry": expiry
    }

    license_key = generate_license(license_data, SECRET_KEY)

    print("\n✅ Generated License Key:\n")
    print(license_key)


if __name__ == "__main__":
    main()
