import smtplib
import os
from email.mime.text import MIMEText

EMAIL = os.environ.get("GMAIL_USER", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")


def send_report(report):

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

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            EMAIL,
            APP_PASSWORD
        )

        server.send_message(msg)

    print("Email sent.")