import os
import sys
import pyotp
import qrcode
from datetime import datetime # For potential future use, e.g., logging last verified time

# --- Configuration Constants ---
SECRET_FILE = "2fa_secret.txt"
DEFAULT_ACCOUNT_NAME = "myuser@example.com" # Should be dynamic in a real app
ISSUER_NAME = "MySecureApp"
QR_CODE_FILENAME = "qrcode_setup.png"
QR_CODE_NEW_DEVICE_FILENAME = "qrcode_new_device.png"
OTP_VALID_WINDOW = 1 # Allows +/- 1 time step for verification to account for clock drift

def get_or_create_secret():
    """Load the saved secret or create a new one if it doesn't exist."""
    secret = None
    if os.path.exists(SECRET_FILE):
        try:
            with open(SECRET_FILE, "r") as f:
                secret = f.read().strip()
            print("[INFO] Loaded existing secret from file.")
        except IOError as e:
            print(f"[ERROR] Could not read secret file: {e}. Generating new secret.")
            secret = None # Force generation of new secret if read fails
    
    if not secret:
        secret = pyotp.random_base32()
        try:
            with open(SECRET_FILE, "w") as f:
                f.write(secret)
            # Set restrictive permissions (Unix-like systems)
            os.chmod(SECRET_FILE, 0o600) # Only owner can read/write
            print("[INFO] Generated and saved new secret.")
            # Only generate QR code on initial creation
            generate_qr_code(secret, filename=QR_CODE_FILENAME, 
                             name=DEFAULT_ACCOUNT_NAME, issuer=ISSUER_NAME)
        except IOError as e:
            print(f"[CRITICAL ERROR] Could not save secret file: {e}. Secret not persistent!")
            # In a real app, this would be a fatal error, you cannot proceed securely.
            sys.exit(1) # Exit if secret cannot be saved securely
            
    return secret

def generate_qr_code(secret, filename, name, issuer):
    """Generate a QR code from a secret."""
    try:
        totp_uri = pyotp.TOTP(secret).provisioning_uri(name=name, issuer_name=issuer)
        qrcode.make(totp_uri).save(filename)
        print(f"[INFO] QR code saved as {filename}. Scan with your authenticator app (e.g., Google Authenticator).")
        print(f"[INFO] Manual secret key (for manual entry if scanning fails): {secret}")
    except Exception as e:
        print(f"[ERROR] Failed to generate QR code: {e}")

def verify_otp(secret):
    """Prompt the user for OTP and verify it."""
    totp = pyotp.TOTP(secret)
    
    # In a real app, you would NOT print this for security.
    print(f"[DEBUG] Current OTP (for testing, valid for {totp.interval} seconds):", totp.now()) 
    
    user_code = input("Enter the OTP from your authenticator app: ")
    
    # Use valid_window to account for clock drift
    if totp.verify(user_code, valid_window=OTP_VALID_WINDOW):
        print("[SUCCESS] OTP is valid! Access granted.")
        # In a real app, you might log the successful authentication time or user details here.
    else:
        print("[ERROR] Invalid OTP. Please check the time sync on your device and try again.")

def add_new_device(secret):
    """
    Generate a QR code using the *existing* secret for scanning on a new device.
    This allows a user to have the same 2FA on multiple devices (e.g., phone and tablet).
    If the intent is to REVOKE access from old devices, you'd generate a NEW secret here.
    """
    print("\n--- Adding a New Device ---")
    print("To add this 2FA to another device:")
    print(f"1. Open your authenticator app on the NEW device.")
    print(f"2. Scan the QR code image '{QR_CODE_NEW_DEVICE_FILENAME}'.")
    print(f"3. Alternatively, manually enter the secret key: {secret}")
    print("Note: This will allow both your old and new devices to generate codes for this account.")
    generate_qr_code(secret, filename=QR_CODE_NEW_DEVICE_FILENAME,
                     name=DEFAULT_ACCOUNT_NAME, issuer=ISSUER_NAME)
    print("---------------------------\n")


if __name__ == "__main__":
    secret = get_or_create_secret()

    # If user wants to add a new device
    if "--new-device" in sys.argv:
        add_new_device(secret)
    elif "--verify" in sys.argv or len(sys.argv) == 1: # Default action if no specific flag
        verify_otp(secret)
    elif "--help" in sys.argv:
        print("Usage:")
        print("  python your_script_name.py           - Verify an OTP")
        print("  python your_script_name.py --verify  - Verify an OTP")
        print("  python your_script_name.py --new-device - Generate QR code for a new device (uses existing secret)")
    else:
        print("[ERROR] Unknown argument. Use --verify, --new-device, or --help.")