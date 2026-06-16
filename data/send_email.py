import smtplib
import os
from email.mime.text import MIMEText

EMAIL = os.environ.get("GMAIL_USER", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")


def send_report(report):
    if not EMAIL or not APP_PASSWORD:
        raise ValueError("Gmail credentials missing. Please configure GMAIL_USER and GMAIL_APP_PASSWORD in your environment variables.")

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

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    try:
        print("Connecting to smtp.gmail.com...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            print("Logging in...")
            server.login(EMAIL, APP_PASSWORD)
            print("Sending message...")
            server.send_message(msg)
        print("Email sent successfully.")
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Gmail authentication failed. Please verify your GMAIL_USER and GMAIL_APP_PASSWORD (use an App Password, not your account password).")
    except Exception as e:
        raise RuntimeError(f"SMTP error occurred: {e}")