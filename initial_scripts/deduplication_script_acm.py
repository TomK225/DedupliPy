#!/usr/bin/env python3
"""
Deduplication script used in the systematic mapping study on design challenges in
machine learning–based systems.

Purpose:
    This script documents and reproduces the deduplication step applied to ACM
    bibliographic records exported as an Excel file prior to screening.

Approach:
    - If a DOI is available, duplicates are identified via exact DOI matching.
    - Otherwise, fuzzy string matching is applied separately to normalized titles
      and author strings using RapidFuzz with predefined similarity thresholds.

Input/Output:
    - Input:  XLSX file containing bibliographic metadata with columns: title, doi, author
    - Output: XLSX file containing unique records (duplicates removed)


"""

import re
from openpyxl import load_workbook
import pandas as pd
from rapidfuzz import fuzz

# Thresholds
FUZZY_TITLE_THRESHOLD = 90
FUZZY_AUTHOR_THRESHOLD = 85

# Normalization
def normalize(text):
    return re.sub(r'[^a-z]+', '', str(text).lower().strip())

def normalize_doi(doi):
    """Normalize DOI without removing numbers, slashes or dots."""
    doi = "" if doi is None else str(doi)
    doi = doi.strip().lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    return doi

# Prepare variables
title_dict = {}   # (short_title, doi, authors) -> count
unique_rows = []  # store deduplicated records
num_publications = 0

# Load Excel file (anonymized placeholder path; adjust to your local setup)
wb = load_workbook('path/to/acm_export.xlsx')
ws = wb.active
headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]

# Iterate over rows
for row in ws.iter_rows(min_row=2, values_only=True):
    num_publications += 1

    row_dict = dict(zip(headers, row))
    raw_title = row_dict.get('title', '')
    raw_doi = row_dict.get('doi', '')
    raw_authors = row_dict.get('author', '')

    short_title = normalize(raw_title)
    doi = normalize_doi(raw_doi)
    authors = normalize(raw_authors)

    found_match = False

    for existing_key in title_dict:
        ex_title, ex_doi, ex_authors = existing_key

        if doi and doi == ex_doi:
            title_dict[existing_key] += 1
            found_match = True
            break

        title_similarity = fuzz.ratio(short_title, ex_title)
        author_similarity = fuzz.ratio(authors, ex_authors)

        if title_similarity >= FUZZY_TITLE_THRESHOLD and author_similarity >= FUZZY_AUTHOR_THRESHOLD:
            title_dict[existing_key] += 1
            found_match = True
            break

    if not found_match:
        title_dict[(short_title, doi, authors)] = 1
        unique_rows.append(row_dict)

# Count duplicates
duplicate_items = {key: count for key, count in title_dict.items() if count > 1}
num_duplicates = sum(duplicate_items.values()) - len(duplicate_items)
num_unique = len(unique_rows)

# Print statistics
print("\n--- Duplicate Report ---")
print(f"Total records: {num_publications}")
print(f"Unique records: {num_unique}")
print(f"Duplicate groups found: {len(duplicate_items)}")
print(f"Duplicates removed: {num_duplicates}")
print("------------------------\n")

# Write new XLSX file (anonymized placeholder path; adjust to your local setup)
output_path = 'path/to/acm_deduplicated_output.xlsx'
output_df = pd.DataFrame(unique_rows)
output_df.to_excel(output_path, index=False)

print(f"Cleaned file written to: '{output_path}'")






