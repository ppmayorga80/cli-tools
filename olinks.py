import os
import re

import pyperclip

def clean_string(text):
    text = text.strip()
    text = re.sub(r"['\"]+","", text)
    return text

def open_links():
    content = pyperclip.paste()
    if content is None:
        return

    lines = [clean_string(x) for x in str(content).split("\n")]
    urls = [line for line in lines if line.startswith("http://") or line.startswith("https://")]

    for url in urls:
        os.system(f"open {url}")


if __name__ == "__main__":
    open_links()
