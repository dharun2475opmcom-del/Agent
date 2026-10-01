import pytest

from search_agent.identity import WebIdentityMatcher


def test_matches_formatted_organization_number():
    page_text = """
    Kontakt oss

    Organisasjonsnummer:
    974 760 673
    """

    matcher = WebIdentityMatcher()

    assert matcher.matches(
        page_text,
        organization_number="974760673",
    )


def test_matches_unformatted_organization_number():
    page_text = """
    Organisasjonsnummer: 974760673
    """

    matcher = WebIdentityMatcher()

    assert matcher.matches(
        page_text,
        organization_number="974 760 673",
    )


def test_rejects_different_organization():
    page_text = """
    Organisasjonsnummer: 974 760 673
    """

    matcher = WebIdentityMatcher()

    assert not matcher.matches(
        page_text,
        organization_number="995880202",
    )


def test_rejects_empty_page():
    matcher = WebIdentityMatcher()

    with pytest.raises(ValueError):
        matcher.matches(
            "",
            organization_number="974760673",
        )


def test_rejects_empty_organization_number():
    matcher = WebIdentityMatcher()

    with pytest.raises(ValueError):
        matcher.matches(
            "Organisasjonsnummer: 974 760 673",
            organization_number="",
        )


def test_rejects_invalid_organization_number_length():
    matcher = WebIdentityMatcher()

    with pytest.raises(ValueError):
        matcher.matches(
            "Organisasjonsnummer: 974 760 673",
            organization_number="1234",
        )


def test_rejects_non_string_page_text():
    matcher = WebIdentityMatcher()

    with pytest.raises(ValueError):
        matcher.matches(
            None,
            organization_number="974760673",
        )