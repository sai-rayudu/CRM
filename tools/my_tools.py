import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import smtplib
from email.message import EmailMessage
import imaplib
import email
import mcp

# === LLM ===
def call_llm(prompt, llm_api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {llm_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok and 'choices' in response.json():
        return response.json()['choices'][0]['message']['content']
    else:
        print("LLM call failed:", response.text)
        return "Sorry, we could not generate a reply at this time."

# === Send email ===
def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "sairamrayudu67@gmail.com"
    smtp_password = "fmdn ztgu gjit iupm"  # Replace with real app password

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

# === Send Mail Tool ===
@mcp.tool
def send_mail(llm_api_key):
    print("✅ Send Mail Tool started")

    base = os.path.dirname(__file__)
    customer_file = os.path.abspath(os.path.join(base, '../customerdata.xlsx'))
    store_file = os.path.abspath(os.path.join(base, '../storedata.xlsx'))

    customers = pd.read_excel(customer_file)
    store = pd.read_excel(store_file)
    today = datetime.today().date()

    for index, row in customers.iterrows():
        last_contact = pd.to_datetime(row['LastContactDate']).date()
        days_since = (today - last_contact).days

        if days_since >= 7:
            name = row['Name']
            email_address = row['Email']
            interest = row['Interest']

            prompt = f"""
Write a short, friendly marketing email for {name} about {interest}.
Store name: Laptop World.
Store details:
{store.to_string(index=False)}
Write only the email body. No extra ** marks or headings.
Keep it clean and simple, no website links.
"""

            mail_content = call_llm(prompt, llm_api_key)
            print(f"Mail to {name}:\n", mail_content)

            send_email(
                email_address,
                f"{name}, check our latest offer at Laptop World!",
                mail_content
            )

            customers.at[index, 'LastContactDate'] = today

    customers.to_excel(customer_file, index=False)
    print("✅ Send Mail Tool finished")

# === Reply Mail Tool ===
@mcp.tool
def reply_mail(llm_api_key):
    print("✅ Reply Mail Tool started")

    imap_server = "imap.gmail.com"
    smtp_user = "sairamrayudu67@gmail.com"
    smtp_password = "fmdn ztgu gjit iupm"  # Replace with real app password

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(smtp_user, smtp_password)
    mail.select("inbox")

    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    store = pd.read_excel(os.path.abspath(os.path.join(os.path.dirname(__file__), '../storedata.xlsx')))
    store_keywords = [word.lower() for word in ' '.join(store.astype(str).values.flatten()).split()]

    for num in mail_ids:
        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        from_email = email.utils.parseaddr(msg["From"])[1]
        subject = msg["Subject"] or ""
        date_tuple = email.utils.parsedate_tz(msg["Date"])
        msg_time = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

        if msg_time.date() != datetime.today().date():
            print(f"⏭️ Skipping old mail from {from_email}")
            continue

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        body_lower = body.lower()
        subject_lower = subject.lower()

        matched = any(word in body_lower or word in subject_lower for word in store_keywords)

        if not matched:
            print(f"⏭️ Skipping unrelated mail from {from_email}")
            continue

        prompt = f"""
Customer Email:
From: {from_email}
Subject: {subject}
Body:
{body}

Write a short, polite reply from Laptop World store team. Do not add extra ** marks or links. Just the reply text.
"""

        reply_text = call_llm(prompt, llm_api_key)

        send_email(
            from_email,
            f"Re: {subject}",
            reply_text
        )

        mail.store(num, '+FLAGS', '\\Seen')

    print("✅ Reply Mail Tool finished")
