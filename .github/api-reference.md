# API Reference for AI Agents

このドキュメントは、AIエージェントがCliparライブラリの内部APIを理解し、適切にコード生成や変更を行うための詳細なリファレンスです。

## 公開API一覧

### エントリポイント (`src/clipar/__init__.py`)

```python
# バージョン自動選択によるインポート
from .entities import (
    namespace,
    group, 
    mutually_exclusive_group,
    NotSelected,
    BaseWrapper,
    NamespaceWrapper,
    GroupWrapper
)
```

実際の実装は実行時のPythonバージョンに応じて選択される:
- Python 3.10/3.11: `v310/`モジュールから
- Python 3.12+: `v312/`モジュールから

### デコレータAPI

#### `@namespace`デコレータ

**用途**: トップレベルCLI名前空間の定義

**シグネチャ**:
```python
# v310版
def namespace[_NS](
    cls: type[_NS] | None = None,
    *,
    prog: str | None = None,
    description: str | None = None,
    epilog: str | None = None,
    parents: list[argparse.ArgumentParser] = [],
    formatter_class: type[argparse.HelpFormatter] = argparse.HelpFormatter,
    prefix_chars: str = '-',
    fromfile_prefix_chars: str | None = None,
    argument_default: Any = None,
    conflict_handler: str = 'error',
    add_help: bool = True,
    allow_abbrev: bool = True,
    exit_on_error: bool = True
) -> type[_NS] | Callable[[type[_NS]], type[_NS]]

# v312版（新ジェネリック構文）
def namespace[NS](
    cls: type[NS] | None = None,
    *,
    # 同じパラメータ
) -> type[NS] | Callable[[type[NS]], type[NS]]
```

**使用例**:
```python
@namespace
class Config:
    input_file: str
    "入力ファイルのパス"
    
    output_file: str = "output.txt"
    "出力ファイルのパス（デフォルト: output.txt）"
    
    verbose: bool = False
    "詳細出力を有効にする"
```

#### `@group`デコレータ

**用途**: 引数グループの定義（階層オプション作成）

**シグネチャ**:
```python
# v310版
def group[_NS](
    cls: type[_NS] | None = None,
    *,
    title: str | None = None,
    description: str | None = None
) -> type[_NS] | Callable[[type[_NS]], type[_NS]]

# v312版
def group[NS](
    cls: type[NS] | None = None,
    *,
    title: str | None = None, 
    description: str | None = None
) -> type[NS] | Callable[[type[NS]], type[NS]]
```

**使用例**:
```python
@group
class DatabaseConfig:
    host: str = "localhost"
    "データベースホスト"
    
    port: int = 5432
    "データベースポート"

@namespace
class AppConfig:
    database = DatabaseConfig
    # --database-host, --database-port オプションが生成される
```

#### `@mutually_exclusive_group`デコレータ

**用途**: 排他的引数グループの定義

**シグネチャ**:
```python
def mutually_exclusive_group[NS](
    cls: type[NS] | None = None,
    *,
    required: bool = False
) -> type[NS] | Callable[[type[NS]], type[NS]]
```

### ベースクラス

#### `BaseWrapper`

**概要**: 全ラッパークラスの基底クラス

**主要メソッド**:
```python
class BaseWrapper:
    def __init__(self, cls: type) -> None: ...
    def __repr__(self) -> str: ...
    def _detect_type(self, field_name: str, annotation: Any) -> tuple[type, bool]: ...
    def _get_type_func(self, field_type: type) -> Callable[[str], Any]: ...
```

#### `NamespaceWrapper`

**概要**: `@namespace`デコレータによって作成されるラッパークラス

**主要メソッド**:
```python
class NamespaceWrapper(BaseWrapper):
    @classmethod
    def parse_args(cls, args: list[str] | None = None) -> Self: ...
    
    def add_argument(
        self,
        parser: argparse.ArgumentParser,
        field_name: str,
        field_type: type,
        default_value: Any,
        help_text: str | None
    ) -> None: ...
```

#### `GroupWrapper`

**概要**: `@group`デコレータによって作成されるラッパークラス

**主要メソッド**:
```python
class GroupWrapper(BaseWrapper):
    def add_to_parser(
        self,
        parser: argparse.ArgumentParser,
        prefix: str = ""
    ) -> None: ...
```

### 型変換システム

#### サポートする型とその動作

| Python型 | CLI動作 | 変換関数 | 例 |
|----------|---------|---------|-----|
| `str` | 位置引数/オプション | `str` | `--name value` |
| `int` | オプション | `int` | `--count 42` |
| `float` | オプション | `float` | `--rate 3.14` |
| `bool` | フラグ | `_bool_type` | `--verbose` |
| `list[str]` | 複数値 | `_list_type(str)` | `--files a.txt b.txt` |
| `list[int]` | 複数値 | `_list_type(int)` | `--numbers 1 2 3` |
| `Path` | ファイルパス | `pathlib.Path` | `--path /data/file.txt` |

#### カスタム型変換の実装

```python
# basewrapper.py内での実装例
def _get_type_func(self, field_type: type) -> Callable[[str], Any]:
    if field_type == bool:
        return self._bool_type
    elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
        inner_type = field_type.__args__[0]
        return self._list_type(self._get_type_func(inner_type))
    elif field_type == pathlib.Path:
        return pathlib.Path
    else:
        return field_type
```

### AST解析システム

#### `ClassAstHolder`

**概要**: クラス定義からヘルプテキストを自動抽出

**実装場所**: `src/clipar/v310/class_ast.py`, `src/clipar/v312/class_ast.py`

**主要メソッド**:
```python
class ClassAstHolder:
    def __init__(self, cls: type) -> None: ...
    
    def get_help_for_field(self, field_name: str) -> str | None:
        """フィールド直後の文字列リテラルをヘルプテキストとして取得"""
        
    def _extract_help_texts(self) -> dict[str, str]:
        """クラス定義のAST解析を実行してヘルプテキストを抽出"""
```

**ヘルプテキスト抽出ルール**:
1. フィールド定義の次の行にある文字列リテラル
2. インデントレベルがフィールドと同じ
3. 複数行文字列もサポート

**例**:
```python
@namespace
class Config:
    input_file: str
    "入力ファイルのパス"  # ← この文字列が抽出される
    
    output_file: str = "output.txt"
    "出力ファイルのパス（デフォルト: output.txt）"
    
    workers: int = 1
    """
    ワーカー数の指定
    並列処理で使用される
    """  # ← 複数行も対応
```

### 特殊値

#### `NotSelected`

**概要**: 未設定オプションを表すsentinel値

**定義場所**: `src/clipar/v310/basewrapper.py`, `src/clipar/v312/basewrapper.py`

```python
class NotSelectedType:
    def __repr__(self) -> str:
        return "NotSelected"
    
    def __bool__(self) -> bool:
        return False

NotSelected = NotSelectedType()
```

**使用パターン**:
```python
config = Config.parse_args()

# 正しい使用方法
if config.optional_field is NotSelected:
    print("オプションが指定されていません")

# 間違った使用方法
if config.optional_field is None:  # NG: Noneとは別の概念
    pass
```

## バージョン間差異

### Python 3.10/3.11 vs 3.12+ の主な違い

#### ジェネリック構文

**v310 (TypeVarベース)**:
```python
from typing import TypeVar

_NS = TypeVar('_NS')

def namespace(
    cls: type[_NS] | None = None,
    ...
) -> type[_NS] | Callable[[type[_NS]], type[_NS]]:
    ...
```

**v312 (新ジェネリック構文)**:
```python
def namespace[NS](
    cls: type[NS] | None = None,
    ...
) -> type[NS] | Callable[[type[NS]], type[NS]]:
    ...
```

#### 実装上の注意点

1. **型パラメータの定義**:
   - v310: `TypeVar`で事前定義が必要
   - v312: `[T]`構文でインライン定義

2. **型チェック**:
   - 両バージョンともmypyで`--strict`レベルでのチェックが必要
   - v312では新しい型システムの恩恵を受けられる

3. **パフォーマンス**:
   - v312版はわずかに最適化されている
   - 実用上の差は微小

## エラーハンドリング

### 一般的なエラーパターン

#### 1. 型注釈の不備

**問題**:
```python
@namespace
class Config:
    input_file  # 型注釈なし - エラー
    output_file: str = "output.txt"
```

**解決**:
```python
@namespace  
class Config:
    input_file: str  # 型注釈必須
    output_file: str = "output.txt"
```

#### 2. バージョン不整合

**問題**: v310でのみ実装を更新し、v312を忘れる

**解決**: 両バージョンの同時更新を徹底

#### 3. ヘルプテキストの配置ミス

**問題**:
```python
@namespace
class Config:
    input_file: str
    
    "入力ファイルのパス"  # 空行があるとAST解析で認識されない
```

**解決**:
```python
@namespace
class Config:
    input_file: str
    "入力ファイルのパス"  # フィールド直後に配置
```

### デバッグのヒント

1. **AST解析の確認**:
   ```python
   holder = ClassAstHolder(ConfigClass)
   print(holder.get_help_for_field("field_name"))
   ```

2. **型検出の確認**:
   ```python
   wrapper = NamespaceWrapper(ConfigClass)
   field_type, is_optional = wrapper._detect_type("field_name", annotation)
   ```

3. **引数パーサの検証**:
   ```python
   config = Config.parse_args(["--help"])
   ```

## 拡張ポイント

### 新しい型のサポート追加

1. **`_get_type_func`メソッドの拡張**:
   ```python
   def _get_type_func(self, field_type: type) -> Callable[[str], Any]:
       # 既存の型チェック...
       
       if field_type == MyCustomType:
           return my_custom_converter
       
       # デフォルト処理...
   ```

2. **両バージョンでの実装**:
   - `src/clipar/v310/basewrapper.py`
   - `src/clipar/v312/basewrapper.py`

### 新しいデコレータの追加

1. **デコレータ関数の実装**（両バージョン）
2. **対応するラッパークラスの作成**  
3. **エンティティファイルでのexport**
4. **テストケースの作成**（両バージョン）

## パフォーマンス考慮事項

### AST解析のコスト

- クラス定義時に一度だけ実行
- 結果はキャッシュされる
- 大規模なクラス定義でも実用的

### 型検出の最適化

- 型注釈の解析は遅延実行
- よく使用される型（str, int, bool）は最適化済み

### メモリ使用量

- インスタンス毎のオーバーヘッドは最小限
- 大量のCLIインスタンス作成でも効率的

## 関連リソース

- [メインAPI仕様書](./ai-specifications.md)
- [開発ガイドライン](./copilot-instructions.md)
- [テスト仕様](../test/test.copilot-instructions.md)
- [型システム仕様](../docs/html/api/index.html)