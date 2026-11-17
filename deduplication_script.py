#!/usr/bin/env python3
"""
Potential duplicate detection for bibliographic records.

The script identifies potential duplicates using:
    - exact DOI matching
    - fuzzy similarity of titles and author metadata

Input requirements:
    - An Excel file (.xlsx) containing bibliographic records
    - Required columns: title, doi, author
    - The input file path must be specified in the script

The source file is not modified.
Potential duplicates are reported only in the console.
"""

import re
from openpyxl import load_workbook
from rapidfuzz import fuzz


# Thresholds
FUZZY_TITLE_THRESHOLD = 90
FUZZY_AUTHOR_THRESHOLD = 85


# Input file
input_path = (
    "path/to/your/input.xlsx"
)


# ------------------------------------------------------------
# Normalization
# ------------------------------------------------------------

def normalize(text):
    if text is None:
        return ""

    return re.sub(
        r"[^a-z]+",
        "",
        str(text).lower().strip()
    )


def normalize_doi(doi):
    if doi is None:
        return ""

    doi = str(doi).strip().lower()
    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")
    doi = doi.replace("doi:", "")

    return doi.strip()


def normalize_header(header):
    if header is None:
        return ""

    return str(header).strip().lower()


# ------------------------------------------------------------
# Load Excel file
# ------------------------------------------------------------

wb = load_workbook(
    input_path,
    read_only=True,
    data_only=True
)

ws = wb.active

required_columns = {"title", "doi", "author"}

header_row = None
headers = None


# Find header row automatically
for row_number in range(1, min(ws.max_row, 20) + 1):

    candidate_headers = [
        normalize_header(cell.value)
        for cell in ws[row_number]
    ]

    if required_columns.issubset(set(candidate_headers)):
        header_row = row_number
        headers = candidate_headers
        break


if header_row is None:
    raise ValueError(
        "Could not find columns: title, doi, author"
    )


# ------------------------------------------------------------
# Read records
# ------------------------------------------------------------

records = []

for excel_row, row in enumerate(
    ws.iter_rows(
        min_row=header_row + 1,
        values_only=True
    ),
    start=header_row + 1
):

    row_dict = dict(zip(headers, row))

    title = row_dict.get("title")
    doi = row_dict.get("doi")
    author = row_dict.get("author")

    # Ignore completely empty rows
    if title is None and doi is None and author is None:
        continue

    records.append({
        "row": excel_row,
        "title": title,
        "doi": normalize_doi(doi),
        "author": normalize(author),
        "norm_title": normalize(title),
    })


# ------------------------------------------------------------
# Identify potential duplicates
# ------------------------------------------------------------

potential_duplicates = []

for i in range(len(records)):

    a = records[i]

    for j in range(i + 1, len(records)):

        b = records[j]

        # Exact DOI match
        if a["doi"] and b["doi"] and a["doi"] == b["doi"]:

            potential_duplicates.append(
                (a, b, "DOI match")
            )

            continue

        # Fuzzy title + author match
        if (
            a["norm_title"]
            and b["norm_title"]
            and a["author"]
            and b["author"]
        ):

            title_similarity = fuzz.ratio(
                a["norm_title"],
                b["norm_title"]
            )

            author_similarity = fuzz.ratio(
                a["author"],
                b["author"]
            )

            if (
                title_similarity >= FUZZY_TITLE_THRESHOLD
                and
                author_similarity >= FUZZY_AUTHOR_THRESHOLD
            ):

                potential_duplicates.append(
                    (a, b, "Title/author match")
                )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n--- Potential Duplicates ---")

if not potential_duplicates:
    print("No potential duplicates found.")

else:
    for number, (a, b, reason) in enumerate(
        potential_duplicates,
        start=1
    ):
        print(f"\n{number}. {reason}")
        print(f"   Row {a['row']}: {a['title']}")
        print(f"   Row {b['row']}: {b['title']}")

print("\n----------------------------")
print(f"Total records: {len(records)}")
print(
    f"Potential duplicate pairs: "
    f"{len(potential_duplicates)}"
)