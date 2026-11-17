#!/usr/bin/env python3
"""
Deduplication script used in the systematic mapping study on design challenges in
machine learning–based systems.

Purpose:
    This script supports transparency and reproducibility by documenting the
    deduplication step applied to retrieved bibliographic records prior to screening.

Approach:
    Potential duplicates are identified using a composite key built from:
    - DOI (lowercased, trimmed),
    - normalized title (lowercased, alphanumeric only),
    - normalized author list (split, cleaned, sorted).
    The script then applies string similarity (SequenceMatcher) to compare keys
    and removes records considered duplicates.

Input/Output:
    - Input:  CSV export (e.g., from Scopus) with at least the columns
              'Title', 'DOI', and 'Authors' (configurable below).
    - Output: CSV file containing only unique records.

Note:

    This script uses a composite-key similarity approach which differs slightly
    from the DOI-first fuzzy matching used in the ACM/IEEE deduplication script.
"""

import csv
import re
from difflib import SequenceMatcher

# --- File paths (anonymized placeholders; adjust to your local setup) ---
input_file = "path/to/export_scopus.csv"
output_file = "path/to/export_scopus_deduplicated.csv"

title_col = "Title"
doi_col = "DOI"
author_col = "Authors"

cleaned_rows = []
duplicates = []

# === Helper functions ===
def normalize_title(title):
    title = "" if title is None else str(title)
    return re.sub(r"[^a-z0-9]+", "", title.lower())

def normalize_authors(authors):
    authors = "" if authors is None else str(authors)
    author_list = [a.strip().lower().replace(",", "") for a in authors.split(",") if a.strip()]
    return ",".join(sorted(author_list))

def similar(a, b, threshold=0.95):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def generate_key(row):
    title = normalize_title(row.get(title_col, ''))
    doi = row.get(doi_col, '').strip().lower()
    authors = normalize_authors(row.get(author_col, ''))
    return f"{doi}_{title}_{authors}"

# === Processing ===
seen_keys = []
with open(input_file, newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    headers = reader.fieldnames

    for row in reader:
        current_key = generate_key(row)
        is_duplicate = False

        for key in seen_keys:
            if similar(key, current_key):
                is_duplicate = True
                duplicates.append(row)
                break

        if not is_duplicate:
            seen_keys.append(current_key)
            cleaned_rows.append(row)

# === Write results ===
with open(output_file, mode='w', newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=headers)
    writer.writeheader()
    writer.writerows(cleaned_rows)

# === Preview & statistics ===
print("Extended duplicate detection completed.")
print(f"Original records:            {len(cleaned_rows) + len(duplicates)}")
print(f"Removed duplicates:          {len(duplicates)}")
print(f"Saved unique records:        {len(cleaned_rows)} -> '{output_file}'")

if duplicates:
    print("\nDuplicate preview (max. 5):")
    for dup in duplicates[:5]:
        print("•", dup.get(title_col, 'Unknown title'))
    if len(duplicates) > 5:
        print("...and additional duplicates were detected.")
else:
    print("\nNo duplicates found.")
