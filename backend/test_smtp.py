import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.insert(0, '.')
from config import settings

print("=" * 60)
print("SMTP Configuration Test")
print("=" * 60)
print(f"SMTP Host: {settings.SMTP_HOST}")
print(f"SMTP Port: {settings.SMTP_PORT}")
print(f"SMTP User: {settings.SMTP_USER}")
print(f"SMTP Password: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'NOT SET'}")
print(f"From Email: {settings.SMTP_FROM_EMAIL}")
print(f"From Name: {settings.SMTP_FROM_NAME}")
print("=" * 60)

test_email = input("\nEnter your email to test: ").strip()

print("\nAttempting to send test email...")

try:
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg['To'] = test_email
    msg['Subject'] = "Test Email from Gemini Chatbot"
    
    body = "This is a test email. If you receive this, your SMTP configuration is working!"
    html = """
    <html>
    <body>
        <h2>Test Email</h2>
        <p>This is a test email. If you receive this, your SMTP configuration is working!</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    
    print(f"\nConnecting to {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
    
    print("Starting TLS...")
    server.starttls()
    
    print(f"Logging in as {settings.SMTP_USER}...")
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    
    print(f"Sending email to {test_email}...")
    server.send_message(msg)
    
    print("Closing connection...")
    server.quit()
    
    print("\n" + "=" * 60)
    print("✓ SUCCESS! Email sent successfully!")
    print(f"✓ Check your inbox at: {test_email}")
    print(f"✓ Also check spam/junk folder")
    print("=" * 60)

except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 60)
    print("✗ AUTHENTICATION FAILED!")
    print("=" * 60)
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. Gmail App Password is incorrect")
    print("2. 2-Factor Authentication not enabled")
    print("3. App Password has spaces (should be removed)")
    print("\nHow to fix:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Enable 2FA if not enabled")
    print("3. Generate new App Password for 'Mail'")
    print("4. Copy the 16-character password (no spaces)")
    print("5. Update SMTP_PASSWORD in backend/.env")
    print("=" * 60)

except smtplib.SMTPException as e:
    print("\n" + "=" * 60)
    print("✗ SMTP ERROR!")
    print("=" * 60)
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. SMTP server settings incorrect")
    print("2. Port blocked by firewall")
    print("3. Network connectivity issue")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print("✗ UNEXPECTED ERROR!")
    print("=" * 60)
    print(f"Error: {e}")
    print(f"Error Type: {type(e).__name__}")
    print("=" * 60)
