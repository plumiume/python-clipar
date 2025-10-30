# Test Instructions for Clipar

## ⚠️ **読む前に - 最重要事項**

**このプロジェクトはv310とv312の並列実装を持つため、テスト実行時の仮想環境選択が極めて重要です。**

- **v310テスト**: Python 3.10/3.11 環境で実行
- **v312テスト**: Python 3.12+ 環境で実行
- **環境不適切 = テスト失敗の主要原因**

**必ず `python --version` でバージョンを確認してからテスト実行してください。**

---

## テスト構造の概要
- `test/unit/` — ユニットテスト（v310/, v312/ に分離）
- `test/integration/` — 統合・E2E テスト（v310/, v312/ に分離）
- `test/test_import_compatibility.py` — トップレベルインポート互換性テスト
- `test/conftest.py` — pytest 設定とフィクスチャ

## テスト実行コマンド（Windows/PowerShell）

**⚠️ 重要**: 下記コマンドは適切な仮想環境で実行してください。環境が不適切だと失敗します。

### 基本テスト実行
```powershell
# 全テスト（現在の Python バージョンに適合するテストが実行される）
# 注意: .venv/ または適切な venv/cp3XX/ 環境で実行
python -m pytest -q

# 特定バージョンのユニットテスト
python -m pytest -q test/unit/v310    # Python 3.10/3.11 環境で実行推奨
python -m pytest -q test/unit/v312    # Python 3.12+ 環境で実行推奨

# 特定バージョンの統合テスト
python -m pytest -q test/integration/v310  # Python 3.10/3.11 環境で実行推奨
python -m pytest -q test/integration/v312  # Python 3.12+ 環境で実行推奨

# インポート互換性テスト（バージョン共通、どの環境でも実行可能）
python -m pytest -q test/test_import_compatibility.py

# 詳細出力
python -m pytest -v test/unit/v310/test_decorator.py
```

### カバレッジ付きテスト（オプション）
```powershell
# カバレッジを追加（uv使用）
uv add --dev pytest-cov

# カバレッジ付きテスト
python -m pytest --cov=clipar --cov-report=html
```

## ⚠️ **重要: 仮想環境の使い分け**

**テスト実行時は必ず適切な仮想環境を有効化してください。不適切な環境では失敗の原因となります。**

- **`.venv/`**: 開発用環境（Python 3.12+、通常の開発作業）
- **`venv/cp310/`**: Python 3.10 専用テスト環境
- **`venv/cp312/`**: Python 3.12 専用テスト環境
- **パッケージ管理**: `uv add` のみ使用、`pip install` 禁止

### テスト用仮想環境の自動構築
以下のコマンドでテスト専用の仮想環境を作成・設定できます（`venv/` ディレクトリはgitで管理されません）：

```powershell
# Python 3.10 テスト環境の作成
uv venv --python 3.10 venv/cp310

# Python 3.12 テスト環境の作成  
uv venv --python 3.12 venv/cp312

# Python 3.10 環境の依存関係同期
venv\cp310\Scripts\activate
uv sync --active
deactivate

# Python 3.12 環境の依存関係同期
venv\cp312\Scripts\activate
uv sync --active
deactivate
```

### 🎯 **推奨: Pythonバージョン別テスト実行手順**

**テスト対象に応じて必ず適切な仮想環境を使用してください:**

```powershell
# === v310テストの場合（Python 3.10/3.11環境が必要） ===
venv\cp310\Scripts\activate  # Python 3.10環境を有効化
python --version              # Python 3.10.x であることを確認
python -m pytest -q test/unit/v310 test/integration/v310
python -m pytest -q test/test_import_compatibility.py  # 互換性テスト
deactivate

# === v312テストの場合（Python 3.12+環境が必要） ===
venv\cp312\Scripts\activate  # Python 3.12環境を有効化
python --version              # Python 3.12.x であることを確認
python -m pytest -q test/unit/v312 test/integration/v312
python -m pytest -q test/test_import_compatibility.py  # 互換性テスト
deactivate

# === 開発環境での全体テスト（Python 3.12+） ===
.venv\Scripts\activate        # 開発環境を有効化
python --version              # Python 3.12.x であることを確認
python -m pytest -q          # 全テスト実行（現在環境に適合するもの）
deactivate
```

**重要な注意事項**: 
- `venv/` ディレクトリは `.gitignore` で除外されているため、各開発者が個別に構築する
- **環境のバージョン確認は必須** - `python --version` で確認してからテスト実行
- v310テストをPython 3.12環境で実行しても動作するが、v310実装の正確性確認には専用環境を推奨
- **環境が不適切だとテスト失敗の原因となるため、上記手順に従うこと**

## テストパターンと規則

### ユニットテスト構造
- **ファイル命名**: `test_<module_name>.py`
- **クラス命名**: `TestClassName` (テスト対象クラス名に `Test` プレフィックス)
- **メソッド命名**: `test_<specific_functionality>`

### 共通フィクスチャ (conftest.py)
```python
@pytest.fixture
def sample_args():
    """基本的なコマンドライン引数"""
    return ["--verbose", "--output", "test.txt", "--count", "5"]

@pytest.fixture  
def complex_args():
    """複雑なサブコマンド付き引数"""
    return ["process", "--input", "data.csv", "--format", "json", "--verbose"]
```

### テスト例パターン
```python
# 1. 基本的なnamespace テスト
@namespace
class TestConfig:
    arg1: str
    arg2: int = 10

config = TestConfig.parse_args(["value1", "--arg2", "20"])
assert config.arg1 == "value1"
assert config.arg2 == 20

# 2. グループ化テスト  
@group
class DatabaseGroup:
    host: str = "localhost"
    port: int = 5432

@namespace
class Config:
    database = DatabaseGroup

# 3. エラー処理テスト
with pytest.raises(SystemExit):
    Config.parse_args(["--invalid-arg"])
```

## バージョン固有の注意事項

### v310 テスト（Python 3.10/3.11）
- `TypeVar` を使用: `_NS = TypeVar('_NS')`
- `Generic[_NS]` 継承パターン
- `typing_extensions.Self` を利用

### v312 テスト（Python 3.12+）
- 新ジェネリック構文: `class Wrapper[NS]:`
- `Self` は標準 typing モジュールから取得
- bound 制約: `[W: BaseWrapper[Any]]`

### 統合テストのバージョン固有差異
- **v310統合テスト**: `DeprecationWarning` が発生しない（警告チェックなし）
- **v312統合テスト**: ネストされたグループで `DeprecationWarning` が正常に発生

### 実装差分の確認
現在 v310 は更新が遅れている可能性があります。確認事項：
1. `namespacewrapper.py` の解析処理統合（v312 では `_after_parse()` に統合済み）
2. ジェネリック構文の差分（機能は同等だが記法が異なる）
3. 新機能の取り込み（Location 型、新しいフック）

### インポート互換性テスト
- **ファイル**: `test/test_import_compatibility.py`
- **目的**: v310/v312実装のトップレベルインポートが両環境で正常に動作することを検証
- **テスト内容**:
  - `@namespace`, `@group`, `@mutually_exclusive_group` デコレータの動作
  - `NotSelected` センチネル値の使用
  - `mixin.ReprMixin` の機能
  - 複雑なネストした構造での互換性
  - バージョン固有の実装詳細の漏れチェック
- **実行環境**: バージョン共通（両環境で同じテストが実行される）

## 開発時の確認手順

### 新機能追加時
1. v312 で機能を実装・テスト（Python 3.12+環境）
2. v310 でも同等機能を実装（ジェネリック構文を旧形式に変換）
3. **適切な仮想環境で**両バージョンでテスト実行
4. 統合テストで互換性確認

### ⚠️ **PR 前必須チェックリスト（環境別実行）**
```powershell
# === 手順 1: Python 3.10環境でv310テスト ===
venv\cp310\Scripts\activate
python --version  # 3.10.x であることを確認
python -m pytest -q test/unit/v310
python -m pytest -q test/integration/v310
deactivate

# === 手順 2: Python 3.12環境でv312テスト ===
venv\cp312\Scripts\activate
python --version  # 3.12.x であることを確認
python -m pytest -q test/unit/v312
python -m pytest -q test/integration/v312

# 3. 型チェック（推奨）
mypy src/clipar/v310/
mypy src/clipar/v312/  # Python 3.12+ でのみ実行
```

### CI/GitHub Actions での実行
- Python 3.10, 3.11 → v310 テストのみ
- Python 3.12+ → v312 テストも含む全テスト

## トラブルシューティング

### ⚠️ **最重要**: 仮想環境関連の問題
**0. テスト失敗の90%は不適切な仮想環境が原因です！**
   - `python --version` でPythonバージョンを確認
   - v310テストは Python 3.10/3.11 環境で実行
   - v312テストは Python 3.12+ 環境で実行
   - **環境不一致がエラーの最大の原因**

### よくある問題
1. **ImportError**: Python バージョンと実装選択の不整合
   - `src/clipar/__init__.py` の version_info チェックを確認
   - **まず仮想環境が適切か確認！**

2. **テスト失敗**: v310/v312 間の実装差分
   - `v312_v310_correspondence_report.md` を参照
   - **適切な環境でテスト実行しているか確認！**

3. **型エラー**: ジェネリック構文の違い
   - v310: `Generic[_NS]`, v312: `[NS]` 形式の変換が必要
   - **Python 3.12環境でv310テストを実行していないか確認！**

4. **SyntaxError**: Python 3.12構文をPython 3.10で実行
   - **v312専用構文が含まれるファイルを古い環境で実行している**
   - 適切な環境に切り替えてください

### デバッグ用コマンド（⚠️ 環境確認必須）
```powershell
# === まず環境確認（必須） ===
python --version  # 3.10.x または 3.12.x を確認

# === 詳細エラー出力 ===
# v310テストの場合（Python 3.10環境推奨）
python -m pytest -v --tb=long test/unit/v310/test_decorator.py::TestSpecificCase

# v312テストの場合（Python 3.12環境推奨）
python -m pytest -v --tb=long test/unit/v312/test_decorator.py::TestSpecificCase

# === 特定テストのみ実行 ===
python -m pytest -k "test_namespace_basic" -v

# === PDB デバッガ起動 ===
python -m pytest --pdb test/unit/v310/test_decorator.py::TestSpecificCase

# === 環境不適切時の対処 ===
# v310テストなのにPython 3.12環境の場合:
venv\cp310\Scripts\activate  # 適切な環境に切り替え
python -m pytest -v test/unit/v310/test_decorator.py::TestSpecificCase
deactivate
```

## 最近の更新履歴

### 2025年10月31日: v310/v312テスト分離とインポート互換性テスト追加
- **v310テストの依存関係修正**: v310ユニットテストがv312モジュールに依存していた問題を解決
- **統合テストの分離**: 統合テストもv310/v312に分離し、`DeprecationWarning`の動作差異に対応
- **インポート互換性テスト追加**: `test/test_import_compatibility.py`でトップレベルインポートの両バージョン互換性を検証
- **テスト構造の完全分離**: 各バージョンが独立してテスト実行可能に
- **自動環境構築手順追加**: `uv venv`コマンドによるテスト専用仮想環境の自動構築手順を文書化
- **ソースドキュメント整備**: 全srcファイルに英語docstringとコメントを追加（開発者向け）

### 修正された問題
- v310環境でのPython 3.12構文エラー（ジェネリック構文）
- 統合テストでのバージョン間警告動作の違い
- テスト依存関係の循環参照

---
**注**: 現在 v310 の更新が遅れています。v312 の新機能を v310 にバックポートする際は、`v312_v310_correspondence_report.md` を参考にしてください。

## 重要：このドキュメントの保守

**テスト関連の変更が行われた際は、最後にこの instructions.md を更新すること**

新しいテストの追加、テスト構造の変更、実行方法の変更など、テスト関連の任意の変更を実施した後は：
1. 該当する変更内容をこのファイルに反映する
2. 新しいコマンド例があれば追加する  
3. 注意事項や制限事項があれば記載する
4. バージョン固有の違いがあれば適切なセクションに記載する

このルールにより、開発者と AI エージェントが常に最新かつ正確なテスト情報にアクセスできます。