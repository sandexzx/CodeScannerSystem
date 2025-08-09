import os
import mimetypes
import smtplib
import logging
import traceback
from email.message import EmailMessage
from typing import Tuple

# Logger for debug output
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

def send_excel_via_smtp(excel_path: str, cfg: dict) -> Tuple[bool, str]:
    """
    Send the given Excel file as an email attachment using SMTP settings from cfg.
    Returns (True, message) on success, (False, error_message) on failure.
    Expected cfg keys:
      - smtp_host (str)
      - smtp_port (int)
      - smtp_username (str)
      - smtp_password (str)
      - smtp_use_tls (bool)
      - mail_from (str)
      - mail_to (str)
      - smtp_debug (bool)  # optional - enable smtplib debug output
    """
    try:
        if not os.path.exists(excel_path):
            logger.error("Excel file not found: %s", excel_path)
            return False, f"Excel file not found: {excel_path}"
    except Exception as e:
        logger.exception("Error checking excel file existence")
        return False, f"Error checking excel file: {str(e)}"

    host = cfg.get("smtp_host") or ""
    port = int(cfg.get("smtp_port") or 0)
    username = cfg.get("smtp_username") or ""
    password = cfg.get("smtp_password") or ""
    use_tls = bool(cfg.get("smtp_use_tls", True))
    mail_from = cfg.get("mail_from") or ""
    mail_to = cfg.get("mail_to") or ""

    if not host or not port or not mail_from or not mail_to:
        return False, "Missing SMTP configuration (host/port/from/to)."

    # Prepare message
    msg = EmailMessage()
    msg["Subject"] = "Exported Excel from CodeScannerSystem"
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg.set_content("Во вложении Excel файл с результатами сканирования.")

    # Guess MIME type
    ctype, encoding = mimetypes.guess_type(excel_path)
    if ctype is None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)

    try:
        with open(excel_path, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(excel_path))
    except Exception as e:
        return False, f"Failed to read attachment: {str(e)}"

    # Send via SMTP
    try:
        # Use SSL for port 465, otherwise use SMTP and optionally STARTTLS
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()

        # Login if username provided
        if username:
            server.login(username, password)

        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully."
    except Exception as e:
        try:
            server.quit()
        except:
            pass
        return False, f"SMTP error: {str(e)}"
