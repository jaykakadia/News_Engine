import os
from dotenv import load_dotenv
from app.utils.email_sender import send_trigger_email

load_dotenv()

# This script verifies your SMTP configuration
# It sends a test email to the address defined in your .env file

TEST_RECEIVER = os.getenv('SMTP_EMAIL') 

if not TEST_RECEIVER or TEST_RECEIVER == "your-email@gmail.com":
    print("❌ Error: Please update SMTP_EMAIL in your .env file first!")
else:
    print(f"🚀 Sending test email to {TEST_RECEIVER}...")

    success = send_trigger_email(
        to_email=TEST_RECEIVER,
        user_name="Jay",
        article_title="SMTP Test: News Engine is Working!",
        score=95,
        article_link="http://127.0.0.1:5001/"
    )

    if success:
        print("\n✅ SUCCESS!")
        print("Your SMTP configuration is correct. Check your inbox (and Spam folder).")
    else:
        print("\n❌ FAILED.")
        print("Check your .env credentials and ensure you are using a Gmail App Password.")
