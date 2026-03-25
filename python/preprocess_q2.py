from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import as_number, find_column, parse_file_year_arg, read_csv, save_dataframe


def _summarize_table3(election_csv: str, year: int) -> pd.DataFrame:
    df = read_csv(election_csv)
    electors_col = find_column(df, 'electors', 'number of electors')
    ballots_col = find_column(df, 'total ballots cast', 'ballots cast')
    turnout_col = find_column(
        df,
        'percentage of voter turnout',
        'voter turnout percentage',
        'voter turnout',
        'turnout percentage',
        required=False,
    )

    summary = pd.DataFrame(
        {
            'year': [int(year)],
            'electors': [as_number(df[electors_col]).sum()],
            'ballots_cast': [as_number(df[ballots_col]).sum()],
        }
    )
    summary['turnout_percent'] = summary['ballots_cast'] / summary['electors'] * 100.0

    if turnout_col is not None:
        summary['average_reported_provincial_turnout_percent'] = as_number(df[turnout_col]).mean()
    return summary


def preprocess_q2(election_files_with_years: list[tuple[str, int]], output_csv: str) -> pd.DataFrame:
    pieces = [_summarize_table3(path, year) for path, year in election_files_with_years]
    summary = pd.concat(pieces, ignore_index=True).sort_values('year').drop_duplicates(subset=['year'])
    save_dataframe(summary, output_csv)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess election turnout data for Question 2.')
    parser.add_argument(
        '--election-file',
        action='append',
        required=True,
        help='Election Table 3 CSV with year in FILE:YEAR format. Repeat this flag for multiple years.',
    )
    parser.add_argument('--output-csv', required=True, help='Where to save the preprocessed CSV.')
    args = parser.parse_args()

    file_year_pairs = [parse_file_year_arg(value) for value in args.election_file]
    result = preprocess_q2(file_year_pairs, args.output_csv)
    print(f'Wrote {len(result)} rows to {Path(args.output_csv).resolve()}')
