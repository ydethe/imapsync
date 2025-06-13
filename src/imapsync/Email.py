# Email.py

from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
import html
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup
import pyhtml2md


class Email:
    @classmethod
    def from_bytes(cls, raw_msg: bytes) -> "Email":
        ret = cls()
        ret.__eml_to_markdown(raw_msg)
        return ret

    def __init__(self, md_content: str = None, dt: datetime = None, parsing_status: bool = None):
        self.markdown = md_content
        self.dt = dt
        self.parsing_status = parsing_status

    def __extract_email_body(self, msg: EmailMessage) -> Tuple[str, bool]:
        """Extract best-effort body (preferring text/html, fallback to text/plain).
        The output is converted to markdown

        Args:
            msg: The email parsed with email.parser.BytesParser

        Returns:
            A tuple with the markdown content, and a flag that is False if a problem occured

        """
        body = ""
        content_type = ""
        status = True

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

        if content_type == "text/html":
            options = pyhtml2md.Options()
            options.splitLines = False

            converter = pyhtml2md.Converter(body_without_reply, options)
            markdown = converter.convert()
            status = converter.ok()
        else:
            markdown = body_without_reply

        return markdown, status

    def __eml_to_markdown(self, raw_bytes: bytes) -> Tuple[str, datetime, bool]:
        """Extract best-effort body (preferring text/html, fallback to text/plain).
        The output is converted to markdown

        Args:
            raw_bytes: Raw message retrieved from the IMAP server

        Returns:
            A tuple with the markdown content, and a flag that is False if a problem occured

        """
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

        subject = msg["subject"] or "(No Subject)"
        from_ = msg["from"] or ""
        to = msg["to"] or ""
        date = msg["date"] or ""
        body, status = self.__extract_email_body(msg)

        md_content = f"""# {subject}

**From:** {from_}
**To:** {to}
**Date:** {date}

{body}
"""

        # Sat, 09 Jul 2022 09:22:41 +0200
        dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")

        self.markdown = md_content
        self.dt = dt
        self.parsing_status = status

    def save_to_file(self, pth: Path):
        with open(pth, "w") as f:
            f.write(self.markdown)
