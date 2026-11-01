from mailer import send_email

send_email(
    subject="Infrastructure Monitoring - Test Email",
    body="""
Your Outlook email integration is working.

Infrastructure Monitoring Platform
Alertmanager notification test.
"""
)
