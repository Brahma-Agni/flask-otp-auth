# magic_link_auth/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class Config:
    # Flask Secret Key for session management and token signing (CRITICAL FOR SECURITY!)
    # In production, ensure this is a strong, randomly generated string stored as an environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-default-secret-key-for-dev'

    # Mail Server Settings (Example: Gmail SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    # Use TLS if your server supports it, typically on port 587.
    # Set to 'false' and MAIL_USE_SSL to 'true' if your server requires SSL on port 465.
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # Your email address (e.g., your_app_email@gmail.com)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # Your email password or app-specific password

    # Default sender for emails. Can be the same as MAIL_USERNAME or a different sender.
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Set to 'true' during development/testing to prevent actual emails from being sent.
    # Remove or set to 'false' for production.
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() in ['true', 'on', '1']

    # OTP related settings
    OTP_EXPIRATION_SECONDS = int(os.environ.get('OTP_EXPIRATION_SECONDS') or 300) # OTP valid for 5 minutes
    OTP_LENGTH = int(os.environ.get('OTP_LENGTH') or 6) # 6 digits for OTP

    # Session cookie security settings (HIGHLY RECOMMENDED FOR PRODUCTION)
    # Ensure these are 'true' when deploying to a live server with HTTPS.
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ['true', 'on', '1'] # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() in ['true', 'on', '1'] # Prevent client-side JS access
    SESSION_COOKIE_SAMESITE = 'Lax' # Helps mitigate CSRF attacks