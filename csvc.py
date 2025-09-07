"""CSV processing file

Usage:
    csvc.py [--filter=LAMBDA] [--columns=COLS] [--exclude-columns=COLS] [--skip-rows=N] [--output=OUT] <FILE>
    csvc.py --list-columns [--skip-rows=N] <FILE>


Arguments:
    <FILE>      The csv file to process

Options:
    -f,--filter=LAMBDA    Filter by LAMBDA expression of the form 'lambda x: True' [default: lambda x: True]
    -c,--columns=COLS     Columns to include in the result [default: *]
    -x,--exclude-columns=COLS      Columns to exclude from the result [default: ]
    -s,--skip-rows=N      Skip rows starting from this number [default: 0]
    -o,--output=OUT       Output file [default: stdout]
    -l,--list-columns      Only list the column names
"""
from docopt import docopt
import pandas as pd
from colorama import Fore, init

init(autoreset=True)


def validate_columns(columns, df) -> bool:
    """validate the column names against a dataframe"""
    good_columns = [x for x in columns if x in df.columns]
    wrong_columns = [x for x in columns if x not in df.columns]
    if len(wrong_columns) > 0:
        for k, xk in enumerate(columns):
            flag = xk in good_columns
            flag_str = "🟢 Column exists in CSV" if flag else "🔴 Column not in CSV"
            if flag:
                print(f"{k + 1}.", Fore.GREEN + f"'{xk}'" + Fore.RESET + f"{flag_str}")
            else:
                print(f"{k + 1}.", Fore.RED + f"'{xk}'" + Fore.RESET + f"{flag_str}")

        print("--------------------")
        print("# Good columns: {len(good_columns)}")
        print("# Wrong columns: {len(wrong_columns)}")

        return False
    return True


def main(arguments):
    # load df
    try:
        skip_rows = int(arguments['--skip-rows'])
        df = pd.read_csv(arguments['<FILE>'], skiprows=skip_rows)
    except Exception as e:
        print(Fore.RED + f"File can't be open: {e}")
        exit(1)

    filter_str = arguments["--filter"]
    filter_fn = eval(arguments['--filter'])
    include_columns = [x.strip() for x in arguments['--columns'].split(',')]
    exclude_columns = [x.strip() for x in arguments['--exclude-columns'].split(',')]

    if arguments["--columns"] == "*" and arguments["--exclude-columns"] == "*":
        print(Fore.RED + "Included Columns and Exclude Columns cannot be both equals to *")
        exit(1)
    if arguments["--exclude-columns"] == "*":
        exclude_columns = df.columns.tolist()
    elif arguments["--columns"] == "*":
        include_columns = df.columns.tolist()

    columns = [x for x in include_columns if x not in exclude_columns]

    if arguments['--list-columns']:
        df_columns = df.columns.tolist()
        for k, xk in enumerate(df_columns):
            print(f"{k + 1}." + Fore.GREEN + f"'{xk}'")
        return

    if not validate_columns(columns, df):
        return

    # Apply filter
    df = df[columns]
    try:
        df = df[df.apply(filter_fn, axis=1)]
    except Exception as e:
        print(Fore.RED + f"Error applying filter expression '{filter_str}': {e}")
        return

    if arguments['--output'] == "stdout":
        with pd.option_context(
                'display.max_rows', None,
                'display.max_columns', None,
                'display.width', 0,
                'display.max_colwidth', None,
                'display.expand_frame_repr', False
        ):
            print(df.to_string(index=False))
    else:
        with open(arguments['--output'], 'w') as fp:
            df.to_csv(fp, index=False)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
