"""Command-line interface for company research."""

from __future__ import annotations

import argparse
import json
import sys

from search_agent.agent import CompanyResearcher
from search_agent.search import BraveSearchProvider, CompanySearchEngine
from search_agent.sources import BRREGClient


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="python -m search_agent",
        description="Research a Norwegian company by organization number.",
    )
    parser.add_argument(
        "organization_number",
        help="Norwegian 9-digit organization number.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum search results per query (default: 5).",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Run the company research CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        provider = BraveSearchProvider()
        search_engine = CompanySearchEngine(
            provider=provider,
        )
        researcher = CompanyResearcher(
            brreg_client=BRREGClient(),
            search_engine=search_engine,
        )

        result = researcher.research(
            args.organization_number,
        )

        payload = result.profile.to_dict()
        payload["search"] = {
            "queries": result.search_execution.queries,
            "result_count": len(result.search_execution.results),
            "accepted_result_count": sum(
                match.accepted
                for match in result.matched_results
            ),
        }
        payload["website"] = {
            "attempted": result.website_result.attempted,
            "verified": result.website_result.verified,
            "url": result.website_result.url,
            "facts_added": result.website_result.facts_added,
        }

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
