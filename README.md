
# DedupliPy

Python scripts for detecting potential duplicate bibliographic records in Excel (.xlsx) and CSV files.

## Overview

DedupliPy provides Python scripts for identifying and processing duplicate bibliographic records using DOI matching and string similarity techniques. The scripts were used to support the preparation of publication datasets for a systematic mapping study.

The repository contains the initial scripts for database-specific and cross-database deduplication, as well as an updated script for identifying potential duplicate records.



## Repository Structure

- `deduplication_script.py` – Updated script for identifying potential duplicate records in Excel files.
- `initial_scripts/` – Initial scripts used for bibliographic record deduplication:
  - `deduplication_script_acm.py` – Deduplication of ACM records.
  - `deduplication_script_ieee.py` – Deduplication of IEEE records.
  - `deduplication_script_scopus.py` – Deduplication of Scopus records.
  - `deduplication_script_cross_db.py` – Consolidation and deduplication of records across ACM, IEEE, and Scopus.


    
## Requirements

- Python 3
- openpyxl
- rapidfuzz
- pandas

## Input and Output

The updated script processes Excel (.xlsx) files containing the following columns:

- `title`
- `doi`
- `author`

The input file path must be specified in the script.

Potential duplicate pairs are reported in the console, including their Excel row numbers. The original input file remains unchanged.

The initial scripts process CSV and Excel files and generate deduplicated output files.

## Usage

Install the required dependencies:

```bash
pip install openpyxl rapidfuzz pandas 
```

Set `input_path` in `deduplication_script.py` to the path of your Excel file.

Run the updated script:

```bash
python deduplication_script.py
```

The initial scripts can be run separately after configuring their respective input and output file paths.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
