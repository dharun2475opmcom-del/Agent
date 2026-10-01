from search_agent.search import BraveSearchProvider


def main() -> None:
    provider = BraveSearchProvider()

    results = provider.search(
        '"974760673"',
        max_results=10,
    )

    print("=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    for index, result in enumerate(results, start=1):
        print()
        print(f"{index}. {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}")
        print(f"Source: {result.source}")

    print()
    print("=" * 70)
    print(f"TOTAL RESULTS: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    main()