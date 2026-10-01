from datetime import datetime, timezone

import pytest

from search_agent.evidence import Evidence, FreshnessChecker


def make_evidence(
    *,
    organization_number: str = "995880202",
    field: str = "name",
    value: str = "Example Company AS",
    day: int = 1,
) -> Evidence:
    return Evidence(
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


def test_detects_changed_value():
    old = make_evidence(
        value="Old Company Name",
        day=1,
    )

    new = make_evidence(
        value="New Company Name",
        day=2,
    )

    change = FreshnessChecker().compare(old, new)

    assert change.field == "name"
    assert change.old_value == "Old Company Name"
    assert change.new_value == "New Company Name"
    assert change.changed is True


def test_detects_unchanged_value():
    old = make_evidence(day=1)
    new = make_evidence(day=2)

    change = FreshnessChecker().compare(old, new)

    assert change.changed is False


def test_detects_newer_evidence():
    old = make_evidence(day=1)
    new = make_evidence(day=2)

    assert FreshnessChecker().is_newer(old, new) is True


def test_detects_older_evidence():
    old = make_evidence(day=2)
    new = make_evidence(day=1)

    assert FreshnessChecker().is_newer(old, new) is False


def test_rejects_different_organizations():
    old = make_evidence(
        organization_number="995880202",
    )

    new = make_evidence(
        organization_number="123456789",
    )

    with pytest.raises(ValueError):
        FreshnessChecker().compare(old, new)


def test_rejects_different_fields():
    old = make_evidence(field="name")
    new = make_evidence(field="website")

    with pytest.raises(ValueError):
        FreshnessChecker().compare(old, new)