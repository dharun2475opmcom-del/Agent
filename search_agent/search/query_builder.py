"""Build targeted web-search queries for company research."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanySearchContext:
    """Identity information used to construct search queries."""

    organization_number: str
    company_name: str


class CompanyQueryBuilder:
    """Build deterministic search queries for a company."""

    def build(self, context: CompanySearchContext) -> list[str]:
        """Return a small set of high-value search queries."""

        org_number = context.organization_number.strip()
        company_name = context.company_name.strip()

        if not org_number:
            raise ValueError("organization_number cannot be empty.")

        if not company_name:
            raise ValueError("company_name cannot be empty.")

        return [
            f'"{org_number}"',
            f'"{company_name}" "{org_number}"',
            f'"{company_name}" official website',
            f'"{company_name}" Norway',
        ]