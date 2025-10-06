# 仮想環境作成・管理ルール（cliparプロジェクト標準）

## 概要
このドキュメントは`clipar`プロジェクトにおける仮想環境の作成・管理・運用に関する標準ルールを定義します。
uvを使用したパッケージ管理を前提とし、複数のPythonバージョンや開発環境に対応します。

## 基本原則

### 1. 仮想環境の命名規則
```
.venv/{machine_name}@{user_name}/cp{python_version_short}-{project_name}
```

**例:**
- `.venv/IKEDA-PC@ikeda/cp312-clipar` (Python 3.12)
- `.venv/IKEDA-PC@ikeda/cp310-clipar` (Python 3.10)
- `.venv/ubuntu-server@developer/cp311-clipar` (Python 3.11)

### 2. 仮想環境の配置
- **場所**: プロジェクトルートの `.venv/` フォルダ内
- **理由**: 
  - プロジェクト固有の環境として管理
  - 複数開発者・複数マシンでの環境分離
  - バージョン管理システム（Git）での除外対象

### 3. Pythonバージョン対応
- **サポート範囲**: Python 3.10以上 (`requires-python = ">=3.10"`)
- **主要バージョン**:
  - `cp310`: Python 3.10（下位互換テスト用）
  - `cp312`: Python 3.12（開発・本番用）
  - `cp313`: Python 3.13（次期バージョンテスト用）

## 仮想環境作成手順

### Phase 1: 環境情報の確認

#### 1.1 システム情報の取得
```bash
# Windows PowerShell
$env:COMPUTERNAME  # マシン名
$env:USERNAME      # ユーザー名

# Linux/macOS
hostname           # マシン名
whoami            # ユーザー名
```

#### 1.2 Python環境の確認
```bash
# 利用可能なPythonバージョンの確認
uv python list

# 特定バージョンの確認
python3.10 --version
python3.12 --version
```

### Phase 2: 仮想環境の作成

#### 2.1 標準的な作成コマンド
```bash
# Python 3.10環境の作成
uv venv .venv/{MACHINE}@{USER}/cp310-clipar --python 3.10

# Python 3.12環境の作成（デフォルト開発環境）
uv venv .venv/{MACHINE}@{USER}/cp312-clipar --python 3.12

# 自動的にマシン名・ユーザー名を取得する場合
# Windows PowerShell
uv venv .venv/$env:COMPUTERNAME@$env:USERNAME/cp312-clipar --python 3.12

# Linux/macOS
uv venv .venv/$(hostname)@$(whoami)/cp312-clipar --python 3.12
```

#### 2.2 プロジェクト固有の例
```bash
# IKEDA-PC@ikedaの環境例
uv venv .venv/IKEDA-PC@ikeda/cp310-clipar --python 3.10
uv venv .venv/IKEDA-PC@ikeda/cp312-clipar --python 3.12
```

### Phase 3: 仮想環境の有効化

#### 3.1 Windows環境
```bash
# PowerShell
.venv\{MACHINE}@{USER}\cp312-clipar\Scripts\Activate.ps1

# Command Prompt
.venv\{MACHINE}@{USER}\cp312-clipar\Scripts\activate.bat

# 実例
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1
```

#### 3.2 Linux/macOS環境
```bash
# Bash/Zsh
source .venv/{MACHINE}@{USER}/cp312-clipar/bin/activate

# 実例
source .venv/ubuntu-server@developer/cp312-clipar/bin/activate
```

### Phase 4: 依存関係のインストール

#### 4.1 基本依存関係
```bash
# プロダクション依存関係のみ
uv pip install -e .

# 開発依存関係も含める
uv pip install -e ".[dev]"
```

#### 4.2 特定の依存関係グループ
```bash
# pyproject.tomlで定義された依存関係グループ
uv pip install --group dev      # 開発用依存関係
uv pip install --group test     # テスト用依存関係（存在する場合）
```

## プロジェクト設定との連携

### pyproject.toml設定
```toml
[project]
name = "clipar"
version = "0.2.0"
requires-python = ">=3.10"
dependencies = [
    "argcomplete>=3.6.2",
    "typing-extensions>=4.14.1",
]

[dependency-groups]
dev = [
    "ipython>=8.37.0",
    "pytest>=8.4.1",
]
```

### 環境別の使い分け

#### Python 3.10環境（下位互換テスト）
```bash
# 有効化
.venv\IKEDA-PC@ikeda\cp310-clipar\Scripts\Activate.ps1

# 用途
- Python 3.12 → 3.10のダウングレード作業
- 下位互換性の確認
- 古いPython環境でのテスト
```

#### Python 3.12環境（メイン開発）
```bash
# 有効化
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1

# 用途
- 日常的な開発作業
- 最新機能の実装・テスト
- 本番環境との整合性確認
```

## 環境管理のベストプラクティス

### 1. 環境の確認と切り替え

#### 現在の環境確認
```bash
# Python実行ファイルの場所
which python    # Linux/macOS
where python    # Windows

# Pythonバージョン
python --version

# インストール済みパッケージ
uv pip list
```

#### 環境の切り替え
```bash
# 現在の環境を無効化
deactivate

# 新しい環境を有効化
.venv\{MACHINE}@{USER}\cp310-clipar\Scripts\Activate.ps1
```

### 2. 依存関係の管理

#### パッケージの追加
```bash
# プロダクション依存関係に追加
uv add package_name

# 開発依存関係に追加
uv add --group dev package_name
```

#### 環境の同期
```bash
# uv.lockからの復元
uv sync

# 特定グループのみ同期
uv sync --group dev
```

### 3. 環境のクリーンアップ

#### キャッシュのクリア
```bash
uv cache clean
```

#### 環境の再作成
```bash
# 環境フォルダの削除（例：Python 3.12環境）
rm -rf .venv/IKEDA-PC@ikeda/cp312-clipar  # Linux/macOS
Remove-Item -Recurse .venv\IKEDA-PC@ikeda\cp312-clipar  # PowerShell

# 再作成
uv venv .venv/IKEDA-PC@ikeda/cp312-clipar --python 3.12
```

## 環境固有の設定

### 1. Git設定（.gitignore）
```gitignore
# 仮想環境を除外
.venv/

# uvキャッシュを除外（通常は不要）
.uv-cache/
```

### 2. VS Code設定（.vscode/settings.json）
```json
{
    "python.defaultInterpreterPath": ".venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

### 3. 環境変数の設定
```bash
# 開発用環境変数（.env ファイル推奨）
PYTHONPATH=src
CLIPAR_DEBUG=true
```

## よくある使用パターン

### パターン1: 新規開発者のセットアップ
```bash
# 1. リポジトリのクローン
git clone <repository_url> clipar
cd clipar

# 2. 仮想環境の作成（自分のマシン・ユーザー名で）
uv venv .venv/$(hostname)@$(whoami)/cp312-clipar --python 3.12

# 3. 環境の有効化
source .venv/$(hostname)@$(whoami)/cp312-clipar/bin/activate  # Linux/macOS
# または
.venv\{MACHINE}@{USER}\cp312-clipar\Scripts\Activate.ps1  # Windows

# 4. 依存関係のインストール
uv pip install -e ".[dev]"
```

### パターン2: 複数Python環境でのテスト
```bash
# Python 3.10でのテスト
.venv\IKEDA-PC@ikeda\cp310-clipar\Scripts\Activate.ps1
python -m pytest test/

# Python 3.12でのテスト
deactivate
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1
python -m pytest test/
```

### パターン3: ダウングレード作業
```bash
# Python 3.10環境で作業
.venv\IKEDA-PC@ikeda\cp310-clipar\Scripts\Activate.ps1

# ファイルの構文チェック
python -m py_compile src/clipar/v312/filename.py

# 型チェック
pyright src/clipar/v312/
```

## チェックリスト

### 新規環境作成時
- [ ] Python バージョンが要件（>=3.10）に適合している
- [ ] 仮想環境の命名規則に従っている
- [ ] .gitignore で仮想環境が除外されている
- [ ] pyproject.toml の依存関係が正しくインストールされている
- [ ] 開発用依存関係（dev group）がインストールされている

### 環境切り替え時
- [ ] 古い環境が正しく無効化されている
- [ ] 新しい環境が正常に有効化されている
- [ ] Python バージョンが期待値と一致している
- [ ] 必要なパッケージがインストールされている

### トラブル時
- [ ] 仮想環境のパスが正しい
- [ ] Python実行ファイルが存在する
- [ ] 依存関係が不足していない
- [ ] キャッシュに問題がない

---

**注意事項:**
- このルールは`clipar`プロジェクト専用に最適化されています
- 他のプロジェクトに適用する場合は、プロジェクト名や要件に応じて調整してください
- 環境名には必ず実際のマシン名・ユーザー名を使用してください（例の値をそのまま使用しないでください）