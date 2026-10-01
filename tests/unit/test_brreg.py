from unittest.mock import Mock, patch

import pytest
import requests

from search_agent.sources.brreg import (
    BRREGClient,
    BRREGError,
    BRREGIdentityMismatchError,
    BRREGNotFoundError,
)


ORG_NUMBER = "995880202"


def make_brreg_response(
    organization_number: str = ORG_NUMBER,
) -> dict:
    """Return a representative BRREG API response."""

    return {
        "organisasjonsnummer": organization_number,
        "navn": "Example Company AS",
        "organisasjonsform": {
            "kode": "AS",
            "beskrivelse": "Aksjeselskap",
        },
        "registrertIMvaRegisteret": True,
        "registreringsdatoEnhetsregisteret": "2010-01-15",
        "forretningsadresse": {
            "adresse": ["Example Street 10"],
            "postnummer": "0123",
            "poststed": "Oslo",
            "kommune": "Oslo",
        },
        "naeringskode1": {
            "kode": "62.010",
            "beskrivelse": "Programmeringstjenester",
        },
        "hjemmeside": "https://example.no",
    }


def mock_response(
    status_code: int = 200,
    json_data: dict | None = None,
) -> Mock:
    """Create a mocked requests.Response."""

    response = Mock()
    response.status_code = status_code

    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("Invalid JSON")

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    else:
        response.raise_for_status.return_value = None

    return response


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_success(mock_get):
    """A valid BRREG response should become a CompanyRecord."""

    mock_get.return_value = mock_response(
        json_data=make_brreg_response()
    )

    client = BRREGClient()

    company = client.get_company(ORG_NUMBER)

    assert company.organization_number == ORG_NUMBER
    assert company.name == "Example Company AS"
    assert company.organization_form == "AS"
    assert company.vat_registered is True
    assert company.registration_date == "2010-01-15"
    assert company.business_address == "Example Street 10"
    assert company.postal_code == "0123"
    assert company.postal_place == "Oslo"
    assert company.municipality == "Oslo"
    assert company.industry_code == "62.010"
    assert company.industry_description == "Programmeringstjenester"
    assert company.website == "https://example.no"

    mock_get.assert_called_once()


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_normalizes_input(mock_get):
    """Formatted organization numbers should be normalized."""

    mock_get.return_value = mock_response(
        json_data=make_brreg_response()
    )

    client = BRREGClient()

    company = client.get_company("NO 995-880-202")

    assert company.organization_number == ORG_NUMBER

    requested_url = mock_get.call_args.args[0]
    assert requested_url.endswith(f"/{ORG_NUMBER}")


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_not_found(mock_get):
    """BRREG 404 should become BRREGNotFoundError."""

    mock_get.return_value = mock_response(status_code=404)

    client = BRREGClient()

    with pytest.raises(BRREGNotFoundError):
        client.get_company(ORG_NUMBER)


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_http_error(mock_get):
    """Unexpected HTTP errors should become BRREGError."""

    mock_get.return_value = mock_response(status_code=500)

    client = BRREGClient()

    with pytest.raises(BRREGError):
        client.get_company(ORG_NUMBER)


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_invalid_json(mock_get):
    """Invalid JSON should become BRREGError."""

    mock_get.return_value = mock_response(status_code=200)

    client = BRREGClient()

    with pytest.raises(BRREGError):
        client.get_company(ORG_NUMBER)


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_identity_mismatch(mock_get):
    """A response for another organization must be rejected."""

    different_org_number = "889640782"

    mock_get.return_value = mock_response(
        json_data=make_brreg_response(
            organization_number=different_org_number
        )
    )

    client = BRREGClient()

    with pytest.raises(BRREGIdentityMismatchError):
        client.get_company(ORG_NUMBER)


@patch("search_agent.sources.brreg.requests.get")
def test_get_company_network_error(mock_get):
    """Network failures should become BRREGError."""

    mock_get.side_effect = requests.RequestException(
        "Connection failed"
    )

    client = BRREGClient()

    with pytest.raises(BRREGError):
        client.get_company(ORG_NUMBER)


def test_invalid_organization_number_is_rejected_before_request():
    """Invalid organization numbers should never reach BRREG."""

    client = BRREGClient()

    with patch("search_agent.sources.brreg.requests.get") as mock_get:
        with pytest.raises(ValueError):
            client.get_company("123456789")

        mock_get.assert_not_called()