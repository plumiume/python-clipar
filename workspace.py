# pyright: reportPrivateUsage=false

from typing import Literal
from clipar import namespace

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

    g: list[int]
    'check list type'
    h: tuple[int, ...]
    'check non-fixed tuple type'
    i: tuple[int, str, float]
    'check fixed tuple type'

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

    gg: list[int] = [1, 2, 3]
    'check list type with default'
    hh: tuple[int, ...] = (1, 2, 3)
    'check non-fixed tuple type with default'
    ii: tuple[int, str, float] = (1, 'x', 1.0)
    'check fixed tuple type with default'

Namespace._parser.print_help()
