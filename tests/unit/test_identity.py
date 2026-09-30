import pytest

from search_agent.identity import (
    IdentityResolver,
    InvalidOrganizationNumber,
    is_valid_org_number,
    normalize_org_number,
    validate_org_number,
)


def test_normalize_org_number():
    assert normalize_org_number("995 880 202") == "995880202"
    assert normalize_org_number("NO 995 880 202") == "995880202"


def test_valid_org_number():
    assert is_valid_org_number("995880202") is True
    assert validate_org_number("995 880 202") == "995880202"


def test_invalid_checksum():
    assert is_valid_org_number("995880201") is False

    with pytest.raises(InvalidOrganizationNumber):
        validate_org_number("995880201")


def test_invalid_length():
    with pytest.raises(InvalidOrganizationNumber):
        normalize_org_number("1234")


def test_identity_resolver():
    resolver = IdentityResolver()
    assert resolver.resolve("NO 995-880-202") == "995880202"
