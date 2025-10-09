# pyright: reportPrivateUsage=false

import argparse
from typing import Literal
from clipar import namespace

class LongLongArgumentNameTestType:
    def __init__(self, value: str):
        self.value = value

@namespace(exit_on_error=False)
class Namespace:

    ## positional arguments

    a: int
    'check single type'
    b: int | str
    'check union type'
    c: Literal['x', 0, 1, True]
    'check literal type'
    d: Literal['a', 'b', 'c', 'd', 'e', 'f']
    'check literals greater than 5'
    e: int | Literal['a', 'b']
    'check union with literal'

    f: int | str | Literal['l1', 'l2', 'l3', 'l4', 'l5', 'l6']
    'check mixed union type'

    g: list[int]
    'check list type'
    h: tuple[int, ...]
    'check non-fixed tuple type'
    i: tuple[int, str, float]
    'check fixed tuple type'

    j: LongLongArgumentNameTestType
    'check custom class type'



    ## optional arguments

    aa: int = 1
    'check single type with default'
    bb: int | str = 'x'
    'check union type with default'
    cc: Literal['x', 0, 1, True] = 0
    'check literal type with default'
    dd: Literal['a', 'b', 'c', 'd', 'e', 'f'] = 'c'
    'check literals greater than 5 with default'
    ee: int | Literal['a', 'b'] = 'a'
    'check union with literal with default'

    ff: int | str | Literal['l1', 'l2', 'l3', 'l4', 'l5', 'l6'] = 'l1'
    'check mixed union type with default'

    gg: list[int] = [1, 2, 3]
    'check list type with default'
    hh: tuple[int, ...] = (1, 2, 3)
    'check non-fixed tuple type with default'
    ii: tuple[int, str, float] = (1, 'x', 1.0)
    'check fixed tuple type with default'

    jj: LongLongArgumentNameTestType = LongLongArgumentNameTestType('default')
    'check custom class type with default'

Namespace._parser.print_help()
