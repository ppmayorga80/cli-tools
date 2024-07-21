"""starts the arxiv app that listen to the xclip
and if there is an arxiv link parse it and copy 
the url to the arxiv article

Usage:
    arxiv.py [--no-open]
    arxiv.py [--no-open] --use-google

Options:
    --no-open     dont open the urls
    --arxiv       open the arxiv file
    --google      open the google search for the arxiv

"""
import os
import re
import time

import requests
import pyperclip

from docopt import docopt

ARXIV_REGEX = re.compile(r"([0-9]/)*([a-z0-9.]+)")
ARXIV_URL_FORMAT = "https://arxiv.org/pdf/{arxiv_id}"
GOOGLE_URL_FORMAT = "https://www.google.com/search?q=arxiv+{arxiv_id}"


class ArxivListener:
    def __init__(self, arxiv: bool = True, open_url: bool = True):
        self.arxiv = arxiv
        self.open_url = open_url

        self.previous_text = ""
        self.previous_arxiv_id = ""

    @classmethod
    def is_arxiv_valid(cls, arxiv_id: str) -> bool:
        number_of_letters = len([x for x in arxiv_id if x.isalpha()])
        number_of_digits = len([x for x in arxiv_id if x.isdigit()])
        number_of_dots = len([x for x in arxiv_id if x == "."])

        if number_of_dots == 0 and number_of_letters > 0 and number_of_digits > 0:
            return True
        elif number_of_dots == 1 and number_of_letters == 0 and number_of_digits > 0:
            return True

        return False

    @classmethod
    def is_url_a_pdf(cls, url:str)->bool:
        try:
            response = requests.head(url)
            if response.status_code==200:
                if response.headers.get("content-type","") == "application/pdf":
                    return True
        
            return False
        except Exception as e:
            return False


    def run(self):
        text = pyperclip.paste()
        if not text or text == self.previous_text:
            return
        self.previous_text = text

        response = ARXIV_REGEX.findall(text)
        if response:
            possible_arxiv_response = [re.sub(r"\.gz$", "", code2) for code1,code2 in response]
            arxiv_response = [arxiv_id for arxiv_id in possible_arxiv_response if self.is_arxiv_valid(arxiv_id)]
            if arxiv_response:
                #take the last arxivid detected
                arxiv_id = arxiv_response[-1]
            else:
                return

            if arxiv_id == self.previous_arxiv_id:
                return


            self.previous_arxiv_id = arxiv_id
            if self.arxiv:
                url = ARXIV_URL_FORMAT.format(arxiv_id=arxiv_id)
            else:
                url = GOOGLE_URL_FORMAT.format(arxiv_id=arxiv_id)

            if not self.is_url_a_pdf(url=url):
                return

            print("input:", text)
            print("arxiv id:", arxiv_id)
            print("url to open:", url)

            if self.open_url:
                os.system(f"open {url}")
            else:
                pyperclip.copy(url)


def main(**kwargs: dict or list):
    # 1. read the arguments
    args = docopt(doc=__doc__, **kwargs)

    # 2. instantiate the arxiv listener
    listener = ArxivListener(arxiv=not args["--use-google"], open_url=not args["--no-open"])
    while (True):
        listener.run()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
