"""Compute a unknown value based on the rule of 3
IF  
    A : B
    C : X
THEN
          B * C
    X = ---------
            A


Usage:
    ro3 <A> <B> <C> <D>

Arguments:
    <A>   data or expression 1 or unknown variable e.g. 3.1416 or "1+2*3" or X
    <B>   data or expression 2 or unknown variable e.g. 3.1416 or "1+2*3" or X
    <C>   data or expression 3 or unknown variable e.g. 3.1416 or "1+2*3" or X
    <D>   data or expression 4 or unknown variable e.g. 3.1416 or "1+2*3" or X
"""

import docopt
from typing import List, Union, Type
from dataclasses import dataclass


def str2num(text: str, default=None, class_type: Type = int):
    val = default
    try:
        val = class_type(eval(text))
    except TypeError:
        pass
    except NameError:
        pass
    return val


@dataclass
class Operand:
    name: str = "X"
    value: Union[float, str] = "X"
    kind: str = "Unknown"

    def __post_init__(self) -> None:
        self.set(name=self.name, value=self.value)

    def __str__(self):
        return f"{self.name} = {self.value}"
        # return f"[{self.kind}:{type(self.value)}]\t{self.name} := {self.value}"

    def set(self, name: str, value: str):
        self.name = name
        v = str2num(value, default=None, class_type=float)
        if v is None:
            self.kind = "Unknown"
        else:
            self.value = v
            self.kind = "Constant"


def ro3(a: List[Operand]) -> float or None:
    if len(a) != 4:
        return None

    unknowns = [a for a in a if a.kind == "Unknown"]
    if len(unknowns) != 1:
        return None

    x_name = unknowns[0].value

    # 0   1
    # 2   3
    order = []
    if a[0].kind == "Unknown":
        order = [1, 2, 3]
    elif a[1].kind == "Unknown":
        order = [0, 3, 2]
    elif a[2].kind == "Unknown":
        order = [0, 3, 1]
    elif a[3].kind == "Unknown":
        order = [1, 2, 0]

    x_value = a[order[0]].value * a[order[1]].value / a[order[2]].value

    x = Operand(name=x_name, value=x_value)

    return x


def main():
    args = docopt.docopt(__doc__)
    a = Operand(name="A", value=args["<A>"])
    b = Operand(name="B", value=args["<B>"])
    c = Operand(name="C", value=args["<C>"])
    d = Operand(name="D", value=args["<D>"])
    var_list = [a, b, c, d]

    x = ro3(var_list)
    print(x)


if __name__ == '__main__':
    main()
