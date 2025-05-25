# magic_link_auth/app.py
import os
import random
import time
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_mail import Mail, Message
from threading import Thread # For sending emails asynchronously

# Import Config and Forms
from config import Config
from forms import SendOtpForm, VerifyOtpForm

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

# --- Helper Functions for Email Sending ---
def send_async_email(app_instance, msg):
    """Sends an email in a separate thread to prevent blocking the web request."""
    with app_instance.app_context():
        try:
            mail.send(msg)
            app.logger.info(f"Email sent successfully to {msg.recipients[0]}")
        except Exception as e:
            app.logger.error(f"Failed to send email to {msg.recipients[0]}: {e}")

def send_email(subject, recipients, html_body):
    """
    Constructs and sends an email.
    Uses a separate thread for sending to avoid performance bottlenecks.
    """
    msg = Message(subject, recipients=recipients, html=html_body)
    Thread(target=send_async_email, args=(app, msg)).start()

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def send_otp():
    """
    Displays the form to enter email and send OTP.
    Generates and stores OTP in session, then sends it via email.
    """
    form = SendOtpForm()
    if form.validate_on_submit():
        email = form.email.data

        # Generate a random numeric OTP
        otp_digits = [str(random.randint(0, 9)) for _ in range(app.config['OTP_LENGTH'])]
        otp = ''.join(otp_digits)

        # --- Store OTP and related info in session ---
        # This is temporary and specific to the user's browser session.
        session['otp'] = otp
        session['otp_email'] = email # Store email to verify against
        session['otp_expiration'] = time.time() + app.config['OTP_EXPIRATION_SECONDS']

        # Render email content using a Jinja2 template
        email_html = render_template('email/otp_email.html', otp=otp,
                                     otp_expiration_minutes=app.config['OTP_EXPIRATION_SECONDS'] // 60)

        # Send the OTP email
        send_email(
            subject=f"Your One-Time Password (OTP) for {request.host}", # Uses request.host for dynamic subject
            recipients=[email],
            html_body=email_html
        )
        flash(f'A One-Time Password has been sent to {email}. Please check your inbox and enter it below.', 'info')
        return redirect(url_for('verify_otp'))

    return render_template('send_otp.html', form=form)


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """
    Displays the form to enter the OTP.
    Verifies the entered OTP against the one stored in the session.
    """
    # If no OTP data is in session, redirect back to send_otp
    if 'otp' not in session or 'otp_expiration' not in session or 'otp_email' not in session:
        flash('Please request an OTP first.', 'warning')
        return redirect(url_for('send_otp'))

    form = VerifyOtpForm()
    if form.validate_on_submit():
        user_entered_otp = form.otp.data

        stored_otp = session.get('otp')
        stored_expiration = session.get('otp_expiration')
        stored_email = session.get('otp_email')

        # Check for OTP expiration
        if time.time() > stored_expiration:
            flash('The OTP has expired. Please request a new one.', 'danger')
            # Clear expired OTP data from session
            session.pop('otp', None)
            session.pop('otp_expiration', None)
            session.pop('otp_email', None)
            return redirect(url_for('send_otp'))

        # Verify OTP
        if user_entered_otp == stored_otp:
            # OTP is correct and not expired! Log the user in.
            session['logged_in'] = True
            session['viewer_email'] = stored_email # Store email for display in protected content

            # Clear OTP from session after successful verification (important for single-use)
            session.pop('otp', None)
            session.pop('otp_expiration', None)
            session.pop('otp_email', None)

            flash('OTP verified successfully! You are logged in.', 'success')
            return redirect(url_for('protected_content'))
        else:
            flash('Incorrect OTP. Please try again.', 'danger')
            # Optionally, implement a lockout mechanism here after too many failed attempts.

    # If GET request or form validation fails, render the OTP verification form
    return render_template('verify_otp.html', form=form,
                           otp_email=session.get('otp_email', 'your email'))


@app.route('/content')
def protected_content():
    """
    Displays content that requires the user to be "logged in".
    Checks the 'logged_in' session variable.
    """
    if not session.get('logged_in'):
        flash('You must log in to access this content.', 'warning')
        return redirect(url_for('send_otp'))

    viewer_email = session.get('viewer_email', 'Guest')
    return render_template('content.html', viewer_email=viewer_email)

@app.route('/logout')
def logout():
    """
    Logs the user out by clearing all relevant session data.
    """
    session.pop('logged_in', None)
    session.pop('viewer_email', None)
    session.pop('otp', None)
    session.pop('otp_expiration', None)
    session.pop('otp_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('send_otp'))

# --- Main entry point for running the application ---
if __name__ == "__main__":
    # Import load_dotenv ONLY when running locally, not required by Gunicorn in production
    from dotenv import load_dotenv
    load_dotenv() # Load environment variables from .env file

    # This check provides a critical security warning during local development if SECRET_KEY is not set.
    if app.config['SECRET_KEY'] == 'v/zR7oat^(SxA8zF88H0<6p>6,%W5i}A(+H' and not app.config['TESTING']:
        print("******************************************************************")
        print("WARNING: Using default SECRET_KEY! This is INSECURE in production!")
        print("         Please set a strong SECRET_KEY in your .env file.")
        print("******************************************************************")

    # Run the Flask development server.
    # host="0.0.0.0" makes it accessible from external IP (useful for Docker/cloud dev environments).
    # port=int(os.environ.get("PORT", 5000)) uses the PORT env var (common on cloud hosts like Render)
    # or defaults to 5000.
    # debug=False is crucial for production.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)