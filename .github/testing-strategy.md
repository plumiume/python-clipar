# Testing Strategy and Guidelines

このドキュメントは、Cliparプロジェクトにおけるテスト戦略、テストケースの設計指針、およびAIエージェントがテストコードを作成・維持する際のガイドラインを定義します。

## テスト戦略概要

### テストピラミッド

Cliparは以下のテストピラミッド構造を採用しています：

```
      E2E Tests (5%)
     ┌─────────────────┐
     │ 実用例・性能評価  │  
     ├─────────────────┤
     │ Integration (25%) │
     │ モジュール間連携  │
     ├─────────────────┤  
     │ Unit Tests (70%) │
     │ 個別機能・境界値  │
     └─────────────────┘
```

### バージョン別テスト構造

```
test/
├── conftest.py                      # 共通フィクスチャ
├── test_import_compatibility.py     # インポート互換性テスト
├── unit/                           # ユニットテスト
│   ├── v310/                       # Python 3.10/3.11専用
│   │   ├── test_decorator.py
│   │   ├── test_basewrapper.py
│   │   ├── test_namespacewrapper.py
│   │   ├── test_groupwrapper.py
│   │   ├── test_class_ast.py
│   │   └── test_mixin.py
│   └── v312/                       # Python 3.12+専用
│       ├── test_decorator.py
│       ├── test_basewrapper.py
│       ├── test_namespacewrapper.py
│       ├── test_groupwrapper.py
│       ├── test_class_ast.py
│       ├── test_mixin.py
│       └── test_help_formatter.py   # v312専用機能
└── integration/                    # 統合テスト
    ├── v310/
    │   ├── test_end_to_end.py
    │   ├── test_inheritance_integration.py
    │   └── test_type_hints_comprehensive.py
    └── v312/
        ├── test_end_to_end.py
        ├── test_inheritance_integration.py
        └── test_type_hints_comprehensive.py
```

## ユニットテスト指針

### 1. デコレータ機能テスト (`test_decorator.py`)

#### テストカテゴリ

**基本デコレータ機能**:
```python
class TestNamespaceDecorator:
    def test_basic_decoration(self):
        """基本的なデコレータ適用のテスト"""
        @namespace
        class Config:
            field: str
            
        assert hasattr(Config, 'parse_args')
        assert isinstance(Config, type)
        
    def test_decoration_with_parameters(self):
        """パラメータ付きデコレータのテスト"""
        @namespace(description="Test CLI")
        class Config:
            field: str
            
        # descriptionが適切に設定されることを確認
        
    def test_decoration_preserves_class_attributes(self):
        """デコレータがクラス属性を保持することを確認"""
        @namespace  
        class Config:
            field: str
            CLASS_CONSTANT = "value"
            
        assert Config.CLASS_CONSTANT == "value"
```

**エラーケース**:
```python
def test_invalid_class_decoration(self):
    """不正なクラスの装飾でエラーが発生することを確認"""
    with pytest.raises(TypeError):
        @namespace
        class InvalidConfig:
            field_without_annotation  # 型注釈なし
```

#### v310 vs v312 の差異テスト

**v310版の型パラメータテスト**:
```python
# test/unit/v310/test_decorator.py
def test_typevar_generic_support():
    """TypeVarベースのジェネリックサポートをテスト"""
    from typing import TypeVar
    
    T = TypeVar('T')
    
    @namespace
    class Config:
        value: T = "default"  # type: ignore
        
    # TypeVarでの型ヒントが適切に処理されることを確認
```

**v312版の新ジェネリック構文テスト**:
```python
# test/unit/v312/test_decorator.py  
def test_new_generic_syntax():
    """新しいジェネリック構文のサポートをテスト"""
    
    def create_generic_namespace[T]():
        @namespace
        class Config:
            value: T = "default"  # type: ignore
        return Config
        
    ConfigClass = create_generic_namespace[str]()
    # 新構文での型パラメータが適切に処理されることを確認
```

### 2. ベースラッパー機能テスト (`test_basewrapper.py`)

#### 型検出テスト

```python
class TestTypeDetection:
    def test_basic_type_detection(self):
        """基本型の検出テスト"""
        wrapper = BaseWrapper(TestClass)
        
        field_type, is_optional = wrapper._detect_type("str_field", str)
        assert field_type == str
        assert not is_optional
        
        field_type, is_optional = wrapper._detect_type("opt_field", str | None)
        assert field_type == str  
        assert is_optional
        
    def test_generic_type_detection(self):
        """ジェネリック型の検出テスト"""
        wrapper = BaseWrapper(TestClass)
        
        field_type, is_optional = wrapper._detect_type("list_field", list[str])
        assert field_type.__origin__ == list
        assert field_type.__args__ == (str,)
        assert not is_optional
```

#### 型変換関数テスト

```python
class TestTypeConversion:
    def test_bool_type_conversion(self):
        """bool型変換のテスト"""
        wrapper = BaseWrapper(TestClass)
        bool_func = wrapper._get_type_func(bool)
        
        assert bool_func("true") is True
        assert bool_func("false") is False
        assert bool_func("1") is True
        assert bool_func("0") is False
        
        with pytest.raises(argparse.ArgumentTypeError):
            bool_func("invalid")
            
    def test_list_type_conversion(self):
        """list型変換のテスト"""
        wrapper = BaseWrapper(TestClass)
        list_func = wrapper._get_type_func(list[int])
        
        result = list_func(["1", "2", "3"])
        assert result == [1, 2, 3]
        
    def test_custom_type_conversion(self):
        """カスタム型変換のテスト"""
        from pathlib import Path
        
        wrapper = BaseWrapper(TestClass)  
        path_func = wrapper._get_type_func(Path)
        
        result = path_func("/tmp/test.txt")
        assert isinstance(result, Path)
        assert str(result) == "/tmp/test.txt"
```

### 3. AST解析テスト (`test_class_ast.py`)

#### ヘルプテキスト抽出テスト

```python
class TestHelpTextExtraction:
    def test_basic_help_extraction(self):
        """基本的なヘルプテキスト抽出"""
        class TestClass:
            field1: str
            "Help for field1"
            
            field2: int = 1
            "Help for field2"
            
        holder = ClassAstHolder(TestClass)
        
        assert holder.get_help_for_field("field1") == "Help for field1"
        assert holder.get_help_for_field("field2") == "Help for field2"
        
    def test_multiline_help_extraction(self):
        """複数行ヘルプテキストの抽出"""
        class TestClass:
            field: str
            """
            Multi-line help text
            with detailed description
            """
            
        holder = ClassAstHolder(TestClass)
        help_text = holder.get_help_for_field("field")
        
        assert "Multi-line help text" in help_text
        assert "with detailed description" in help_text
        
    def test_no_help_text(self):
        """ヘルプテキストがない場合"""
        class TestClass:
            field: str
            
        holder = ClassAstHolder(TestClass)
        assert holder.get_help_for_field("field") is None
        
    def test_invalid_help_placement(self):
        """不正なヘルプテキスト配置"""
        class TestClass:
            field: str
            
            "Help text after empty line"  # 空行があると認識されない
            
        holder = ClassAstHolder(TestClass)
        assert holder.get_help_for_field("field") is None
```

#### エラーケーステスト

```python
def test_source_not_available(self):
    """ソースコードが取得できないクラス"""
    import builtins
    
    holder = ClassAstHolder(builtins.str)  # ビルトインクラス
    assert holder.get_help_for_field("any_field") is None
    
def test_malformed_source(self):
    """不正な形式のソースコード処理"""
    # 動的生成されたクラスなど
    DynamicClass = type('DynamicClass', (), {'field': str})
    
    holder = ClassAstHolder(DynamicClass)
    # エラーを発生させず、空の結果を返すことを確認
    assert holder.help_texts == {}
```

### 4. 名前空間ラッパーテスト (`test_namespacewrapper.py`)

#### CLI解析テスト

```python
class TestNamespaceWrapper:
    def test_basic_argument_parsing(self, sample_namespace_class):
        """基本的な引数解析"""
        config = sample_namespace_class.parse_args([
            "input.txt",
            "--output-file", "output.txt",  
            "--verbose"
        ])
        
        assert config.input_file == "input.txt"
        assert config.output_file == "output.txt"
        assert config.verbose is True
        
    def test_default_values(self, sample_namespace_class):
        """デフォルト値の処理"""
        config = sample_namespace_class.parse_args(["input.txt"])
        
        assert config.input_file == "input.txt"
        assert config.output_file == "output.txt"  # デフォルト値
        assert config.verbose is False  # デフォルト値
        
    def test_help_generation(self, sample_namespace_class):
        """ヘルプテキストの生成"""
        with pytest.raises(SystemExit):  # --help は sys.exit() を呼ぶ
            sample_namespace_class.parse_args(["--help"])
```

#### エラーハンドリングテスト

```python
def test_missing_required_argument(self, sample_namespace_class):
    """必須引数の欠如でエラー"""
    with pytest.raises(SystemExit):
        sample_namespace_class.parse_args([])  # input_file が必須
        
def test_invalid_argument_type(self, sample_namespace_class):
    """不正な型の引数でエラー"""
    with pytest.raises(SystemExit):
        sample_namespace_class.parse_args([
            "input.txt",
            "--workers", "not_a_number"
        ])
```

### 5. グループラッパーテスト (`test_groupwrapper.py`)

#### ネストグループテスト

```python
class TestGroupWrapper:
    def test_nested_group_options(self, nested_group_class):
        """ネストしたグループのオプション生成"""
        config = nested_group_class.parse_args([
            "--database-host", "db.example.com",
            "--database-port", "3306",
            "--server-host", "api.example.com",
            "--server-port", "8080"
        ])
        
        assert config.database.host == "db.example.com"
        assert config.database.port == 3306
        assert config.server.host == "api.example.com"
        assert config.server.port == 8080
        
    def test_group_default_values(self, nested_group_class):
        """グループのデフォルト値"""
        config = nested_group_class.parse_args([])
        
        assert config.database.host == "localhost"  # グループ内デフォルト
        assert config.database.port == 5432
        
    def test_group_help_text(self, nested_group_class):
        """グループレベルのヘルプテキスト"""
        # --help でグループの説明が含まれることを確認
        with pytest.raises(SystemExit):
            nested_group_class.parse_args(["--help"])
```

## 統合テスト指針

### 1. エンドツーエンドテスト (`test_end_to_end.py`)

#### 実用的なCLIシナリオ

```python
class TestEndToEnd:
    def test_file_processing_cli(self):
        """ファイル処理CLIの完全動作テスト"""
        @namespace(description="File processor")
        class FileProcessor:
            input_files: list[str]
            "Input file paths"
            
            output_dir: str = "./output"
            "Output directory"
            
            format: str = "json"
            "Output format (json|xml|csv)"
            
            workers: int = 1
            "Number of parallel workers"
            
            verbose: bool = False
            "Enable verbose logging"
            
        # 複数のコマンドライン引数パターンをテスト
        test_cases = [
            # 基本的な使用例
            {
                "args": ["file1.txt", "file2.txt"],
                "expected": {
                    "input_files": ["file1.txt", "file2.txt"],
                    "output_dir": "./output",
                    "format": "json",
                    "workers": 1,
                    "verbose": False
                }
            },
            # 全オプション指定
            {
                "args": [
                    "data.txt", 
                    "--output-dir", "/tmp/results",
                    "--format", "csv",
                    "--workers", "4", 
                    "--verbose"
                ],
                "expected": {
                    "input_files": ["data.txt"],
                    "output_dir": "/tmp/results",
                    "format": "csv", 
                    "workers": 4,
                    "verbose": True
                }
            }
        ]
        
        for case in test_cases:
            config = FileProcessor.parse_args(case["args"])
            for key, expected_value in case["expected"].items():
                assert getattr(config, key) == expected_value
                
    def test_database_connection_cli(self):
        """データベース接続CLIのテスト"""
        @group
        class DatabaseConfig:
            host: str = "localhost"
            "Database host"
            
            port: int = 5432  
            "Database port"
            
            name: str = "mydb"
            "Database name"
            
            ssl: bool = False
            "Enable SSL connection"
            
        @namespace(description="Database tool")  
        class DbTool:
            database = DatabaseConfig
            
            command: str
            "Command to execute (backup|restore|query)"
            
            timeout: int = 30
            "Connection timeout in seconds"
            
        config = DbTool.parse_args([
            "backup",
            "--database-host", "prod-db.example.com",
            "--database-port", "5433",
            "--database-ssl",
            "--timeout", "60"
        ])
        
        assert config.command == "backup"
        assert config.database.host == "prod-db.example.com"
        assert config.database.port == 5433
        assert config.database.ssl is True
        assert config.timeout == 60
```

### 2. 型ヒント包括テスト (`test_type_hints_comprehensive.py`)

#### 複雑な型サポートテスト

```python
class TestTypeHintsComprehensive:
    def test_union_types(self):
        """Union型のサポート"""
        @namespace
        class Config:
            value: str | int
            "String or integer value"
            
            optional_value: str | None = None
            "Optional string value"
            
        # 文字列として解析される（第一の型）
        config = Config.parse_args(["hello"])
        assert config.value == "hello"
        assert config.optional_value is None
        
    def test_complex_generics(self):
        """複雑なジェネリック型"""
        @namespace
        class Config:
            string_list: list[str] = []
            "List of strings"
            
            int_list: list[int] = []
            "List of integers" 
            
            # TODO: dict型のサポート（将来実装）
            # config_dict: dict[str, str] = {}
            
        config = Config.parse_args([
            "--string-list", "a", "b", "c",
            "--int-list", "1", "2", "3"
        ])
        
        assert config.string_list == ["a", "b", "c"]
        assert config.int_list == [1, 2, 3]
        
    def test_pathlib_support(self):
        """pathlib.Pathのサポート"""
        from pathlib import Path
        
        @namespace
        class Config:
            input_path: Path
            "Input file path"
            
            output_path: Path = Path("./output.txt")
            "Output file path"
            
        config = Config.parse_args(["/tmp/input.txt"])
        
        assert isinstance(config.input_path, Path)
        assert str(config.input_path) == "/tmp/input.txt"
        assert isinstance(config.output_path, Path)
```

### 3. 継承統合テスト (`test_inheritance_integration.py`)

#### クラス継承との統合

```python
class TestInheritanceIntegration:
    def test_base_class_inheritance(self):
        """基底クラスからの継承"""
        class BaseConfig:
            verbose: bool = False
            "Enable verbose output"
            
        @namespace
        class AppConfig(BaseConfig):
            input_file: str
            "Input file path"
            
        config = AppConfig.parse_args(["test.txt", "--verbose"])
        
        assert config.input_file == "test.txt"
        assert config.verbose is True
        
    def test_mixin_inheritance(self):
        """Mixinクラスとの組み合わせ"""
        from clipar import ReprMixin
        
        @namespace
        class Config(ReprMixin):
            name: str
            "Configuration name"
            
            value: int = 42
            "Configuration value"
            
        config = Config.parse_args(["test"])
        
        # ReprMixinの機能が利用可能であることを確認
        repr_str = repr(config)
        assert "name='test'" in repr_str
        assert "value=42" in repr_str
```

## パフォーマンステスト

### 1. 大規模CLI定義のテスト

```python
class TestPerformance:
    def test_large_namespace_performance(self):
        """大規模な名前空間定義のパフォーマンス"""
        import time
        
        # 100個のフィールドを持つ大規模CLIを動的生成
        fields = {}
        for i in range(100):
            fields[f"field_{i}"] = str
            fields[f"field_{i}_default"] = f"default_{i}"
            
        LargeConfig = type("LargeConfig", (), fields)
        LargeConfig = namespace(LargeConfig)
        
        # 解析時間の測定
        start_time = time.time()
        config = LargeConfig.parse_args([])
        parse_time = time.time() - start_time
        
        # 1秒以内で完了することを確認
        assert parse_time < 1.0
        
        # メモリ使用量の概算チェック
        import sys
        size = sys.getsizeof(config)
        assert size < 10_000  # 10KB未満
        
    def test_deep_nesting_performance(self):
        """深いネスト構造のパフォーマンス"""
        @group
        class Level3Config:
            field: str = "level3"
            
        @group  
        class Level2Config:
            level3 = Level3Config
            field: str = "level2"
            
        @group
        class Level1Config:
            level2 = Level2Config
            field: str = "level1"
            
        @namespace
        class RootConfig:
            level1 = Level1Config
            
        start_time = time.time()
        config = RootConfig.parse_args([])
        parse_time = time.time() - start_time
        
        assert parse_time < 0.1  # 100ms以内
        assert config.level1.field == "level1"
        assert config.level1.level2.field == "level2" 
        assert config.level1.level2.level3.field == "level3"
```

### 2. メモリ使用量テスト

```python
def test_memory_usage(self):
    """メモリ使用量の測定"""
    import tracemalloc
    import gc
    
    tracemalloc.start()
    
    # 大量のCLI定義を作成・破棄
    for i in range(1000):
        @namespace
        class TempConfig:
            field: str = f"default_{i}"
            
        config = TempConfig.parse_args([])
        
        # 明示的にガベージコレクション
        del TempConfig, config
        gc.collect()
        
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # ピークメモリ使用量が妥当な範囲内であることを確認
    peak_mb = peak / 1024 / 1024
    assert peak_mb < 50  # 50MB未満
```

## エラーシナリオテスト

### 1. 実行時エラーテスト

```python
class TestErrorScenarios:
    def test_type_conversion_errors(self):
        """型変換エラーの適切な処理"""
        @namespace
        class Config:
            port: int
            "Port number"
            
        with pytest.raises(SystemExit):
            Config.parse_args(["not_a_number"])
            
    def test_missing_required_arguments(self):
        """必須引数欠如エラー"""
        @namespace
        class Config:
            required_field: str
            "Required field"
            
        with pytest.raises(SystemExit):
            Config.parse_args([])
            
    def test_conflicting_arguments(self):
        """競合する引数エラー"""
        @mutually_exclusive_group(required=True)
        class ExclusiveConfig:
            option_a: bool = False
            option_b: bool = False
            
        @namespace
        class Config:
            exclusive = ExclusiveConfig
            
        with pytest.raises(SystemExit):
            Config.parse_args(["--exclusive-option-a", "--exclusive-option-b"])
```

### 2. 設定エラーテスト

```python
def test_invalid_decorator_usage(self):
    """不正なデコレータ使用」
    with pytest.raises(TypeError):
        @namespace
        class InvalidConfig:
            field_without_annotation = "value"  # 型注釈なし
            
def test_unsupported_type_annotation(self):
    """サポートされていない型注釈」
    with pytest.raises(TypeError):
        @namespace 
        class Config:
            complex_field: complex  # 複素数型は未サポート
```

## テスト実行とCI/CD

### 環境別テスト実行

```powershell
# Python 3.10環境
venv\cp310\Scripts\Activate.ps1
python -m pytest test/unit/v310/ test/integration/v310/ -v --cov=clipar.v310

# Python 3.12環境  
venv\cp312\Scripts\Activate.ps1
python -m pytest test/unit/v312/ test/integration/v312/ -v --cov=clipar.v312

# 全体テスト（開発環境）
python -m pytest test/ -v --cov=clipar --cov-report=html
```

### カバレッジ目標

- **ユニットテスト**: 95%以上
- **統合テスト**: 85%以上  
- **全体**: 90%以上

### CI/CDでの自動テスト

```yaml
# .github/workflows/test.yml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
        os: [ubuntu-latest, windows-latest, macos-latest]
        
    steps:
    - name: Test with pytest
      run: |
        if [[ "${{ matrix.python-version }}" == "3.10" || "${{ matrix.python-version }}" == "3.11" ]]; then
          pytest test/unit/v310/ test/integration/v310/ --cov=clipar.v310
        else
          pytest test/unit/v312/ test/integration/v312/ --cov=clipar.v312
        fi
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## テストデータ管理

### フィクスチャ設計

```python
# test/conftest.py
@pytest.fixture
def sample_args():
    """サンプル引数のフィクスチャ"""
    return [
        "input.txt",
        "--output-file", "output.txt",
        "--workers", "4",
        "--verbose"
    ]

@pytest.fixture  
def complex_args():
    """複雑な引数パターンのフィクスチャ"""
    return [
        "data.csv",
        "--database-host", "db.example.com",
        "--database-port", "5432", 
        "--server-host", "api.example.com",
        "--server-port", "8080",
        "--format", "json",
        "--workers", "8",
        "--timeout", "60",
        "--verbose"
    ]

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """テスト用一時ディレクトリ"""
    return tmp_path_factory.mktemp("clipar_test_data")
```

### モックとスタブの活用

```python
class TestWithMocks:
    @pytest.fixture
    def mock_argparse_parser(self, mocker):
        """ArgumentParserのモック」
        return mocker.patch("argparse.ArgumentParser")
        
    def test_parser_configuration(self, mock_argparse_parser):
        """パーサー設定のテスト（実際のCLI実行なし）」
        @namespace(description="Test CLI")
        class Config:
            field: str
            
        # モックが適切に呼ばれることを確認
        mock_argparse_parser.assert_called_once()
        call_kwargs = mock_argparse_parser.call_args[1]
        assert call_kwargs["description"] == "Test CLI"
```

## 品質保証とコードレビューガイドライン

### テストコード品質チェックリスト

- [ ] **明確なテスト名**: テスト内容が名前から理解できる
- [ ] **独立性**: 各テストが他のテストに依存しない
- [ ] **再現性**: 何度実行しても同じ結果
- [ ] **境界値テスト**: 正常系・異常系の境界を網羅
- [ ] **エラーメッセージ**: 失敗時に有用な情報を提供

### パフォーマンステストのガイドライン

- **測定の一貫性**: 同一環境での複数回実行
- **妥当な閾値**: 実用的な許容範囲の設定
- **環境依存性**: CI環境でも安定動作する設計

## 関連ドキュメント

- [メインテスト仕様](../test/test.copilot-instructions.md)
- [開発ワークフロー](./development-workflow.md)
- [API仕様書](./api-reference.md)
- [アーキテクチャ](./architecture.md)