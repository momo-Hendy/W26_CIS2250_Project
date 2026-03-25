from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import as_number, read_csv


def run_question_2(data_csv: str, start_year: int, end_year: int, output_png: str | None = None, show: bool = True) -> pd.DataFrame:
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype(int)
    df['turnout_percent'] = as_number(df['turnout_percent'])
    filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)].sort_values('year')

    if filtered.empty:
        raise ValueError(f'No rows found between {start_year} and {end_year}. Available years: {df["year"].tolist()}')

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(filtered['year'], filtered['turnout_percent'], marker='o')
    for _, row in filtered.iterrows():
        ax.annotate(f"{row['turnout_percent']:.2f}%", (row['year'], row['turnout_percent']), xytext=(0, 8), ha='center', textcoords='offset points')
    ax.set_title('Voter Turnout Across Canadian Federal Elections')
    ax.set_xlabel('Election Year')
    ax.set_ylabel('Voter turnout percentage (%)')
    ax.set_xticks(filtered['year'].tolist())
    fig.tight_layout()

    if output_png:
        Path(output_png).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_png, bbox_inches='tight')

    print(filtered[['year', 'electors', 'ballots_cast', 'turnout_percent']].to_string(index=False))

    if show:
        plt.show()
    else:
        plt.close(fig)

    return filtered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Answer Question 2: turnout over time.')
    parser.add_argument('--data-csv', required=True, help='Preprocessed CSV from preprocess_q2.py')
    parser.add_argument('--start-year', type=int, required=True)
    parser.add_argument('--end-year', type=int, required=True)
    parser.add_argument('--output-png', help='Optional path to save the graph')
    parser.add_argument('--no-show', action='store_true', help='Do not open a plot window')
    args = parser.parse_args()

    run_question_2(args.data_csv, args.start_year, args.end_year, args.output_png, show=not args.no_show)
