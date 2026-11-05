"""Cases found by checking the HowToLiveBetter book (2026-11-05): all were false alarms."""

import json

from claimcite.check import check_reference, quote_found
from claimcite.extract import extract_references
from claimcite.models import Record, Reference
from claimcite.sources import parse_crossref


def crossref(**message):
    return json.dumps({"message": {"DOI": "10.1/x", **message}})


def test_crossref_title_markup_is_removed():
    escaped = (
        "Number of Deaths due to Carbon Monoxide Poisoning&lt;sup&gt;&lt;xref ref-type=\"fn\" rid=\"pn1\"&gt;"
        "①&lt;/xref&gt;&lt;/sup&gt; by Month — China, 2018"
    )
    assert parse_crossref(crossref(title=[escaped])).title == (
        "Number of Deaths due to Carbon Monoxide Poisoning by Month — China, 2018"
    )
    assert parse_crossref(crossref(title=["Effect of Long-term Vitamin D\n   <sub>3</sub>\n Supplementation"])).title == (
        "Effect of Long-term Vitamin D3 Supplementation"
    )
    assert parse_crossref(crossref(title=["<i>Do</i>\n   Men Overperceive"])).title == "Do Men Overperceive"


def test_journal_and_pages_are_not_a_title():
    text = "Dargie E 等 (2015). Journal of Sex & Marital Therapy, 41(2), 181-202. <https://doi.org/10.1080/0092623X.2013.864367>"
    (ref,) = extract_references(text)
    assert ref.title is None


def test_any_publication_year_counts():
    # Online first in 2024, in a 2026 issue: authors usually cite the issue year.
    record = parse_crossref(crossref(
        title=["Return-to-Work After Attempted Digit Replantation"],
        issued={"date-parts": [[2024, 10]]},
        **{"published-print": {"date-parts": [[2026, 1]]}, "published-online": {"date-parts": [[2024, 10, 3]]}},
    ))

    class OneRecord:
        def doi(self, _):
            return record

    ref = Reference("doi", "10.1/x", 1, year=2026, title="Return-to-Work After Attempted Digit Replantation")
    f = check_reference(ref, OneRecord())
    assert f.year_match is True
    assert f.status == "ok"

    ref.year = 2021
    assert check_reference(ref, OneRecord()).year_match is False


def test_multiplication_sign_matches_x():
    assert quote_found("8 x 8", "the so-called 8 × 8 rule") is True


def test_pubmed_record_years_include_epub_date():
    r = Record(source="pubmed", year=2026, years=[2026, 2024])
    assert 2024 in r.years
