#!/usr/bin/env python3

'''
utils.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      utils.py provides shared utility functions used across the
      preprocessing and visualization scripts in the project.

      Functions include CSV reading, column finding, numeric
      conversion, and file saving helpers.
'''

#
#   Packages and modules
#
import re
import os
import csv

import pandas as pd


#
#   Functions
#

def normalize(text):
    '''
    Normalize a string by removing all non-alphanumeric characters
    and converting to lowercase. Used for fuzzy column matching.
    '''

    return re.sub(r'[^a-z0-9]+', '', str(text).strip().lower())

    #
    #   End of Function
    #


def build_normalized_map(columns):
    '''
    Build a dictionary mapping normalized column names to their
    original column names. This allows case-insensitive lookups.
    '''

    result = {}
    for col in columns:
        result[normalize(col)] = col

    return result

    #
    #   End of Function
    #


def find_column(df, *candidates, required=True):
    '''
    Search a DataFrame's columns for any of the given candidate names.
    Uses fuzzy matching through normalization. Returns the original
    column name if found, or None if not found and not required.

    If required is True and no match is found, raises a KeyError.
    '''

    normalized = build_normalized_map(df.columns)

    # Try exact normalized match first
    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]

    # Try partial match as fallback
    for candidate in candidates:
        key = normalize(candidate)
        for norm_col, raw_col in normalized.items():
            if key and (key in norm_col or norm_col in key):
                return raw_col

    if required:
        raise KeyError(
            "Could not find any of these columns: {}. "
            "Available columns: {}".format(candidates, list(df.columns))
        )

    return None

    #
    #   End of Function
    #


def as_number(series):
    '''
    Convert a pandas Series to numeric values. Strips commas,
    percent signs, and whitespace before converting. Returns
    NaN for values that cannot be converted.
    '''

    cleaned = (
        series.astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('%', '', regex=False)
        .str.strip()
        .replace({'': None, 'nan': None, 'NaN': None})
    )

    return pd.to_numeric(cleaned, errors='coerce')

    #
    #   End of Function
    #


def ensure_dir(path):
    '''
    Create a directory (and any parent directories) if it does
    not already exist. Returns the path as a string.
    '''

    if not os.path.exists(path):
        os.makedirs(path)

    return path

    #
    #   End of Function
    #


def read_csv(path):
    '''
    Read a CSV file into a pandas DataFrame using UTF-8 with
    BOM handling. This is the standard way Statistics Canada
    and Elections Canada CSV files are encoded.
    '''

    return pd.read_csv(path, encoding='utf-8-sig')

    #
    #   End of Function
    #


def save_dataframe(df, output_path):
    '''
    Save a pandas DataFrame to a CSV file. Creates the parent
    directory if it does not exist. Uses UTF-8 with BOM encoding
    for compatibility with Statistics Canada data format.
    '''

    # Make sure the output directory exists
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        ensure_dir(parent_dir)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    #
    #   End of Function
    #


def clean_party_name(name):
    '''
    Clean a political party name by stripping whitespace and
    removing the French translation after the slash if present.
    For example: "Liberal Party of Canada/Parti libéral" becomes
    "Liberal Party of Canada".
    '''

    text = str(name).strip()

    if '/' in text:
        text = text.split('/')[0].strip()

    return text

    #
    #   End of Function
    #


def parse_file_year_arg(value):
    '''
    Parse a command line argument in FILE:YEAR format and return
    a tuple of (filename, year). Raises ValueError if the format
    is incorrect.

    Example: "table_tableau03.csv:2019" returns ("table_tableau03.csv", 2019)
    '''

    if ':' not in value:
        print("Error: Expected FILE:YEAR format, got '{}'".format(value))
        print("Example: table_tableau03.csv:2019")
        raise ValueError(
            "Expected FILE:YEAR format, got '{}'".format(value)
        )

    file_part, year_part = value.rsplit(':', 1)

    return file_part, int(year_part)

    #
    #   End of Function
    #


#
#   End of Script
#
