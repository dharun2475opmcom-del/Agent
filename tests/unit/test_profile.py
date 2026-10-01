from datetime import datetime, timezone

import pytest

from search_agent.agent import CompanyProfile
from search_agent.evidence import Evidence
from search_agent.extractions import CompanyFact


def make_fact(
    organization_number: str,
    field: str,
    value: str,
) -> CompanyFact:
    evidence = Evidence(
        organization_number=organization_number,
        field=field,
        value=value,
        source_name="Test source",
        source_url="https://example.no",
        retrieved_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    return CompanyFact(
        organization_number=organization_number,
        field=field,
        value=value,
        evidence=evidence,
    )


def test_profile_adds_fact():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    fact = make_fact(
        "995880202",
        "name",
        "Example Company AS",
    )

    profile.add_fact(fact)

    assert profile.has("name")
    assert profile.get("name") == "Example Company AS"


def test_profile_rejects_fact_from_different_company():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    fact = make_fact(
        "123456789",
        "name",
        "Different Company AS",
    )

    with pytest.raises(ValueError):
        profile.add_fact(fact)


def test_profile_keeps_existing_fact_when_timestamps_are_equal():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    first = make_fact(
        "995880202",
        "name",
        "Old Company Name",
    )

    second = make_fact(
        "995880202",
        "name",
        "New Company Name",
    )

    profile.add_fact(first)
    profile.add_fact(second)

    assert profile.get("name") == "Old Company Name"
    assert len(profile.facts) == 1


def test_profile_to_dict():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    profile.add_fact(
        make_fact(
            "995880202",
            "name",
            "Example Company AS",
        )
    )

    data = profile.to_dict()

    assert data["organization_number"] == "995880202"
    assert data["facts"]["name"]["value"] == "Example Company AS"
    assert (
        data["facts"]["name"]["evidence"]["source_url"]
        == "https://example.no"
    )


def make_fact_at(
    organization_number: str,
    field: str,
    value: str,
    day: int,
) -> CompanyFact:
    evidence = Evidence(
        organization_number=organization_number,
        field=field,
        value=value,
        source_name="Test source",
        source_url="https://example.no",
        retrieved_at=datetime(
            2026,
            1,
            day,
            tzinfo=timezone.utc,
        ),
    )

    return CompanyFact(
        organization_number=organization_number,
        field=field,
        value=value,
        evidence=evidence,
    )


def test_profile_keeps_newer_fact():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    old_fact = make_fact_at(
        "995880202",
        "name",
        "Old Company Name",
        1,
    )

    new_fact = make_fact_at(
        "995880202",
        "name",
        "New Company Name",
        2,
    )

    profile.add_fact(old_fact)
    profile.add_fact(new_fact)

    assert profile.get("name") == "New Company Name"


def test_profile_does_not_replace_newer_fact_with_older_fact():
    profile = CompanyProfile(
        organization_number="995880202",
    )

    newer_fact = make_fact_at(
        "995880202",
        "name",
        "New Company Name",
        2,
    )

    older_fact = make_fact_at(
        "995880202",
        "name",
        "Old Company Name",
        1,
    )

    profile.add_fact(newer_fact)
    profile.add_fact(older_fact)

    assert profile.get("name") == "New Company Name"