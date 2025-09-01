import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def sign_license(data: dict, private_key_path=None):
    if private_key_path is None:
        private_key_path = os.path.join(os.path.dirname(__file__), "private_key.pem")

    payload_json = json.dumps(data, separators=(',', ':'), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()

    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    signature = private_key.sign(
        payload_b64.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    signature_b64 = base64.urlsafe_b64encode(signature).decode()
    return f"{payload_b64}.{signature_b64}"


def main():
    print("🔐 CodexPro RSA License Generator\n")

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

    license_key = sign_license(license_data)

    # Path for saving the license file
    license_file = os.path.expanduser("~/.codexpro.license")

    # Write the license key
    with open(license_file, "w") as f:
        f.write(license_key)

    print("\n✅ License generated and saved successfully!")
    print(f"📂 Saved to: {license_file}\n")
    print("🔑 License Key:\n")
    print(license_key)


if __name__ == "__main__":
    main()
