from search_agent.sources import (
    HTMLTextExtractor,
    WebFetcher,
)


def main() -> None:
    url = "https://www.brreg.no/"

    fetcher = WebFetcher()
    extractor = HTMLTextExtractor()

    page = fetcher.fetch(url)
    text = extractor.extract(page.text)

    print("=" * 70)
    print("URL:")
    print(page.url)
    print()
    print("HTTP status:")
    print(page.status_code)
    print()
    print("Content type:")
    print(page.content_type)
    print()
    print("Extracted text:")
    print("=" * 70)
    print(text[:5000])
    print("=" * 70)


if __name__ == "__main__":
    main()