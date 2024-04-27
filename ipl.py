import streamlit as st
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup

# User-defined constants for email configuration
sender_email = "work.abtech@gmail.com"
sender_password = "qnew lrkh ikqc iuao"
recipient_emails = ["tech67451@gmail.com", "priyabratgupta4@gmail.com"]
tickets_date = st.sidebar.date_input("Select desired date for ticket notifications", datetime.today())  # Desired date for ticket notifications, format "YYYY-MM-DD"
num_of_messages_to_send = 10  # Number of notification messages to send once tickets are available
fetch_status_delay = 300 
interval_between_messages = 60  # Seconds between each notification message
rcb_tickets_page_url = "https://shop.royalchallengers.com/ticket"

# Gmail SMTP server details
smtp_server = 'smtp.gmail.com'
smtp_port = 587

def getPage(url: str) -> request:
    """
    Fetches and returns the content of a webpage at a given URL.
    """
    req = request.Request(
        url,
        headers={
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
    )
    return request.urlopen(req)

def get_dates_of_available_tickets(tickets_bsobj: BeautifulSoup) -> list:
    """
    Extracts and returns a list of dates when tickets are available from the parsed
    HTML content of the RCB tickets page.
    """
    dates = list()
    for p in tickets_bsobj.findAll("p", {"class": "css-1nm99ps"}):
        dates.append(p.text)
    return dates

def send_email(subject, body, recipient):
    # Create a MIMEText object for the email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Establish a connection to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Start TLS encryption
    server.login(sender_email, sender_password)  # Login to the Gmail account

    # Send the email
    server.sendmail(sender_email, recipient, message.as_string())

    # Close the connection
    server.quit()

# Streamlit app
st.title("Ticket Availability Notifier")

st.write("""
    This app monitors the availability of tickets for a specific date and sends notifications via email when the tickets become available.
""")

def check_ticket_availability():
    while True:
        tickets_page = getPage(rcb_tickets_page_url)
        tickets_bsobj = BeautifulSoup(tickets_page, features="html.parser")
        available_tickets_dates = get_dates_of_available_tickets(tickets_bsobj)

        for available_ticket_date in available_tickets_dates:
            date_obj = datetime.strptime(available_ticket_date, "%A, %b %d, %Y %I:%M %p")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            if formatted_date == tickets_date:
                st.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Tickets available. Sending email...")
                for message_num in range(num_of_messages_to_send):
                    for recipient_email in recipient_emails:
                        send_email(f'Tickets available for {tickets_date}', f'The match tickets for {tickets_date} are available. Login to {rcb_tickets_page_url} to book the tickets immediately.', recipient_email)
                        st.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Email sent successfully to {recipient_email} - {message_num + 1} time(s)")
                        time.sleep(interval_between_messages)
        st.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Tickets not available. Retrying in {fetch_status_delay} seconds...")
        time.sleep(fetch_status_delay)

check_ticket_availability()
