# Data Import — bhoomirashi.gov.in Export

## Source File

**File:** `[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features (1).xlsx`

- **Origin:** bhoomirashi.gov.in (Government of Odisha land records portal)
- **Notification:** S.O. 1988E
- **Tentative Publish Date:** 22/06/2020
- **Scope:** Khordha district, Khordha tahsil, 6 villages in Odisha

### Sheet Contents

| Sheet | Rows | Description |
|-------|------|-------------|
| Document Information | 2 | Provenance metadata (title, publish date) |
| Land Details | 249 | Survey numbers with area, land type, nature, category |
| Land Parties | 478 | Owner/party records linked to survey numbers |

### Villages Covered

1. Kanjiama
2. Saradhapur
3. Taratua
4. Kumbharabasta
5. Wilkisannagar
6. Gurujanga

## Running the Import

```bash
# From the backend directory
python -m app.scripts.import_bhoomirashi_xlsx

# Or via seed script (creates tables + roles + users + imports data)
python -m app.seed
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `BHOOMIRASHI_XLSX` | No | Path to xlsx file (auto-detected if in repo root) |

### Idempotency

The import script is idempotent:
- **Truncate mode** (default in seed.py): Deletes all existing parcels in Odisha state before re-importing.
- **Upsert mode**: On (survey_number, village) unique constraint — updates existing, inserts new.

## Data Cleaning

### Bilingual Fields

The bhoomirashi export contains multi-line cells with English and Odia (Devanagari) text:

```
"Anabadi\nअनबाडी"
```

The import script splits these into `name_en` and `name_or` components using Unicode block detection:
- Lines with more Devanagari characters (U+0900–U+097F) → Odia
- Lines with more Latin characters → English

Embedded `"` characters from the source are stripped.

### Area Parsing

Area values like `"0.0607\nHectares"` are parsed to extract the numeric hectare value (0.0607).

### Ownership Mapping

| Source (`Land Nature`) | Target (`ownership_status`) |
|------------------------|---------------------------|
| Government | `govt` |
| Private | `private` |

### Land Type Mapping

All parcels in this dataset have `Land Type = "Wet"`. The `LandType` enum was extended with a `wet` value (Alembic migration `004_landtype_wet_village_coords`).

## Geocoding

### Method

Village coordinates were sourced from **OpenStreetMap Nominatim** (August 2026):

| Village | Latitude | Longitude | Source |
|---------|----------|-----------|--------|
| Kanjiama | 20.1750 | 85.6300 | Estimated (Khordha tahsil centroid + offset) |
| Saradhapur | 20.1860 | 85.5892 | Nominatim confirmed |
| Taratua | 20.1900 | 85.6100 | Estimated (Khordha tahsil centroid + offset) |
| Kumbharabasta | 20.1800 | 85.6000 | Estimated (Khordha tahsil centroid + offset) |
| Wilkisannagar | 20.1920 | 85.6350 | Estimated (Khordha tahsil centroid + offset) |
| Gurujanga | 20.1966 | 85.6220 | Nominatim confirmed |

### Known Limitations

1. **4 of 6 villages** could not be resolved by Nominatim (too small/not in OSM). Coordinates are estimated from the Khordha tahsil centroid (~20.186, 85.623) with small offsets.
2. **Parcel markers are village-level approximations**, not surveyed boundaries. Each parcel's Point is at the village centroid + random jitter (±200m) to prevent stacking.
3. **No true polygon geometry** exists in the source data. When surveyed parcel polygons become available, the `geom` column can be upgraded from Point to Polygon without schema changes.
4. **Bilingual text cleaning** may imperfectly separate English/Odia in complex mixed-script cells (e.g., addresses with both scripts on the same line).

## Dashboard Data

The following charts are computed from the imported data:

- **Parcels by Village** (bar chart): Count of survey numbers per village
- **Area by Village** (bar chart): Total hectares per village
- **Area by Ownership** (pie chart): Government vs private land area
- **Co-ownership Distribution** (bar chart): How many parcels have 1, 2, 3, 4, 5+ owners

## Extending the Import

To add data from another district or state:

1. Place the new xlsx file in the repo root
2. Update `import_bhoomirashi_xlsx.py` if the column structure differs
3. Add village coordinates to `VILLAGE_COORDS`
4. Run the import with `truncate=False` to append without deleting existing data
