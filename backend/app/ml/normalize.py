"""Pure normalization helpers for BhoomiRashi workbook ingestion.

All functions are deterministic and side-effect free so they can be shared by
the ingestion pipeline, the offline training script, and inference-time feature
preparation. Raw source values are never mutated in place; normalized forms
are always derived copies.
"""

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Optional

# Odia/Devanagari and ASCII digit ranges, mapped positionally to ASCII digits
_DIGIT_TRANSLATION = str.maketrans(
    "୦୧୨୩୪୫୬୭୮୯०१२३४५६७८९01２34５67８9",
    "012345678901234567890123456789",
)

_QUOTED_RE = re.compile(r'^"(.*)"$', re.DOTALL)


def cell_text(value) -> Optional[str]:
    """Cell value to collapsed single-line text, or None for empty cells."""
    if value is None:
        return None
    text = str(value).replace("\r", "\n")
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text or None


def raw_text(value) -> Optional[str]:
    """Cell value preserved exactly as-is (only type-coerced) for auditability."""
    if value is None:
        return None
    return str(value)


def strip_quotes(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    match = _QUOTED_RE.match(value.strip())
    return match.group(1).strip() if match else value.strip()


def normalize_text(value: Optional[str]) -> Optional[str]:
    """Deterministic normalization for search/matching only: NFKC, casefold,
    quote removal, whitespace collapse. Never used to overwrite raw values."""
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", value)
    text = strip_quotes(text) or ""
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold() or None


def transliterate_digits(value: str) -> str:
    """Map Odia/Devanagari digit glyphs to ASCII digits (one-to-one, positional)."""
    return value.translate(_DIGIT_TRANSLATION)


def normalize_survey_number(raw: Optional[str]) -> Optional[str]:
    """Normalized searchable form of a (possibly bilingual/compound) survey number:
    keep ASCII digits, '/', '&', '-', letters; drop spaces. Raw value is preserved
    separately by the caller.

    Handles bilingual (English + Odia/Devanagari) forms where the same number
    appears in two scripts separated by whitespace/newlines: the duplicate
    transliterated segments are collapsed.
    """
    if raw is None:
        return None
    # NFKC + transliterate all digits to ASCII
    ascii_form = transliterate_digits(unicodedata.normalize("NFKC", raw))
    # Strip everything except digits, letters, /, &, -
    ascii_form = re.sub(r"[^0-9A-Za-z/&\-]", "", ascii_form)
    if not ascii_form:
        return None
    # Detect bilingual duplication: if the string is exactly
    # repeated (e.g. "242242" or "244/789&244/955244/789&244/955"),
    # collapse to the first half.
    n = len(ascii_form)
    for half in range(n // 2, 0, -1):
        if n % half == 0 and ascii_form[:half] * (n // half) == ascii_form:
            return ascii_form[:half]
    return ascii_form


def survey_number_head(raw: Optional[str]) -> Optional[int]:
    """Leading numeric part of a survey number (feature for inference).
    Returns None when the number does not start with digits."""
    normalized = normalize_survey_number(raw)
    if not normalized:
        return None
    match = re.match(r"\d+", normalized)
    return int(match.group(0)) if match else None


def is_compound_survey(raw: Optional[str]) -> bool:
    normalized = normalize_survey_number(raw)
    return bool(normalized) and ("/" in normalized or "&" in normalized)


def parse_area_hectares(raw: Optional[str]) -> tuple[Optional[Decimal], Optional[str]]:
    """Parse an area cell like '0.0607\\nHectares'.

    Returns (value, None) on success, (None, reason) when the cell is empty or
    not a plain positive number after removing only the presentation word
    'Hectares'/'Acres'-style suffixes. Ambiguous values are rejected, not guessed.
    """
    if raw is None:
        return None, "missing area"
    text = unicodedata.normalize("NFKC", str(raw))
    text = re.sub(r"(?i)hectares?", "", text)
    text = re.sub(r"\s+", "", text)
    if not text:
        return None, "empty area"
    try:
        value = Decimal(text)
    except InvalidOperation:
        return None, f"non-numeric area: {str(raw)[:50]!r}"
    if value <= 0:
        return None, f"non-positive area: {value}"
    return value, None


def parcel_dedupe_key(district: str, sub_district: str, village: str,
                      survey_number: str) -> str:
    """Deterministic dedupe key for a parcel row: normalized location + normalized
    survey number."""
    parts = [normalize_text(x) or "" for x in (district, sub_district, village)]
    parts.append(normalize_survey_number(survey_number) or "")
    return "|".join(parts)


def party_dedupe_key(source_sno: str, name: str, address: Optional[str]) -> str:
    """Deterministic dedupe key for a party row."""
    parts = [normalize_text(source_sno) or "",
             normalize_text(name) or "",
             normalize_text(address) or ""]
    return "|".join(parts)


def normalize_party_type(raw: Optional[str]) -> tuple[str, bool]:
    """Map workbook party type to NLAMS vocabulary.

    Returns (canonical, mapped). 'Owner ...' variants collapse to 'owner';
    anything else is preserved as a lowercased unmapped source value.
    """
    normalized = normalize_text(raw)
    if not normalized:
        return "unknown", False
    if normalized.startswith("owner"):
        return "owner", True
    return normalized, False


def map_land_type(raw: Optional[str]) -> tuple[str, bool]:
    """Map workbook Land Type to the LandParcel.land_type vocabulary.
    Returns (canonical, mapped); unmapped values are preserved lowercased."""
    normalized = normalize_text(raw)
    mapping = {"wet": "agricultural", "dry": "agricultural", "agricultural": "agricultural",
               "residential": "residential", "commercial": "commercial",
               "forest": "forest", "government": "govt", "govt": "govt"}
    if not normalized:
        return "other", False
    if normalized in mapping:
        return mapping[normalized], normalized in ("agricultural", "residential", "commercial", "forest", "govt")
    return normalized, False


def map_ownership_status(raw: Optional[str]) -> tuple[str, bool]:
    """Map workbook Land Nature to OwnershipStatus vocabulary.
    NOTE: this is a source-reported classification, NOT verified legal title."""
    normalized = normalize_text(raw)
    if normalized == "government":
        return "govt", True
    if normalized == "private":
        return "private", True
    if not normalized:
        return "private", False
    return normalized, False
