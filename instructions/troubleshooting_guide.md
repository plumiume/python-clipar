# 仮想環境トラブルシューティングガイド

## よくある問題と解決方法

### 1. 環境作成時の問題

#### ❌ 問題: Python バージョンが見つからない
```
Error: Could not find Python 3.10
```

**解決方法:**
```bash
# 利用可能なPythonバージョンの確認
uv python list

# 特定バージョンのインストール（uvが対応している場合）
uv python install 3.10

# システムにPython 3.10をインストール（公式サイトから）
# Windows: https://www.python.org/downloads/
# Linux: sudo apt install python3.10  # Ubuntu/Debian
# macOS: brew install python@3.10
```

#### ❌ 問題: 権限エラーで環境作成に失敗
```
Permission denied: '.venv'
```

**解決方法:**
```bash
# Windows
# 管理者権限でPowerShellを実行

# Linux/macOS
# ディレクトリの権限確認
ls -ld .

# 権限修正（必要に応じて）
chmod 755 .

# または、別の場所に作成
mkdir ~/venvs
uv venv ~/venvs/clipar-cp312 --python 3.12
```

#### ❌ 問題: 既存の環境が存在する
```
Error: Directory already exists: .venv/IKEDA-PC@ikeda/cp312-clipar
```

**解決方法:**
```bash
# Windows PowerShell
Remove-Item -Recurse -Force .venv\IKEDA-PC@ikeda\cp312-clipar

# Linux/macOS
rm -rf .venv/IKEDA-PC@ikeda/cp312-clipar

# または、強制再作成
uv venv .venv/IKEDA-PC@ikeda/cp312-clipar --python 3.12 --clear
```

### 2. 環境有効化時の問題

#### ❌ 問題: PowerShellでスクリプト実行が拒否される
```
Execution of scripts is disabled on this system
```

**解決方法:**
```powershell
# 現在のポリシー確認
Get-ExecutionPolicy

# ユーザーレベルでの許可
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一時的な実行（推奨）
powershell -ExecutionPolicy Bypass -Command ".venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1"
```

#### ❌ 問題: 環境のパスが見つからない
```
bash: .venv/IKEDA-PC@ikeda/cp312-clipar/bin/activate: No such file or directory
```

**解決方法:**
```bash
# 環境の存在確認
ls -la .venv/

# パスの詳細確認
find .venv -name "activate" -type f

# 正しいパスで再実行
source .venv/actual-machine@actual-user/cp312-clipar/bin/activate
```

#### ❌ 問題: 環境が有効化されない
**現象:** `python --version` が期待したバージョンと異なる

**解決方法:**
```bash
# 現在のPython実行ファイルの場所確認
which python   # Linux/macOS
where python   # Windows

# 環境変数PATH確認
echo $PATH  # Linux/macOS
echo $env:PATH  # PowerShell

# 強制的に仮想環境のPythonを使用
.venv/IKEDA-PC@ikeda/cp312-clipar/bin/python --version  # Linux/macOS
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\python.exe --version  # Windows
```

### 3. 依存関係インストール時の問題

#### ❌ 問題: パッケージのインストールに失敗
```
Error installing packages: No module named 'pip'
```

**解決方法:**
```bash
# pipが環境に含まれているか確認
python -m pip --version

# pipの再インストール
python -m ensurepip --upgrade

# uvを使用した代替方法
uv pip install -e .
```

#### ❌ 問題: 依存関係の競合
```
ERROR: pip's dependency resolver does not currently have a solution...
```

**解決方法:**
```bash
# 環境をクリーンにして再作成
deactivate
rm -rf .venv/IKEDA-PC@ikeda/cp312-clipar
uv venv .venv/IKEDA-PC@ikeda/cp312-clipar --python 3.12

# 段階的なインストール
source .venv/IKEDA-PC@ikeda/cp312-clipar/bin/activate
uv pip install -e .  # プロダクション依存関係のみ
uv pip install -e ".[dev]"  # 開発依存関係を追加
```

#### ❌ 問題: pyproject.tomlが見つからない
```
Error: Could not find pyproject.toml
```

**解決方法:**
```bash
# 現在のディレクトリ確認
pwd

# プロジェクトルートに移動
cd /path/to/clipar

# pyproject.tomlの存在確認
ls -la pyproject.toml
```

### 4. Python バージョン関連の問題

#### ❌ 問題: Python 3.12の構文がPython 3.10で実行される
**現象:** 新しいジェネリック構文でSyntaxError

**解決方法:**
```bash
# 現在のPython環境確認
python --version

# 正しい環境に切り替え
deactivate
source .venv/IKEDA-PC@ikeda/cp310-clipar/bin/activate  # Python 3.10用

# または適切なファイルを使用
# v310/ フォルダのファイルを使用（Python 3.10互換版）
# v312/ フォルダのファイルを使用（Python 3.12専用版）
```

#### ❌ 問題: typing_extensions が古い
```
ImportError: cannot import name 'Self' from 'typing_extensions'
```

**解決方法:**
```bash
# typing_extensionsのアップデート
uv pip install --upgrade typing-extensions

# 特定バージョンの指定
uv pip install "typing-extensions>=4.14.1"

# 環境の同期
uv sync
```

### 5. IDE・エディタ統合の問題

#### ❌ 問題: VS Codeが間違ったPythonインタープリターを使用
**現象:** VS Codeでのコード実行やデバッグが期待した環境で行われない

**解決方法:**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": ".venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe"
}
```

**または:**
1. Ctrl+Shift+P → "Python: Select Interpreter"
2. 適切な仮想環境のPythonを選択

#### ❌ 問題: PyCharmでインタープリターが認識されない
**解決方法:**
1. File → Settings → Project → Python Interpreter
2. "Add Interpreter" → "Existing environment"
3. パスを指定: `.venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe`
4. "Make available to all projects" のチェックを外す

### 6. 型チェック・リンターの問題

#### ❌ 問題: pyrightが型エラーを報告
```
error: Type variable "T" is unbound
```

**解決方法:**
```bash
# Python 3.10環境で作業していることを確認
python --version  # Python 3.10.x であることを確認

# 適切なファイルバージョンを使用
# v310/ フォルダのファイルを使用（Python 3.10互換）
# v312/ フォルダの修正が必要な場合は、ジェネリック構文を変換
```

#### ❌ 問題: mypyの設定が適用されない
**解決方法:**
```ini
# pyproject.toml または mypy.ini
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
```

### 7. パフォーマンス・キャッシュの問題

#### ❌ 問題: 環境の動作が異常に遅い
**解決方法:**
```bash
# uvキャッシュのクリア
uv cache clean

# Pythonキャッシュのクリア
find . -name "__pycache__" -type d -exec rm -rf {} +  # Linux/macOS
Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse  # PowerShell

# 環境の再作成
deactivate
rm -rf .venv/IKEDA-PC@ikeda/cp312-clipar
uv venv .venv/IKEDA-PC@ikeda/cp312-clipar --python 3.12
```

#### ❌ 問題: パッケージのインストールが非常に遅い
**解決方法:**
```bash
# ネットワーク接続の確認
ping pypi.org

# ミラーサイトの使用
uv pip install --index-url https://pypi.org/simple/ -e .

# ローカルキャッシュの活用
uv pip install --no-network -e .  # オフラインモード（キャッシュからのみ）
```

### 8. プロジェクト固有の問題

#### ❌ 問題: cliparモジュールがインポートできない
```
ModuleNotFoundError: No module named 'clipar'
```

**解決方法:**
```bash
# 開発モードでのインストールを確認
uv pip install -e .

# PYTHONPATHの設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/macOS
$env:PYTHONPATH = "$env:PYTHONPATH;$(pwd)\src"  # PowerShell

# プロジェクトルートから実行
cd /path/to/clipar
python -c "import clipar; print(clipar.__file__)"
```

#### ❌ 問題: テストが実行できない
```
No tests ran / ModuleNotFoundError during test
```

**解決方法:**
```bash
# 現在のディレクトリと環境確認
pwd
python --version

# pytest の明示的実行
python -m pytest test/ -v

# テストディレクトリ内から実行
cd test
python -m pytest . -v

# 環境の確認
uv pip show pytest
```

### 9. 環境の診断・検証

#### 総合診断スクリプト
```bash
#!/bin/bash
# diagnose-env.sh - 環境の健全性チェック

echo "=== Python Environment Diagnosis ==="
echo "Python executable: $(which python)"
echo "Python version: $(python --version)"
echo "Virtual environment: $VIRTUAL_ENV"
echo

echo "=== Package Information ==="
python -c "
import sys
import site
print(f'sys.executable: {sys.executable}')
print(f'sys.prefix: {sys.prefix}')
print(f'site.getsitepackages(): {site.getsitepackages()}')
"
echo

echo "=== Installed Packages ==="
uv pip list
echo

echo "=== Project Structure ==="
ls -la
echo

echo "=== Import Test ==="
python -c "
try:
    import clipar
    print(f'✓ clipar imported successfully from {clipar.__file__}')
except ImportError as e:
    print(f'✗ clipar import failed: {e}')

try:
    from typing_extensions import Self
    print('✓ typing_extensions.Self imported successfully')
except ImportError as e:
    print(f'✗ typing_extensions.Self import failed: {e}')
"
```

**Windows PowerShell版:**
```powershell
# diagnose-env.ps1
Write-Host "=== Python Environment Diagnosis ==="
Write-Host "Python executable: $(where python)"
Write-Host "Python version: $(python --version)"
Write-Host "Virtual environment: $env:VIRTUAL_ENV"
Write-Host

Write-Host "=== Package Information ==="
python -c @"
import sys
import site
print(f'sys.executable: {sys.executable}')
print(f'sys.prefix: {sys.prefix}')
print(f'site.getsitepackages(): {site.getsitepackages()}')
"@
Write-Host

Write-Host "=== Installed Packages ==="
uv pip list
Write-Host

Write-Host "=== Import Test ==="
python -c @"
try:
    import clipar
    print(f'✓ clipar imported successfully from {clipar.__file__}')
except ImportError as e:
    print(f'✗ clipar import failed: {e}')

try:
    from typing_extensions import Self
    print('✓ typing_extensions.Self imported successfully')
except ImportError as e:
    print(f'✗ typing_extensions.Self import failed: {e}')
"@
```

### 10. 緊急時の対処法

#### 完全リセット手順
```bash
# 1. 全ての仮想環境を削除
rm -rf .venv/  # Linux/macOS
Remove-Item -Recurse -Force .venv\  # PowerShell

# 2. キャッシュのクリア
uv cache clean

# 3. 基本環境の再作成
uv venv .venv/$(hostname)@$(whoami)/cp312-clipar --python 3.12  # Linux/macOS
uv venv .venv\$env:COMPUTERNAME@$env:USERNAME\cp312-clipar --python 3.12  # PowerShell

# 4. 環境の有効化
source .venv/$(hostname)@$(whoami)/cp312-clipar/bin/activate  # Linux/macOS
.venv\$env:COMPUTERNAME@$env:USERNAME\cp312-clipar\Scripts\Activate.ps1  # PowerShell

# 5. 依存関係の再インストール
uv pip install -e ".[dev]"

# 6. 動作確認
python -c "import clipar; print('OK')"
python -m pytest test/ -v
```

---

**🚨 重要な注意事項:**
- 問題解決前に必ず現在の状態をバックアップしてください
- 複数の解決方法を同時に試さず、段階的に実行してください
- 実際のマシン名・ユーザー名に置き換えて実行してください
- 権限に関わる操作は慎重に行ってください

**📞 サポート情報:**
- このガイドで解決しない場合は、エラーメッセージの全文とシステム情報を記録してください
- Python環境の診断スクリプトの結果を保存してください
- 問題の再現手順を明確にしてください