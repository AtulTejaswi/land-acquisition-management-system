"""Unit tests for workbook normalization (pure functions, no DB)."""

import pytest

from app.ml.normalize import (
    cell_text,
    is_compound_survey,
    map_land_type,
    map_ownership_status,
    normalize_party_type,
    normalize_survey_number,
    normalize_text,
    parcel_dedupe_key,
    parse_area_hectares,
    strip_quotes,
    survey_number_head,
)


def test_cell_text_collapses_line_breaks():
    assert cell_text('242\n२४२') == "242 २४२"
    assert cell_text(None) is None
    assert cell_text("  spaced   out  ") == "spaced out"


def test_strip_quotes_removes_wrapping_quotes():
    assert strip_quotes('"Wet"') == "Wet"
    assert strip_quotes('"Government"') == "Government"
    assert strip_quotes("no quotes") == "no quotes"


def test_normalize_text_casefolds_and_collapses():
    assert normalize_text('  "KHORDHA"\n') == "khordha"
    assert normalize_text(None) is None


def test_normalize_survey_number_bilingual():
    raw = "244\n/789 &\n244\n/955\n२४४/\n७८९ &\n२४४/\n९५५"
    normalized = normalize_survey_number(raw)
    # Bilingual form collapses duplicate transliterated segments
    assert normalized == "244/789&244/955"
    assert survey_number_head(raw) == 244
    assert is_compound_survey(raw) is True
    assert is_compound_survey("242\n२४२") is False


def test_parse_area_hectares():
    from decimal import Decimal
    assert parse_area_hectares("0.0607\nHectares") == (Decimal("0.0607"), None)
    assert parse_area_hectares("0.0607 Hectares") == (Decimal("0.0607"), None)
    value, error = parse_area_hectares("12 hectares")
    assert value == Decimal("12") and error is None
    value, error = parse_area_hectares(None)
    assert value is None and error == "missing area"
    value, error = parse_area_hectares("about one acre")
    assert value is None and "non-numeric" in error
    value, error = parse_area_hectares("-5\nHectares")
    assert value is None and "non-positive" in error


def test_parcel_dedupe_key_deterministic():
    a = parcel_dedupe_key("KHORDHA", "Khordha", "Kanjiama", "242\n२४२")
    b = parcel_dedupe_key("khordha ", "khordha", "kanjiama", "242")
    assert a == b
    assert a != parcel_dedupe_key("KHORDHA", "Khordha", "Kanjiama", "243")


def test_map_land_type():
    assert map_land_type('"Wet"') == ("agricultural", False)
    assert map_land_type('"Residential"') == ("residential", True)
    value, mapped = map_land_type('"Gharabari"')
    assert value == "gharabari" and mapped is False
    value, mapped = map_land_type(None)
    assert value == "other" and mapped is False


def test_map_ownership_status_is_source_reported():
    assert map_ownership_status('"Government"') == ("govt", True)
    assert map_ownership_status('"Private"') == ("private", True)
    value, mapped = map_ownership_status(None)
    assert value == "private" and mapped is False


def test_normalize_party_type_variants():
    assert normalize_party_type("Owner") == ("owner", True)
    assert normalize_party_type("Owner Affected Party Affected Party")[0] == "owner"
    value, mapped = normalize_party_type("Tenant")
    assert value == "tenant" and mapped is False
    assert normalize_party_type(None) == ("unknown", False)
