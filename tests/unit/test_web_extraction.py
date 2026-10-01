from datetime import datetime, timezone

import pytest

from search_agent.extractions import WebFactExtractor


RETRIEVED_AT = datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc,
)


def test_extracts_organization_number():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Contact us
        Organisasjonsnummer:
        974 760 673
        """,
        source_url="https://example.no",
        source_name="Example Company website",
        retrieved_at=RETRIEVED_AT,
    )

    assert len(facts) >= 1

    fact = next(
        fact for fact in facts
        if fact.field == "organization_number"
    )

    assert fact.organization_number == "974760673"
    assert fact.value == "974760673"
    assert fact.evidence.source_name == "Example Company website"
    assert fact.evidence.source_url == "https://example.no"
    assert fact.evidence.retrieved_at == RETRIEVED_AT
    assert fact.evidence.confidence == 1.0


def test_accepts_arbitrary_source_name():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="Organisasjonsnummer: 974760673",
        source_url="https://example.no/company",
        source_name="Example Business Directory",
        retrieved_at=RETRIEVED_AT,
    )

    fact = next(
        fact for fact in facts
        if fact.field == "organization_number"
    )

    assert fact.evidence.source_name == "Example Business Directory"


def test_extracts_unformatted_organization_number():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974 760 673",
        page_text="Organisasjonsnummer: 974760673",
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    fact = next(
        fact for fact in facts
        if fact.field == "organization_number"
    )

    assert fact.value == "974760673"


def test_extracts_email():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Organisasjonsnummer: 974 760 673
        Email: kontakt@example.no
        """,
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    email_facts = [
        fact for fact in facts
        if fact.field == "email"
    ]

    assert len(email_facts) == 1
    assert email_facts[0].value == "kontakt@example.no"


def test_extracts_multiple_emails_without_duplicates():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Organisasjonsnummer: 974760673
        kontakt@example.no
        kontakt@example.no
        salg@example.no
        """,
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    emails = [
        fact.value
        for fact in facts
        if fact.field == "email"
    ]

    assert emails == [
        "kontakt@example.no",
        "salg@example.no",
    ]


def test_extracts_phone():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Organisasjonsnummer: 974760673
        Telefon: +47 22 33 44 55
        """,
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    phone_facts = [
        fact for fact in facts
        if fact.field == "phone"
    ]

    assert len(phone_facts) == 1
    assert phone_facts[0].value == "+47 22 33 44 55"


def test_extracts_website():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Organisasjonsnummer: 974760673
        Website: https://www.example.no
        """,
        source_url="https://directory.example.no/company",
        source_name="Example Business Directory",
        retrieved_at=RETRIEVED_AT,
    )

    website_facts = [
        fact for fact in facts
        if fact.field == "website"
    ]

    assert len(website_facts) == 1
    assert website_facts[0].value == "https://www.example.no"


def test_extracts_postal_address():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Organisasjonsnummer: 974760673
        Besøksadresse:
        0150 Oslo
        """,
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    address_facts = [
        fact for fact in facts
        if fact.field == "address"
    ]

    assert len(address_facts) == 1
    assert address_facts[0].value == "0150 Oslo"


def test_returns_no_identity_fact_when_number_is_missing():
    extractor = WebFactExtractor()

    facts = extractor.extract(
        organization_number="974760673",
        page_text="""
        Example Company AS
        Oslo, Norway
        """,
        source_url="https://example.no",
        source_name="Example website",
        retrieved_at=RETRIEVED_AT,
    )

    assert not any(
        fact.field == "organization_number"
        for fact in facts
    )


def test_rejects_empty_organization_number():
    extractor = WebFactExtractor()

    with pytest.raises(ValueError):
        extractor.extract(
            organization_number="",
            page_text="974 760 673",
            source_url="https://example.no",
            source_name="Example website",
        )


def test_rejects_empty_page_text():
    extractor = WebFactExtractor()

    with pytest.raises(ValueError):
        extractor.extract(
            organization_number="974760673",
            page_text="",
            source_url="https://example.no",
            source_name="Example website",
        )


def test_rejects_empty_source_url():
    extractor = WebFactExtractor()

    with pytest.raises(ValueError):
        extractor.extract(
            organization_number="974760673",
            page_text="974760673",
            source_url="",
            source_name="Example website",
        )


def test_rejects_empty_source_name():
    extractor = WebFactExtractor()

    with pytest.raises(ValueError):
        extractor.extract(
            organization_number="974760673",
            page_text="974760673",
            source_url="https://example.no",
            source_name="",
        )