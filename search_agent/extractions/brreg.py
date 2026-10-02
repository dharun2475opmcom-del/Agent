"""Extract structured facts from BRREG company records."""

from __future__ import annotations

from datetime import datetime, timezone

from search_agent.evidence import Evidence
from search_agent.extractions.models import CompanyFact
from search_agent.sources import CompanyRecord, CompanyRole


class BRREGFactExtractor:
    """Convert a BRREG CompanyRecord into evidence-backed facts."""

    SOURCE_NAME = "BRREG Enhetsregisteret"

    def extract(
        self,
        company: CompanyRecord,
        *,
        source_url: str,
        retrieved_at: datetime | None = None,
    ) -> list[CompanyFact]:
        """Extract available facts from a BRREG company record."""

        retrieved = retrieved_at or datetime.now(timezone.utc)

        values = {
            "name": company.name,
            "organization_form": company.organization_form,
            "vat_registered": company.vat_registered,
            "registration_date": company.registration_date,
            "business_address": company.business_address,
            "postal_code": company.postal_code,
            "postal_place": company.postal_place,
            "municipality": company.municipality,
            "industry_code": company.industry_code,
            "industry_description": company.industry_description,
            "website": company.website,
            "email": company.email,
            "phone": company.phone,
            "mobile": company.mobile,
            "employee_count": company.employee_count,
            "employee_count_registered": company.employee_count_registered,
            "foundation_date": company.foundation_date,
            "purpose": company.purpose,
            "capital_amount": company.capital_amount,
            "capital_currency": company.capital_currency,
        }

        return self._facts_from_values(
            company.organization_number,
            values,
            source_url=source_url,
            retrieved_at=retrieved,
        )

    def extract_roles(
        self,
        organization_number: str,
        roles: list[CompanyRole],
        *,
        source_url: str,
        retrieved_at: datetime | None = None,
    ) -> list[CompanyFact]:
        """Extract active public roles without publishing birth data."""

        retrieved = retrieved_at or datetime.now(timezone.utc)

        role_values = [
            {
                "role_code": role.role_code,
                "role": role.role_description,
                "person_name": role.person_name,
                "organization_number": role.organization_number,
                "organization_name": role.organization_name,
                "deregistered": role.deregistered,
            }
            for role in roles
            if not role.deregistered
        ]

        if not role_values:
            return []

        evidence = Evidence(
            organization_number=organization_number,
            field="roles",
            value=role_values,
            source_name=self.SOURCE_NAME,
            source_url=source_url,
            retrieved_at=retrieved,
            evidence_text=f"Public BRREG roles: {role_values}",
            confidence=1.0,
        )

        return [
            CompanyFact(
                organization_number=organization_number,
                field="roles",
                value=role_values,
                evidence=evidence,
            )
        ]

    @staticmethod
    def _facts_from_values(
        organization_number: str,
        values: dict[str, object],
        *,
        source_url: str,
        retrieved_at: datetime,
    ) -> list[CompanyFact]:
        facts: list[CompanyFact] = []

        for field, value in values.items():
            if value is None or value == "":
                continue

            evidence = Evidence(
                organization_number=organization_number,
                field=field,
                value=value,
                source_name=BRREGFactExtractor.SOURCE_NAME,
                source_url=source_url,
                retrieved_at=retrieved_at,
                evidence_text=f"{field}: {value}",
                confidence=1.0,
            )

            facts.append(
                CompanyFact(
                    organization_number=organization_number,
                    field=field,
                    value=value,
                    evidence=evidence,
                )
            )

        return facts
