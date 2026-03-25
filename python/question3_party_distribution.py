from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import as_number, read_csv


def run_question_3(data_csv: str, year: int, top_n: int | None = None, output_png: str | None = None, show: bool = True) -> pd.DataFrame:
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype('Int64')
    filtered = df[df['year'] == year].copy()

    if filtered.empty:
        raise ValueError(f'No data found for year {year} in {data_csv}.')

    filtered['vote_percent'] = as_number(filtered['vote_percent'])
    filtered['valid_votes'] = as_number(filtered['valid_votes'])
    filtered = filtered.dropna(subset=['vote_percent']).sort_values('vote_percent', ascending=True)
    if top_n is not None:
        filtered = filtered.tail(top_n)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(filtered['party'], filtered['vote_percent'])
    for _, row in filtered.iterrows():
        ax.annotate(f"{row['vote_percent']:.2f}%", (row['vote_percent'], row['party']), xytext=(6, 0), va='center', textcoords='offset points')

    ax.set_title(f'Vote Distribution by Political Party ({year})')
    ax.set_xlabel('Percentage of valid votes (%)')
    ax.set_ylabel('Political party name')
    fig.tight_layout()

    if output_png:
        Path(output_png).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_png, bbox_inches='tight')

    print(filtered[['party', 'valid_votes', 'vote_percent']].sort_values('vote_percent', ascending=False).to_string(index=False))

    if show:
        plt.show()
    else:
        plt.close(fig)

    return filtered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Answer Question 3: party vote distribution.')
    parser.add_argument('--data-csv', required=True, help='Preprocessed CSV from preprocess_q3.py')
    parser.add_argument('--year', type=int, required=True, help='Election year to display')
    parser.add_argument('--top-n', type=int, help='Optional number of top parties to show')
    parser.add_argument('--output-png', help='Optional path to save the graph')
    parser.add_argument('--no-show', action='store_true', help='Do not open a plot window')
    args = parser.parse_args()

    run_question_3(args.data_csv, args.year, args.top_n, args.output_png, show=not args.no_show)
