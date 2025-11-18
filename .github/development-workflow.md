# Development Workflow Guide for AI Agents

このドキュメントは、AIエージェントがCliparプロジェクトで効率的に開発作業を行うための具体的なワークフローを定義します。

## 基本開発フロー

### 1. 環境確認と準備

#### Python環境の確認
```powershell
# 現在のPython環境確認
python --version

# 期待される環境:
# - 開発用: Python 3.12+ (.venv/)
# - テスト用: Python 3.10 (venv/cp310/), Python 3.12+ (venv/cp312/)
```

#### 仮想環境の切り替え
```powershell
# Python 3.10環境でのテスト
venv\cp310\Scripts\Activate.ps1
python --version  # 確認: 3.10.x または 3.11.x

# Python 3.12+環境でのテスト  
venv\cp312\Scripts\Activate.ps1
python --version  # 確認: 3.12.x 以上

# 開発環境に戻る
.venv\Scripts\Activate.ps1
```

#### 依存関係の同期
```powershell
# 開発環境での依存関係同期
uv sync

# 新しいパッケージの追加例
uv add --dev new-package
uv add runtime-package
```

### 2. 機能開発のワークフロー

#### Step 2.1: 要件分析と影響範囲の特定

**チェック項目**:
- [ ] 変更が公開APIに影響するか？
- [ ] v310とv312両方への実装が必要か？
- [ ] 新しい型サポートが必要か？
- [ ] テストケースの追加が必要か？

**影響範囲の例**:
```
新デコレータ追加 → v310/, v312/, entities.py, tests/
型サポート拡張 → v310/basewrapper.py, v312/basewrapper.py, tests/
バグ修正 → 該当ファイル, 対応するテスト
```

#### Step 2.2: 実装順序の決定

**推奨順序**:
1. v310実装 → v312実装（または同時）
2. ユニットテスト作成（両バージョン）
3. 統合テスト作成（必要に応じて）
4. ドキュメント更新

#### Step 2.3: コード実装

**新機能追加の例（デコレータ）**:

1. **v310実装** (`src/clipar/v310/decorator.py`):
   ```python
   from typing import TypeVar
   
   _NS = TypeVar('_NS')
   
   def new_decorator(
       cls: type[_NS] | None = None,
       *,
       new_param: str | None = None
   ) -> type[_NS] | Callable[[type[_NS]], type[_NS]]:
       # 実装
   ```

2. **v312実装** (`src/clipar/v312/decorator.py`):
   ```python
   def new_decorator[NS](
       cls: type[NS] | None = None,
       *,
       new_param: str | None = None
   ) -> type[NS] | Callable[[type[NS]], type[NS]]:
       # 実装（v310と同等）
   ```

3. **エクスポート** (`src/clipar/entities.py`):
   ```python
   # 他のインポートと共に追加
   new_decorator = import_version_specific().new_decorator
   ```

#### Step 2.4: テスト実装

**ユニットテスト** (`test/unit/v310/test_new_feature.py`):
```python
import pytest
from clipar.v310 import new_decorator

class TestNewDecorator:
    def test_basic_functionality(self):
        @new_decorator
        class TestClass:
            field: str
            
        # テスト実装
        
    def test_with_parameters(self):
        @new_decorator(new_param="value")
        class TestClass:
            field: str
            
        # テスト実装
```

**同様のテストをv312版にも作成**: `test/unit/v312/test_new_feature.py`

### 3. テストとバリデーション

#### 段階的テスト実行

**フェーズ1: 開発環境での基本テスト**
```powershell
# 開発環境(.venv)でのクイックテスト
python -m pytest test/test_import_compatibility.py -v

# 現在のPython版に対応するテスト
python -m pytest test/unit/ test/integration/ -x --tb=short
```

**フェーズ2: Python 3.10環境でのテスト**
```powershell
venv\cp310\Scripts\Activate.ps1
python --version  # 確認必須

# v310テスト
python -m pytest test/unit/v310/ -v
python -m pytest test/integration/v310/ -v

# 全体テスト
python -m pytest -x
deactivate
```

**フェーズ3: Python 3.12+環境でのテスト**
```powershell
venv\cp312\Scripts\Activate.ps1  
python --version  # 確認必須

# v312テスト
python -m pytest test/unit/v312/ -v
python -m pytest test/integration/v312/ -v

# 全体テスト
python -m pytest -x
deactivate
```

#### カバレッジ確認

```powershell
# カバレッジ測定
python -m pytest --cov=clipar --cov-report=html --cov-report=term

# カバレッジレポートの確認
# htmlcov/index.html を開く
```

### 4. 型チェックとリンティング

#### mypy型チェック
```powershell
# 厳密な型チェック
python -m mypy src/clipar --strict

# 特定ファイルのチェック  
python -m mypy src/clipar/v310/decorator.py --strict
python -m mypy src/clipar/v312/decorator.py --strict
```

#### 型注釈の品質確認
```powershell
# 型注釈の完全性チェック
python -c "
from clipar import namespace
help(namespace)
"
```

### 5. ドキュメント更新

#### API変更時の必須更新

1. **メインREADME** (`README.md`):
   - 使用例の追加・更新
   - 機能一覧の更新

2. **API仕様書** (`.github/api-reference.md`):
   - 新しいAPIの詳細仕様
   - 使用例とサンプルコード

3. **Sphinxドキュメント** (`sphinx/source/`):
   ```powershell
   # ドキュメントビルド
   cd sphinx
   python build_docs.py
   ```

#### ヘルプテキストの確認
```powershell
# 生成されたヘルプの確認
python -c "
from examples.basic_example import Config
Config.parse_args(['--help'])
"
```

### 6. パフォーマンステスト

#### 大規模CLI定義での動作確認
```python
# テスト用の大規模クラス定義
@namespace
class LargeConfig:
    field1: str
    "Field 1 help"
    field2: int = 1
    "Field 2 help"
    # ... field100まで定義

# パフォーマンス測定
import time
start = time.time()
config = LargeConfig.parse_args([])
end = time.time()
print(f"Parse time: {end - start:.4f}s")
```

#### メモリ使用量の確認
```python
import tracemalloc

tracemalloc.start()
config = Config.parse_args([])
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

## トラブルシューティング

### よくある問題と解決策

#### 1. テスト失敗: Python環境不整合

**症状**:
```
ImportError: cannot import name 'new_feature' from 'clipar.v312'
```

**原因**: Python 3.10環境でv312専用機能を使用

**解決**:
```powershell
# 適切な環境の確認と切り替え
python --version
# Python 3.10.x → venv\cp310\Scripts\Activate.ps1
# Python 3.12.x → venv\cp312\Scripts\Activate.ps1
```

#### 2. 型チェックエラー: ジェネリック構文

**症状**:
```
mypy: error: Invalid syntax (Python 3.10 doesn't support this syntax)
```

**原因**: v312のジェネリック構文をv310環境で実行

**解決**: 適切なファイルで適切な構文を使用:
- v310/: `TypeVar`ベース
- v312/: 新ジェネリック構文

#### 3. AST解析失敗: ヘルプテキスト抽出不可

**症状**: ヘルプテキストが表示されない

**原因**: フィールド定義とヘルプ文字列の間に空行

**解決**:
```python
# NG
class Config:
    field: str
    
    "Help text"  # 空行のため認識されない

# OK
class Config:
    field: str
    "Help text"  # 直後の行で認識される
```

#### 4. パッケージ管理エラー

**症状**:
```
pip: command not found or not allowed
```

**解決**: `uv`コマンドを使用:
```powershell
# NG
pip install package

# OK  
uv add package
uv add --dev dev-package
uv sync
```

### デバッグテクニック

#### 1. AST解析の詳細確認
```python
from clipar.v310.class_ast import ClassAstHolder  # または v312

@namespace
class DebugConfig:
    field: str
    "Help text"

holder = ClassAstHolder(DebugConfig)
print("Help texts:", holder.help_texts)
print("Field help:", holder.get_help_for_field("field"))
```

#### 2. 引数解析プロセスの追跡
```python
import argparse

@namespace(add_help=True)
class DebugConfig:
    field: str = "default"

# デバッグ用引数で実行
config = DebugConfig.parse_args(["--help"])
```

#### 3. 型検出ロジックの確認
```python
from clipar.v310.namespacewrapper import NamespaceWrapper

wrapper = NamespaceWrapper(DebugConfig)
field_type, is_optional = wrapper._detect_type("field", str)
type_func = wrapper._get_type_func(field_type)
print(f"Type: {field_type}, Optional: {is_optional}, Converter: {type_func}")
```

## CI/CD統合

### GitHub Actions設定例

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install uv
      run: pip install uv
      
    - name: Install dependencies
      run: uv sync
      
    - name: Run tests
      run: |
        if [[ "${{ matrix.python-version }}" == "3.10" || "${{ matrix.python-version }}" == "3.11" ]]; then
          uv run pytest test/unit/v310/ test/integration/v310/ -v
        else
          uv run pytest test/unit/v312/ test/integration/v312/ -v
        fi
        
    - name: Type check
      run: uv run mypy src/clipar --strict
```

### プリコミットフック設定

```yaml
# .pre-commit-config.yaml
repos:
- repo: local
  hooks:
  - id: pytest
    name: pytest
    entry: python -m pytest
    language: system
    pass_filenames: false
    
  - id: mypy
    name: mypy
    entry: python -m mypy src/clipar --strict
    language: system
    pass_filenames: false
```

## リリースプロセス

### バージョンアップ手順

1. **機能テスト完了確認**
2. **両バージョンでの互換性確認**
3. **ドキュメント更新**
4. **CHANGELOGの更新**
5. **タグ作成とリリース**

```powershell
# リリース前チェックリスト実行
python scripts/pre_release_check.py

# タグ作成（hatch-vcsが自動でバージョンを決定）
git tag v1.x.x
git push origin v1.x.x
```

## 参考資料

- [AIエージェント仕様](./ai-specifications.md)
- [API リファレンス](./api-reference.md)
- [メイン開発ガイド](./copilot-instructions.md)
- [テスト仕様](../test/test.copilot-instructions.md)