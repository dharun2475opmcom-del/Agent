from search_agent.cli import run


def test_cli_requires_brave_api_key(monkeypatch, capsys):
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)

    exit_code = run(["974760673"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "api key" in captured.err.lower()


def test_cli_outputs_company_profile(monkeypatch, capsys):
    class FakeResult:
        profile = type(
            "Profile",
            (),
            {
                "to_dict": lambda self: {
                    "organization_number": "974760673",
                    "facts": {},
                }
            },
        )()

        search_execution = type(
            "SearchExecution",
            (),
            {
                "queries": ['"974760673"'],
                "results": [],
            },
        )()

        matched_results = []

        website_result = type(
            "WebsiteResult",
            (),
            {
                "attempted": True,
                "verified": True,
                "url": "https://example.no",
                "facts_added": 1,
            },
        )()

    class FakeResearcher:
        def __init__(self, **kwargs):
            pass

        def research(self, organization_number):
            assert organization_number == "974760673"
            return FakeResult()

    monkeypatch.setattr(
        "search_agent.cli.BraveSearchProvider",
        lambda: object(),
    )
    monkeypatch.setattr(
        "search_agent.cli.CompanyResearcher",
        FakeResearcher,
    )

    exit_code = run(["974760673"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"organization_number": "974760673"' in captured.out
    assert '"verified": true' in captured.out
