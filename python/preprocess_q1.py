from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re

import pandas as pd

from utils import as_number, find_column, parse_file_year_arg, read_csv, save_dataframe
from preprocess_q2 import preprocess_q2


MONTHS = {
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
}


def _extract_cpi_by_year(cpi_csv: str) -> pd.DataFrame:
    # Try the standard tidy StatCan format first.
    try:
        df = read_csv(cpi_csv)
    except Exception:
        df = None

    if df is not None and set(df.columns) != {df.columns[0]}:
        year_col = find_column(df, 'REF_DATE', 'ref_date', 'year', required=False)
        value_col = find_column(df, 'VALUE', 'value', required=False)
        geo_col = find_column(df, 'GEO', 'geography', 'geo', required=False)
        product_col = find_column(df, 'Products and product groups', 'products', required=False)
        if year_col and value_col:
            tidy = df.copy()
            if geo_col:
                canada_mask = tidy[geo_col].astype(str).str.contains(r'^Canada$', case=False, na=False)
                if canada_mask.any():
                    tidy = tidy[canada_mask]
            if product_col:
                all_items_mask = tidy[product_col].astype(str).str.contains('all-items|all items', case=False, na=False)
                if all_items_mask.any():
                    tidy = tidy[all_items_mask]
            tidy = tidy[[year_col, value_col]].copy()
            # Keep only year-like REF_DATE rows.
            extracted_years = tidy[year_col].astype(str).str.extract(r'(\d{4})')[0]
            tidy['year'] = pd.to_numeric(extracted_years, errors='coerce')
            tidy['cpi_yearly_change_percent'] = as_number(tidy[value_col])
            tidy = tidy.dropna(subset=['year', 'cpi_yearly_change_percent'])
            if not tidy.empty:
                return tidy[['year', 'cpi_yearly_change_percent']].groupby('year', as_index=False).mean()

    # Fallback for the "download entire table" wide layout.
    parsed_rows = []
    with open(cpi_csv, encoding='utf-8-sig', newline='') as fh:
        reader = csv.reader(fh)
        for row in reader:
            parsed_rows.append(row)
    max_len = max(len(r) for r in parsed_rows)
    normalized_rows = [r + [''] * (max_len - len(r)) for r in parsed_rows]
    rows = pd.DataFrame(normalized_rows).fillna('')
    canada_row_idx = None
    header_idx = None
    units_idx = None
    data_start_idx = None
    for i in range(len(rows)):
        first = str(rows.iloc[i, 0]).strip()
        if first == 'Geography' and any(str(x).strip() == 'Canada' for x in rows.iloc[i, 1:].tolist()):
            canada_row_idx = i
        if first.startswith('Products and product groups'):
            header_idx = i
            units_idx = i + 1
            data_start_idx = i + 2
            break

    if header_idx is None:
        raise ValueError('Could not understand the CPI CSV structure.')

    geography = str(rows.iloc[canada_row_idx, 1]).strip() if canada_row_idx is not None else ''
    if geography.lower() != 'canada':
        raise ValueError('The uploaded CPI file does not appear to be filtered to Canada in a way this script can use.')

    headers = [str(x).strip() for x in rows.iloc[header_idx].tolist()]
    units = [str(x).strip() for x in rows.iloc[units_idx].tolist()]
    data = rows.iloc[data_start_idx:].copy()
    data.columns = headers
    product_col = headers[0]
    all_items = data[data[product_col].astype(str).str.contains('all-items|all items', case=False, na=False)]
    if all_items.empty:
        raise ValueError('Could not find an All-items row in the CPI CSV.')
    all_items_row = all_items.iloc[0]

    records: list[dict[str, float]] = []
    for col, unit in zip(headers[1:], units[1:]):
        col_text = col.lower()
        unit_text = unit.lower()
        year_match = re.search(r'(\d{4})', col_text)
        month_match = any(month in col_text for month in MONTHS)
        if year_match and ('percentage change' in unit_text) and month_match:
            records.append(
                {
                    'year': int(year_match.group(1)),
                    'cpi_yearly_change_percent': float(as_number(pd.Series([all_items_row[col]])).iloc[0]),
                }
            )

    result = pd.DataFrame(records).dropna().drop_duplicates(subset=['year']).sort_values('year')
    if result.empty:
        raise ValueError(
            'The uploaded CPI file was parsed, but it only contains recent monthly percentage-change columns and not the historical election years needed for Q1.'
        )
    return result


def preprocess_q1(election_files_with_years: list[tuple[str, int]], cpi_csv: str, output_csv: str) -> pd.DataFrame:
    election_summary = preprocess_q2(election_files_with_years, output_csv=Path(output_csv).with_name('_tmp_q1_turnout.csv'))
    cpi_summary = _extract_cpi_by_year(cpi_csv)
    merged = election_summary.merge(cpi_summary, on='year', how='inner').sort_values('year')
    if merged.empty:
        available_election_years = election_summary['year'].tolist()
        available_cpi_years = cpi_summary['year'].tolist()
        raise ValueError(
            'No overlapping years were found between election turnout and CPI data. '
            f'Election years: {available_election_years}. CPI years: {available_cpi_years}.'
        )
    save_dataframe(merged, output_csv)
    return merged


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess election turnout and CPI data for Question 1.')
    parser.add_argument(
        '--election-file',
        action='append',
        required=True,
        help='Election Table 3 CSV with year in FILE:YEAR format. Repeat for multiple years.',
    )
    parser.add_argument('--cpi-csv', required=True, help='Statistics Canada CPI CSV.')
    parser.add_argument('--output-csv', required=True, help='Where to save the preprocessed CSV.')
    args = parser.parse_args()

    file_year_pairs = [parse_file_year_arg(value) for value in args.election_file]
    result = preprocess_q1(file_year_pairs, args.cpi_csv, args.output_csv)
    print(f'Wrote {len(result)} rows to {Path(args.output_csv).resolve()}')
