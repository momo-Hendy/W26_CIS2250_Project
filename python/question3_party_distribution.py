#!/usr/bin/env python3

'''
question3_party_distribution.py
  Author(s): Mohamed Hendy (1332794)
  Earlier contributors(s): Raaif Rizwan, Ahmet Ozer, Ali Muqedi

  Project: CIS*2250 Term Project - How Canada Votes
  Date of Last Update: March 2026

  Functional Summary
      question3_party_distribution.py reads the preprocessed CSV
      from preprocess_q3.py and generates a horizontal bar chart
      showing how votes were distributed among political parties
      in a specific Canadian federal election.

      The user specifies which election year to display and
      optionally how many top parties to include in the chart.

      X-axis: Percentage of valid votes (%)
      Y-axis: Political party name

     Commandline Parameters: 2-4
        sys.argv[1] = preprocessed data CSV file path
        sys.argv[2] = election year (integer)
        sys.argv[3] = (optional) number of top parties to show
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

def run_question_3(data_csv, year, top_n=None, output_png=None):
    '''
    Read the preprocessed Q3 data and generate a horizontal bar
    chart of vote distribution by political party for the
    specified election year.

    Parameters:
        data_csv - path to the preprocessed CSV from preprocess_q3.py
        year - the election year to display (integer)
        top_n - optional number of top parties to show
        output_png - optional path to save the plot as a PNG file
    '''

    # Read the preprocessed data
    df = read_csv(data_csv)
    df['year'] = as_number(df['year']).astype('Int64')

    # Filter to the requested year
    filtered = df[df['year'] == year].copy()

    if filtered.empty:
        print("Error: No data found for year {} in {}.".format(
            year, data_csv), file=sys.stderr)
        sys.exit(1)

    # Convert numeric columns
    filtered['vote_percent'] = as_number(filtered['vote_percent'])
    filtered['valid_votes'] = as_number(filtered['valid_votes'])

    # Remove rows with missing vote percentages
    filtered = filtered.dropna(subset=['vote_percent'])

    # Sort by vote percentage ascending (for horizontal bar chart)
    filtered = filtered.sort_values('vote_percent', ascending=True)

    # Keep only the top N parties if specified
    if top_n is not None:
        filtered = filtered.tail(top_n)

    # Create the horizontal bar chart
    fig = plt.figure(figsize=(10, 7))

    plt.barh(filtered['party'], filtered['vote_percent'])

    # Annotate each bar with its exact percentage
    for _, row in filtered.iterrows():
        plt.annotate(
            "{:.2f}%".format(row['vote_percent']),
            (row['vote_percent'], row['party']),
            xytext=(6, 0),
            va='center',
            textcoords='offset points'
        )

    # Set axis labels and title
    plt.title('Vote Distribution by Political Party ({})'.format(year))
    plt.xlabel('Percentage of valid votes (%)')
    plt.ylabel('Political party name')
    plt.tight_layout()

    # Save the plot to a file if requested
    if output_png:
        fig.savefig(output_png, bbox_inches='tight')

    # Print the data to the screen
    print(filtered[['party', 'valid_votes', 'vote_percent']]
          .sort_values('vote_percent', ascending=False)
          .to_string(index=False))

    # Close the figure to free memory
    plt.close(fig)

    return filtered

    #
    #   End of Function
    #


def main(argv):
    '''
    Main function in the script. Reads command line arguments
    and generates the Question 3 bar chart.
    '''

    #
    #   Check that we have been given the right number of parameters
    #
    if len(argv) < 3 or len(argv) > 5:
        print("Usage: question3_party_distribution.py "
              "<data csv> <year> [top n] [output png]")
        sys.exit(1)

    data_csv = argv[1]

    try:
        year = int(argv[2])
    except ValueError as err:
        print("Error: year '{}' is not an integer: {}".format(
            argv[2], err), file=sys.stderr)
        sys.exit(1)

    # Parse optional arguments
    top_n = None
    output_png = None

    if len(argv) >= 4:
        # Check if the third argument is a number (top_n) or a filename
        try:
            top_n = int(argv[3])
        except ValueError:
            # Not a number, treat it as the output filename
            output_png = argv[3]

    if len(argv) == 5:
        output_png = argv[4]

    # Generate the plot
    run_question_3(data_csv, year, top_n, output_png)

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
