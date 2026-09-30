"""Normalize and validate Norwegian organization numbers."""

from __future__ import annotations

import re


class InvalidOrganizationNumber(ValueError):
    """Raised when an organization number is malformed or invalid."""


_WEIGHTS = (3, 2, 7, 6, 5, 4, 3, 2)


def normalize_org_number(value: str) -> str:
    """Return a canonical 9-digit organization number.

    Accepts common formatting such as spaces, hyphens, and the optional
    Norwegian "NO" prefix.
    """
    if not isinstance(value, str):
        raise InvalidOrganizationNumber("Organization number must be a string.")

    cleaned = value.strip().upper()
    if cleaned.startswith("NO"):
        cleaned = cleaned[2:]

    digits = re.sub(r"[^0-9]", "", cleaned)

    if len(digits) != 9:
        raise InvalidOrganizationNumber(
            "Organization number must contain exactly 9 digits."
        )

    return digits


def is_valid_org_number(value: str) -> bool:
    """Return True when the organization number passes Modulus-11 validation."""
    try:
        org_number = normalize_org_number(value)
    except InvalidOrganizationNumber:
        return False

    digits = [int(digit) for digit in org_number]
    weighted_sum = sum(
        digit * weight for digit, weight in zip(digits[:8], _WEIGHTS)
    )

    remainder = weighted_sum % 11
    check_digit = 0 if remainder == 0 else 11 - remainder

    return check_digit != 10 and check_digit == digits[8]


def validate_org_number(value: str) -> str:
    """Normalize and validate an organization number."""
    org_number = normalize_org_number(value)

    if not is_valid_org_number(org_number):
        raise InvalidOrganizationNumber(
            f"Invalid Norwegian organization number: {org_number}"
        )

    return org_number


class IdentityResolver:
    """Resolve raw input to a validated canonical organization number."""

    def resolve(self, value: str) -> str:
        return validate_org_number(value)
