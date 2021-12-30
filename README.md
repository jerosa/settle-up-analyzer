# Settle Up Expenses Analyzer

Simple processing and expenses analyser from Settle Up application.

## Installation

1. Create .venv virtual environment with requirements using `py -m venv .venv`. 
2. Activate .venv `.venv\Scripts\activate`
3. Install requirements `pip install -r requirements.txt`

### New packages

To add new requirements add new line in requirements.in and compile with `pip-compile requirements.in` and for installation use `pip-sync`

## Usage

1. Export transactions.csv from Settle Up (share with email)
2. Create .secrets.toml redefining variables present in settings.toml
```toml
workdir = "path"
filename_to_process = "20211230_transactions.csv"
user_to_analyse = "MyUser"
```
3. Execute the file preprocessing `python preprocess.py`
4. Create/Open expenses.xlsx file adding all the expenses processed in the previous step adding the category for custom analysis. Example:

|      Date & time      | Purpose | Category | Month | Amount |
|:---------------------:|:-------:|:--------:|:-----:|:------:|
| 2021-04-28   20:16:49 | Babel   | Bar      | 4     | 2.2   |
| 2021-05-12   15:00:14 | Ikea    | Shop     | 5     | 17    |

5. Analyse. `python analyse.py`
