"""HTML parsing utilities for public company research."""

from __future__ import annotations

from bs4 import BeautifulSoup


class HTMLExtractionError(ValueError):
    """Raised when HTML text extraction cannot be completed."""


class HTMLTextExtractor:
    """Extract clean human-readable text from HTML."""

    def extract(self, html: str) -> str:
        """Return normalized visible text from an HTML document."""

        if not isinstance(html, str):
            raise HTMLExtractionError(
                "HTML content must be a string."
            )

        if not html.strip():
            raise HTMLExtractionError(
                "HTML content cannot be empty."
            )

        soup = BeautifulSoup(html, "html.parser")

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "template",
            ]
        ):
            element.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)