from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import as_number, read_csv


def run_question_1(data_csv: str, year: int, output_png: str | None = None, show: bool = True) -> pd.DataFrame:
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype(int)
    df['turnout_percent'] = as_number(df['turnout_percent'])
    df['cpi_yearly_change_percent'] = as_number(df['cpi_yearly_change_percent'])
    df = df.sort_values('year')

    selected = df[df['year'] == year]
    if selected.empty:
        raise ValueError(f'Year {year} was not found in {data_csv}. Available years: {df["year"].tolist()}')

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['cpi_yearly_change_percent'], df['turnout_percent'])

    for _, row in df.iterrows():
        ax.annotate(str(int(row['year'])), (row['cpi_yearly_change_percent'], row['turnout_percent']), xytext=(5, 5), textcoords='offset points')

    sel = selected.iloc[0]
    ax.scatter([sel['cpi_yearly_change_percent']], [sel['turnout_percent']], s=120)
    ax.annotate(
        f"selected: {year}\nCPI={sel['cpi_yearly_change_percent']:.2f}%\nTurnout={sel['turnout_percent']:.2f}%",
        (sel['cpi_yearly_change_percent'], sel['turnout_percent']),
        xytext=(15, -10),
        textcoords='offset points',
    )

    ax.set_title('Consumer Price Index vs Voter Turnout')
    ax.set_xlabel('Consumer Price Index (CPI) yearly change (%)')
    ax.set_ylabel('Voter turnout percentage (%)')
    fig.tight_layout()

    if output_png:
        Path(output_png).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_png, bbox_inches='tight')

    print(f"Year {year}: CPI change = {sel['cpi_yearly_change_percent']:.2f}%, turnout = {sel['turnout_percent']:.2f}%")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Answer Question 1: CPI vs voter turnout.')
    parser.add_argument('--data-csv', required=True, help='Preprocessed CSV from preprocess_q1.py')
    parser.add_argument('--year', type=int, required=True, help='Election year to highlight')
    parser.add_argument('--output-png', help='Optional path to save the graph')
    parser.add_argument('--no-show', action='store_true', help='Do not open a plot window')
    args = parser.parse_args()

    run_question_1(args.data_csv, args.year, args.output_png, show=not args.no_show)
