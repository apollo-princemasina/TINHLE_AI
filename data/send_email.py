import smtplib
import os
import requests
from email.mime.text import MIMEText

EMAIL = os.environ.get("GMAIL_USER", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")


def send_report(report):
    print("--- send_report called ---")
    print(f"RESEND_API_KEY configured: {bool(RESEND_API_KEY)}")
    print(f"SENDGRID_API_KEY configured: {bool(SENDGRID_API_KEY)}")
    print(f"TO_EMAIL: '{TO_EMAIL}'")
    print(f"GMAIL_USER (EMAIL): '{EMAIL}'")
    print(f"GMAIL_APP_PASSWORD configured: {bool(APP_PASSWORD)}")

    subject = "TINHLE AI Drought Assessment"

    body = f"""
TINHLE AI REPORT

Location: {report['location']}

Predicted Rainfall:
{report['predicted_rainfall']}

Drought Probability:
{report['drought_probability']:.2f}

Drought Class:
{report['drought_class']}

Environmental Score:
{report['environmental_score']}

Environmental Label:
{report['environmental_label']}

Community Risk:
{report['community_risk']}

Final TINHLE Risk:
{report['tinhle_risk']}

TINHLE Classification:
{report['tinhle_risk_class']}
"""

    # 1. Check for Resend HTTPS API (Recommended for Railway)
    if RESEND_API_KEY:
        print("Using Resend HTTPS API to send email...")
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        to_address = TO_EMAIL or EMAIL
        if not to_address:
            raise ValueError("Recipient email not specified. Please set TO_EMAIL or GMAIL_USER environment variable.")
        
        payload = {
            "from": "TINHLE AI <onboarding@resend.dev>",
            "to": [to_address],
            "subject": subject,
            "html": f"<pre>{body}</pre>"
        }
        try:
            response = requests.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print("Email sent successfully via Resend.")
                return
            else:
                raise RuntimeError(f"Resend API error (status {response.status_code}): {response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to send email via Resend: {e}")

    # 2. Check for SendGrid HTTPS API
    if SENDGRID_API_KEY:
        print("Using SendGrid HTTPS API to send email...")
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        to_address = TO_EMAIL or EMAIL
        if not to_address:
            raise ValueError("Recipient email not specified. Please set TO_EMAIL or GMAIL_USER environment variable.")
        
        payload = {
            "personalizations": [{"to": [{"email": to_address}]}],
            "from": {"email": to_address},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        try:
            response = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 202]:
                print("Email sent successfully via SendGrid.")
                return
            else:
                raise RuntimeError(f"SendGrid API error (status {response.status_code}): {response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to send email via SendGrid: {e}")

    # 3. Fallback to standard SMTP (Gmail)
    if not EMAIL or not APP_PASSWORD:
        raise ValueError("No email configuration found. Railway blocks standard SMTP ports (465/587) by default on standard plans. "
                         "Please sign up for a free Resend account (resend.com) and add the RESEND_API_KEY environment variable to send reports over HTTPS.")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL or EMAIL

    try:
        print("Connecting to smtp.gmail.com...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            print("Logging in...")
            server.login(EMAIL, APP_PASSWORD)
            print("Sending message...")
            server.send_message(msg)
        print("Email sent successfully via SMTP.")
    except Exception as e:
        raise RuntimeError(
            f"SMTP error: {e}. Note: Railway blocks outbound SMTP ports (465/587) by default. "
            f"To fix this, please configure a Resend API Key (RESEND_API_KEY) in Railway variables to send emails over HTTPS instead."
        )