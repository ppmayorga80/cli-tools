"""starts the arxiv app that listen to the xclip
and if there is an arxiv link parse it and copy 
the url to the arxiv article

Usage:
    arxiv.py [--no-open] [--arxiv]
    arxiv.py [--no-open] --google

Options:
    --no-open     dont open the urls
    --arxiv       open the arxiv file
    --google      open the google search for the arxiv

"""
import os
import re
import time

import pyperclip

from docopt import docopt


ARXIV_REGEX = re.compile(r"([0-9])+\/([a-z0-9.]+)")
ARXIV_URL_FORMAT = "https://arxiv.org/pdf/{arxiv_id}"
GOOGLE_URL_FORMAT = "https://www.google.com/search?q=arxiv+{arxiv_id}"

class Arxiv:
    def __init__(self, arxiv:bool=True, open_url:bool=True):
        self.arxiv = arxiv
        self.open_url = open_url
        
        self.previous_text = ""

    def run(self):
        text = pyperclip.paste()
        if not text or text == self.previous_text:
            return
        self.previous_text = text

        response = ARXIV_REGEX.findall(text)
        if response:
            code1, code2 = response[0]
            arxiv_id = re.sub(r"\.gz$", "",code2)

            if self.arxiv:
                url = ARXIV_URL_FORMAT.format(arxiv_id=arxiv_id)
            else:
                url = GOOGLE_URL_FORMAT.format(arxiv_id=arxiv_id)

            print("input:", text)
            print("arxiv id:", arxiv_id)
            print("url to open:", url)


            if self.open_url:
                os.system(f"open {url}")

def main(**kwargs: dict or list):
    args = docopt(doc=__doc__, **kwargs)
    print(args)
    arxiv_opener = Arxiv(arxiv=args["--arxiv"], open_url=not args["--no-open"])
    while(True):
        arxiv_opener.run()
        time.sleep(0.5)

if __name__ == "__main__":
    main()