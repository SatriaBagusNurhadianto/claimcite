from claimcite.extract import extract_references

LINE = (
    "- 来源：Jha P 等 (2013). 21st-century hazards of smoking and benefits of cessation "
    "in the United States. NEJM. <https://doi.org/10.1056/NEJMsa1211128>；"
    "Öberg M, Jaakkola MS (2011). Worldwide burden of disease from exposure to second-hand "
    "smoke: a retrospective analysis of data from 192 countries. Lancet：「603,000 deaths were "
    "attributable to second-hand smoke in 2004」，「61% of DALYs were in children」. "
    "<https://doi.org/10.1016/S0140-6736(10)61388-8>（二手烟那两个数字）；"
    "上海市卫生健康委员会 (2021). 选对药物. <https://wsjkw.sh.gov.cn/jtyx/20211119/x.html>"
)


def test_extracts_dois_with_stated_metadata():
    refs = extract_references(LINE)
    dois = [r for r in refs if r.kind == "doi"]
    assert [r.id for r in dois] == ["10.1056/nejmsa1211128", "10.1016/s0140-6736(10)61388-8"]

    first, second = dois
    assert first.year == 2013
    assert first.title == "21st-century hazards of smoking and benefits of cessation in the United States"
    assert first.quotes == []
    assert first.line == 1

    assert second.year == 2011
    assert second.title.startswith("Worldwide burden of disease")
    assert second.quotes == [
        "603,000 deaths were attributable to second-hand smoke in 2004",
        "61% of DALYs were in children",
    ]


def test_plain_web_links_are_kept_but_not_identifiers():
    refs = extract_references(LINE)
    assert refs[-1].kind == "url"
    assert refs[-1].year == 2021


def test_pmid_forms():
    text = "Aspirin did not help (PMID: 30221596). See also https://pubmed.ncbi.nlm.nih.gov/31055709/"
    refs = extract_references(text)
    assert [(r.kind, r.id) for r in refs] == [("pmid", "30221596"), ("pmid", "31055709")]


def test_bare_doi_and_trailing_punctuation():
    text = "Coffee and mortality, doi:10.1007/s10654-019-00524-3.\nSecond line 10.1039/d0fo00787k;"
    refs = extract_references(text)
    assert [(r.id, r.line) for r in refs] == [
        ("10.1007/s10654-019-00524-3", 1),
        ("10.1039/d0fo00787k", 2),
    ]


def test_english_quotes_are_extracted():
    text = 'Smith J (2020). A trial. BMJ: "the effect was null". https://doi.org/10.1136/bmj.x1'
    (ref,) = extract_references(text)
    assert ref.quotes == ["the effect was null"]
