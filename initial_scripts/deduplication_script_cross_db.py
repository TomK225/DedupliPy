#!/usr/bin/env python3

"""
Cross-database deduplication script used in the systematic mapping study on
design challenges in machine learning–based systems.

Purpose:
    This script performs the final cross-database deduplication step after
    database-specific preprocessing of ACM, IEEE, and Scopus records.

Approach:
    - Records from multiple sources (CSV and XLSX) are consolidated.
    - Duplicate records are identified using exact DOI matching.
    - If no DOI match is found, fuzzy string similarity is applied to
      normalized titles and author metadata using predefined thresholds.

Input/Output:
    - Input:  Deduplicated outputs from ACM (XLSX), IEEE (CSV), and Scopus (CSV)
    - Output: Single XLSX file containing unique records across all databases.

Note:
    Database-specific deduplication is performed prior to this step. This script
    only addresses duplicates arising from overlaps between databases.
"""



import re
import pandas as pd
from openpyxl import load_workbook
from rapidfuzz import fuzz

# Parameters (anonymized placeholder paths; adjust to your local setup)
FILES = [
    "path/to/acm_deduplicated_output.xlsx",   # ACM: XLSX
    "path/to/ieee_deduplicated_output.csv",   # IEEE: CSV
    "path/to/scopus_deduplicated_output.csv", # Scopus: CSV
]
FUZZY_TITLE_THRESHOLD = 90
FUZZY_AUTHOR_THRESHOLD = 85

# Helper functions
def normalize(text):
    """Lowercase, strip, and keep letters only (a-z)."""
    return re.sub(r"[^a-z]+", "", str(text).lower().strip())

def normalize_doi(doi):
    """Normalize DOI without removing numbers, slashes or dots."""
    doi = "" if doi is None else str(doi)
    doi = doi.strip().lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    return doi

def iter_rows_any(file_path):
    """
    Yield rows as dicts from either XLSX (first sheet) or CSV.
    """
    if file_path.lower().endswith(".xlsx"):
        wb = load_workbook(file_path)
        ws = wb.active
        headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        for row in ws.iter_rows(min_row=2, values_only=True):
            yield dict(zip(headers, row))

    elif file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        for _, row in df.iterrows():
            yield row.to_dict()

    else:
        raise ValueError(f"Unsupported file type: {file_path}")

# Counters and storage
title_dict = {}  # (short_title, doi, authors) -> count
unique_rows = []
num_publications = 0

# Process all input files
for file in FILES:
    print(f"Processing file: {file}")

    for row_dict in iter_rows_any(file):
        num_publications += 1

        raw_title = row_dict.get("Title", row_dict.get("title", ""))
        raw_doi = row_dict.get("DOI", row_dict.get("doi", ""))
        raw_authors = row_dict.get("Authors", row_dict.get("author", ""))

        short_title = normalize(raw_title)
        doi = normalize_doi(raw_doi)
        authors = normalize(raw_authors)

        found_match = False

        for existing_key in title_dict:
            ex_title, ex_doi, ex_authors = existing_key

            # DOI-first exact match (after normalization)
            if doi and doi == ex_doi:
                title_dict[existing_key] += 1
                found_match = True
                break

            # Otherwise: fuzzy title + author matching
            title_similarity = fuzz.ratio(short_title, ex_title)
            author_similarity = fuzz.ratio(authors, ex_authors)

            if (
                title_similarity >= FUZZY_TITLE_THRESHOLD
                and author_similarity >= FUZZY_AUTHOR_THRESHOLD
            ):
                title_dict[existing_key] += 1
                found_match = True
                break

        if not found_match:
            title_dict[(short_title, doi, authors)] = 1
            unique_rows.append(row_dict)

# Summarize duplicates
duplicate_items = {key: count for key, count in title_dict.items() if count > 1}
num_duplicates = sum(duplicate_items.values()) - len(duplicate_items)
num_unique = len(unique_rows)

# Report
print("\n--- Duplicate Report ---")
print(f"Total records across all files: {num_publications}")
print(f"Unique records:                {num_unique}")
print(f"Duplicate groups found:        {len(duplicate_items)}")
print(f"Duplicates removed:            {num_duplicates}")
print("------------------------\n")

# Write merged, deduplicated output as XLSX (anonymized placeholder path)
output_path = "path/to/combined_deduplicated_output.xlsx"
output_df = pd.DataFrame(unique_rows)
output_df.to_excel(output_path, index=False)

print(f"Cleaned file written to: '{output_path}'")







