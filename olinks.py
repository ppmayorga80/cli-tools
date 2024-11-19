import os
import re

import pyperclip


def clean_string(text):
    text = text.strip()
    text = re.sub(r"['\"]+", "", text)
    return text


def text_to_valid_urls(content):
    lines = [f"http{x}" for x in content.split("http")]
    lines = [xk.strip() for x in lines for xk in x.split("\n")]
    lines = [clean_string(x) for x in lines]

    regex = re.compile(r"^https?:.*$")
    lines = [x for x in lines if x and regex.findall(x)]
    return lines


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

    urls = text_to_valid_urls(str(content))
    urls = dedup(urls)

    for url in urls:
        os.system(f"open {url}")


if __name__ == "__main__":
    open_links()
