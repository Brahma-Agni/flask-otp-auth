# magic_link_auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

class SendOtpForm(FlaskForm):
    """
    Form for users to submit their email address to receive an OTP.
    """
    email = StringField('Email Address', validators=[DataRequired(), Email(message='Please enter a valid email address.')])
    submit = SubmitField('Send OTP')

class VerifyOtpForm(FlaskForm):
    """
    Form for users to enter the received OTP.
    """
    otp = StringField('One-Time Password (OTP)', validators=[
        DataRequired('Please enter the OTP.'),
        Length(min=6, max=6, message='OTP must be 6 digits.') # Assuming 6-digit OTP as per config
    ])
    submit = SubmitField('Verify OTP')

    # Custom validator to ensure OTP is numeric (or alphanumeric if your OTP_LENGTH allows)
    def validate_otp(self, field):
        if not field.data.isdigit(): # Checks if all characters are digits
            raise ValidationError('OTP must be numeric.')