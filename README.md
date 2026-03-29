# How Canada Votes — CIS*2250 Term Project

**Group:** Luanda 406
**Members:** Raaif Rizwan, Ahmet Ozer, Ali Muqedi, Mohamed Hendy
**Course:** CIS*2250 (01) W26 — Software Design II

## Overview

This project analyzes Canadian federal election data alongside
Statistics Canada economic data to answer three research questions:

1. Do changes in the Consumer Price Index affect voter turnout?
2. How has voter turnout changed between the 43rd and 44th federal elections?
3. How are votes distributed among political parties in each election?

Each question has a **preprocessing script** that prepares the raw CSV
data, and a **visualization script** that generates a plot from the
preprocessed data.

## Required Datasets

### Elections Canada — Official Voting Results

Download from the Government of Canada Open Data Portal (open.canada.ca):

- **43rd General Election (2019):**
  - `table_tableau03_43_elec.csv` — Table 3: Number of ballots cast and voter turnout
  - `table_tableau08_43_elec.csv` — Table 8: Number of valid votes by political affiliation
  - `table_tableau09_43_elec.csv` — Table 9: Percentage of valid votes by political affiliation

- **44th General Election (2021):**
  - `table_tableau03_44_elec.csv` — Table 3: Number of ballots cast and voter turnout
  - `table_tableau08_44_elec.csv` — Table 8: Number of valid votes by political affiliation
  - `table_tableau09_44_elec.csv` — Table 9: Percentage of valid votes by political affiliation

### Statistics Canada — Consumer Price Index

Download from Statistics Canada (www150.statcan.gc.ca):

- Search for Table **18-10-0005-01** (CPI, annual average, not seasonally adjusted)
- Set Geography to **Canada** and Reference period to **2018** or earlier
- Download using **"Download selected data (for database loading)"**
- Save as `cpi_annual.csv`

## Project Files

| File | Purpose |
|------|---------|
| `utils.py` | Shared utility functions (CSV reading, column finding, etc.) |
| `preprocess_q1.py` | Preprocesses election turnout + CPI data for Question 1 |
| `preprocess_q2.py` | Preprocesses election turnout data for Question 2 |
| `preprocess_q3.py` | Preprocesses party vote distribution data for Question 3 |
| `question1_cpi_vs_turnout.py` | Generates scatter plot for Question 1 |
| `question2_turnout_over_time.py` | Generates line chart for Question 2 |
| `question3_party_distribution.py` | Generates bar chart for Question 3 |

## Dependencies

- Python 3
- pandas
- matplotlib

## How to Run

All scripts use positional command line arguments (no flags). Each
question follows a two-step process: preprocess first, then visualize.

---

### Question 1: CPI vs Voter Turnout

**What it does:** Compares the year-over-year CPI percentage change
against voter turnout for each election year using a scatter plot.

**Step 1 — Preprocess:**

```
python3 preprocess_q1.py <output csv> <cpi csv> <election file:year> [election file:year ...]
```

Example:
```
python3 preprocess_q1.py processed_q1.csv cpi_annual.csv table_tableau03_43_elec.csv:2019 table_tableau03_44_elec.csv:2021
```

This reads the CPI data and both Table 3 election files, computes
turnout percentage and CPI yearly change, and saves the merged
result to `processed_q1.csv`.

Output columns: `year, electors, ballots_cast, turnout_percent, cpi_yearly_change_percent`

**Step 2 — Visualize:**

```
python3 question1_cpi_vs_turnout.py <data csv> <year> [output png]
```

Example:
```
python3 question1_cpi_vs_turnout.py processed_q1.csv 2019 q1_plot.png
```

Parameters:
- `<data csv>` — the preprocessed CSV from step 1
- `<year>` — the election year to highlight on the scatter plot (2019 or 2021)
- `[output png]` — optional filename to save the plot image

The plot shows all election years as points with the selected year
highlighted and annotated with its exact CPI change and turnout values.

---

### Question 2: Voter Turnout Over Time

**What it does:** Shows how voter turnout changed between the 43rd
and 44th federal elections using a line chart.

**Step 1 — Preprocess:**

```
python3 preprocess_q2.py <output csv> <election file:year> [election file:year ...]
```

Example:
```
python3 preprocess_q2.py processed_q2.csv table_tableau03_43_elec.csv:2019 table_tableau03_44_elec.csv:2021
```

This reads each Table 3 file, sums electors and ballots cast across
all provinces, computes turnout percentage, and saves the result to
`processed_q2.csv`.

Output columns: `year, electors, ballots_cast, turnout_percent`

**Step 2 — Visualize:**

```
python3 question2_turnout_over_time.py <data csv> <start year> <end year> [output png]
```

Example:
```
python3 question2_turnout_over_time.py processed_q2.csv 2019 2021 q2_plot.png
```

Parameters:
- `<data csv>` — the preprocessed CSV from step 1
- `<start year>` — first election year to include
- `<end year>` — last election year to include
- `[output png]` — optional filename to save the plot image

The plot shows a line connecting each election year with markers
annotated with the exact turnout percentage.

---

### Question 3: Party Vote Distribution

**What it does:** Shows how votes were distributed among political
parties in a specific election using a horizontal bar chart.

**Step 1 — Preprocess:**

```
python3 preprocess_q3.py <table8 csv> <table9 csv> <year> <output csv>
```

Example for 2019:
```
python3 preprocess_q3.py table_tableau08_43_elec.csv table_tableau09_43_elec.csv 2019 processed_q3_2019.csv
```

Example for 2021:
```
python3 preprocess_q3.py table_tableau08_44_elec.csv table_tableau09_44_elec.csv 2021 processed_q3_2021.csv
```

This reads Table 8 (vote counts) and Table 9 (vote percentages),
merges them by party name, and saves the result.

Output columns: `party, valid_votes, vote_percent, year`

**Step 2 — Visualize:**

```
python3 question3_party_distribution.py <data csv> <year> [top n] [output png]
```

Example:
```
python3 question3_party_distribution.py processed_q3_2019.csv 2019 6 q3_plot.png
```

Parameters:
- `<data csv>` — the preprocessed CSV from step 1
- `<year>` — the election year to display
- `[top n]` — optional number of top parties to show (e.g. 6)
- `[output png]` — optional filename to save the plot image

The plot shows a horizontal bar for each party with bars annotated
with the exact vote percentage.

---

## Demo Workflow

**Before the demo**, run all preprocessing steps:

```
python3 preprocess_q1.py processed_q1.csv cpi_annual.csv table_tableau03_43_elec.csv:2019 table_tableau03_44_elec.csv:2021
python3 preprocess_q2.py processed_q2.csv table_tableau03_43_elec.csv:2019 table_tableau03_44_elec.csv:2021
python3 preprocess_q3.py table_tableau08_43_elec.csv table_tableau09_43_elec.csv 2019 processed_q3_2019.csv
python3 preprocess_q3.py table_tableau08_44_elec.csv table_tableau09_44_elec.csv 2021 processed_q3_2021.csv
```

**During the demo**, run the visualization scripts and vary the
parameters to explore the data:

```
python3 question1_cpi_vs_turnout.py processed_q1.csv 2019 q1_2019.png
python3 question1_cpi_vs_turnout.py processed_q1.csv 2021 q1_2021.png

python3 question2_turnout_over_time.py processed_q2.csv 2019 2021 q2_plot.png

python3 question3_party_distribution.py processed_q3_2019.csv 2019 6 q3_2019.png
python3 question3_party_distribution.py processed_q3_2021.csv 2021 6 q3_2021.png
```
