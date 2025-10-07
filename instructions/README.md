# Instructions - clipar プロジェクト管理ドキュメント

このフォルダには、cliparプロジェクトの開発・管理に関する包括的な指示書が含まれています。

## 📁 ファイル構成

### 🎯 [virtual_environment_docs_index.md](./virtual_environment_docs_index.md)
**👈 まずはここから！ドキュメント全体のインデックス**
- 全ドキュメントの概要と使い分け
- クイックスタートガイド
- 現在のプロジェクト構成
- 使用シーン別ガイド

---

### 🏗️ 仮想環境管理

#### [virtual_environment_rules.md](./virtual_environment_rules.md)
**標準的な仮想環境作成・管理ルール**
- `.venv/{machine}@{user}/cp{version}-{project}` 命名規則
- uvを使用したパッケージ管理
- Python 3.10/3.12 複数バージョン対応
- プロジェクト設定との連携方法

#### [os_specific_commands.md](./os_specific_commands.md)
**OS別の具体的なコマンド例**
- Windows（PowerShell/Command Prompt）
- Linux/macOS（Bash/Zsh/Fish）
- 自動化スクリプト例
- IDE統合設定（VS Code/PyCharm）

#### [troubleshooting_guide.md](./troubleshooting_guide.md)
**問題解決のための完全ガイド**
- 10の主要問題カテゴリ
- 段階的な解決手順
- 環境診断スクリプト
- 緊急時の完全リセット方法

---

### 🔄 コード移行

#### [downgrade_py312_to_py310_instructions.md](./downgrade_py312_to_py310_instructions.md)
**Python 3.12→3.10 ダウングレード作業指示書**
- ジェネリック構文 `class Foo[T]:` → `class Foo(Generic[_T]):`
- TypeVar定義と使用方法
- bound制約・複数制約の変換
- ファイル別の具体的変更点

---

## 🚀 使い方

### 新規開発者
1. **[virtual_environment_docs_index.md](./virtual_environment_docs_index.md)** で全体を把握
2. **[virtual_environment_rules.md](./virtual_environment_rules.md)** でクイックスタート
3. 問題があれば **[troubleshooting_guide.md](./troubleshooting_guide.md)** を参照

### Python 3.12→3.10 ダウングレード作業
1. **[downgrade_py312_to_py310_instructions.md](./downgrade_py312_to_py310_instructions.md)** を熟読
2. **[virtual_environment_rules.md](./virtual_environment_rules.md)** でPython 3.10環境を構築
3. **[os_specific_commands.md](./os_specific_commands.md)** でOS固有のコマンドを確認

### トラブル発生時
1. **[troubleshooting_guide.md](./troubleshooting_guide.md)** で該当する問題を検索
2. 診断スクリプトを実行して状況を把握
3. 段階的な解決手順を実行

---

## 📋 主な規則・規約

### 仮想環境命名
```
.venv/{MACHINE_NAME}@{USER_NAME}/cp{PYTHON_VERSION}-clipar
```
例: `.venv/IKEDA-PC@ikeda/cp312-clipar`

### Python バージョン対応
- **cp310**: Python 3.10（下位互換テスト・ダウングレード作業用）
- **cp312**: Python 3.12（メイン開発環境）

### ディレクトリ構造
```
src/clipar/
├── v310/    # Python 3.10互換版（ダウングレード済み）
└── v312/    # Python 3.12専用版（ジェネリック構文使用）
```

---

## ⚡ クイックリファレンス

### 環境作成
```bash
# Python 3.12（メイン開発）
uv venv .venv/{MACHINE}@{USER}/cp312-clipar --python 3.12

# Python 3.10（ダウングレード作業）
uv venv .venv/{MACHINE}@{USER}/cp310-clipar --python 3.10
```

### 環境有効化
```bash
# Windows PowerShell
.venv\{MACHINE}@{USER}\cp312-clipar\Scripts\Activate.ps1

# Linux/macOS
source .venv/{MACHINE}@{USER}/cp312-clipar/bin/activate
```

### 依存関係インストール
```bash
uv pip install -e ".[dev]"
```

---

## 🔄 ドキュメント更新について

これらの指示書は以下の情報に基づいて作成されています：

- **プロジェクト設定**: `pyproject.toml`（Python >=3.10, uv管理）
- **実際の環境**: `.venv/` フォルダ構造
- **開発フロー**: Python 3.12→3.10 ダウングレード要件
- **作成日**: 2025年10月6日

プロジェクト設定や要件が変更された場合は、これらのドキュメントも合わせて更新してください。

---

**💡 ヒント**: 初めて使用する場合は、必ず [virtual_environment_docs_index.md](./virtual_environment_docs_index.md) から始めることをお勧めします。