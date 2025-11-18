# Code Quality Standards and Guidelines

このドキュメントは、Cliparプロジェクトにおけるコード品質基準、静的解析ルール、およびAIエージェントがコード品質を維持するためのガイドラインを定義します。

## 品質基準概要

### 品質目標

- **型安全性**: 100%の型注釈カバレッジ、mypy --strict通過
- **テストカバレッジ**: 90%以上の総合カバレッジ
- **コード複雑度**: Cyclomatic complexity 10以下
- **パフォーマンス**: 100フィールドCLI解析 < 100ms
- **メモリ効率**: 1000 CLIインスタンス生成時 < 50MB

### 品質チェック項目

```
✅ 型チェック (mypy --strict)
✅ リンター (flake8, black)  
✅ テストカバレッジ (pytest-cov)
✅ 複雑度チェック (radon)
✅ セキュリティスキャン (bandit)
✅ 依存関係監査 (pip-audit)
```

## 型安全性ガイドライン

### 型注釈の要求事項

#### 必須: 全パブリック関数・メソッド

```python
# ✅ 正しい例
def process_config(config: NamespaceWrapper) -> dict[str, Any]:
    """設定を処理して辞書を返す"""
    return {"status": "processed"}

# ❌ 間違った例  
def process_config(config):  # 型注釈なし
    return {"status": "processed"}
```

#### 必須: クラス属性の型注釈

```python
# ✅ 正しい例
class NamespaceWrapper(BaseWrapper):
    cls: type
    parser_options: ArgumentParserOptions
    _field_cache: dict[str, FieldInfo] | None = None
    
# ❌ 間違った例
class NamespaceWrapper(BaseWrapper):
    def __init__(self, cls):  # 型注釈なし
        self.cls = cls
```

#### ジェネリック型の適切な使用

**v310版（TypeVarベース）**:
```python
from typing import TypeVar, Generic

_T = TypeVar('_T')

class Container(Generic[_T]):
    def __init__(self, value: _T) -> None:
        self.value = value
    
    def get(self) -> _T:
        return self.value

def process[_NS](cls: type[_NS]) -> Callable[[type[_NS]], type[_NS]]:
    # 実装
```

**v312版（新ジェネリック構文）**:
```python
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value

def process[NS](cls: type[NS]) -> Callable[[type[NS]], type[NS]]:
    # 実装
```

### mypy設定基準

```ini
# pyproject.toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
warn_return_any = true
warn_unreachable = true

# バージョン別設定
[[tool.mypy.overrides]]
module = "clipar.v310.*"
python_version = "3.10"

[[tool.mypy.overrides]]  
module = "clipar.v312.*"
python_version = "3.12"
```

### 型チェック実行

```powershell
# 全体の型チェック
python -m mypy src/clipar --strict

# バージョン別チェック
python -m mypy src/clipar/v310 --strict --python-version 3.10
python -m mypy src/clipar/v312 --strict --python-version 3.12

# 特定ファイルの詳細チェック
python -m mypy src/clipar/v310/decorator.py --strict --show-error-codes
```

## コードスタイルガイドライン

### フォーマッター設定

#### Black設定
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
    | \.mypy_cache
    | \.pytest_cache
    | \.venv
    | venv
    | build
    | dist
)/
'''
```

#### isort設定
```toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### フォーマット実行

```powershell
# 自動フォーマット
python -m black src/ test/
python -m isort src/ test/

# チェックのみ（CI用）
python -m black src/ test/ --check
python -m isort src/ test/ --check-only
```

### コードスタイル規則

#### 命名規則

```python
# クラス名: PascalCase
class NamespaceWrapper:
    pass

# 関数・変数名: snake_case  
def parse_args() -> None:
    field_name = "example"

# 定数: UPPER_SNAKE_CASE
MAX_FIELD_COUNT = 1000

# プライベート属性: _prefix
class Example:
    def __init__(self) -> None:
        self._private_attr = "value"
```

#### ドキュメント文字列

```python
def complex_function(
    config: NamespaceWrapper,
    options: dict[str, Any] | None = None
) -> tuple[bool, str]:
    """複雑な処理を実行する関数
    
    Args:
        config: 名前空間ラッパーのインスタンス
        options: 追加オプション。Noneの場合はデフォルト使用
        
    Returns:
        処理結果のタプル: (成功フラグ, メッセージ)
        
    Raises:
        ValueError: 不正な設定が渡された場合
        TypeError: 型が不正な場合
        
    Example:
        >>> wrapper = NamespaceWrapper(MyConfig)
        >>> success, msg = complex_function(wrapper)
        >>> print(f"Result: {success}, {msg}")
    """
```

## 静的解析設定

### flake8設定

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # whitespace before ':' (Black compatibility)
    W503,  # line break before binary operator
    E501   # line too long (handled by Black)
exclude = 
    .git,
    __pycache__,
    .pytest_cache,
    .mypy_cache,
    .venv,
    venv,
    build,
    dist

# プロジェクト固有ルール
per-file-ignores =
    __init__.py: F401  # imported but unused
    test_*.py: S101    # assert statement (pytest)
```

### pylint設定

```toml
# pyproject.toml  
[tool.pylint]
load-plugins = [
    "pylint.extensions.docparams",
    "pylint.extensions.typing"
]

[tool.pylint.messages_control]
disable = [
    "missing-module-docstring",  # モジュールレベルdocstring不要
    "too-few-public-methods",    # 設定クラスで有効
    "too-many-arguments"         # デコレータで許可
]

[tool.pylint.format]
max-line-length = 88

[tool.pylint.basic]
good-names = ["i", "j", "k", "ex", "ns", "_"]
```

### bandit (セキュリティチェック)

```toml
[tool.bandit]
exclude_dirs = ["test", "tests"]
skips = ["B101"]  # assert_used (テストで必要)
```

## 複雑度管理

### radon設定

```powershell
# 複雑度チェック実行
python -m radon cc src/ --min B  # B以上の複雑度を報告
python -m radon mi src/          # 保守性インデックス
```

### 複雑度基準

| メトリクス | 許容値 | アクション |
|-----------|--------|------------|
| Cyclomatic Complexity | 10以下 | 10超過でリファクタリング必須 |
| Maintainability Index | 70以上 | 70未満でリファクタリング検討 |
| Lines of Code (関数) | 50行以下 | 50行超過で分割検討 |

### 複雑度削減パターン

#### Before（複雑度高）:
```python
def process_field(self, field_name: str, annotation: Any, default: Any) -> None:
    if hasattr(annotation, '__origin__'):
        if annotation.__origin__ is Union:
            non_none_types = [arg for arg in annotation.__args__ if arg is not type(None)]
            if len(non_none_types) == 1:
                field_type = non_none_types[0]
                is_optional = True
            else:
                raise TypeError("Complex Union not supported")
        elif annotation.__origin__ is list:
            field_type = annotation
            is_optional = False
        else:
            raise TypeError(f"Unsupported generic type: {annotation}")
    else:
        field_type = annotation
        is_optional = False
        
    if field_type == bool:
        type_func = self._bool_type
    elif field_type == int:
        type_func = int
    elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
        inner_type = field_type.__args__[0]
        type_func = self._list_type(self._get_type_func(inner_type))
    else:
        type_func = field_type
        
    # さらに処理が続く...
```

#### After（複雑度削減）:
```python
def process_field(self, field_name: str, annotation: Any, default: Any) -> None:
    field_type, is_optional = self._detect_type(field_name, annotation)
    type_func = self._get_type_func(field_type)
    self._add_argument(field_name, field_type, type_func, default, is_optional)

def _detect_type(self, field_name: str, annotation: Any) -> tuple[type, bool]:
    """型注釈から実際の型と省略可能性を検出"""
    if hasattr(annotation, '__origin__'):
        return self._handle_generic_type(annotation)
    return annotation, False

def _handle_generic_type(self, annotation: Any) -> tuple[type, bool]:
    """ジェネリック型の処理"""
    if annotation.__origin__ is Union:
        return self._handle_union_type(annotation)
    elif annotation.__origin__ is list:
        return annotation, False
    else:
        raise TypeError(f"Unsupported generic type: {annotation}")
```

## テストコード品質基準

### テストコード規則

```python
class TestNamespaceWrapper:
    """テストクラス名: Test + 対象クラス名"""
    
    def test_basic_functionality_positive_case(self):
        """テストメソッド名: test_ + 機能 + ケース種別"""
        # Given (準備)
        @namespace
        class Config:
            field: str = "default"
            
        # When (実行)
        config = Config.parse_args([])
        
        # Then (検証) 
        assert config.field == "default"
        
    def test_invalid_input_raises_error(self):
        """異常系テストの例"""
        @namespace
        class Config:
            port: int
            
        # 適切な例外の検証
        with pytest.raises(SystemExit):
            Config.parse_args(["invalid_number"])
```

### テストカバレッジ要求

```powershell
# カバレッジ測定と報告
python -m pytest --cov=clipar --cov-report=html --cov-report=term-missing --cov-fail-under=90

# 詳細カバレッジ確認
python -m coverage report --show-missing --skip-covered
```

### カバレッジ除外ルール

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/test*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*"
]

[tool.coverage.report]  
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:"
]
```

## パフォーマンス基準

### ベンチマークテスト

```python
import time
import pytest

class TestPerformance:
    def test_large_cli_parsing_performance(self):
        """大規模CLI解析のパフォーマンステスト"""
        # 100フィールドのCLI作成
        fields = {f"field_{i}": str for i in range(100)}
        LargeConfig = type("LargeConfig", (), fields)
        LargeConfig = namespace(LargeConfig)
        
        # パフォーマンス測定
        start_time = time.perf_counter()
        config = LargeConfig.parse_args([])
        end_time = time.perf_counter()
        
        parse_time = end_time - start_time
        assert parse_time < 0.1  # 100ms以内
        
    @pytest.mark.benchmark
    def test_memory_usage_benchmark(self):
        """メモリ使用量ベンチマーク"""
        import tracemalloc
        
        tracemalloc.start()
        
        configs = []
        for _ in range(1000):
            @namespace
            class Config:
                field: str = "default"
            configs.append(Config.parse_args([]))
            
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 50  # 50MB未満
```

### プロファイリングガイドライン

```python
# cProfileを使用したプロファイリング
import cProfile
import pstats

def profile_cli_parsing():
    @namespace
    class Config:
        # 大量フィールド定義
        pass
    
    pr = cProfile.Profile()
    pr.enable()
    
    # 測定対象の実行
    for _ in range(100):
        Config.parse_args([])
        
    pr.disable()
    
    # 結果分析
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 上位10関数を表示
```

## 自動化とCI/CD統合

### pre-commit設定

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.9.1
  hooks:
  - id: black
    language_version: python3.10

- repo: https://github.com/pycqa/isort
  rev: 5.12.0
  hooks:
  - id: isort

- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:
  - id: flake8

- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.6.0
  hooks:
  - id: mypy
    additional_dependencies: [types-all]
    args: [--strict]

- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5
  hooks:
  - id: bandit
    args: [-r, src/]
```

### GitHub Actions品質チェック

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
        
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --dev
        
    - name: Run Black
      run: uv run black src/ test/ --check
      
    - name: Run isort  
      run: uv run isort src/ test/ --check-only
      
    - name: Run flake8
      run: uv run flake8 src/ test/
      
    - name: Run mypy
      run: uv run mypy src/clipar --strict
      
    - name: Run bandit
      run: uv run bandit -r src/
      
    - name: Run tests with coverage
      run: |
        uv run pytest --cov=clipar --cov-report=xml --cov-fail-under=90
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 品質メトリクス監視

### SonarQube統合

```properties
# sonar-project.properties
sonar.projectKey=clipar
sonar.organization=plumiume
sonar.sources=src
sonar.tests=test
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.flake8.reportPaths=flake8-report.txt
sonar.python.bandit.reportPaths=bandit-report.json
```

### 品質ゲート設定

| メトリクス | 新規コード閾値 | 全体閾値 |
|-----------|---------------|----------|
| Coverage | 90% | 85% |
| Duplicated Lines | 3% | 5% |  
| Maintainability Rating | A | B |
| Reliability Rating | A | A |
| Security Rating | A | A |
| Technical Debt Ratio | 5% | 10% |

## ドキュメント品質基準

### APIドキュメント自動生成

```python
# 適切なdocstring例
class NamespaceWrapper(BaseWrapper):
    """名前空間デコレータのラッパークラス
    
    このクラスは@namespaceデコレータによって作成され、
    CLIの引数解析とArgumentParserの管理を行います。
    
    Attributes:
        cls: ラップ対象のクラス
        parser_options: ArgumentParserのオプション設定
        
    Example:
        >>> @namespace
        ... class Config:
        ...     field: str = "default"
        >>> config = Config.parse_args([])
        >>> config.field
        'default'
    """
    
    def parse_args(self, args: list[str] | None = None) -> Self:
        """コマンドライン引数を解析してインスタンスを作成
        
        Args:
            args: 解析する引数リスト。Noneの場合はsys.argvを使用
            
        Returns:
            解析されたCLI設定のインスタンス
            
        Raises:
            SystemExit: 引数解析エラーまたは--helpの場合
        """
```

### ドキュメント生成

```powershell
# Sphinx文書の生成
cd sphinx
python build_docs.py

# APIドキュメントの更新確認
sphinx-build -b html source build/html -W  # 警告をエラーとして扱う
```

## エラーハンドリング品質基準

### 例外設計

```python
# カスタム例外階層
class CliparError(Exception):
    """Clipar固有エラーの基底クラス"""

class DefinitionError(CliparError):
    """クラス定義時のエラー"""
    def __init__(self, message: str, cls: type | None = None) -> None:
        super().__init__(message)
        self.cls = cls

class TypeConversionError(CliparError):
    """型変換エラー"""
    def __init__(self, message: str, field_name: str, field_type: type) -> None:
        super().__init__(message)
        self.field_name = field_name
        self.field_type = field_type

# 適切なエラーメッセージ
def _get_type_func(self, field_type: type) -> Callable[[str], Any]:
    if field_type not in SUPPORTED_TYPES:
        raise TypeConversionError(
            f"Type {field_type.__name__} is not supported. "
            f"Supported types: {[t.__name__ for t in SUPPORTED_TYPES]}",
            field_name="unknown",
            field_type=field_type
        )
```

## 継続的品質改善

### レビューチェックリスト

#### コードレビュー必須項目
- [ ] 型注釈の完全性
- [ ] テストカバレッジの維持・向上
- [ ] パフォーマンスへの影響評価
- [ ] エラーハンドリングの適切性
- [ ] ドキュメント（docstring）の更新
- [ ] バージョン間整合性（v310/v312）

#### 品質メトリクスレビュー
- [ ] mypy --strict でエラーなし
- [ ] flake8/black チェック通過
- [ ] テストカバレッジ 90% 以上維持
- [ ] パフォーマンス劣化なし
- [ ] セキュリティスキャン通過

### 定期的品質監査

```powershell
# 月次品質レポート生成
python scripts/quality_report.py

# 技術的負債分析
python -m radon raw src/ --summary
python -m radon hal src/  # Halstead メトリクス

# 依存関係監査
pip-audit
```

## 関連ドキュメント

- [開発ワークフロー](./development-workflow.md) - 日常的な開発プロセス
- [テスト戦略](./testing-strategy.md) - 包括的なテスト方針
- [アーキテクチャ](./architecture.md) - 設計品質の基準
- [API仕様書](./api-reference.md) - インターフェース品質の基準