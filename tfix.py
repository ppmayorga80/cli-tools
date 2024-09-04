"""Turing taskgen fixer

Usage:
    fix.py [--inplace] [--force] <FILE>

Options:
    -i,--inplace    save the output in the same file (a backup is saved at /tmp)
    -f,--force      use this option to force writing the output
"""
import os
import re
import tempfile
from itertools import count

from docopt import docopt


def is_ok(content: str) -> bool:
    # 1. check the number of #
    # 2. check the main titles
    for title in ("# Question", "# Long Answer", "# Short Answer"):
        response = re.findall(rf"^\s*{title}$", content, re.MULTILINE)
        if not response or len(response) != 1:
            print(rf"FILE>CONTENT Does not have '{title}'")
            return False

    # 3. check references
    # response = re.findall(r"\[@[^@[]]\]", content, re.MULTILINE)
    response = re.findall(r"\[@.*\]", content, re.MULTILINE)
    if response:
        print(f"FILE>CONTENT contains references at {response}")
        return False

    # 4. check ::::
    response = re.findall(r"^:{2,}|:{2,}$", content, re.MULTILINE)
    if response:
        print(f"FILE>CONTENT contains many colons at {response}")
        return False

    # 5. check asteriks **
    content2 = content

    # 5.a remove valid theorems, corollaries,etc
    lines2 = []
    for k, line_k in enumerate(content2.split("\n")):
        new_line = line_k
        for response in re.finditer(r"^\s*\*\*[^*]+\*\*", line_k):
            a, b = response.span()
            new_line = new_line[0:a] + " " * (b - a) + new_line[b:]
        lines2.append(new_line)
    content2 = "\n".join(lines2)

    # 5.b remove valid equations of $$ EQUATION $$
    for response in re.finditer(r"\$\$[^$]+\$\$", content2, re.MULTILINE):
        a, b = response.span()
        middle = re.sub(r"\S", " ", response.group())
        content2 = content2[0:a] + middle + content2[b:]

    # 5.c remove valid equations of $ EQUATION $
    for response in re.finditer(r"\$[^$]+\$", content2, re.MULTILINE):
        a, b = response.span()
        middle = re.sub(r"\S", " ", response.group())
        content2 = content2[0:a] + middle + content2[b:]

    ok_flag = True
    for k, (line_k, line2_k) in enumerate(zip(content.split("\n"), content2.split("\n"))):
        if "*" in line2_k:
            ok_flag = False
            print(f"ERROR : INVALID ASTERISK")
            print(f"LINE  : {k}")
            print(f"TEXT  : {line_k}")
            print(f"FILTER: {line2_k}")
            print("")

    return ok_flag


def fix(content: str) -> str:
    # 1. fix empty lines to real empty lines
    new_content = "\n".join([re.sub(r"^\s+$", "", line) for line in content.split("\n")])

    # 2. one or more empty lines -> 1 empty line
    new_content = re.sub(r"\n{2,}", r"\n\n", new_content).strip()

    break_set = ("# Question", "# Long Answer", "# Short Answer", "")
    lines = [line.strip() for line in new_content.split("\n")]
    new_lines = []
    k = 0
    while k < len(lines):
        if lines[k] in break_set:
            new_lines.append(lines[k])
            k += 1
            continue

        k0 = k
        k += 1
        while k < len(lines):
            if lines[k] not in break_set:
                k += 1
            else:
                break

        merged_lines = " ".join(lines[k0:k])
        new_lines.append(merged_lines)

    new_content = "\n".join(new_lines)
    return new_content


def fix_equations(content: str) -> str:
    regex = re.compile(r"\\[\[\]]")
    new_content = regex.sub("$$", content)
    return new_content


def print_content(content: str):
    for k, line_k in enumerate(content.split("\n")):
        print(line_k)


def main(file: str, inplace: bool = False, force: bool = False):
    if not os.path.exists(file):
        print(f"FILE: '{file}' doesn't exists")
        return

    with open(file) as fp:
        content = fp.read()
    if (not force) and (not is_ok(content)):
        return

    new_content = fix(content)
    new_content = fix_equations(new_content)
    if inplace:
        with open(file, "w") as fp:
            fp.write(new_content)
        with tempfile.NamedTemporaryFile("w", delete=False) as fp:
            print(f"BACKUP TEMPFILE: {fp.name}")
            fp.write(new_content)

    print_content(new_content)


def poc1():
    is_valid = is_ok("""
    # Question
    
    # Long Answer
    
    # Short Answer
    
    ** Theorem 1 **  Pythagoras
    $$
    Let x* be the solution of f(x), then
    f(x*)=0
    $$
    
        hello $f(x*)=0$ and WORLD* my friend
    """)
    print(is_valid)


if __name__ == "__main__":
    # poc1()
    args = docopt(__doc__)
    main(file=args["<FILE>"], inplace=args["--inplace"], force=args["--force"])
