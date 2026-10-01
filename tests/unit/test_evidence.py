from datetime import datetime, timezone

import pytest

from search_agent.evidence import Evidence


def test_create_evidence():
    retrieved_at = datetime.now(timezone.utc)

    evidence = Evidence(
        organization_number="995880202",
        field="name",
        value="Example Company AS",
        source_name="BRREG",
        source_url="https://data.brreg.no/",
        retrieved_at=retrieved_at,
        evidence_text="Example Company AS",
        confidence=1.0,
    )

    assert evidence.organization_number == "995880202"
    assert evidence.field == "name"
    assert evidence.value == "Example Company AS"
    assert evidence.source_name == "BRREG"
    assert evidence.source_url == "https://data.brreg.no/"
    assert evidence.retrieved_at == retrieved_at
    assert evidence.confidence == 1.0


def test_source_date_is_optional():
    evidence = Evidence(
        organization_number="995880202",
        field="name",
        value="Example Company AS",
        source_name="BRREG",
        source_url="https://data.brreg.no/",
        retrieved_at=datetime.now(timezone.utc),
    )

    assert evidence.source_date is None
    assert evidence.evidence_text is None


def test_empty_organization_number_is_rejected():
    with pytest.raises(ValueError):
        Evidence(
            organization_number="",
            field="name",
            value="Example Company AS",
            source_name="BRREG",
            source_url="https://data.brreg.no/",
            retrieved_at=datetime.now(timezone.utc),
        )


def test_empty_field_is_rejected():
    with pytest.raises(ValueError):
        Evidence(
            organization_number="995880202",
            field="",
            value="Example Company AS",
            source_name="BRREG",
            source_url="https://data.brreg.no/",
            retrieved_at=datetime.now(timezone.utc),
        )


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError):
        Evidence(
            organization_number="995880202",
            field="name",
            value="Example Company AS",
            source_name="BRREG",
            source_url="https://data.brreg.no/",
            retrieved_at=datetime.now(timezone.utc),
            confidence=1.5,
        )


def test_negative_confidence_is_rejected():
    with pytest.raises(ValueError):
        Evidence(
            organization_number="995880202",
            field="name",
            value="Example Company AS",
            source_name="BRREG",
            source_url="https://data.brreg.no/",
            retrieved_at=datetime.now(timezone.utc),
            confidence=-0.1,
        )