"""
Usage:
    xlscat.py [--rows=ROWS] [--cols=COLS] [--coltype=T] [--colsep=C] [--rowsep=C] [--skip-nan] <PATH>

Arguments:
    <PATH>   the xls file to be printed out

Options:
    --rows=ROWS    comma separated values of the rows to be printed [default: 1]
    --cols=COLS    csv values of the columns to be printed [default: A]
    --coltype=T    how to interpret column values {name,ref} [default: ref]
    --colsep=C     the character to be used as column separator [default: \t]
    --rowsep=C     the character to be used as row separator [default: \n]
    --skip-nan     flag indicating to not print nan values
"""
import re

import numpy as np
import pandas as pd
from docopt import docopt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('max_colwidth', None)


def openfile(path: str) -> pd.DataFrame:
    if re.findall(r"\.xlsx?$", path):
        df = pd.read_excel(path, header=None)
    else:
        df = pd.read_csv(path, header=None)
    return df


def col_id_to_num(col: str) -> int:
    assert all(re.findall(r"[A-Z]+", ci) for ci in col)

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)
    first_digit = {ci: ni for ni, ci in zip(range(26), alphabet)}
    next_digit = {ci: ni + 1 for ni, ci in zip(range(26), alphabet)}

    value_fn = lambda ci, i: first_digit[ci] if i == 0 else next_digit[ci]
    n = sum([value_fn(ci, i) * (base ** i) for i, ci in enumerate(col[::-1])])

    return n


def main():
    args = docopt(__doc__)
    col_type = args["--coltype"].upper()
    assert col_type in ("REF", "NAME")
    col_sep = args["--colsep"] or r"\n"
    row_sep = args["--rowsep"] or r"\n"
    col_sep = col_sep.replace("\\n", "\n").replace("\\t", "\t")
    row_sep = row_sep.replace("\\n", "\n").replace("\\t", "\t")

    rows = [int(r.strip())-1 for r in args["--rows"].split(",")]
    columns = [c.strip() for c in args["--cols"].split(",")]
    cols = [col_id_to_num(c) if col_type == "REF" else c for c in columns]

    df = openfile(args["<PATH>"])

    i = 0
    for ri in rows:
        if i > 0:
            print(row_sep, end="")
        j = 0
        for cj in cols:
            x_rc = df.iloc[ri, cj]
            try:
                if np.isnan(x_rc):
                    continue
            except Exception:
                pass

            if j > 0:
                print(col_sep, end="")
            print(x_rc, end="")
            j += 1
        i += 1


if __name__ == "__main__":
    main()
