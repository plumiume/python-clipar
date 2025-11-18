# Architectural Design Document

## 概要

Cliparは型注釈とデコレータを活用したPythonのCLIライブラリです。本ドキュメントでは、システムアーキテクチャの設計思想、実装戦略、および技術的判断の背景を詳しく説明します。

## 設計思想

### 核となる理念

1. **宣言的設計**: コードが仕様そのものとなる
2. **型安全性**: コンパイル時エラー検出
3. **最小限の記述**: ボイラープレートの排除
4. **段階的移行**: 既存argparseからの簡単な移行

### 設計原則

- **単一責任の原則**: 各クラスが明確な責任を持つ
- **開放閉鎖の原則**: 拡張可能だが既存コードを変更しない
- **依存関係逆転**: 抽象に依存し、具象に依存しない

## システムアーキテクチャ

### 全体構成図

```
┌─────────────────────────────────────────┐
│                User Code                │
│  @namespace class Config: ...           │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           Entry Point                   │
│     src/clipar/__init__.py              │
│   (Version Selection Logic)             │
└─────────────┬───────────────────────────┘
              │
      ┌───────▼────────┐
      │ Version Router │
      │ (entities.py)  │
      └───────┬────────┘
              │
    ┌─────────▼──────────┐
    │   Implementation   │
    │                    │
    │  v310/     v312/   │
    │  ├─decorator.py    │
    │  ├─wrapper.py      │
    │  ├─ast.py          │
    │  └─...             │
    └────────────────────┘
```

### レイヤー構造

#### Layer 1: ユーザーインターフェース
- **責任**: 型注釈とデコレータによるCLI定義
- **構成要素**: `@namespace`, `@group`, 型注釈
- **例**:
```python
@namespace
class Config:
    input_file: str
    "Input file path"
    
    workers: int = 1
    "Number of worker processes"
```

#### Layer 2: デコレータシステム  
- **責任**: クラス変換とメタデータ抽出
- **構成要素**: `decorator.py` のデコレータ関数群
- **機能**: クラスをCLIラッパーに変換

#### Layer 3: ラッパーシステム
- **責任**: CLI動作の具体的実装
- **構成要素**: `NamespaceWrapper`, `GroupWrapper`, `BaseWrapper`
- **機能**: argparseとの連携、型変換、解析実行

#### Layer 4: 支援システム
- **責任**: メタデータ抽出と型処理
- **構成要素**: `ClassAstHolder`, 型検出ロジック
- **機能**: AST解析、型変換関数の選択

## 並列実装戦略

### Python バージョン対応の必要性

#### 問題背景
Python 3.12で導入された新しいジェネリック構文は、旧バージョンと構文レベルで互換性がありません:

```python
# Python 3.12+ の新構文
def func[T](param: T) -> T: ...
class Container[T]: ...

# Python 3.10/3.11 でサポートされる構文
from typing import TypeVar
T = TypeVar('T')
def func(param: T) -> T: ...
class Container(Generic[T]): ...
```

#### 解決アプローチ

**選択肢1**: 最低公倍数的アプローチ（旧構文のみ使用）
- **メリット**: 実装が単一
- **デメリット**: 新機能の恩恵を受けられない

**選択肢2**: 条件分岐による動的選択
- **メリット**: 単一コードベース
- **デメリット**: 複雑性増大、型チェックの困難

**選択肢3**: 並列実装（採用）
- **メリット**: 各バージョンで最適化、明確な分離
- **デメリット**: コード重複、同期の必要性

### 実装構造

```
src/clipar/
├── __init__.py           # バージョン選択エントリポイント  
├── entities.py           # 統一インターフェース
├── v310/                 # Python 3.10/3.11 対応
│   ├── decorator.py      
│   ├── basewrapper.py    
│   ├── namespacewrapper.py
│   ├── groupwrapper.py   
│   ├── class_ast.py      
│   └── mixin.py          
└── v312/                 # Python 3.12+ 対応
    ├── decorator.py      # 新ジェネリック構文使用
    ├── basewrapper.py    # 最適化された実装
    ├── namespacewrapper.py
    ├── groupwrapper.py   
    ├── class_ast.py      
    ├── help_formatter.py # v312専用機能
    └── mixin.py          
```

### バージョン選択ロジック

```python
# src/clipar/__init__.py
import sys

if sys.version_info >= (3, 12):
    from .v312.decorator import namespace, group, mutually_exclusive_group
    from .v312.basewrapper import BaseWrapper, NotSelected
    from .v312.namespacewrapper import NamespaceWrapper  
    from .v312.groupwrapper import GroupWrapper
else:
    from .v310.decorator import namespace, group, mutually_exclusive_group
    from .v310.basewrapper import BaseWrapper, NotSelected
    from .v310.namespacewrapper import NamespaceWrapper
    from .v310.groupwrapper import GroupWrapper
```

## 核心設計決定

### 1. AST解析によるヘルプテキスト抽出

#### 課題
従来のアプローチではヘルプテキストの指定が困難:
```python
# 従来的アプローチ
@namespace(help_texts={"field": "Help for field"})
class Config:
    field: str
```

#### 解決策: AST解析
```python
# Cliparのアプローチ
@namespace
class Config:
    field: str
    "Help for field"  # フィールド直後の文字列を自動抽出
```

#### 実装詳細

```python
class ClassAstHolder:
    def _extract_help_texts(self) -> dict[str, str]:
        """クラス定義をAST解析してヘルプテキストを抽出"""
        
        # 1. ソースコードの取得
        source = inspect.getsource(self.cls)
        
        # 2. AST解析
        tree = ast.parse(source)
        class_node = tree.body[0]  # クラス定義ノード
        
        # 3. フィールド定義後の文字列リテラルを検索
        for i, node in enumerate(class_node.body):
            if isinstance(node, ast.AnnAssign) and node.target.id:
                field_name = node.target.id
                
                # 次のノードが文字列リテラルかチェック
                if (i + 1 < len(class_node.body) and 
                    isinstance(class_node.body[i + 1], ast.Expr) and
                    isinstance(class_node.body[i + 1].value, ast.Constant)):
                    
                    help_text = class_node.body[i + 1].value.value
                    self.help_texts[field_name] = help_text
```

**利点**:
- 型定義とヘルプが近接し、可読性向上
- デコレータ引数の複雑化を回避
- IDE支援（シンタックスハイライト、補完）

**制限**:
- フィールド直後に配置が必須
- 動的なヘルプテキスト生成は不可能

### 2. 型変換システムの設計

#### 設計目標
- 型注釈から自動的に適切な変換関数を選択
- カスタム型への拡張性確保
- エラーメッセージの改善

#### 実装戦略

```python
class BaseWrapper:
    def _detect_type(self, field_name: str, annotation: Any) -> tuple[type, bool]:
        """型注釈から実際の型と省略可能性を検出"""
        
        # Union型の処理（Optional[T] は Union[T, None]）
        if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
            # None以外の型を抽出
            non_none_types = [arg for arg in annotation.__args__ if arg is not type(None)]
            if len(non_none_types) == 1:
                return non_none_types[0], True  # Optional型
                
        return annotation, False  # 必須型
        
    def _get_type_func(self, field_type: type) -> Callable[[str], Any]:
        """型に応じた変換関数を選択"""
        
        if field_type == bool:
            return self._bool_type
        elif field_type == int:
            return int
        elif field_type == float:
            return float
        elif field_type == pathlib.Path:
            return pathlib.Path
        elif hasattr(field_type, '__origin__'):
            # ジェネリック型の処理（list[str], dict[str, int] など）
            return self._handle_generic_type(field_type)
        else:
            return field_type  # カスタム型はそのまま使用
```

#### 特殊ケース: bool型の処理

```python
def _bool_type(self, value: str) -> bool:
    """文字列をbooleanに変換（CLIフラグ用）"""
    
    # 'true', 'false' 文字列の処理
    if value.lower() in ('true', '1', 'yes', 'on'):
        return True
    elif value.lower() in ('false', '0', 'no', 'off'):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")
```

### 3. ネストしたグループの設計

#### 課題
複雑なCLI構造（`--database-host`, `--server-port` など）の表現

#### 解決策: 階層的グループ

```python
@group  
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    
@group
class ServerConfig:
    host: str = "0.0.0.0" 
    port: int = 8080

@namespace
class Config:
    database = DatabaseConfig
    server = ServerConfig
    # 生成されるオプション: --database-host, --database-port, --server-host, --server-port
```

#### 実装詳細

```python
class GroupWrapper:
    def add_to_parser(self, parser: argparse.ArgumentParser, prefix: str = "") -> None:
        """グループの引数をパーサーに追加"""
        
        for field_name, field_info in self._get_field_info().items():
            # オプション名の生成: prefix + field_name
            option_name = f"--{prefix}{field_name}".replace("_", "-")
            
            parser.add_argument(
                option_name,
                type=field_info.type_func,
                default=field_info.default,
                help=field_info.help_text
            )
```

## パフォーマンス設計

### AST解析の最適化

#### 問題
クラス定義毎のAST解析はコストが高い

#### 解決策
```python
class ClassAstHolder:
    _cache: dict[type, 'ClassAstHolder'] = {}
    
    def __new__(cls, target_cls: type) -> 'ClassAstHolder':
        """クラス毎にインスタンスをキャッシュ"""
        if target_cls not in cls._cache:
            instance = super().__new__(cls)
            instance.__init__(target_cls)
            cls._cache[target_cls] = instance
        return cls._cache[target_cls]
```

### 型検出の遅延実行

```python
class BaseWrapper:
    def __init__(self, cls: type) -> None:
        self.cls = cls
        self._field_cache: dict[str, FieldInfo] | None = None
        
    @property 
    def field_info(self) -> dict[str, FieldInfo]:
        """フィールド情報を遅延評価で生成"""
        if self._field_cache is None:
            self._field_cache = self._analyze_fields()
        return self._field_cache
```

## エラーハンドリング設計

### 段階的エラー検出

#### 1. 定義時エラー
```python
@namespace
class BadConfig:
    field_without_annotation  # SyntaxError at decoration time
```

#### 2. 解析時エラー  
```python
@namespace
class Config:
    unsupported_type: ComplexType  # TypeError at parse_args() time
```

#### 3. 実行時エラー
```python
config = Config.parse_args(["--field", "invalid_value"])  # ArgumentTypeError
```

### カスタムエラー階層

```python
class CliparError(Exception):
    """Clipar固有エラーの基底クラス"""

class DefinitionError(CliparError):
    """クラス定義の問題"""
    
class TypeConversionError(CliparError):  
    """型変換の問題"""
    
class ParseError(CliparError):
    """引数解析の問題"""
```

## 拡張性設計

### 新しい型サポートの追加

#### プラグイン機構（将来拡張）
```python
class TypeConverter:
    def can_handle(self, field_type: type) -> bool:
        """この変換器が対象型を処理可能かチェック"""
        
    def convert(self, value: str, field_type: type) -> Any:
        """文字列を対象型に変換"""

class TypeRegistry:
    converters: list[TypeConverter] = []
    
    @classmethod
    def register(cls, converter: TypeConverter) -> None:
        cls.converters.insert(0, converter)  # 優先順位で挿入
        
    @classmethod  
    def find_converter(cls, field_type: type) -> TypeConverter | None:
        for converter in cls.converters:
            if converter.can_handle(field_type):
                return converter
        return None
```

### カスタムデコレータの追加

#### 基盤クラス
```python
class BaseDecorator:
    """新しいデコレータ実装の基底クラス"""
    
    def __init__(self, **options):
        self.options = options
        
    def transform_class(self, cls: type) -> type:
        """クラス変換の実装（サブクラスでオーバーライド）"""
        raise NotImplementedError
        
    def __call__(self, cls: type | None = None):
        if cls is None:
            return self  # パラメータ付きデコレータ
        else:
            return self.transform_class(cls)  # パラメータなしデコレータ
```

## セキュリティ考慮事項

### AST解析の安全性

#### 制限事項
- ユーザー定義クラスのソースコードのみ解析
- 外部ライブラリやビルトインクラスは対象外
- 動的生成されたクラスには対応しない

#### 安全性確保
```python
def _extract_help_texts(self) -> dict[str, str]:
    try:
        source = inspect.getsource(self.cls)
        
        # ソースコードの妥当性チェック
        if len(source) > MAX_SOURCE_LENGTH:
            raise ValueError("Source code too large")
            
        # AST解析実行
        tree = ast.parse(source)
        
    except (OSError, TypeError) as e:
        # ソースが取得できない場合（ビルトインクラスなど）
        logger.warning(f"Cannot extract source for {self.cls}: {e}")
        return {}
```

### 型変換の安全性

#### インジェクション対策
```python
def _get_type_func(self, field_type: type) -> Callable[[str], Any]:
    # 許可された型のみ処理
    if field_type not in ALLOWED_TYPES:
        raise SecurityError(f"Type {field_type} not allowed")
        
    # evalなどの危険な実行は禁止
    if hasattr(field_type, '__call__') and field_type.__name__ == 'eval':
        raise SecurityError("eval type not allowed")
```

## テスト戦略

### テストピラミッド

```
    E2E Tests (少)
   ┌─────────────────┐
   │ Integration     │
   │ Tests (中)      │
   ├─────────────────┤
   │ Unit Tests (多) │
   └─────────────────┘
```

#### ユニットテスト
- 各クラス・メソッドの単体テスト
- モックを活用した隔離テスト
- 境界値・異常系テスト

#### 統合テスト  
- モジュール間連携テスト
- 実際のCLI実行テスト
- バージョン間互換性テスト

#### E2Eテスト
- 実用的なCLI例での動作確認
- パフォーマンステスト
- 実環境想定テスト

### テストデータ戦略

```python
# test/conftest.py
@pytest.fixture
def sample_namespace_class():
    @namespace
    class TestConfig:
        input_file: str
        "Input file path"
        
        output_file: str = "output.txt" 
        "Output file path"
        
        verbose: bool = False
        "Enable verbose output"
        
    return TestConfig

@pytest.fixture  
def complex_nested_class():
    @group
    class DatabaseConfig:
        host: str = "localhost"
        port: int = 5432
        
    @namespace
    class AppConfig:
        database = DatabaseConfig
        workers: int = 1
        
    return AppConfig
```

## 今後の拡張計画

### Phase 1: 基本機能完成
- [ ] 基本デコレータ（namespace, group）
- [ ] 基本型サポート（str, int, bool, list）
- [ ] AST解析ヘルプシステム
- [ ] 並列実装（v310/v312）

### Phase 2: 機能拡張
- [ ] より多くの型サポート（Enum, datetime など）
- [ ] サブコマンド機能
- [ ] 設定ファイル統合
- [ ] シェル補完サポート

### Phase 3: 高度機能
- [ ] プラグインシステム
- [ ] 動的CLI生成
- [ ] パフォーマンス最適化
- [ ] 他ライブラリとの統合

## 参考資料

- [設計判断記録 (ADR)](../docs/adr/)
- [API仕様書](./api-reference.md)
- [開発ワークフロー](./development-workflow.md)
- [パフォーマンス測定結果](../docs/performance/)