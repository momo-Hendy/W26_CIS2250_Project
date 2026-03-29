#!/usr/bin/env python3

'''
preprocess_q1.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      preprocess_q1.py reads Elections Canada Table 3 CSV files
      and a Statistics Canada CPI CSV file, then merges the
      voter turnout data with the CPI yearly change data.

      The script computes the year-over-year CPI percentage
      change from the raw CPI index values, and matches them
      to the election years.

      The output CSV contains the following columns:
          year, electors, ballots_cast, turnout_percent,
          cpi_yearly_change_percent

     Commandline Parameters: 4+
        sys.argv[1] = output CSV file path
        sys.argv[2] = CPI CSV file path
        sys.argv[3] = first election file in FILE:YEAR format
        sys.argv[4] = (optional) additional election files in FILE:YEAR format
'''

#
#   Packages and modules
#
import sys
import csv
import re
import os

import pandas as pd

from utils import as_number, find_column, parse_file_year_arg
from utils import read_csv, save_dataframe
from preprocess_q2 import preprocess_q2


#
# Define any "constants" for the file here.
# Names of constants should be in UPPER_CASE.
#
MONTHS = {
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
}


#
#   Functions
#

def extract_cpi_by_year(cpi_csv):
    '''
    Read a Statistics Canada CPI CSV file and extract the
    year-over-year CPI percentage change for each year.

    Supports two formats:
        1. The standard tidy StatCan "database loading" format
           with columns like REF_DATE, GEO, VALUE, UOM
        2. The wide "download entire table" layout

    If the UOM indicates raw index values (e.g. 2002=100),
    the function computes the year-over-year percentage change.
    If the values are already percentage changes, they are
    used directly.

    Returns a DataFrame with columns: year, cpi_yearly_change_percent
    '''

    #
    # Try the standard tidy StatCan format first
    #
    try:
        df = read_csv(cpi_csv)
    except Exception:
        df = None

    if df is not None and set(df.columns) != {df.columns[0]}:

        year_col = find_column(df, 'REF_DATE', 'ref_date', 'year',
                               required=False)
        value_col = find_column(df, 'VALUE', 'value', required=False)
        geo_col = find_column(df, 'GEO', 'geography', 'geo',
                              required=False)
        product_col = find_column(df, 'Products and product groups',
                                  'products', required=False)

        if year_col and value_col:
            tidy = df.copy()

            # Filter to Canada only if geography column exists
            if geo_col:
                canada_mask = tidy[geo_col].astype(str).str.contains(
                    r'^Canada$', case=False, na=False
                )
                if canada_mask.any():
                    tidy = tidy[canada_mask]

            # Filter to All-items only if product column exists
            if product_col:
                all_items_mask = tidy[product_col].astype(str).str.contains(
                    'all-items|all items', case=False, na=False
                )
                if all_items_mask.any():
                    tidy = tidy[all_items_mask]

            # Check if the UOM indicates raw index values
            uom_col = find_column(df, 'UOM', 'uom', required=False)
            is_raw_index = False
            if uom_col:
                uom_vals = tidy[uom_col].astype(str).str.lower().unique()
                # If UOM contains '=100' (e.g. '2002=100'), it is a raw index
                is_raw_index = any('=100' in v for v in uom_vals)

            # Extract year and CPI value from each row
            tidy = tidy[[year_col, value_col]].copy()
            extracted_years = tidy[year_col].astype(str).str.extract(
                r'(\d{4})'
            )[0]
            tidy['year'] = pd.to_numeric(extracted_years, errors='coerce')
            tidy['cpi_value'] = as_number(tidy[value_col])
            tidy = tidy.dropna(subset=['year', 'cpi_value'])

            if is_raw_index and not tidy.empty:
                # Compute average CPI index per year, then compute
                # the year-over-year percentage change
                yearly_avg = tidy.groupby(
                    'year', as_index=False
                )['cpi_value'].mean()
                yearly_avg = yearly_avg.sort_values('year')
                yearly_avg['cpi_yearly_change_percent'] = (
                    yearly_avg['cpi_value'].pct_change() * 100.0
                )
                yearly_avg = yearly_avg.dropna(
                    subset=['cpi_yearly_change_percent']
                )
                if not yearly_avg.empty:
                    return yearly_avg[['year', 'cpi_yearly_change_percent']]

            elif not tidy.empty:
                # VALUE is already a percentage change, use it directly
                tidy = tidy.rename(
                    columns={'cpi_value': 'cpi_yearly_change_percent'}
                )
                return tidy[['year', 'cpi_yearly_change_percent']].groupby(
                    'year', as_index=False
                ).mean()

    #
    # Fallback: try the "download entire table" wide layout
    #
    parsed_rows = []

    try:
        fh = open(cpi_csv, encoding='utf-8-sig', newline='')
    except IOError as err:
        print("Unable to open CPI file '{}': {}".format(
            cpi_csv, err), file=sys.stderr)
        sys.exit(1)

    reader = csv.reader(fh)
    for row in reader:
        parsed_rows.append(row)
    fh.close()

    # Normalize all rows to the same length
    max_len = max(len(r) for r in parsed_rows)
    normalized_rows = [r + [''] * (max_len - len(r)) for r in parsed_rows]
    rows = pd.DataFrame(normalized_rows).fillna('')

    # Search for the Geography and Products header rows
    canada_row_idx = None
    header_idx = None
    units_idx = None
    data_start_idx = None

    for i in range(len(rows)):
        first = str(rows.iloc[i, 0]).strip()

        if first == 'Geography':
            row_vals = rows.iloc[i, 1:].tolist()
            if any(str(x).strip() == 'Canada' for x in row_vals):
                canada_row_idx = i

        if first.startswith('Products and product groups'):
            header_idx = i
            units_idx = i + 1
            data_start_idx = i + 2
            break

    if header_idx is None:
        print("Error: Could not understand the CPI CSV structure.",
              file=sys.stderr)
        sys.exit(1)

    # Verify that we found Canada in the geography row
    if canada_row_idx is not None:
        geography = str(rows.iloc[canada_row_idx, 1]).strip()
    else:
        geography = ''

    if geography.lower() != 'canada':
        print("Error: The CPI file does not appear to be filtered "
              "to Canada.", file=sys.stderr)
        sys.exit(1)

    # Extract the headers and units rows
    headers = [str(x).strip() for x in rows.iloc[header_idx].tolist()]
    units = [str(x).strip() for x in rows.iloc[units_idx].tolist()]

    # Get the data rows
    data = rows.iloc[data_start_idx:].copy()
    data.columns = headers

    # Find the All-items row
    product_col = headers[0]
    all_items = data[
        data[product_col].astype(str).str.contains(
            'all-items|all items', case=False, na=False
        )
    ]

    if all_items.empty:
        print("Error: Could not find an All-items row in the CPI CSV.",
              file=sys.stderr)
        sys.exit(1)

    all_items_row = all_items.iloc[0]

    # Extract year and CPI percentage change from column headers
    records = []
    for col, unit in zip(headers[1:], units[1:]):
        col_text = col.lower()
        unit_text = unit.lower()

        year_match = re.search(r'(\d{4})', col_text)
        month_match = any(month in col_text for month in MONTHS)

        if year_match and ('percentage change' in unit_text) and month_match:
            cpi_val = as_number(
                pd.Series([all_items_row[col]])
            ).iloc[0]

            records.append({
                'year': int(year_match.group(1)),
                'cpi_yearly_change_percent': float(cpi_val),
            })

    result = pd.DataFrame(records)
    result = result.dropna()
    result = result.drop_duplicates(subset=['year'])
    result = result.sort_values('year')

    if result.empty:
        print("Error: The CPI file was parsed but no usable data "
              "was found for the election years.", file=sys.stderr)
        sys.exit(1)

    return result

    #
    #   End of Function
    #


def preprocess_q1(election_files_with_years, cpi_csv, output_csv):
    '''
    Main preprocessing function for Question 1. Combines election
    turnout data from Table 3 files with CPI data from Statistics
    Canada.

    Parameters:
        election_files_with_years - list of (filename, year) tuples
        cpi_csv - path to the Statistics Canada CPI CSV file
        output_csv - path to save the combined output CSV

    Returns the merged DataFrame.
    '''

    # First get the election turnout summary using preprocess_q2
    # We save to a temporary file that will be cleaned up
    tmp_output = output_csv.replace('.csv', '_tmp_turnout.csv')
    election_summary = preprocess_q2(election_files_with_years, tmp_output)

    # Then get the CPI data
    cpi_summary = extract_cpi_by_year(cpi_csv)

    # Merge the two datasets on the year column
    merged = election_summary.merge(cpi_summary, on='year', how='inner')
    merged = merged.sort_values('year')

    if merged.empty:
        election_years = election_summary['year'].tolist()
        cpi_years = cpi_summary['year'].tolist()
        print("Error: No overlapping years found between election "
              "and CPI data.", file=sys.stderr)
        print("  Election years: {}".format(election_years),
              file=sys.stderr)
        print("  CPI years: {}".format(cpi_years), file=sys.stderr)
        sys.exit(1)

    # Save the combined result
    save_dataframe(merged, output_csv)

    # Clean up the temporary file
    if os.path.exists(tmp_output):
        os.remove(tmp_output)

    return merged

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and runs the preprocessing pipeline for Question 1.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) < 4:
        print("Usage: preprocess_q1.py <output csv> <cpi csv> "
              "<election file:year> [election file:year ...]")
        sys.exit(1)

    output_csv = argv[1]
    cpi_csv = argv[2]

    # Parse all the election file arguments
    file_year_pairs = []
    for i in range(3, len(argv)):
        try:
            pair = parse_file_year_arg(argv[i])
            file_year_pairs.append(pair)
        except ValueError as err:
            print("Error parsing argument '{}': {}".format(
                argv[i], err), file=sys.stderr)
            sys.exit(1)

    # Run the preprocessing
    result = preprocess_q1(file_year_pairs, cpi_csv, output_csv)
    print("Wrote {} rows to {}".format(len(result), output_csv))

    #
    #   End of Function
    #


##
## Call our main function, passing the system argv as the parameter
##
if __name__ == "__main__":
    main(sys.argv)


#
#   End of Script
#
