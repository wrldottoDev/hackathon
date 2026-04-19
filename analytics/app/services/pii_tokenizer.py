from __future__ import annotations

import hashlib
import re


class PiiTokenizer:
    _accountish_pattern = re.compile(
        r"(?<!\w)(?:[A-Z]{2,5}-)?\d[\d -]{6,22}\d(?!\w)",
        re.IGNORECASE,
    )
    _email_pattern = re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE)
    _ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def tokenize_identifier(self, value: str, kind: str) -> str:
        normalized = " ".join(value.strip().upper().split())
        digest = hashlib.sha256(f"{self._secret}:{kind}:{normalized}".encode("utf-8")).hexdigest()
        return f"{kind.upper()}_{digest[:12]}"

    def tokenize_name(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return self.tokenize_identifier(normalized, "name")

    def mask_text(self, text: str | None) -> str:
        if not text:
            return ""

        masked = self._email_pattern.sub(
            lambda match: self.tokenize_identifier(match.group(0), "email"),
            text,
        )
        masked = self._ip_pattern.sub(
            lambda match: self.tokenize_identifier(match.group(0), "ip"),
            masked,
        )
        masked = self._accountish_pattern.sub(
            lambda match: self.tokenize_identifier(
                match.group(0),
                self._classify_numeric_identifier(match.group(0)),
            ),
            masked,
        )
        return masked

    def extract_financial_tokens(self, *texts: str | None) -> list[str]:
        tokens: set[str] = set()
        for text in texts:
            if not text:
                continue
            for match in self._accountish_pattern.finditer(text):
                tokens.add(
                    self.tokenize_identifier(
                        match.group(0),
                        self._classify_numeric_identifier(match.group(0)),
                    )
                )
        return sorted(tokens)

    def _classify_numeric_identifier(self, value: str) -> str:
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) == 8:
            return "sinpe"
        return "acct"
