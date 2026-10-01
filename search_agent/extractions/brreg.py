"""Extract structured facts from BRREG company records."""

from __future__ import annotations

from datetime import datetime, timezone

from search_agent.evidence import Evidence
from search_agent.extractions.models import CompanyFact
from search_agent.sources import CompanyRecord


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
        }

        facts: list[CompanyFact] = []

        for field, value in values.items():
            if value is None or value == "":
                continue

            evidence = Evidence(
                organization_number=company.organization_number,
                field=field,
                value=value,
                source_name=self.SOURCE_NAME,
                source_url=source_url,
                retrieved_at=retrieved,
                evidence_text=f"{field}: {value}",
                confidence=1.0,
            )

            facts.append(
                CompanyFact(
                    organization_number=company.organization_number,
                    field=field,
                    value=value,
                    evidence=evidence,
                )
            )

        return facts
