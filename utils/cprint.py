"""This file is a wrapper for the print function called cprint
    that uses color provided by colorama
    print -> COLOR WRAPPER -> cprint

    cprint family functions use the same parameters as print with extra
    parameters:
        fg_color:str
        bg_color:str
        style:str

    cprint family functions with predefined fg_color, bg_color and style:
        cprint_info         cyan text
        cprint_success      light green over black
        cprint_warning      light yellow over black
        cprint_error        light white over red
"""
import sys
from typing import Any, List
from typing import IO

from colorama import init, Fore, Back, Style

# set auto-reset functionality
init(autoreset=True)

# Known Colors:
#       BLACK, WHITE
#       RED, GREEN, BLUE
#       CYAN, MAGENTA, YELLOW
#       LIGHT BLACK, LIGHT WHITE
#       LIGHT RED, LIGHT GREEN, LIGHT BLUE
#       LIGHT CYAN, LIGHT MAGENTA, LIGHT YELLOW
#
# Known Styles:
#       DIM
#       NORMAL
#       BRIGHT
#

# the fg_color_map is a classic dictionary used to map from string to Fore color
fg_color_map = Fore.__dict__

# the bg_color_map is a classic dictionary used to map from string to Back color
bg_color_map = Back.__dict__

# the style_map is a classic dictionary used to map from string to Style
style_map = Style.__dict__


def fix_color_name(color: str) -> str:
    """Given a color string, fix the name to conform with Fore.X and Back.X color names"""
    color = color.upper()
    color = color.replace(" EX", "_EX")
    color = color.replace(" ", "")
    color = f"{color}_EX" if color.startswith(
        "LIGHT") and not color.endswith("_EX") else color
    return color


def cformat(*value: Any,
            fg_color: str = '',
            bg_color: str = '',
            style: str = '') -> str or List[str]:
    """*value is a list of parameters to be printed with colors:
    fore-ground -> fg_color
    back-ground ->bg_color
    style -> style
    Example:
        txt1 = cformat("Hello", fg_color="red", style="dim")
        txt2 = cformat("Hello","world", 3.14, fg_color="blue", style="normal")

    txt1 is formatted properly to be printed with bold (dim) red color
    txt2 format three values in normal blue

    :param value: sequence of values
    :type value: Any
    :param fg_color: foreground color name (red, blue, cyan,...)
    :type fg_color: str
    :param bg_color: background color name
    :type bg_color: str
    :param style: style name (dim, normal, bright)
    :type style: str
    :return: transformed values as a single string
    :rtype: str or List[str]
    """
    #1. get real values for foreground, background and style
    fg = fg_color_map.get(fix_color_name(fg_color), "")
    bg = bg_color_map.get(fix_color_name(bg_color), "")
    st = style_map.get(style.upper(), "")

    #2. build a list of formatted arguments
    # every value (converted to string) with prefixes
    # for foreground, background and style (bg+fg+st)
    args = list(bg + fg + st + str(v) for v in value)

    #3. if one value, return str
    if len(args) == 1:
        return args[0]
    #otherwise return a list of formatted values
    return args


def cprint(*value: Any,
           fg_color: str = '',
           bg_color: str = '',
           style: str = '',
           sep: str = ' ',
           end: str = '\n',
           file: IO = sys.stdout,
           flush: bool = False):
    """Wrapper to the print function with extra color and style parameters
    Color names are RGB and CMYK and W with "Light" prefixes
        Red, Green, Blue
        Cyan, Magenta, Yellow
        Black, White
    Prefixes Example:
        Light Blue

    Styles:
        Dim
        Normal
        Bright

    :param value: the value to print
    :type value: Any
    :param fg_color: Foreground color
    :type fg_color: str
    :param bg_color: Background color
    :type bg_color: str (see the list above for a complete list of names)
    :param style: The style Normal, Dim or Bright
    :type style: str
    :param sep: separator character between values
    :type sep: str
    :param end: the end character, usually end line terminator '\n'
    :type end: str
    :param file: the file pointer to print, usually sys.stdout
    :type file: IO
    :param flush: flag to flush after call the function, usually False
    :type flush: bool
    :return: Nothing
    :rtype: None
    """
    args = cformat(*value, fg_color=fg_color, bg_color=bg_color, style=style)
    print(*args, sep=sep, end=end, file=file, flush=flush)


def cprint_info(*value, sep=' ', end='\n', file=sys.stdout, flush=False):
    """Wrapper for cprint with colors for INFO messages"""
    return cprint(*value,
                  fg_color="LIGHT CYAN",
                  style="",
                  sep=sep,
                  end=end,
                  file=file,
                  flush=flush)


def cprint_success(*value, sep=' ', end='\n', file=sys.stdout, flush=False):
    """Wrapper for cprint with colors for SUCCESS messages"""
    return cprint(*value,
                  fg_color="LIGHT GREEN",
                  bg_color="BLACK",
                  style="BRIGHT",
                  sep=sep,
                  end=end,
                  file=file,
                  flush=flush)


def cprint_warning(*value, sep=' ', end='\n', file=sys.stdout, flush=False):
    """Wrapper for cprint with colors for WARNING messages"""
    return cprint(*value,
                  fg_color="LIGHT YELLOW",
                  bg_color="BLACK",
                  style="BRIGHT",
                  sep=sep,
                  end=end,
                  file=file,
                  flush=flush)


def cprint_error(*value, sep=' ', end='\n', file=sys.stdout, flush=False):
    """Wrapper for cprint with colors for ERROR messages"""
    return cprint(*value,
                  fg_color="LIGHT WHITE",
                  bg_color="RED",
                  style="BRIGHT",
                  sep=sep,
                  end=end,
                  file=file,
                  flush=flush)
