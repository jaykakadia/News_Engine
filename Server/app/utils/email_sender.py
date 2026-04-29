"""
Email alert sender using Gmail SMTP.
Sends email notifications when triggers fire for users.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_trigger_email(to_email, user_name, article_title, score, article_link=""):
    """
    Sends an email alert when a trigger fires.
    
    Requires SMTP_EMAIL and SMTP_PASSWORD in .env file.
    For Gmail, use an App Password (not your regular password).
    """
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_email or not smtp_password:
        print("  ⚠️  Email alert skipped: SMTP_EMAIL or SMTP_PASSWORD not configured in .env")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔔 News Alert: {article_title[:60]}..."
        msg['From'] = smtp_email
        msg['To'] = to_email
        
        # HTML email body
        html = f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem;">
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 2rem; border: 1px solid rgba(255,255,255,0.1);">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: #38bdf8;">⚡ News Engine</span>
                </div>
                
                <p style="color: #94a3b8; font-size: 0.9rem;">Hi {user_name},</p>
                <p style="color: #94a3b8; font-size: 0.9rem;">A news article matching your interests has been detected!</p>
                
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 1.25rem; margin: 1.5rem 0;">
                    <p style="font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.5rem;">{article_title}</p>
                    <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 0.2rem 0.6rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600;">
                        Relevance Score: {int(score)}
                    </span>
                </div>
                
                {f'<a href="{article_link}" style="display: inline-block; background: #38bdf8; color: #000; padding: 0.75rem 1.5rem; border-radius: 0.75rem; font-weight: 600; text-decoration: none; margin-top: 0.5rem;">Read Article →</a>' if article_link else ''}
                
                <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 2rem 0;">
                <p style="color: #64748b; font-size: 0.75rem; text-align: center;">
                    You're receiving this because of your interest settings in News Engine.<br>
                    Manage your interests in the Settings page.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        print(f"  ✉️  Email alert sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"  ⚠️  Email alert failed: {e}")
        return False
