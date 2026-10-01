from datetime import datetime, timezone

import pytest

from search_agent.extractions import (
    BRREGFactExtractor,
    CompanyFact,
)
from search_agent.sources import CompanyRecord


def make_company() -> CompanyRecord:
    """Create a test company record."""

    return CompanyRecord(
        organization_number="995880202",
        name="Example Company AS",
        organization_form="AS",
        vat_registered=True,
        registration_date="2020-01-15",
        business_address="Example Street 1",
        postal_code="0001",
        postal_place="Oslo",
        municipality="Oslo",
        industry_code="62010",
        industry_description="Computer programming activities",
        website="https://example.no",
        raw_data={},
    )


def test_company_fact_requires_matching_evidence():
    company = make_company()

    extractor = BRREGFactExtractor()

    facts = extractor.extract(
        company,
        source_url="https://data.brreg.no/enhetsregisteret/",
    )

    assert facts

    for fact in facts:
        assert fact.organization_number == company.organization_number
        assert fact.evidence.organization_number == (
            company.organization_number
        )
        assert fact.evidence.field == fact.field
        assert fact.evidence.value == fact.value


def test_extractor_skips_missing_values():
    company = CompanyRecord(
        organization_number="995880202",
        name="Example Company AS",
        organization_form="AS",
        vat_registered=None,
        registration_date=None,
        business_address=None,
        postal_code=None,
        postal_place=None,
        municipality=None,
        industry_code=None,
        industry_description=None,
        website=None,
        raw_data={},
    )

    facts = BRREGFactExtractor().extract(
        company,
        source_url="https://data.brreg.no/enhetsregisteret/",
    )

    fields = {fact.field for fact in facts}

    assert fields == {
        "name",
        "organization_form",
    }


def test_extractor_preserves_retrieval_time():
    timestamp = datetime(
        2026,
        2,
        10,
        12,
        30,
        tzinfo=timezone.utc,
    )

    facts = BRREGFactExtractor().extract(
        make_company(),
        source_url="https://data.brreg.no/enhetsregisteret/",
        retrieved_at=timestamp,
    )

    assert facts

    for fact in facts:
        assert fact.evidence.retrieved_at == timestamp


def test_company_fact_rejects_mismatched_evidence():
    company = make_company()

    extractor = BRREGFactExtractor()

    facts = extractor.extract(
        company,
        source_url="https://data.brreg.no/enhetsregisteret/",
    )

    assert facts

    first_fact = facts[0]

    with pytest.raises(ValueError):
        CompanyFact(
            organization_number=company.organization_number,
            field=first_fact.field,
            value="incorrect value",
            evidence=first_fact.evidence,
        )