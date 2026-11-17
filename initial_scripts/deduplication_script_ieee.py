
#!/usr/bin/env python3
"""
Deduplication script used in the systematic mapping study on design challenges in
machine learning–based systems.

Purpose:
    This script documents and reproduces the deduplication step applied to
    bibliographic records retrieved from IEEE prior to screening.

Approach:
    - If a DOI is present, duplicates are identified via exact DOI matching.
    - Otherwise, fuzzy matching is applied using RapidFuzz:
        * Title similarity threshold: 90
        * Author similarity threshold: 85

Input/Output:
    - Input:  CSV file (e.g., IEEE export) with columns: Title, DOI, Authors
    - Output: CSV file containing unique records (duplicates removed)


"""

import csv
import re
from rapidfuzz import fuzz

# Thresholds for fuzzy matching
FUZZY_TITLE_THRESHOLD = 90
FUZZY_AUTHOR_THRESHOLD = 85

# Normalization function
def normalize(text):
    return re.sub(r'[^a-z]+', '', str(text).lower().strip())

# Data structures
title_dict = {}      # (short_title, doi, authors) -> count
unique_rows = []     # Store non-duplicate records
num_publications = 0

# Read input file
with open('path/to/exportIEEE.csv', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    headers = reader.fieldnames

    for row in reader:
        num_publications += 1

        raw_title = row.get('Title', '')
        raw_doi = row.get('DOI', '')
        raw_authors = row.get('Authors', '')

        short_title = normalize(raw_title)
        doi = raw_doi.lower().strip()
        authors = raw_authors.lower().strip()

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
            unique_rows.append(row)

# Count duplicates
duplicate_items = {key: count for key, count in title_dict.items() if count > 1}

num_duplicates = sum(duplicate_items.values()) - len(duplicate_items)
num_unique = len(unique_rows)

# Report
print("\n--- Duplicate Report ---")
print(f"Total records: {num_publications}")
print(f"Unique records: {num_unique}")
print(f"Duplicate groups found: {len(duplicate_items)}")
print(f"Duplicates removed: {num_duplicates}")
print("------------------------\n")

# Write output file
output_path = 'path/to/ieee_deduplicated_output.csv'
with open(output_path, mode='w', newline='', encoding='utf-8') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"Cleaned file written to: '{output_path}'")

