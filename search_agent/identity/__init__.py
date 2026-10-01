"""Identity utilities for Norwegian company organization numbers."""

from .matcher import EntityMatch, EntityMatcher
from .resolver import (
    IdentityResolver,
    InvalidOrganizationNumber,
    is_valid_org_number,
    normalize_org_number,
    validate_org_number,
)
from .web_matcher import WebIdentityMatcher

__all__ = [
    "EntityMatch",
    "EntityMatcher",
    "IdentityResolver",
    "InvalidOrganizationNumber",
    "WebIdentityMatcher",
    "is_valid_org_number",
    "normalize_org_number",
    "validate_org_number",
]