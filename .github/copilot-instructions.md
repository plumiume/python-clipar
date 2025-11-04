## 目的
このファイルは、このリポジトリで自動化エージェント（Copilot など）が即戦力として動けるよう、必須の設計・開発・テスト情報を短くまとめたものです。

## 重要なポイント（要約）
- **パッケージ名**: `clipar`（ソースは `src/clipar`）- 型注釈とデコレータで CLI を定義する軽量ライブラリ
- **並列実装の構造**: `src/clipar/v310/`（Python 3.10/3.11）と `src/clipar/v312/`（Python 3.12+）が共存
- **バージョン選択機構**: `src/clipar/__init__.py` が実行時の `sys.version_info` でどちらの実装をインポートするかを決定
  - Python 3.12+ → `v312/` をインポート
  - Python 3.10/3.11 → `v310/` をインポート
- **公開 API の変更時は両バージョンの更新が必須** - 片側のみの更新は実行時エラーの原因

## アーキテクチャ／設計の「なぜ」

### ライブラリの目的
Python の型注釈（`str`, `int`, `bool` など）とクラスデコレータ（`@namespace`, `@group`）を使って、宣言的に CLI を定義できるライブラリ。argparse のボイラープレートを排除し、型安全性を確保。

### 並列実装が必要な理由
Python 3.12 で導入された新しいジェネリック構文（`class Foo[T]:`）は Python 3.10/3.11 と互換性がない。`TypeVar` ベースの旧構文と新構文の両方をサポートするため、最適化された実装を各バージョン用に用意している。

**具体例**:
```python
# v310/decorator.py (Python 3.10/3.11)
_NS = TypeVar('_NS')
def __call__[self, namespace_type: type[_NS] | None = None]: ...

# v312/decorator.py (Python 3.12+)
def __call__[NS](self, namespace_type: type[NS] | None = None): ...
```

### AST パースによるヘルプテキスト抽出
`class_ast.py` の `ClassAstHolder` がクラス定義を AST 解析し、フィールド直後の文字列リテラルをヘルプテキストとして抽出する独自機構:

```python
@namespace
class Config:
    input_file: str
    "Path to the input data file (required)"  # ← AST 解析で抽出
    
    workers: int = 4
    "Number of parallel workers"  # ← これも抽出
```

これにより、`Config.parse_args(['--help'])` で自動的にヘルプが表示される。

## 主要なファイル／ディレクトリ（参照用）

### エントリポイント
- `src/clipar/__init__.py` — バージョン選択ロジック（START HERE）
  - `sys.version_info` を判定して `v310` or `v312` からインポート
  - 変更時は両バージョンの実装が揃っているか確認

### 実装本体（v310/ と v312/ で同じ構造）
- `decorator.py` — `@namespace`, `@group`, `@mutually_exclusive_group` デコレータ
- `basewrapper.py` — `BaseWrapper` 基底クラス、`NotSelected` sentinel、型変換ロジック
- `namespacewrapper.py` — トップレベル CLI 名前空間、`ArgumentParser` オプション管理
- `groupwrapper.py` — 引数グループ（`--database-host` のような階層オプション）
- `class_ast.py` — AST 解析でクラス定義からヘルプテキストを抽出
- `mixin.py` — `ReprMixin`（自動 `__repr__`）、`BaseMixin`（コマンド追跡）

### v312 固有ファイル
- `v312/help_formatter.py` — カスタムヘルプフォーマッタ（現在は TODO）

### その他
- `entities.py` — バージョン選択後のラッパークラスを re-export
- `test/` — `unit/v310/`, `unit/v312/`, `integration/v310/`, `integration/v312/` に分離
- `test/conftest.py` — pytest フィクスチャ（`sample_args`, `complex_args`）
- `pyproject.toml` — hatchling ビルド設定、開発依存パッケージ（pytest, sphinx など）

## コーディング／変更ルール（守るべき具体例）

### 並列実装の整合性維持
公開 API を変更する場合、**必ず両方の `v310/` と `v312/` に実装とテストを追加・更新する**:

1. `v310/decorator.py` を変更 → `v312/decorator.py` も同様に変更
2. `test/unit/v310/test_decorator.py` にテスト追加 → `test/unit/v312/test_decorator.py` にも追加
3. 両環境でテスト実行して成功を確認（後述の「テスト」セクション参照）

**アンチパターン**: `v310` 側だけを更新して `v312` を放置すること（実行時エラーの原因）

### ヘルプテキストの記述パターン
フィールドの**直後の行に文字列リテラル**を置く（README の「Adding Help Messages」セクション参照）:

```python
@namespace
class Config:
    input_file: str
    "Path to the input data file (required)"  # ← この形式
    
    workers: int = 4
    "Number of parallel workers"
```

この文字列は `class_ast.py` の `ClassAstHolder` が AST 解析で抽出し、argparse のヘルプに自動反映される。

### NotSelected の使い方
`NotSelected` は未設定オプションを表す sentinel 値（`basewrapper.py` で定義）:

```python
from clipar import NotSelected

config = Config.parse_args()
if config.optional_arg is NotSelected:
    print("オプション引数が指定されていません")
```

**注意**: `None` と比較しない（`None` は明示的な `None` 値として扱われる）。

### ネストしたグループの定義
`@group` デコレータで階層オプションを作成:

```python
@group
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432

@namespace
class AppConfig:
    database = DatabaseConfig  # --database-host, --database-port が生成される
```

テストも同様の構造で `unit/v310/test_groupwrapper.py` などに分かれている。

## パッケージ管理（重要）
- **パッケージマネージャー**: `uv` を使用。`pip` 系コマンドは禁止。
- **パッケージ追加**: `uv add <package>` のみ使用可能。
- **開発依存**: `uv add --dev <package>` で開発用パッケージを追加。
- **同期**: `uv sync` で依存関係を同期。

## 仮想環境構成
- `.venv/` — 開発用仮想環境（Python 3.12+）
- `venv/cp310/` — Python 3.10 テスト用環境
- `venv/cp312/` — Python 3.12 テスト用環境
- **重要**: Python 実行前に目的の仮想環境が有効になっているかを必ず確認する。

## テスト／ローカル検証（具体的コマンド）

**⚠️ 最重要**: テスト実行前に `python --version` で Python バージョンを確認すること！
- `v310` テストは Python 3.10/3.11 環境で実行
- `v312` テストは Python 3.12+ 環境で実行
- 不適切な環境での実行はテスト失敗の主要原因

### 基本テストコマンド（PowerShell）

```powershell
# 全テスト（現在の Python 環境に対応するテストのみ実行）
python -m pytest -q

# バージョン別ユニットテスト
python -m pytest -q test/unit/v310    # Python 3.10/3.11 環境で実行
python -m pytest -q test/unit/v312    # Python 3.12+ 環境で実行

# バージョン別統合テスト
python -m pytest -q test/integration/v310
python -m pytest -q test/integration/v312

# インポート互換性テスト（どの環境でも実行可能）
python -m pytest -q test/test_import_compatibility.py

# 詳細出力（特定テストファイル）
python -m pytest -v test/unit/v310/test_decorator.py
```

### 複数環境でのテスト（推奨ワークフロー）

```powershell
# Python 3.10 環境でテスト
venv\cp310\Scripts\activate
python --version  # 確認: Python 3.10.x または 3.11.x
python -m pytest -q test/unit/v310
deactivate

# Python 3.12 環境でテスト
venv\cp312\Scripts\activate
python --version  # 確認: Python 3.12.x 以上
python -m pytest -q test/unit/v312
deactivate
```

### カバレッジ測定（オプション）

```powershell
# カバレッジツールの追加
uv add --dev pytest-cov

# カバレッジ付き実行
python -m pytest --cov=clipar --cov-report=html test/
```

## プロジェクト固有のパターン／アンチパターン

### パターン ✅
- **CLI 定義**: クラスとフィールドの型注釈で記述し、`@namespace`/`@group` デコレータで登録
- **ヘルプテキスト**: フィールド直後の文字列リテラルを使用（AST 解析で自動抽出）
- **グループ化**: ネストした `@group` クラスで複雑な階層オプションを表現
- **型変換**: `basewrapper.py` の型検出ロジックで自動的に型変換関数を選択
- **未設定判定**: `NotSelected` sentinel を使って未設定オプションを検出

### アンチパターン ❌
- `v310` 側だけを更新して `v312` を放置（API 不整合の原因）
- `None` と `NotSelected` を混同する（意味が異なる）
- 不適切な Python 環境でバージョン固有テストを実行
- `pip` コマンドでパッケージを追加（`uv` のみ使用可能）
- ヘルプテキストをデコレータ引数で指定（文字列リテラル方式を使用）

## よくある変更シナリオ

### 1. 新しいデコレータオプションを追加
1. 両方の `v310/namespacewrapper.py` と `v312/namespacewrapper.py` の `ArgumentParserOptions` TypedDict を更新
2. `NamespaceWithOptions.__call__()` docstring を更新してパラメータを文書化
3. `test/unit/v310/test_decorator.py` と `test/unit/v312/test_decorator.py` にテスト追加

### 2. 型サポートを拡張
1. `basewrapper.py`（両バージョン）の型検出ロジックを修正
2. 必要に応じて型変換関数を追加（`_bool_type()` パターンを参照）
3. `test_basewrapper.py`（両バージョン）にユニットテスト追加
4. 実際の CLI 例を使った統合テストを追加

### 3. ドキュメント更新
- **インラインヘルプ**: クラスフィールド直後の文字列リテラルを追加/修正
- **Sphinx ドキュメント**: `sphinx/source/` のファイルを編集し、`uv run sphinx-build -b html . _build/html` でビルド
- **README 例**: `examples/` の実装と同期を保つ

## PR 作成時のチェックリスト（簡易）
1. **環境確認**: 適切な仮想環境（.venv, venv/cp310/, venv/cp312/）が有効になっているか確認。
2. **パッケージ管理**: 新規依存がある場合は `uv add` コマンドでのみ追加し、`uv sync` で同期。
3. 変更が `v310` と `v312` の双方に影響するか確認。必要なら両方更新してテストを追加。
4. 既存のユニットテスト（`test/unit/...`）と統合テスト（`test/integration/...`）をローカルで実行して成功させる。
5. `pyproject.toml` の依存に沿って dev 環境を整える（uv による依存管理）。
6. README や `instructions/` にある開発方針が変わる場合は、そのファイルも更新する。

## 参照先（必ず確認するファイル）
- `src/clipar/__init__.py` — バージョン選択の起点
- `src/clipar/v310/` および `src/clipar/v312/` の主要ファイル:
  - `decorator.py` — デコレータ実装
  - `basewrapper.py` — 基底クラスと型変換ロジック
  - `class_ast.py` — AST 解析とヘルプテキスト抽出
  - `namespacewrapper.py`, `groupwrapper.py` — CLI 構造管理
- `test/` — ユニット/統合テスト（バージョン別フォルダ構造）
- `pyproject.toml` — 依存関係とビルド設定
- `README.md` — 基本的な使用例とパターン
- `test/test.copilot-instructions.md` — テスト固有の詳細ガイド

---

## フィードバック歓迎
この指示ファイルで不明瞭な部分や、追記してほしい運用（CI/CD、ブランチ戦略、リリースプロセスなど）があれば教えてください。
