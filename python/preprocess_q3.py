from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import as_number, clean_party_name, find_column, parse_file_year_arg, read_csv, save_dataframe


def _pick_party_column(df: pd.DataFrame) -> str:
    return find_column(
        df,
        'political affiliation',
        'political party',
        'party',
        'affiliation',
        'name of political party',
    )


def _extract_total_vote_column(df: pd.DataFrame, party_col: str) -> str | None:
    return find_column(df, 'Total', 'Canada', required=False)


def preprocess_q3(table8_csv: str, table9_csv: str, year: int, output_csv: str) -> pd.DataFrame:
    votes_df = read_csv(table8_csv)
    pct_df = read_csv(table9_csv)

    party_col_votes = _pick_party_column(votes_df)
    party_col_pct = _pick_party_column(pct_df)
    vote_col = _extract_total_vote_column(votes_df, party_col_votes)
    pct_col = _extract_total_vote_column(pct_df, party_col_pct)

    if vote_col is not None:
        votes = votes_df[[party_col_votes, vote_col]].copy()
        votes.columns = ['party', 'valid_votes']
        votes['valid_votes'] = as_number(votes['valid_votes'])
    else:
        provincial_vote_cols = [c for c in votes_df.columns if c != party_col_votes]
        votes = votes_df[[party_col_votes] + provincial_vote_cols].copy()
        votes['valid_votes'] = sum(as_number(votes[c]).fillna(0) for c in provincial_vote_cols)
        votes = votes[[party_col_votes, 'valid_votes']]
        votes.columns = ['party', 'valid_votes']
    votes['party'] = votes['party'].map(clean_party_name)

    pct = pct_df[[party_col_pct, pct_col]].copy()
    pct.columns = ['party', 'vote_percent']
    pct['party'] = pct['party'].map(clean_party_name)
    pct['vote_percent'] = as_number(pct['vote_percent'])

    merged = votes.merge(pct, on='party', how='inner')
    merged['year'] = int(year)
    merged = merged.dropna(subset=['party', 'vote_percent'])
    merged = merged[(merged['vote_percent'] > 0) | (merged['valid_votes'] > 0)]
    merged = merged.sort_values('vote_percent', ascending=False).reset_index(drop=True)
    save_dataframe(merged, output_csv)
    return merged


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess party vote data for Question 3.')
    parser.add_argument('--table8-csv', required=True, help='Election Table 8 CSV for one election year.')
    parser.add_argument('--table9-csv', required=True, help='Election Table 9 CSV for one election year.')
    parser.add_argument('--year', type=int, required=True, help='Election year represented by these files.')
    parser.add_argument('--output-csv', required=True, help='Where to save the preprocessed CSV.')
    args = parser.parse_args()

    result = preprocess_q3(args.table8_csv, args.table9_csv, args.year, args.output_csv)
    print(f'Wrote {len(result)} rows to {Path(args.output_csv).resolve()}')
