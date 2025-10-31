## 目的
このファイルは、このリポジトリで自動化エージェント（Copilot など）が即戦力として動けるよう、必須の設計・開発・テスト情報を短くまとめたものです。

## 重要なポイント（要約）
- パッケージ名: `clipar`（ソースは `src/clipar`）。
- バージョン特化実装が並列に存在する: `src/clipar/v310/` と `src/clipar/v312/`。
- `src/clipar/__init__.py` が実行時の Python バージョンでどちらの実装を選ぶかを決定する（3.12 以上 → v312、3.10/3.11 → v310）。この切替に注意して変更を加える。

## アーキテクチャ／設計の「なぜ」
- 目的: Python の型注釈とクラスデコレータを使って CLI を定義する軽量ライブラリ。
- 並行実装の理由: Python 3.12 の新機能（型や AST の違いなど）に対応するため、互換性を保ちながら最適化した実装をそれぞれ用意している。

## 主要なファイル／ディレクトリ（参照用）
- `src/clipar/__init__.py` — 実装を選ぶエントリポイント。ここを見ればバージョン選択のロジックがわかる。
- `src/clipar/v310/` と `src/clipar/v312/` — 実装本体。`basewrapper.py`, `decorator.py`, `class_ast.py` が共通的な役割を担う。
- `src/clipar/entities.py` — エンティティ（データ構造）関連。
- `test/` — テストは `unit/` と `integration/` に分かれており、さらに `v310/` と `v312/` に対応したテスト群がある。
- `pyproject.toml` — ビルド（hatchling）と開発依存（pytest など）を確認できる。
- `instructions/` と `DEVELOPMENT_GUIDE.md` — 開発上の補足ドキュメントがある。必ず参照する。

## コーディング／変更ルール（守るべき具体例）
- 並列実装の整合性: 公開 API を変更する場合、可能なら両方の `v310`/`v312` に実装を追加・更新してテストを揃える。
- バージョン切替注意: `__init__.py` のロジックは単純だが、片側のみ変更しても別バージョンで動作しない可能性があるため、PR で明示的に対応状況を記載する。
- ヘルプ文（引数説明）は、フィールドの直後に文字列リテラルを置くパターンが使われている（参照: README の「Adding Help Messages」セクション）ので同様の方法で実装する。
- NotSelected/NotSelectedType: sentinel（未選択）値が `basewrapper.py` に存在する。オプションの未設定判定で使われるので取り扱いに注意。

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
- 開発依存に `pytest` がある。一般的なテスト実行はプロジェクトルートで次のコマンドを使う（PowerShell の例）:

```powershell
# 開発環境での全テスト（.venv が有効な状態で）
python -m pytest -q

# 特定ディレクトリ（例: v310 のユニットテスト）
python -m pytest -q test/unit/v310

# integration テスト
python -m pytest -q test/integration

# Python 3.10 環境でのテスト（venv/cp310/ を有効化してから）
venv\cp310\Scripts\activate
python -m pytest -q test/unit/v310

# Python 3.12 環境でのテスト（venv/cp312/ を有効化してから）
venv\cp312\Scripts\activate  
python -m pytest -q test/unit/v312
```

- 注意: `v312` 用テストは Python 3.12 以上で実行する必要があります（`__init__.py` の選択ロジックに依存）。複数バージョンでの検証は適切な仮想環境を使って実行してください。

## プロジェクト固有のパターン／アンチパターン
- パターン: CLI 定義はクラスとフィールドの型注釈で記述し、`@namespace`/`@group` デコレータで登録する。フィールド直後の文字列リテラルを help に使う。
- パターン: グループ化（ネストした group クラス）で複雑な階層オプションを表現する。テストも同様の構造で分かれている。
- アンチパターン: `v310` 側だけを先に更新して `v312` を放置すること（互換性・差分の原因になる）。

## PR 作成時のチェックリスト（簡易）
1. **環境確認**: 適切な仮想環境（.venv, venv/cp310/, venv/cp312/）が有効になっているか確認。
2. **パッケージ管理**: 新規依存がある場合は `uv add` コマンドでのみ追加し、`uv sync` で同期。
3. 変更が `v310` と `v312` の双方に影響するか確認。必要なら両方更新してテストを追加。
4. 既存のユニットテスト（`test/unit/...`）と統合テスト（`test/integration/...`）をローカルで実行して成功させる。
5. `pyproject.toml` の依存に沿って dev 環境を整える（uv による依存管理）。
6. README や `instructions/` にある開発方針が変わる場合は、そのファイルも更新する。

## 参照先（必ず確認するファイル）
- `src/clipar/__init__.py`
- `src/clipar/v310/` および `src/clipar/v312/` の主要ファイル（`decorator.py`, `basewrapper.py`, `class_ast.py`）
- `test/`（ユニット/統合およびバージョン別フォルダ）
- `pyproject.toml`, `README.md`, `DEVELOPMENT_GUIDE.md`, `instructions/`

---
フィードバックをください：この指示ファイルのどの部分が不明瞭か、追記してほしい運用（CI、ブランチ戦略、ターゲット Python バージョンなど）があれば教えてください。
