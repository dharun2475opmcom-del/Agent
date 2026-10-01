from search_agent.search import (
    CompanySearchEngine,
    CompanySearchContext,
    MockSearchProvider,
    SearchResult,
)


def test_search_engine_executes_all_queries():
    provider = MockSearchProvider(
        [
            SearchResult(
                title="Example Company",
                url="https://example.no",
                source="test",
            )
        ]
    )

    engine = CompanySearchEngine(provider)

    context = CompanySearchContext(
        organization_number="995880202",
        company_name="Example Company AS",
    )

    execution = engine.search(
        context,
        max_results_per_query=1,
    )

    assert len(execution.queries) == 4
    assert len(execution.results) == 4

    assert execution.queries[0] == '"995880202"'
    assert execution.results[0].url == "https://example.no"


def test_search_engine_respects_max_results_per_query():
    provider = MockSearchProvider(
        [
            SearchResult(
                title="Result 1",
                url="https://example.no/1",
            ),
            SearchResult(
                title="Result 2",
                url="https://example.no/2",
            ),
            SearchResult(
                title="Result 3",
                url="https://example.no/3",
            ),
        ]
    )

    engine = CompanySearchEngine(provider)

    context = CompanySearchContext(
        organization_number="995880202",
        company_name="Example Company AS",
    )

    execution = engine.search(
        context,
        max_results_per_query=2,
    )

    assert len(execution.results) == 8


def test_search_engine_rejects_invalid_result_limit():
    provider = MockSearchProvider()
    engine = CompanySearchEngine(provider)

    context = CompanySearchContext(
        organization_number="995880202",
        company_name="Example Company AS",
    )

    try:
        engine.search(
            context,
            max_results_per_query=0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass