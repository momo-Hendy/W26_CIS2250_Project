#!/usr/bin/env python3

'''
preprocess_q3.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      preprocess_q3.py reads Elections Canada Table 8 and Table 9
      CSV files and combines them to produce a summary of how
      votes were distributed among political parties.

      Table 8 provides the total number of valid votes received
      by each party. Table 9 provides the percentage of valid
      votes for each party. The script extracts the party name,
      total valid votes, and vote percentage from both files and
      merges them together by matching the party names.

      The output CSV contains the following columns:
          party, valid_votes, vote_percent, year

     Commandline Parameters: 4
        sys.argv[1] = Table 8 CSV file path
        sys.argv[2] = Table 9 CSV file path
        sys.argv[3] = election year (integer)
        sys.argv[4] = output CSV file path
'''

#
#   Packages and modules
#
import sys

import pandas as pd

from utils import as_number, clean_party_name, find_column
from utils import read_csv, save_dataframe


#
#   Functions
#

def pick_party_column(df):
    '''
    Find the column in a DataFrame that contains the political
    party or affiliation names. Tries several common column name
    variations used in Elections Canada data.
    '''

    return find_column(
        df,
        'political affiliation',
        'political party',
        'party',
        'affiliation',
        'name of political party',
    )

    #
    #   End of Function
    #


def extract_total_column(df):
    '''
    Find the column containing the total or Canada-wide values
    in an Elections Canada CSV file. Returns None if not found.
    '''

    return find_column(df, 'Total', 'Canada', required=False)

    #
    #   End of Function
    #


def preprocess_q3(table8_csv, table9_csv, year, output_csv):
    '''
    Main preprocessing function for Question 3. Reads Table 8
    (vote counts) and Table 9 (vote percentages) and merges
    them into a single summary file.

    Parameters:
        table8_csv - path to Elections Canada Table 8 CSV
        table9_csv - path to Elections Canada Table 9 CSV
        year - the election year these files represent
        output_csv - path to save the combined output CSV

    Returns the merged DataFrame.
    '''

    # Read both input files
    votes_df = read_csv(table8_csv)
    pct_df = read_csv(table9_csv)

    # Find the party name columns in each file
    party_col_votes = pick_party_column(votes_df)
    party_col_pct = pick_party_column(pct_df)

    # Find the total/Canada column for vote counts
    vote_col = extract_total_column(votes_df)
    pct_col = extract_total_column(pct_df)

    # Extract vote counts per party
    if vote_col is not None:
        # Use the total column directly
        votes = votes_df[[party_col_votes, vote_col]].copy()
        votes.columns = ['party', 'valid_votes']
        votes['valid_votes'] = as_number(votes['valid_votes'])
    else:
        # Sum across all provincial columns if no total column exists
        provincial_vote_cols = [
            c for c in votes_df.columns if c != party_col_votes
        ]
        votes = votes_df[[party_col_votes] + provincial_vote_cols].copy()
        votes['valid_votes'] = sum(
            as_number(votes[c]).fillna(0) for c in provincial_vote_cols
        )
        votes = votes[[party_col_votes, 'valid_votes']]
        votes.columns = ['party', 'valid_votes']

    # Clean up the party names
    votes['party'] = votes['party'].map(clean_party_name)

    # Extract vote percentages per party
    pct = pct_df[[party_col_pct, pct_col]].copy()
    pct.columns = ['party', 'vote_percent']
    pct['party'] = pct['party'].map(clean_party_name)
    pct['vote_percent'] = as_number(pct['vote_percent'])

    # Merge vote counts and percentages by party name
    merged = votes.merge(pct, on='party', how='inner')
    merged['year'] = int(year)

    # Remove rows with missing data or zero votes
    merged = merged.dropna(subset=['party', 'vote_percent'])
    merged = merged[
        (merged['vote_percent'] > 0) | (merged['valid_votes'] > 0)
    ]

    # Sort by vote percentage descending
    merged = merged.sort_values('vote_percent', ascending=False)
    merged = merged.reset_index(drop=True)

    # Save the result
    save_dataframe(merged, output_csv)

    return merged

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and runs the preprocessing pipeline for Question 3.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) != 5:
        print("Usage: preprocess_q3.py <table8 csv> <table9 csv> "
              "<year> <output csv>")
        sys.exit(1)

    table8_csv = argv[1]
    table9_csv = argv[2]

    try:
        year = int(argv[3])
    except ValueError as err:
        print("Error: year '{}' is not an integer: {}".format(
            argv[3], err), file=sys.stderr)
        sys.exit(1)

    output_csv = argv[4]

    # Run the preprocessing
    result = preprocess_q3(table8_csv, table9_csv, year, output_csv)
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
