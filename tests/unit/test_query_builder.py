import pytest

from search_agent.search import (
    CompanyQueryBuilder,
    CompanySearchContext,
)


def test_query_builder_creates_targeted_queries():
    context = CompanySearchContext(
        organization_number="995880202",
        company_name="Example Company AS",
    )

    queries = CompanyQueryBuilder().build(context)

    assert queries == [
        '"995880202"',
        '"Example Company AS" "995880202"',
        '"Example Company AS" official website',
        '"Example Company AS" Norway',
    ]


def test_query_builder_requires_organization_number():
    context = CompanySearchContext(
        organization_number="",
        company_name="Example Company AS",
    )

    with pytest.raises(ValueError):
        CompanyQueryBuilder().build(context)


def test_query_builder_requires_company_name():
    context = CompanySearchContext(
        organization_number="995880202",
        company_name="",
    )

    with pytest.raises(ValueError):
        CompanyQueryBuilder().build(context)