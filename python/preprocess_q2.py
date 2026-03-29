#!/usr/bin/env python3

'''
preprocess_q2.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      preprocess_q2.py reads one or more Elections Canada Table 3
      CSV files and computes the overall voter turnout percentage
      for each election year.

      For each file, the script sums up the total electors and
      total ballots cast across all provinces, then calculates
      the voter turnout percentage using the formula:
          (Total Ballots Cast / Electors) x 100

      The results are saved into a processed CSV file with
      the following columns:
          year, electors, ballots_cast, turnout_percent

     Commandline Parameters: 3+
        sys.argv[1] = output CSV file path
        sys.argv[2] = first election file in FILE:YEAR format
        sys.argv[3] = (optional) additional election files in FILE:YEAR format
'''

#
#   Packages and modules
#
import sys

import pandas as pd

from utils import as_number, find_column, parse_file_year_arg
from utils import read_csv, save_dataframe


#
#   Functions
#

def summarize_table3(election_csv, year):
    '''
    Read a single Elections Canada Table 3 CSV file and compute
    the total electors, ballots cast, and turnout percentage
    for the given election year across all provinces.

    Returns a DataFrame with one row containing the summary.
    '''

    df = read_csv(election_csv)

    # Find the relevant columns in the CSV
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

    # Sum up totals across all provinces
    total_electors = as_number(df[electors_col]).sum()
    total_ballots = as_number(df[ballots_col]).sum()

    # Build the summary row
    summary = pd.DataFrame({
        'year': [int(year)],
        'electors': [total_electors],
        'ballots_cast': [total_ballots],
    })

    # Calculate turnout percentage
    summary['turnout_percent'] = (
        summary['ballots_cast'] / summary['electors'] * 100.0
    )

    return summary

    #
    #   End of Function
    #


def preprocess_q2(election_files_with_years, output_csv):
    '''
    Process multiple election Table 3 files and combine the
    turnout summaries into a single CSV file sorted by year.

    Parameters:
        election_files_with_years - list of (filename, year) tuples
        output_csv - path to save the output CSV

    Returns the combined DataFrame.
    '''

    # Process each election file
    pieces = []
    for path, year in election_files_with_years:
        summary = summarize_table3(path, year)
        pieces.append(summary)

    # Combine all years into one DataFrame
    combined = pd.concat(pieces, ignore_index=True)
    combined = combined.sort_values('year')
    combined = combined.drop_duplicates(subset=['year'])

    # Save the result
    save_dataframe(combined, output_csv)

    return combined

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and runs the preprocessing pipeline for Question 2.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) < 3:
        print("Usage: preprocess_q2.py <output csv> "
              "<election file:year> [election file:year ...]")
        sys.exit(1)

    output_csv = argv[1]

    # Parse all the election file arguments
    file_year_pairs = []
    for i in range(2, len(argv)):
        try:
            pair = parse_file_year_arg(argv[i])
            file_year_pairs.append(pair)
        except ValueError as err:
            print("Error parsing argument '{}': {}".format(
                argv[i], err), file=sys.stderr)
            sys.exit(1)

    # Run the preprocessing
    result = preprocess_q2(file_year_pairs, output_csv)
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
