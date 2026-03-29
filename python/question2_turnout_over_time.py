#!/usr/bin/env python3

'''
question2_turnout_over_time.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      question2_turnout_over_time.py reads the preprocessed CSV
      from preprocess_q2.py and generates a line chart showing
      how voter turnout has changed across Canadian federal
      elections over time.

      The user specifies a start year and end year to filter
      which elections are displayed on the chart.

      X-axis: Election Year
      Y-axis: Voter turnout percentage (%)

     Commandline Parameters: 3-4
        sys.argv[1] = preprocessed data CSV file path
        sys.argv[2] = start year (integer)
        sys.argv[3] = end year (integer)
        sys.argv[4] = (optional) output PNG file path
'''

#
#   Packages and modules
#
import sys

import pandas as pd
from matplotlib import pyplot as plt

from utils import as_number, read_csv


#
#   Functions
#

def run_question_2(data_csv, start_year, end_year, output_png=None):
    '''
    Read the preprocessed Q2 data and generate a line chart
    of voter turnout over time for elections within the
    specified year range.

    Parameters:
        data_csv - path to the preprocessed CSV from preprocess_q2.py
        start_year - first election year to include (integer)
        end_year - last election year to include (integer)
        output_png - optional path to save the plot as a PNG file
    '''

    # Read the preprocessed data
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype(int)
    df['turnout_percent'] = as_number(df['turnout_percent'])

    # Filter to the requested year range
    filtered = df[
        (df['year'] >= start_year) & (df['year'] <= end_year)
    ]
    filtered = filtered.sort_values('year')

    if filtered.empty:
        print("Error: No data found between {} and {}.".format(
            start_year, end_year), file=sys.stderr)
        print("Available years: {}".format(
            df['year'].tolist()), file=sys.stderr)
        sys.exit(1)

    # Create the line chart
    fig = plt.figure(figsize=(8, 6))

    # Plot the turnout data as a line with markers
    plt.plot(
        filtered['year'],
        filtered['turnout_percent'],
        marker='o'
    )

    # Annotate each point with its exact turnout percentage
    for _, row in filtered.iterrows():
        plt.annotate(
            "{:.2f}%".format(row['turnout_percent']),
            (row['year'], row['turnout_percent']),
            xytext=(0, 8),
            ha='center',
            textcoords='offset points'
        )

    # Set axis labels and title
    plt.title('Voter Turnout Across Canadian Federal Elections')
    plt.xlabel('Election Year')
    plt.ylabel('Voter turnout percentage (%)')
    plt.xticks(filtered['year'].tolist())
    plt.tight_layout()

    # Save the plot to a file if requested
    if output_png:
        fig.savefig(output_png, bbox_inches='tight')

    # Print the data to the screen
    print(filtered[['year', 'electors', 'ballots_cast',
                     'turnout_percent']].to_string(index=False))

    # Close the figure to free memory
    plt.close(fig)

    return filtered

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and generates the Question 2 line chart.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) < 4 or len(argv) > 5:
        print("Usage: question2_turnout_over_time.py "
              "<data csv> <start year> <end year> [output png]")
        sys.exit(1)

    data_csv = argv[1]

    try:
        start_year = int(argv[2])
    except ValueError as err:
        print("Error: start year '{}' is not an integer: {}".format(
            argv[2], err), file=sys.stderr)
        sys.exit(1)

    try:
        end_year = int(argv[3])
    except ValueError as err:
        print("Error: end year '{}' is not an integer: {}".format(
            argv[3], err), file=sys.stderr)
        sys.exit(1)

    # Check if an output file was specified
    output_png = None
    if len(argv) == 5:
        output_png = argv[4]

    # Generate the plot
    run_question_2(data_csv, start_year, end_year, output_png)

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
