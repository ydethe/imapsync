# Email.py

from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
import html
from typing import Tuple

from bs4 import BeautifulSoup
import pyhtml2md


def extract_email_body(msg: EmailMessage) -> Tuple[str, bool]:
    """Extract best-effort body (preferring text/plain, fallback to text/html)."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                body = part.get_content()
                break

        if len(body) == 0:
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_content()
                    break

    else:
        content_type = msg.get_content_type()
        body = msg.get_content()

    if content_type == "text/html":
        soup = BeautifulSoup(body, features="html.parser")
        for div in soup.find_all("div", {"class": "gmail_quote"}):
            div.decompose()
        lines = html.unescape(str(soup)).strip().split("\n")
    else:
        lines = body.strip().split("\n")

    body_without_reply = ""
    for line in lines:
        if line.strip().startswith(">"):
            break
        body_without_reply += line

    status = True
    if content_type == "text/html":
        options = pyhtml2md.Options()
        options.splitLines = False

        converter = pyhtml2md.Converter(body_without_reply, options)
        markdown = converter.convert()
        status = converter.ok()
    else:
        markdown = body_without_reply

    return markdown, status


def eml_to_markdown(raw_bytes: bytes) -> Tuple[str, bool]:
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    subject = msg["subject"] or "(No Subject)"
    from_ = msg["from"] or ""
    to = msg["to"] or ""
    date = msg["date"] or ""
    body, status = extract_email_body(msg)

    md_content = f"""# {subject}

**From:** {from_}
**To:** {to}
**Date:** {date}

{body}
"""

    return md_content, status
