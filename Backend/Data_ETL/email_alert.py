import smtplib
from email.message import EmailMessage

username = "bot.test.9123@gmail.com"
password = "PNh(\(L5fGtz#DG$"
file_name = ""


def main(message):
    global file_name
    msg = EmailMessage()
    msg["Subject"] = "Web scraper failed!"
    msg["From"] = username
    msg["To"] = "sami.viik2@gmail.com"
    msg.set_content(message)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(username, password)
        smtp.send_message(msg)
