from clipar.decorator import namespace
from typing import Literal

@namespace
class CliExample:

    opt: str = 'default value'  # parser.add_argument('--opt', default='default value')
    pos: str  # parser.add_argument('pos')

    nargs_star: list[str]  # parser.add_argument('nargs_star', nargs='*')
    nargs_len: tuple[str, str, str]  # parser.add_argument('nargs_len', nargs=3)

    choices: Literal['a', 'b', 'c'] = 'a'  # parser.add_argument('--choices', choices=['a', 'b', 'c'], default='a')
    choices_list: list[Literal['a', 'b', 'c']] = ['a', 'b']  # parser.add_argument('--choices-list', choices=['a', 'b', 'c'], nargs='*', default=['a', 'b'])

    # Boolean flags (フラグ系)
    flag: bool = False  # parser.add_argument('--flag', action='store_true')
    verbose: bool  # parser.add_argument('--verbose', action='store_true') デフォルトなしのbool
    
    # Numeric types (数値系)
    count: int = 0  # parser.add_argument('--count', type=int, default=0)
    port: int = 8080  # parser.add_argument('--port', type=int, default=8080)
    timeout: float = 30.0  # parser.add_argument('--timeout', type=float, default=30.0)
    rate: float  # parser.add_argument('--rate', type=float, required=True)
    
    # Optional types (オプショナル系)
    optional_str: str | None = None  # parser.add_argument('--optional-str', default=None)
    optional_int: int | None  # parser.add_argument('--optional-int', type=int, default=None)

    # Union types (ユニオン型)
    union_type: str | int = 'default'  # parser.add_argument('--union-type', type=lambda x: x if x.isdigit() else x, default='default')
    
    # Multiple values with different constraints (複数値の制約)
    multiple_files: list[str] = []  # parser.add_argument('--multiple-files', nargs='*', default=[])
    pair_values: tuple[str, int]  # parser.add_argument('pair_values', nargs=2) + type conversion
    fixed_trio: tuple[str, str, str] = ('default1', 'default2', 'default3')  # parser.add_argument('--fixed-trio', nargs=3, default=['default1', 'default2', 'default3'])

    # primitive collections (プリミティブコレクション)
    str_list: list[str] = []  # parser.add_argument('--str-list', nargs='*', default=[])
    int_set: set[int] = set()  # parser.add_argument('--int-set', nargs='*', type=int, default=set())
    float_tuple: tuple[float, ...] = (1.0, 2.0, 3.0)  # parser.add_argument('--float-tuple', nargs='+', type=float, default=(1.0, 2.0, 3.0))
    
    # Complex nested types (複雑なネスト型) (表現の限界のため、処理しない)
    config_dict: dict[str, str] = {}  # parser.add_argument('--config-dict', action='append', nargs=2) + dict conversion
    nested_list: list[list[str]]  # 複雑な変換が必要 - custom action or post-processing
    
    # Special string patterns (特殊な文字列パターン)
    email: str  # parser.add_argument('email') 将来的にバリデーション可能
    url: str = 'http://localhost'  # parser.add_argument('--url', default='http://localhost')
    file_path: str  # parser.add_argument('file_path', type=argparse.FileType('r'))
    # これらはアノテーションに特殊化クラスを使用すればよい
    
    # Enum-like choices with different types (異なる型のenum的選択肢)
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'  # parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    mode: Literal[1, 2, 3] = 1  # parser.add_argument('--mode', type=int, choices=[1, 2, 3], default=1)
    mixed_choices: Literal['auto', 42, True] = 'auto'  # parser.add_argument('--mixed-choices', choices=['auto', '42', 'True'], default='auto') + type conversion

cli_example = CliExample.parse_args()
