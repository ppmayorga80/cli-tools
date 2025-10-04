"""CSV Obfuscator

Usage:
    csvobf.py [--no-obf] [--output=PATH] [--force] [--cols=NAMES] [--p-empty-rows=P] [--p-obf=P] [--p-fill=P] <FILENAME>

Arguments:
    <FILENAME>         The CSV file to process.

Options:
    --no-obf           Don't obfuscate CSV file.
    --force            Enforce to write the output file if it already exists.
    --output=PATH      Output file path. If omitted, prints to stdout.
    --cols=NAMES       Comma-separated list of columns to obfuscate. If omitted, all columns are obfuscated.
    --p-empty-rows=P   Probability of obfuscating empty rows [default: 0.2].
    --p-obf=P          Probability of substituting a character during obfuscation [default: 0.01].
    --p-fill=P         Probability of fill with empty character during obfuscation [default: 0.01].
"""
import os
import sys
from collections import defaultdict

import pandas as pd
from random import random, choice, randint
from docopt import docopt


class Homoglyph:
    HOMOGLYPHS = {
        # Lowercase
        "a": ["а"],  # Cyrillic a
        "c": ["с"],  # Cyrillic es
        "e": ["е"],  # Cyrillic ie
        "g": ["ɡ"],  # Latin small letter script g (confusable)
        "i": ["і"],  # Cyrillic i
        "j": ["ј"],  # Cyrillic je
        "l": ["ⅼ"],  # Roman numeral fifty
        "o": ["о"],  # Cyrillic o
        "p": ["р"],  # Cyrillic er
        "q": ["ԛ"],  # Cyrillic qa
        "s": ["ѕ"],  # Cyrillic dze
        "u": ["υ"],  # Greek upsilon
        "v": ["ν"],  # Greek nu
        "x": ["х"],  # Cyrillic ha
        "y": ["у"],  # Cyrillic u
        "z": ["ᴢ"],  # Modifier small capital Z

        # Uppercase
        "A": ["Α", "А"],  # Greek Alpha, Cyrillic A
        "B": ["Β", "В"],  # Greek Beta, Cyrillic Ve
        "C": ["Ϲ", "С"],  # Greek Sigma, Cyrillic Es
        "D": ["Ꭰ"],  # Cherokee A
        "E": ["Ε", "Е"],  # Greek Epsilon, Cyrillic Ie
        "H": ["Η", "Н"],  # Greek Eta, Cyrillic En
        "I": ["Ι", "І"],  # Greek Iota, Cyrillic I
        "J": ["Ј"],  # Cyrillic Je
        "K": ["Κ", "К"],  # Greek Kappa, Cyrillic Ka
        "L": ["Ꮮ"],  # Cherokee L
        "M": ["Μ", "М"],  # Greek Mu, Cyrillic Em
        "N": ["Ν"],  # Greek Nu
        "O": ["Ο", "О"],  # Greek Omicron, Cyrillic O
        "P": ["Ρ", "Р"],  # Greek Rho, Cyrillic Er
        "Q": ["Ԛ"],  # Cyrillic Qa
        "S": ["Ѕ"],  # Cyrillic Dze
        "T": ["Τ", "Т"],  # Greek Tau, Cyrillic Te
        "U": ["Ս"],  # Armenian Se
        "X": ["Χ", "Х"],  # Greek Chi, Cyrillic Ha
        "Y": ["Υ"],  # Greek Upsilon, Cyrillic U
        "Z": ["Ζ"],  # Greek Zeta

        # Digits
        "0": ["О"],  # Cyrillic O
        "3": ["З"],  # Cyrillic Ze

        # Symbols
        "-": ["‐"],  # Hyphen-like
        "_": ["＿"],  # Fullwidth underscore
    }

    @classmethod
    def random_map(cls, c):
        if c in cls.HOMOGLYPHS:
            return choice(cls.HOMOGLYPHS[c])
        return None

    @classmethod
    def random_sub(cls, text: str, probability: float = 0.3) -> tuple[str, bool]:
        new_text = ""
        changed = False
        for c in text:
            if random() < probability:
                mapped_c = cls.random_map(c)
                if mapped_c:
                    changed = True
                    new_text += mapped_c
                else:
                    new_text += c
            else:
                new_text += c
        return new_text, changed


def obfuscate(df: pd.DataFrame, col_names_and_flags, p_obf, p_empty, p_fill) -> pd.DataFrame:
    only_col_names = [x for x, _ in col_names_and_flags]

    # 4. obfuscate cells
    counter = defaultdict(int)
    for k, row in df.iterrows():
        for col_name, obfuscate_flag in col_names_and_flags:
            if obfuscate_flag:
                original_value = row[col_name]
                new_value, changed = Homoglyph.random_sub(original_value, probability=p_obf)
                row[col_name] = new_value
                counter[col_name] += 1

    # 5. obf  spaces to , and ;
    for k, row in df.iterrows():
        for c in only_col_names:
            val = row[c]
            new_val = ""
            for ci in val:
                if ci == " " and random() < 0.35:
                    ci = ", " if random() < 0.5 else "; "
                new_val += ci
            row[c] = new_val

    new_id = 0
    new_rows = []
    for k, row in df.iterrows():
        new_id += 1
        row_dict = {k: v for k, v in row.items()}
        row_dict["id"] = new_id
        new_rows.append(row_dict)

        if random() < p_empty:
            for _ in range(randint(3, 10)):
                new_id += 1
                row_dict = {k: "" for k, v in row.items()}
                row_dict["id"] = new_id
                new_rows.append(row_dict)

    new_df = pd.DataFrame(new_rows)
    return new_df


def df_to_text(df):
    lines = [",".join([c for c in df.columns])]
    for k, row in df.iterrows():
        current_line = [str(v) for k, v in row.items()]
        lines.append(",".join(current_line))
    return "\n".join(lines)


def main():
    arguments = docopt(__doc__)
    p_obf = float(arguments["--p-obf"]) if arguments["--p-obf"] is not None else 0.0
    p_empty = float(arguments["--p-empty-rows"]) if arguments["--p-empty-rows"] is not None else 0.0
    p_fill = float(arguments["--p-fill"]) if arguments["--p-fill"] is not None else 0.0

    if arguments["--no-obf"]:
        p_obf, p_empty, p_empty = 0, 0, 0

    # 1. read the csv file
    df = pd.read_csv(arguments["<FILENAME>"], dtype=str).fillna("NAN")

    # 2. read the columns
    if not arguments["--cols"]:
        # obfuscate all columns
        col_names_and_flags = [(x, True) for x in df.columns]
    else:
        col_names_and_flags = []
        for col in arguments["--cols"].split(","):
            col_list = col.split(":")
            col_name = col_list[0]
            col_obfuscate = False
            if len(col_list) > 1:
                temp = col_list[1].strip().lower()
                if temp == 'true':
                    col_obfuscate = True
            col_names_and_flags.append((col_name, col_obfuscate))

    # 3. filter out only the valid column names
    col_names_and_flags = [(x, f) for x, f in col_names_and_flags if x in df.columns]
    exit_flag = False
    for x, f in [(x, f) for x, f in col_names_and_flags if x not in df.columns]:
        print(f"Column '{x}' does not exist in CSV file", file=sys.stderr)
        exit_flag = True
    if exit_flag:
        exit(1)

    df = df[[x for x, _ in col_names_and_flags]]

    if not arguments["--no-obf"]:
        df = obfuscate(df, col_names_and_flags, p_obf, p_empty, p_fill)

    # print out the df
    if arguments["--output"]:
        if arguments["--force"] or not os.path.exists(arguments["--output"]):
            with open(arguments["--output"], "w") as fp:
                fp.write(df_to_text(df))
        else:
            print(f"Output file '{arguments['--output']}' already exists", file=sys.stderr)
            exit(1)
    else:
        print(df_to_text(df), file=sys.stderr)


if __name__ == '__main__':
    main()
