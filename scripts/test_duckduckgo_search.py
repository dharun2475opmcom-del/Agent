from search_agent.search.duckduckgo import (
    DUCKDUCKGO_HTML_URL,
    DuckDuckGoSearchProvider,
)


def main() -> None:
    import requests

    response = requests.get(
        DUCKDUCKGO_HTML_URL,
        params={
            "q": '"974760673"',
        },
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=10,
    )

    print("=" * 70)
    print("HTTP STATUS")
    print("=" * 70)
    print(response.status_code)

    print()
    print("=" * 70)
    print("CONTENT TYPE")
    print("=" * 70)
    print(response.headers.get("Content-Type"))

    print()
    print("=" * 70)
    print("FINAL URL")
    print("=" * 70)
    print(response.url)

    print()
    print("=" * 70)
    print("RESPONSE LENGTH")
    print("=" * 70)
    print(len(response.text))

    print()
    print("=" * 70)
    print("FIRST 5000 CHARACTERS")
    print("=" * 70)
    print(response.text[:5000])


if __name__ == "__main__":
    main()