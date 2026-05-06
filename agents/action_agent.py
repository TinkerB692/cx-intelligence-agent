import smtplib
from email.mime.text import MIMEText
import os

class ActionAgent:
    def __init__(self, smtp_server=None, smtp_port=587, smtp_user=None, smtp_pass=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def send_email(self, report, recipient="admin@company.com", dry_run=True):
        """
        Sends the executive summary via email.
        If dry_run is True, it simply prints the email and saves it to a file.
        """
        if not report:
            print("No report to send.")
            return

        subject = report['subject']
        body = report['body']
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.smtp_user or "ai-monitor@company.com"
        msg['To'] = recipient
        
        if dry_run or not self.smtp_server:
            print("\n" + "*"*60)
            print(" DRY RUN: MOCK EMAIL SENT ")
            print("*"*60)
            print(f"To: {msg['To']}")
            print(f"From: {msg['From']}")
            print(f"Subject: {msg['Subject']}\n")
            print(msg.get_payload())
            print("*"*60 + "\n")
            
            # Save to file
            os.makedirs("data/processed", exist_ok=True)
            with open("data/processed/latest_report.eml", "w") as f:
                f.write(msg.as_string())
            print("Email saved to data/processed/latest_report.eml")
            
        else:
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                server.quit()
                print(f"Email successfully sent to {recipient}")
            except Exception as e:
                print(f"Failed to send email: {e}")
