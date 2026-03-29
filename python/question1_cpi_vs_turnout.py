#!/usr/bin/env python3

'''
question1_cpi_vs_turnout.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      question1_cpi_vs_turnout.py reads the preprocessed CSV from
      preprocess_q1.py and generates a scatter plot comparing
      the Consumer Price Index yearly change against voter turnout
      percentage for Canadian federal elections.

      The user specifies which election year to highlight on the
      plot. All available election years are plotted as points,
      with the selected year highlighted and annotated.

      X-axis: Consumer Price Index (CPI) yearly change (%)
      Y-axis: Voter turnout percentage (%)

     Commandline Parameters: 2-3
        sys.argv[1] = preprocessed data CSV file path
        sys.argv[2] = election year to highlight (integer)
        sys.argv[3] = (optional) output PNG file path
'''

#
#   Packages and modules
#
import sys
import os

import pandas as pd
from matplotlib import pyplot as plt

from utils import as_number, read_csv


#
#   Functions
#

def run_question_1(data_csv, year, output_png=None):
    '''
    Read the preprocessed Q1 data and generate a scatter plot
    of CPI yearly change vs voter turnout. The specified year
    is highlighted on the plot.

    Parameters:
        data_csv - path to the preprocessed CSV from preprocess_q1.py
        year - the election year to highlight (integer)
        output_png - optional path to save the plot as a PNG file
    '''

    # Read the preprocessed data
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype(int)
    df['turnout_percent'] = as_number(df['turnout_percent'])
    df['cpi_yearly_change_percent'] = as_number(
        df['cpi_yearly_change_percent']
    )
    df = df.sort_values('year')

    # Check that the requested year exists in the data
    selected = df[df['year'] == year]
    if selected.empty:
        print("Error: Year {} was not found in {}.".format(
            year, data_csv), file=sys.stderr)
        print("Available years: {}".format(
            df['year'].tolist()), file=sys.stderr)
        sys.exit(1)

    # Create the scatter plot
    fig = plt.figure(figsize=(8, 6))

    # Plot all election years as points
    plt.scatter(
        df['cpi_yearly_change_percent'],
        df['turnout_percent']
    )

    # Label each point with its year
    for _, row in df.iterrows():
        plt.annotate(
            str(int(row['year'])),
            (row['cpi_yearly_change_percent'], row['turnout_percent']),
            xytext=(5, 5),
            textcoords='offset points'
        )

    # Highlight the selected year with a larger marker
    sel = selected.iloc[0]
    plt.scatter(
        [sel['cpi_yearly_change_percent']],
        [sel['turnout_percent']],
        s=120
    )

    # Annotate the selected year with its values
    plt.annotate(
        "selected: {}\nCPI={:.2f}%\nTurnout={:.2f}%".format(
            year,
            sel['cpi_yearly_change_percent'],
            sel['turnout_percent']
        ),
        (sel['cpi_yearly_change_percent'], sel['turnout_percent']),
        xytext=(15, -10),
        textcoords='offset points'
    )

    # Set axis labels and title
    plt.title('Consumer Price Index vs Voter Turnout')
    plt.xlabel('Consumer Price Index (CPI) yearly change (%)')
    plt.ylabel('Voter turnout percentage (%)')
    plt.tight_layout()

    # Save the plot to a file if requested
    if output_png:
        fig.savefig(output_png, bbox_inches='tight')

    # Print the selected year's data
    print("Year {}: CPI change = {:.2f}%, turnout = {:.2f}%".format(
        year,
        sel['cpi_yearly_change_percent'],
        sel['turnout_percent']
    ))

    # Close the figure to free memory
    plt.close(fig)

    return selected

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and generates the Question 1 scatter plot.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) < 3 or len(argv) > 4:
        print("Usage: question1_cpi_vs_turnout.py "
              "<data csv> <year> [output png]")
        sys.exit(1)

    data_csv = argv[1]

    try:
        year = int(argv[2])
    except ValueError as err:
        print("Error: year '{}' is not an integer: {}".format(
            argv[2], err), file=sys.stderr)
        sys.exit(1)

    # Check if an output file was specified
    output_png = None
    if len(argv) == 4:
        output_png = argv[3]

    # Generate the plot
    run_question_1(data_csv, year, output_png)

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
