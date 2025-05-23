"""Module for sending credentials to the ActionVFX API.

This module contains the necessary functions and classes for sending
credentials to the ActionVFX API.
"""
# Standard modules import
import os
import json

# Third-party modules import
import urllib.request
import urllib.error
import base64
from cryptography.fernet import Fernet


# Constants
API_URL = "sign in url"
USER_INFO_URL = "user_url"

# Constants for generating the key and saving the session

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".actionvfx_session.json")
KEY_FILE = os.path.join(os.path.expanduser("~"), ".actionvfx_key.key")


def load_or_generate_key():
    """Load or generate a key for encryption."""
    if os.path.exists(KEY_FILE):
        # Load the token from the file
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        # Generate a new crypted file
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key


# Load the key
SECRET_KEY = load_or_generate_key()
fernet = Fernet(SECRET_KEY)


def encrypt_data(data):
    """Ecrypt data given."""
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


def decrypt_data(encrypted_data):
    """Decrypt data given."""
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data


def save_session(user_data, token):
    """Save the user session data to an encrypted file."""
    session_data = {
        "username": user_data.get("username"),
        "firstname": user_data.get("first_name"),
        "lastname": user_data.get("last_name"),
        "Authorization": token,
        "is_premium": not user_data.get("free_subscriber", True)

    }

    # Convert the session data to a JSON string
    json_data = json.dumps(session_data)
    encrypted_data = encrypt_data(json_data)

    # Save the encrypted data to the file
    with open(SESSION_FILE, "wb") as file:
        file.write(encrypted_data)


def load_session():
    """Load the user session data from an encrypted file."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "rb") as file:
                encrypted_data = file.read()

            decrypted_data = decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            return None
    return None


def delete_session():
    """Delete the user session file."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def authenticate(email=None, password=None):
    """
    Authenticate the user with the ActionVFX API and return session details.

    Args:
        email (str): The user's email address.
        password (str): The user's password.

    Returns:
        dict: A dictionary containing the user's session details.
    """
    saved_session = load_session()
    if saved_session:
        return saved_session

    if not email or not password:
        raise ValueError("Email and password are required.")

    # Send the credentials to the API, email and password
    payload = json.dumps(
        {"email": email, "password": password}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }

    # Create the request
    req = urllib.request.Request(
        API_URL, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            # Primero intentamos obtener el token desde los headers
            response_headers = response.info()
            token = response_headers.get("Authorization")

            # Si no está en los headers, lo buscamos en el JSON
            response_data = json.loads(response.read().decode("utf-8"))
            print(response_data)
            if not token:
                token = response_data.get("token")

            if not token:
                raise ValueError("No token found in response.")

            # Obtener los datos del usuario
            user_data = response_data.get("data", {})
            if not user_data:
                raise ValueError("No user data found in response.")

            # Extraer tier si existe (ej: Premium, Free, etc.)
            membership_info = user_data.get("membership", {})
            membership_tier = membership_info.get("tier", "Unknown")

            session_details = {
                "username": user_data.get("username"),
                "firstname": user_data.get("first_name"),
                "lastname": user_data.get("last_name"),
                "Authorization": token,
                "Status": user_data.get("free_subscriber", True),
            }

            save_session(session_details, token)

            return session_details

    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        print(f"HTTP Error {e.code}: {error_message}")
        raise ValueError(f"HTTP Error {e.code}: {error_message}") from e
    except urllib.error.URLError as e:
        print(f"Connection Failed: {e.reason}")
        raise ValueError(f"Connection Failed: {e.reason}") from e
    except json.JSONDecodeError:
        print("Invalid API response: malformed JSON")
        raise ValueError("Invalid API response: malformed JSON")


"""
delete_session()
# For debug purposes introduce your email and password and run the function
print(authenticate(
    email="G5A8w@example.com", password="password"))
"""
