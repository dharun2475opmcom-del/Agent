"""BRREG Enhetsregisteret source client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from search_agent.identity import validate_org_number


BRREG_BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


class BRREGError(RuntimeError):
    """Base exception for BRREG source errors."""


class BRREGNotFoundError(BRREGError):
    """Raised when BRREG cannot find the requested organization."""


class BRREGIdentityMismatchError(BRREGError):
    """Raised when BRREG returns a different organization number."""


@dataclass(frozen=True)
class CompanyRecord:
    """Normalized company data returned by BRREG."""

    organization_number: str
    name: str
    organization_form: str | None
    status: str | None
    registration_date: str | None
    business_address: str | None
    postal_code: str | None
    postal_place: str | None
    municipality: str | None
    industry_code: str | None
    industry_description: str | None
    website: str | None
    raw_data: dict[str, Any]


class BRREGClient:
    """Client for the official BRREG Enhetsregisteret API."""

    def __init__(
        self,
        base_url: str = BRREG_BASE_URL,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_company(self, organization_number: str) -> CompanyRecord:
        """Fetch and normalize a company from BRREG."""

        org_number = validate_org_number(organization_number)

        url = f"{self.base_url}/{org_number}"

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Signalpost-CompanyResearch/1.0",
                },
            )
        except requests.RequestException as exc:
            raise BRREGError(
                f"Failed to contact BRREG for {org_number}."
            ) from exc

        if response.status_code == 404:
            raise BRREGNotFoundError(
                f"Organization {org_number} was not found in BRREG."
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise BRREGError(
                f"BRREG returned HTTP {response.status_code} "
                f"for organization {org_number}."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise BRREGError(
                f"BRREG returned invalid JSON for organization {org_number}."
            ) from exc

        returned_org_number = str(data.get("organisasjonsnummer", "")).strip()

        if returned_org_number != org_number:
            raise BRREGIdentityMismatchError(
                "BRREG returned organization "
                f"{returned_org_number!r}, expected {org_number!r}."
            )

        return self._parse_company(data, org_number)

    @staticmethod
    def _parse_company(
        data: dict[str, Any],
        organization_number: str,
    ) -> CompanyRecord:
        """Convert raw BRREG JSON into a stable CompanyRecord."""

        business_address = data.get("forretningsadresse") or {}

        address_lines = business_address.get("adresse") or []
        address = ", ".join(
            str(line).strip()
            for line in address_lines
            if str(line).strip()
        )

        postal_code = business_address.get("postnummer")
        postal_place = business_address.get("poststed")
        municipality = business_address.get("kommune")

        if not address and postal_code and postal_place:
            address = f"{postal_code} {postal_place}"

        industry = data.get("naeringskode1") or {}

        return CompanyRecord(
            organization_number=organization_number,
            name=str(data.get("navn", "")).strip(),
            organization_form=(
                str(data["organisasjonsform"].get("kode")).strip()
                if data.get("organisasjonsform")
                else None
            ),
            status=(
                str(data.get("registrertIMvaRegisteret")).strip()
                if data.get("registrertIMvaRegisteret") is not None
                else None
            ),
            registration_date=(
                str(data.get("registreringsdatoEnhetsregisteret")).strip()
                if data.get("registreringsdatoEnhetsregisteret")
                else None
            ),
            business_address=address or None,
            postal_code=str(postal_code).strip() if postal_code else None,
            postal_place=str(postal_place).strip() if postal_place else None,
            municipality=str(municipality).strip() if municipality else None,
            industry_code=(
                str(industry.get("kode")).strip()
                if industry.get("kode")
                else None
            ),
            industry_description=(
                str(industry.get("beskrivelse")).strip()
                if industry.get("beskrivelse")
                else None
            ),
            website=(
                str(data.get("hjemmeside")).strip()
                if data.get("hjemmeside")
                else None
            ),
            raw_data=data,
        )