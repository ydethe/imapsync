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

    @classmethod
    def from_bin_file(cls, pth: Path) -> "Email":
        ret = cls()
        with open(pth, "rb") as f:
            raw_msg = f.read()
        ret.__eml_to_markdown(raw_msg)
        return ret

    def __init__(
        self,
        subject: str = "",
        from_: str = "",
        to: str = "",
        body: str = "",
        date: datetime = None,
        parsing_status: bool = None,
    ):
        self.parsing_status = parsing_status
        self.date = date
        self.subject = subject
        self.from_ = from_
        self.to = to
        self.body = body

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

        # Sat, 09 Jul 2022 09:22:41 +0200
        self.date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
        self.subject = subject
        self.from_ = from_
        self.to = to
        self.body = body
        self.parsing_status = status

    def get_markdown(self) -> str:
        sdt = self.date.strftime("%a, %d %b %Y %H:%M:%S %z")

        md_content = f"""# {self.subject}

**From:** {self.from_}
**To:** {self.to}
**Date:** {sdt}

{self.body}
"""
        return md_content

    def save_to_file(self, pth: Path):
        with open(pth, "w") as f:
            f.write(self.get_markdown())
