# How Canada Votes — tightened Milestone 2 scripts

These scripts now match the **actual structure of the CSVs you uploaded** much more closely:

- `table_tableau03.csv` does **not** contain an election-year column, so the preprocess step now expects `FILE:YEAR`
- `table_tableau08.csv` and `table_tableau09.csv` use a party column plus province columns, with `Total` in Table 9
- the uploaded CPI file is a **wide StatCan download**, not the tidy `REF_DATE, GEO, VALUE` layout described in your report, so the Q1 preprocessing now detects that and gives a clear error if the file does not contain the historical election years you need

## What works with the uploaded files

### Question 2
You can preprocess a Table 3 file by telling the script which election year it represents:

```bash
python preprocess_q2.py \
  --election-file /mnt/data/table_tableau03.csv:2019 \
  --output-csv processed/question2.csv
```

Then graph it:

```bash
python question2_turnout_over_time.py \
  --data-csv processed/question2.csv \
  --start-year 2019 \
  --end-year 2019
```

### Question 3
The uploaded Table 8 and Table 9 files look like the 2019 election, so this should work directly:

```bash
python preprocess_q3.py \
  --table8-csv /mnt/data/table_tableau08.csv \
  --table9-csv /mnt/data/table_tableau09.csv \
  --year 2019 \
  --output-csv processed/question3_2019.csv

python question3_party_distribution.py \
  --data-csv processed/question3_2019.csv \
  --year 2019 \
  --top-n 6
```

## Question 1 note

Your uploaded CPI file (`1810000411-eng.csv`) is **not yet in the historical tidy format your report describes**. It appears to be a recent cross-sectional StatCan download with columns like January 2025 / December 2025 / January 2026, which is not enough to compare against the election years in your report.

So Q1 is now **safer and clearer**:

- it tries both the tidy StatCan format and the wide download format
- if there are no overlapping election years, it raises a useful message instead of silently producing wrong output

## Combined runner

You can also use:

```bash
python main_menu.py preprocess-q2 --election-file /mnt/data/table_tableau03.csv:2019 --output-csv processed/question2.csv
python main_menu.py question2 --data-csv processed/question2.csv --start-year 2019 --end-year 2019
```
