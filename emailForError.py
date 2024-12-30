import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback


# Read password from a file
def get_password(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()  # Strips any extra whitespace or newline

# Example usage
password_file = "password.txt"  # Replace with the path to your password file

# Use the password for your email function
print("Password retrieved successfully.")

# Configuration
SMTP_SERVER = "mail.gmx.net"  # Replace with your SMTP server
SMTP_PORT = 587
EMAIL = "***REMOVED***"
PASSWORD = get_password(password_file)
TO_EMAIL = "***REMOVED***"

def send_email(subject, body):
    try:
        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)
def main():
    try:
        # Your main program logic here
        print("Running the main program...")
        # Simulate a crash (remove this in the real code)
        raise ValueError("Simulated error")
        
        # Send success email if no exceptions occur
        send_email("Program Finished Successfully", "Your Python program has completed successfully.")
    except Exception as e:
        # Send crash email with the error details
        error_message = traceback.format_exc()
        send_email("Program Crashed", f"Your Python program encountered an error:\n\n{error_message}")
        print("An error occurred:", e)

if __name__=="__main__":
    main()