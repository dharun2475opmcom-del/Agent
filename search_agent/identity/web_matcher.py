"""Verify that web-page text belongs to the target organization."""

from __future__ import annotations

import re


class WebIdentityMatcher:
    """Match web-page text against a Norwegian organization number."""

    def matches(
        self,
        page_text: str,
        *,
        organization_number: str,
    ) -> bool:
        """Return True when the page contains the target organization number."""

        if not isinstance(page_text, str):
            raise ValueError("page_text must be a string.")

        if not page_text.strip():
            raise ValueError("page_text cannot be empty.")

        if not organization_number.strip():
            raise ValueError(
                "organization_number cannot be empty."
            )

        normalized_org_number = re.sub(
            r"\D",
            "",
            organization_number,
        )

        if len(normalized_org_number) != 9:
            raise ValueError(
                "organization_number must contain 9 digits."
            )

        page_digits = re.sub(
            r"\D",
            "",
            page_text,
        )

        return normalized_org_number in page_digits