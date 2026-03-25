from __future__ import annotations

import argparse

from preprocess_q1 import preprocess_q1
from preprocess_q2 import preprocess_q2
from preprocess_q3 import preprocess_q3
from question1_cpi_vs_turnout import run_question_1
from question2_turnout_over_time import run_question_2
from question3_party_distribution import run_question_3
from utils import parse_file_year_arg


def main() -> None:
    parser = argparse.ArgumentParser(
        description='How Canada Votes - Milestone 2 helper runner',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    p1 = subparsers.add_parser('preprocess-q1')
    p1.add_argument('--election-file', action='append', required=True, help='Table 3 file in FILE:YEAR format. Repeat for multiple years.')
    p1.add_argument('--cpi-csv', required=True)
    p1.add_argument('--output-csv', required=True)

    q1 = subparsers.add_parser('question1')
    q1.add_argument('--data-csv', required=True)
    q1.add_argument('--year', required=True, type=int)
    q1.add_argument('--output-png')
    q1.add_argument('--no-show', action='store_true')

    p2 = subparsers.add_parser('preprocess-q2')
    p2.add_argument('--election-file', action='append', required=True, help='Table 3 file in FILE:YEAR format. Repeat for multiple years.')
    p2.add_argument('--output-csv', required=True)

    q2 = subparsers.add_parser('question2')
    q2.add_argument('--data-csv', required=True)
    q2.add_argument('--start-year', required=True, type=int)
    q2.add_argument('--end-year', required=True, type=int)
    q2.add_argument('--output-png')
    q2.add_argument('--no-show', action='store_true')

    p3 = subparsers.add_parser('preprocess-q3')
    p3.add_argument('--table8-csv', required=True)
    p3.add_argument('--table9-csv', required=True)
    p3.add_argument('--year', required=True, type=int)
    p3.add_argument('--output-csv', required=True)

    q3 = subparsers.add_parser('question3')
    q3.add_argument('--data-csv', required=True)
    q3.add_argument('--year', required=True, type=int)
    q3.add_argument('--top-n', type=int)
    q3.add_argument('--output-png')
    q3.add_argument('--no-show', action='store_true')

    args = parser.parse_args()

    if args.command == 'preprocess-q1':
        preprocess_q1([parse_file_year_arg(v) for v in args.election_file], args.cpi_csv, args.output_csv)
    elif args.command == 'question1':
        run_question_1(args.data_csv, args.year, args.output_png, show=not args.no_show)
    elif args.command == 'preprocess-q2':
        preprocess_q2([parse_file_year_arg(v) for v in args.election_file], args.output_csv)
    elif args.command == 'question2':
        run_question_2(args.data_csv, args.start_year, args.end_year, args.output_png, show=not args.no_show)
    elif args.command == 'preprocess-q3':
        preprocess_q3(args.table8_csv, args.table9_csv, args.year, args.output_csv)
    elif args.command == 'question3':
        run_question_3(args.data_csv, args.year, args.top_n, args.output_png, show=not args.no_show)


if __name__ == '__main__':
    main()
