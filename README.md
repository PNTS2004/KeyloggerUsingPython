# Python Keylogger with Email Alerts

This is a simple Python keylogger I built that logs keystrokes and emails them to you. It's got two modes:

- **Normal Mode:** sends logs every 30 seconds.
- **Fast Typing Mode:** if someone types really fast (100 keystrokes in 40 seconds), it sends the logs immediately and switches to sending less often (every 15 mins) to avoid spamming.

---

## Important Disclaimer

**This is for educational purposes only.**  
Please **do not use this to monitor anyone without their knowledge or permission**. That’s illegal and just... don’t do it. You are fully responsible for how you use this code.

---

## How it Works

- Listens to your keyboard using `pynput`
- Logs keys to a text file in your home directory (`key_log.txt`)
- Sends that log file to your email address
- Clears the file after sending
- Fast typing triggers an immediate send (kind of like an alert)

---

## What You Need

- Python 3.6 or higher
- Gmail account (or any email with SMTP support)
- These Python packages:
  ```bash
  pip install pynput python-dotenv

