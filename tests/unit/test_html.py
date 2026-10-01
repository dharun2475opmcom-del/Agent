import pytest

from search_agent.sources import (
    HTMLExtractionError,
    HTMLTextExtractor,
)


def test_extracts_visible_text():
    html = """
    <html>
        <head>
            <title>Example Company</title>
        </head>
        <body>
            <h1>Example Company AS</h1>
            <p>We provide software services in Norway.</p>
        </body>
    </html>
    """

    text = HTMLTextExtractor().extract(html)

    assert "Example Company" in text
    assert "Example Company AS" in text
    assert "We provide software services in Norway." in text


def test_removes_scripts_and_styles():
    html = """
    <html>
        <head>
            <style>
                body { color: red; }
            </style>
            <script>
                console.log("secret");
            </script>
        </head>
        <body>
            <p>Visible company information.</p>
        </body>
    </html>
    """

    text = HTMLTextExtractor().extract(html)

    assert "Visible company information." in text
    assert "color: red" not in text
    assert 'console.log("secret")' not in text


def test_normalizes_whitespace():
    html = """
    <html>
        <body>
            <p>
                Company
                information
            </p>
        </body>
    </html>
    """

    text = HTMLTextExtractor().extract(html)

    assert "Company" in text
    assert "information" in text
    assert "Company\ninformation" == text


def test_extracts_multiple_elements_as_lines():
    html = """
    <html>
        <body>
            <h1>Example Company AS</h1>
            <p>Founded in 2015.</p>
            <p>Located in Norway.</p>
        </body>
    </html>
    """

    text = HTMLTextExtractor().extract(html)

    assert text.splitlines() == [
        "Example Company AS",
        "Founded in 2015.",
        "Located in Norway.",
    ]


def test_rejects_empty_html():
    with pytest.raises(HTMLExtractionError):
        HTMLTextExtractor().extract("")


def test_rejects_non_string_html():
    with pytest.raises(HTMLExtractionError):
        HTMLTextExtractor().extract(None)