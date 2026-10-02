"""External company data sources."""

from .brreg import (
    BRREGClient,
    BRREGError,
    BRREGIdentityMismatchError,
    BRREGNotFoundError,
    BRREGRoleClient,
    CompanyRecord,
    CompanyRole,
)
from .html import (
    HTMLExtractionError,
    HTMLTextExtractor,
)
from .web import (
    WebFetchError,
    WebFetcher,
    WebFetchNotFoundError,
    WebPage,
)

__all__ = [
    "BRREGClient",
    "BRREGError",
    "BRREGIdentityMismatchError",
    "BRREGNotFoundError",
    "BRREGRoleClient",
    "CompanyRecord",
    "CompanyRole",
    "HTMLExtractionError",
    "HTMLTextExtractor",
    "WebFetchError",
    "WebFetcher",
    "WebFetchNotFoundError",
    "WebPage",
]
