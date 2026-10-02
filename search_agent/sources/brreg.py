"""BRREG Enhetsregisteret source client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from search_agent.identity import validate_org_number


BRREG_BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"
BRREG_ROLES_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


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
    vat_registered: bool | None
    registration_date: str | None
    business_address: str | None
    postal_code: str | None
    postal_place: str | None
    municipality: str | None
    industry_code: str | None
    industry_description: str | None
    website: str | None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    employee_count: int | None = None
    employee_count_registered: bool | None = None
    foundation_date: str | None = None
    purpose: str | None = None
    capital_amount: float | None = None
    capital_currency: str | None = None
    bankrupt: bool | None = None
    under_liquidation: bool | None = None
    under_forced_liquidation: bool | None = None
    registered_in_business_register: bool | None = None
    latest_annual_accounts_year: int | None = None
    raw_data: dict[str, Any] | None = None


@dataclass(frozen=True)
class CompanyRole:
    """A public role associated with a company."""

    role_code: str
    role_description: str
    person_name: str | None
    organization_number: str | None
    organization_name: str | None
    deregistered: bool


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

        returned_org_number = str(
            data.get("organisasjonsnummer", "")
        ).strip()

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
        website = data.get("hjemmeside")
        if website:
            website = str(website).strip().replace("\\", "")

        capital = data.get("kapital") or {}
        capital_amount = capital.get("belop")
        if capital_amount is not None:
            try:
                capital_amount = float(capital_amount)
            except (TypeError, ValueError):
                capital_amount = None

        employee_count = data.get("antallAnsatte")
        if employee_count is not None:
            try:
                employee_count = int(employee_count)
            except (TypeError, ValueError):
                employee_count = None

        return CompanyRecord(
            organization_number=organization_number,
            name=str(data.get("navn", "")).strip(),
            organization_form=(
                str(data["organisasjonsform"].get("kode")).strip()
                if data.get("organisasjonsform")
                else None
            ),
            vat_registered=(
                bool(data.get("registrertIMvaRegisteret"))
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
            website=website or None,
            email=(
                str(data.get("epostadresse")).strip()
                if data.get("epostadresse")
                else None
            ),
            phone=(
                str(data.get("telefon")).strip()
                if data.get("telefon")
                else None
            ),
            mobile=(
                str(data.get("mobil")).strip()
                if data.get("mobil")
                else None
            ),
            employee_count=employee_count,
            employee_count_registered=(
                bool(data.get("harRegistrertAntallAnsatte"))
                if data.get("harRegistrertAntallAnsatte") is not None
                else None
            ),
            foundation_date=(
                str(data.get("stiftelsesdato")).strip()
                if data.get("stiftelsesdato")
                else None
            ),
            purpose=(
                str(data.get("vedtektsfestetFormaal")).strip()
                if data.get("vedtektsfestetFormaal")
                else None
            ),
            capital_amount=capital_amount,
            capital_currency=(
                str(capital.get("valuta")).strip()
                if capital.get("valuta")
                else None
            ),
            bankrupt=(
                bool(data.get("konkurs"))
                if data.get("konkurs") is not None
                else None
            ),
            under_liquidation=(
                bool(data.get("underAvvikling"))
                if data.get("underAvvikling") is not None
                else None
            ),
            under_forced_liquidation=(
                bool(data.get("underTvangsavviklingEllerTvangsopplosning"))
                if data.get("underTvangsavviklingEllerTvangsopplosning") is not None
                else None
            ),
            registered_in_business_register=(
                bool(data.get("registrertIForetaksregisteret"))
                if data.get("registrertIForetaksregisteret") is not None
                else None
            ),
            latest_annual_accounts_year=(
                max(
                    (
                        int(year)
                        for year in (data.get("sisteInnsendteAarsregnskap") or [])
                        if str(year).isdigit()
                    ),
                    default=None,
                )
            ),
            raw_data=data,
        )


class BRREGRoleClient:
    """Client for the public BRREG roles endpoint."""

    def __init__(
        self,
        base_url: str = BRREG_ROLES_URL,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_roles(self, organization_number: str) -> list[CompanyRole]:
        """Fetch public roles for a company by organization number."""

        org_number = validate_org_number(organization_number)
        url = f"{self.base_url}/{org_number}/roller"

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
                f"Failed to contact BRREG roles API for {org_number}."
            ) from exc

        if response.status_code == 404:
            raise BRREGNotFoundError(
                f"Roles for organization {org_number} were not found."
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise BRREGError(
                f"BRREG roles API returned HTTP {response.status_code} "
                f"for organization {org_number}."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise BRREGError(
                f"BRREG roles API returned invalid JSON for {org_number}."
            ) from exc

        return self._parse_roles(data)

    @staticmethod
    def _parse_roles(data: dict[str, Any]) -> list[CompanyRole]:
        """Normalize the public BRREG roles response."""

        roles: list[CompanyRole] = []

        for group in data.get("rollegrupper") or []:
            for raw_role in group.get("roller") or []:
                role_type = raw_role.get("type") or {}
                person = raw_role.get("person") or {}
                person_name_data = person.get("navn") or {}

                person_name = " ".join(
                    str(person_name_data.get(part, "")).strip()
                    for part in ("fornavn", "mellomnavn", "etternavn")
                    if str(person_name_data.get(part, "")).strip()
                ) or None

                entity = raw_role.get("enhet") or {}
                entity_number = (
                    str(entity.get("organisasjonsnummer")).strip()
                    if entity.get("organisasjonsnummer")
                    else None
                )
                entity_name_parts = entity.get("navn") or []
                entity_name = (
                    " ".join(str(part).strip() for part in entity_name_parts if str(part).strip())
                    or None
                )

                roles.append(
                    CompanyRole(
                        role_code=str(role_type.get("kode", "")).strip(),
                        role_description=str(
                            role_type.get("beskrivelse", "")
                        ).strip(),
                        person_name=person_name,
                        organization_number=entity_number,
                        organization_name=entity_name,
                        deregistered=bool(raw_role.get("avregistrert")),
                    )
                )

        return roles
