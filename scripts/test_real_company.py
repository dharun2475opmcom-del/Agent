from search_agent.agent import CompanyResearcher
from search_agent.search import (
    CompanySearchEngine,
    MockSearchProvider,
)
from search_agent.sources import BRREGClient


def main() -> None:
    organization_number = "974760673"

    researcher = CompanyResearcher(
        brreg_client=BRREGClient(),
        search_engine=CompanySearchEngine(
            provider=MockSearchProvider(),
        ),
    )

    result = researcher.research(
        organization_number,
    )

    print("=" * 70)
    print("COMPANY RESEARCH RESULT")
    print("=" * 70)

    print()
    print("Organization number:")
    print(result.profile.organization_number)

    print()
    print("Facts:")
    print("-" * 70)

    for field, fact in result.profile.facts.items():
        print(f"{field}: {fact.value}")

    print()
    print("Evidence:")
    print("-" * 70)

    for field, fact in result.profile.facts.items():
        evidence = fact.evidence

        print()
        print(f"Field: {field}")
        print(f"Value: {fact.value}")
        print(f"Source: {evidence.source_name}")
        print(f"URL: {evidence.source_url}")
        print(f"Retrieved: {evidence.retrieved_at.isoformat()}")
        print(f"Evidence: {evidence.evidence_text}")
        print(f"Confidence: {evidence.confidence}")

    print()
    print("Official website research:")
    print("-" * 70)
    print(f"Attempted: {result.website_result.attempted}")
    print(f"Verified: {result.website_result.verified}")
    print(f"URL: {result.website_result.url}")
    print(f"Facts added: {result.website_result.facts_added}")

    print()
    print("Search:")
    print("-" * 70)
    print(f"Queries: {result.search_execution.queries}")
    print(f"Results found: {len(result.search_execution.results)}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()