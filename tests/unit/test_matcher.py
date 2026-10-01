import pytest

from search_agent.identity import EntityMatcher
from search_agent.search import SearchResult


def test_matcher_accepts_exact_organization_number():
    result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
        snippet="Organization number 995880202",
    )

    match = EntityMatcher().match(
        result,
        organization_number="995880202",
        company_name="Example Company AS",
    )

    assert match.organization_number_match is True
    assert match.company_name_match is True
    assert match.score == 1.0
    assert match.accepted is True


def test_matcher_accepts_company_name_with_lower_score():
    result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
        snippet="Official company website",
    )

    match = EntityMatcher().match(
        result,
        organization_number="995880202",
        company_name="Example Company AS",
    )

    assert match.organization_number_match is False
    assert match.company_name_match is True
    assert match.score == 0.2
    assert match.accepted is False


def test_matcher_rejects_unrelated_result():
    result = SearchResult(
        title="Completely Different Company",
        url="https://different.no",
        snippet="Another company",
    )

    match = EntityMatcher().match(
        result,
        organization_number="995880202",
        company_name="Example Company AS",
    )

    assert match.organization_number_match is False
    assert match.company_name_match is False
    assert match.score == 0.0
    assert match.accepted is False


def test_matcher_rejects_empty_identity():
    result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
    )

    with pytest.raises(ValueError):
        EntityMatcher().match(
            result,
            organization_number="",
            company_name="Example Company AS",
        )


def test_matcher_rejects_empty_company_name():
    result = SearchResult(
        title="Example Company AS",
        url="https://example.no",
    )

    with pytest.raises(ValueError):
        EntityMatcher().match(
            result,
            organization_number="995880202",
            company_name="",
        )