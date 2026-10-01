"""Extract structured company facts from verified web-page text."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from search_agent.evidence import Evidence
from search_agent.extractions.models import CompanyFact


class WebFactExtractor:
    """Extract deterministic company facts from verified web text."""

    def extract(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime | None = None,
    ) -> list[CompanyFact]:
        """Extract facts from a web page already verified for the company."""

        if not organization_number.strip():
            raise ValueError("organization_number cannot be empty.")

        if not page_text.strip():
            raise ValueError("page_text cannot be empty.")

        if not source_url.strip():
            raise ValueError("source_url cannot be empty.")

        if not source_name.strip():
            raise ValueError("source_name cannot be empty.")

        retrieved = retrieved_at or datetime.now(timezone.utc)

        facts: list[CompanyFact] = []

        organization_number_fact = self._extract_organization_number(
            organization_number=organization_number,
            page_text=page_text,
            source_url=source_url,
            source_name=source_name,
            retrieved_at=retrieved,
        )

        if organization_number_fact is not None:
            facts.append(organization_number_fact)

        facts.extend(
            self._extract_email(
                organization_number=organization_number,
                page_text=page_text,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved,
            )
        )

        facts.extend(
            self._extract_phone(
                organization_number=organization_number,
                page_text=page_text,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved,
            )
        )

        facts.extend(
            self._extract_website(
                organization_number=organization_number,
                page_text=page_text,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved,
            )
        )

        facts.extend(
            self._extract_address(
                organization_number=organization_number,
                page_text=page_text,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved,
            )
        )

        return facts

    def _extract_organization_number(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
    ) -> CompanyFact | None:
        """Extract and verify the organization's published number."""

        normalized_target = re.sub(
            r"\D",
            "",
            organization_number,
        )

        page_digits = re.sub(
            r"\D",
            "",
            page_text,
        )

        if normalized_target not in page_digits:
            return None

        evidence = Evidence(
            organization_number=normalized_target,
            field="organization_number",
            value=normalized_target,
            source_name=source_name,
            source_url=source_url,
            retrieved_at=retrieved_at,
            evidence_text=(
                "Organization number found on verified page: "
                f"{organization_number}"
            ),
            confidence=1.0,
        )

        return CompanyFact(
            organization_number=normalized_target,
            field="organization_number",
            value=normalized_target,
            evidence=evidence,
        )

    def _extract_email(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
    ) -> list[CompanyFact]:
        """Extract email addresses from page text."""

        pattern = (
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        )

        emails = list(
            dict.fromkeys(
                match.group(0).lower()
                for match in re.finditer(
                    pattern,
                    page_text,
                )
            )
        )

        return [
            self._make_fact(
                organization_number=organization_number,
                field="email",
                value=email,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved_at,
                evidence_text=f"Email found on page: {email}",
            )
            for email in emails
        ]

    def _extract_phone(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
    ) -> list[CompanyFact]:
        """Extract likely Norwegian telephone numbers from page text."""

        pattern = (
            r"(?<!\d)"
            r"(?:\+47[\s.-]*)?"
            r"(?:\d[\s.-]*){8}"
            r"(?!\d)"
        )

        phones: list[str] = []

        normalized_org_number = re.sub(
            r"\D",
            "",
            organization_number,
        )

        for match in re.finditer(
            pattern,
            page_text,
        ):
            raw_phone = match.group(0).strip()

            digits = re.sub(
                r"\D",
                "",
                raw_phone,
            )

            # Remove the Norwegian country code when present.
            if raw_phone.startswith("+47"):
                digits = digits[2:]

            if len(digits) != 8:
                continue

            # Never treat the company's organization number as a phone number.
            if digits == normalized_org_number:
                continue

            # Avoid duplicates after normalization.
            if any(
                re.sub(r"\D", "", phone).removeprefix("47") == digits
                for phone in phones
            ):
                continue

            phones.append(raw_phone)

        return [
            self._make_fact(
                organization_number=organization_number,
                field="phone",
                value=phone,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved_at,
                evidence_text=f"Phone number found on page: {phone}",
            )
            for phone in phones
        ]

    def _extract_website(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
    ) -> list[CompanyFact]:
        """Extract explicit website URLs from page text."""

        pattern = r'\bhttps?://[^\s<>"\']+'

        websites = list(
            dict.fromkeys(
                match.group(0).rstrip(".,);")
                for match in re.finditer(
                    pattern,
                    page_text,
                )
            )
        )

        return [
            self._make_fact(
                organization_number=organization_number,
                field="website",
                value=website,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved_at,
                evidence_text=f"Website found on page: {website}",
            )
            for website in websites
        ]

    def _extract_address(
        self,
        *,
        organization_number: str,
        page_text: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
    ) -> list[CompanyFact]:
        """Extract likely Norwegian postal addresses."""

        pattern = (
            r"\b"
            r"\d{4}"
            r"\s+"
            r"[A-Za-zÆØÅæøå][A-Za-zÆØÅæøå .'-]{1,60}"
            r"\b"
        )

        addresses = list(
            dict.fromkeys(
                match.group(0).strip()
                for match in re.finditer(
                    pattern,
                    page_text,
                )
            )
        )

        return [
            self._make_fact(
                organization_number=organization_number,
                field="address",
                value=address,
                source_url=source_url,
                source_name=source_name,
                retrieved_at=retrieved_at,
                evidence_text=f"Address found on page: {address}",
            )
            for address in addresses
        ]

    @staticmethod
    def _make_fact(
        *,
        organization_number: str,
        field: str,
        value: str,
        source_url: str,
        source_name: str,
        retrieved_at: datetime,
        evidence_text: str,
    ) -> CompanyFact:
        """Create an evidence-backed company fact."""

        normalized_org_number = re.sub(
            r"\D",
            "",
            organization_number,
        )

        evidence = Evidence(
            organization_number=normalized_org_number,
            field=field,
            value=value,
            source_name=source_name,
            source_url=source_url,
            retrieved_at=retrieved_at,
            evidence_text=evidence_text,
            confidence=1.0,
        )

        return CompanyFact(
            organization_number=normalized_org_number,
            field=field,
            value=value,
            evidence=evidence,
        )