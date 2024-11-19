import os
import re

import pyperclip

def clean_string(text):
    text = text.strip()
    text = re.sub(r"['\"]+","", text)
    return text

def dedup(data):
    new_data = []
    for x in data:
        if x not in new_data:
            new_data.append(x)
    return new_data

def open_links():
    content = pyperclip.paste()
    if content is None:
        return

    lines = [clean_string(x) for x in str(content).split("\n")]
    urls = [line for line in lines if line.startswith("http://") or line.startswith("https://")]
    urls = dedup(urls)
    
    for url in urls:
        os.system(f"open {url}")


if __name__ == "__main__":
    open_links()
