# OS別コマンドリファレンス - 仮想環境管理

## Windows環境

### PowerShell（推奨）

#### 環境作成
```powershell
# システム情報の取得
$env:COMPUTERNAME  # 結果例: IKEDA-PC
$env:USERNAME      # 結果例: ikeda

# 仮想環境の作成
uv venv .venv\$env:COMPUTERNAME@$env:USERNAME\cp312-clipar --python 3.12
uv venv .venv\$env:COMPUTERNAME@$env:USERNAME\cp310-clipar --python 3.10

# 明示的な指定（推奨）
uv venv .venv\IKEDA-PC@ikeda\cp312-clipar --python 3.12
```

#### 環境の有効化・無効化
```powershell
# 有効化
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1

# 現在の環境確認
where python
python --version

# 無効化
deactivate
```

#### 依存関係管理
```powershell
# インストール
uv pip install -e .
uv pip install -e ".[dev]"

# パッケージリスト
uv pip list

# 特定パッケージの確認
uv pip show pytest
```

#### 環境のクリーンアップ
```powershell
# 環境フォルダの削除
Remove-Item -Recurse -Force .venv\IKEDA-PC@ikeda\cp312-clipar

# キャッシュクリア
uv cache clean
```

### Command Prompt

#### 環境作成
```cmd
:: システム情報の取得
echo %COMPUTERNAME%  REM 結果例: IKEDA-PC
echo %USERNAME%      REM 結果例: ikeda

:: 仮想環境の作成
uv venv .venv\%COMPUTERNAME%@%USERNAME%\cp312-clipar --python 3.12
```

#### 環境の有効化・無効化
```cmd
:: 有効化
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\activate.bat

:: 現在の環境確認
where python
python --version

:: 無効化
deactivate
```

## Linux/macOS環境

### Bash/Zsh（標準）

#### 環境作成
```bash
# システム情報の取得
hostname           # 結果例: ubuntu-server
whoami            # 結果例: developer

# 仮想環境の作成
uv venv .venv/$(hostname)@$(whoami)/cp312-clipar --python 3.12
uv venv .venv/$(hostname)@$(whoami)/cp310-clipar --python 3.10

# 明示的な指定（推奨）
uv venv .venv/ubuntu-server@developer/cp312-clipar --python 3.12
```

#### 環境の有効化・無効化
```bash
# 有効化
source .venv/ubuntu-server@developer/cp312-clipar/bin/activate

# 現在の環境確認
which python
python --version

# 無効化
deactivate
```

#### 依存関係管理
```bash
# インストール
uv pip install -e .
uv pip install -e ".[dev]"

# パッケージリスト
uv pip list

# 特定パッケージの確認
uv pip show pytest
```

#### 環境のクリーンアップ
```bash
# 環境フォルダの削除
rm -rf .venv/ubuntu-server@developer/cp312-clipar

# キャッシュクリア
uv cache clean
```

### Fish Shell

#### 環境の有効化
```fish
# 有効化（Fish用のアクティベーションスクリプト）
source .venv/ubuntu-server@developer/cp312-clipar/bin/activate.fish
```

## 環境確認用コマンド集

### 共通確認コマンド

#### Python環境の詳細確認
```python
# Pythonスクリプトで実行
import sys
import site

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Virtual environment: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
print(f"Site packages: {site.getsitepackages()}")
```

#### パッケージ情報の確認
```bash
# インストール済みパッケージの詳細
uv pip list --format=json

# 依存関係ツリー
uv pip list --tree  # uvが対応している場合
```

### OS固有の確認コマンド

#### Windows
```powershell
# 環境変数の確認
Get-ChildItem Env: | Where-Object {$_.Name -like "*PYTHON*"}

# パス情報
$env:PATH -split ";"

# プロセス情報
Get-Process -Name python*
```

#### Linux/macOS
```bash
# 環境変数の確認
env | grep -i python

# パス情報
echo $PATH | tr ':' '\n'

# プロセス情報
ps aux | grep python
```

## 自動化スクリプト例

### Windows PowerShell自動化スクリプト

#### 環境作成・セットアップスクリプト
```powershell
# setup-venv.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$PythonVersion,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectName = "clipar"
)

$MachineName = $env:COMPUTERNAME
$UserName = $env:USERNAME
$VenvPath = ".venv\$MachineName@$UserName\cp$PythonVersion-$ProjectName"

Write-Host "Creating virtual environment: $VenvPath"
uv venv $VenvPath --python $PythonVersion

Write-Host "Activating environment..."
& $VenvPath\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
uv pip install -e ".[dev]"

Write-Host "Environment setup complete!"
Write-Host "To activate: $VenvPath\Scripts\Activate.ps1"
```

#### 使用例
```powershell
# Python 3.12環境の作成
.\setup-venv.ps1 -PythonVersion "312"

# Python 3.10環境の作成
.\setup-venv.ps1 -PythonVersion "310"
```

### Linux/macOS自動化スクリプト

#### 環境作成・セットアップスクリプト
```bash
#!/bin/bash
# setup-venv.sh

PYTHON_VERSION=${1:-312}
PROJECT_NAME=${2:-clipar}
MACHINE_NAME=$(hostname)
USER_NAME=$(whoami)
VENV_PATH=".venv/$MACHINE_NAME@$USER_NAME/cp$PYTHON_VERSION-$PROJECT_NAME"

echo "Creating virtual environment: $VENV_PATH"
uv venv "$VENV_PATH" --python "3.${PYTHON_VERSION:2}"

echo "Activating environment..."
source "$VENV_PATH/bin/activate"

echo "Installing dependencies..."
uv pip install -e ".[dev]"

echo "Environment setup complete!"
echo "To activate: source $VENV_PATH/bin/activate"
```

#### 使用例
```bash
# 実行権限の付与
chmod +x setup-venv.sh

# Python 3.12環境の作成
./setup-venv.sh 312

# Python 3.10環境の作成
./setup-venv.sh 310
```

## IDE・エディタ固有の設定

### VS Code

#### settings.json（プロジェクト用）
```json
{
    "python.defaultInterpreterPath": ".venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "test"
    ]
}
```

#### launch.json（デバッグ設定）
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "python": ".venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe"
        }
    ]
}
```

### PyCharm

#### インタープリター設定
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing environment
3. パス指定: `.venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/python.exe`（Windows）
4. パス指定: `.venv/ubuntu-server@developer/cp312-clipar/bin/python`（Linux/macOS）

## トラブルシューティング

### Windows固有の問題

#### PowerShellスクリプト実行ポリシー
```powershell
# 現在のポリシー確認
Get-ExecutionPolicy

# ポリシー変更（管理者権限が必要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一時的な回避
powershell -ExecutionPolicy Bypass -File script.ps1
```

#### パス区切り文字の問題
```powershell
# Windowsでは \ を使用
.venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\Activate.ps1

# PowerShellでは / も使用可能（非推奨）
.venv/IKEDA-PC@ikeda/cp312-clipar/Scripts/Activate.ps1
```

### Linux/macOS固有の問題

#### 権限エラー
```bash
# 実行権限の確認
ls -la .venv/ubuntu-server@developer/cp312-clipar/bin/activate

# 権限の修正
chmod +x .venv/ubuntu-server@developer/cp312-clipar/bin/activate
```

#### シェルの互換性
```bash
# 現在のシェル確認
echo $SHELL

# Bashでの実行を強制
bash -c "source .venv/ubuntu-server@developer/cp312-clipar/bin/activate && python --version"
```

### 共通の問題

#### 環境が見つからない
```bash
# 環境の存在確認
ls -la .venv/

# パスの確認（絶対パスで試行）
pwd
ls -la $(pwd)/.venv/
```

#### Python実行ファイルが見つからない
```bash
# Windows
dir .venv\IKEDA-PC@ikeda\cp312-clipar\Scripts\python.exe

# Linux/macOS
ls -la .venv/ubuntu-server@developer/cp312-clipar/bin/python
```

---

**注意事項:**
- 実際のマシン名・ユーザー名は環境に応じて置き換えてください
- 各OSの固有機能を活用して効率的な環境管理を行ってください
- 自動化スクリプトは組織のセキュリティポリシーに準拠して使用してください