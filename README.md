
# DedupliPy

A Python script for detecting potential duplicate bibliographic records in Excel (.xlsx) files.

## Overview

DedupliPy identifies potential duplicate bibliographic records using exact DOI matching and fuzzy similarity matching of titles and author information. It is intended to support the preparation of publication datasets, particularly for systematic literature reviews and mapping studies.

## Requirements

- Python 3
- openpyxl
- rapidfuzz

## Input and Output

The script processes Excel (.xlsx) files containing the following columns:

- `title`
- `doi`
- `author`

The input file path must be specified in the script.

Potential duplicate pairs are reported in the console, including their Excel row numbers. The original input file remains unchanged.

## Usage

Install the required dependencies:

```bash
pip install openpyxl rapidfuzz
```

Set `input_path` in `deduplication_script.py` to the path of your Excel file.

Run the script:

```bash
python deduplication_script.py
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
