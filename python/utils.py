from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd


def normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', str(text).strip().lower())


def build_normalized_map(columns: Iterable[str]) -> dict[str, str]:
    return {normalize(col): col for col in columns}


def find_column(df: pd.DataFrame, *candidates: str, required: bool = True) -> str | None:
    normalized = build_normalized_map(df.columns)
    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        key = normalize(candidate)
        for norm_col, raw_col in normalized.items():
            if key and (key in norm_col or norm_col in key):
                return raw_col

    if required:
        raise KeyError(
            f"Could not find any of these columns: {candidates}. Available columns: {list(df.columns)}"
        )
    return None


def as_number(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('%', '', regex=False)
        .str.strip()
        .replace({'': None, 'nan': None, 'NaN': None})
    )
    return pd.to_numeric(cleaned, errors='coerce')


def ensure_dir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def read_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, encoding='utf-8-sig', **kwargs)


def save_dataframe(df: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')


def clean_party_name(name: str) -> str:
    text = str(name).strip()
    if '/' in text:
        text = text.split('/')[0].strip()
    return text


def parse_file_year_arg(value: str) -> tuple[str, int]:
    if ':' not in value:
        raise ValueError(
            f"Expected FILE:YEAR format, got {value!r}. Example: table_tableau03.csv:2019"
        )
    file_part, year_part = value.rsplit(':', 1)
    return file_part, int(year_part)
