"""
Usage:
   keymap.py --home 
   keymap.py --end 

"""
from docopt import docopt
import pyautogui as pg

if __name__=="__main__":
    args = docopt(__doc__)
    if args["--home"]:
        pg.hotkey("home")
    elif args["--end"]:
        pg.hotkey(["fn","right"])
    
