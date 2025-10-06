# 仮想環境管理ドキュメント - インデックス

## 📚 ドキュメント一覧

cliparプロジェクトの仮想環境管理に関する包括的なドキュメントセットです。

### 🏗️ [virtual_environment_rules.md](./virtual_environment_rules.md)
**メインドキュメント - 仮想環境作成・管理の標準ルール**
- 基本原則と命名規則
- 仮想環境作成の段階的手順
- プロジェクト設定との連携
- 環境管理のベストプラクティス
- よくある使用パターン
- 完了確認チェックリスト

### 💻 [os_specific_commands.md](./os_specific_commands.md)
**OS別コマンドリファレンス**
- Windows（PowerShell/Command Prompt）
- Linux/macOS（Bash/Zsh/Fish）
- 環境確認用コマンド集
- 自動化スクリプト例
- IDE・エディタ統合設定

### 🛠️ [troubleshooting_guide.md](./troubleshooting_guide.md)
**トラブルシューティングガイド**
- よくある問題と解決方法
- 環境作成・有効化・依存関係の問題
- 型チェック・リンターの問題
- 環境診断スクリプト
- 緊急時の完全リセット手順

### 🔄 [downgrade_py312_to_py310_instructions.md](./downgrade_py312_to_py310_instructions.md)
**Python 3.12→3.10 ダウングレード指示書**
- ジェネリック構文の変更ルール
- TypeVar使用方法
- 具体的な変更パターン
- 仮想環境の設定と管理
- 完了確認チェックリスト

## 🚀 クイックスタート

### 新規開発者向け（初回セットアップ）
```bash
# 1. 自分の環境に合わせて仮想環境を作成
uv venv .venv/{YOUR_MACHINE}@{YOUR_USER}/cp312-clipar --python 3.12

# 2. 環境を有効化
# Windows: .venv\{YOUR_MACHINE}@{YOUR_USER}\cp312-clipar\Scripts\Activate.ps1
# Linux/macOS: source .venv/{YOUR_MACHINE}@{YOUR_USER}/cp312-clipar/bin/activate

# 3. 依存関係をインストール
uv pip install -e ".[dev]"

# 4. 動作確認
python -c "import clipar; print('OK')"
python -m pytest test/ -v
```

### Python 3.10ダウングレード作業向け
```bash
# Python 3.10環境の作成
uv venv .venv/{YOUR_MACHINE}@{YOUR_USER}/cp310-clipar --python 3.10

# 環境の有効化
# Windows: .venv\{YOUR_MACHINE}@{YOUR_USER}\cp310-clipar\Scripts\Activate.ps1
# Linux/macOS: source .venv/{YOUR_MACHINE}@{YOUR_USER}/cp310-clipar/bin/activate

# 依存関係のインストール
uv pip install -e ".[dev]"

# 構文チェック（v312フォルダの変更後）
python -m py_compile src/clipar/v312/filename.py
```

## 📋 現在のプロジェクト構成

### 仮想環境構造
```
.venv/
├── IKEDA-PC@ikeda/
│   └── cp312-clipar/        # Python 3.12（メイン開発環境）
├── ikeko@ENVY13BF/
└── PLUNIUME@pluniume/
```

### プロジェクト設定
- **Python要件**: `>=3.10`
- **パッケージマネージャ**: `uv`
- **主要依存関係**: `argcomplete`, `typing-extensions`
- **開発依存関係**: `ipython`, `pytest`

### ディレクトリ構造
```
clipar/
├── src/clipar/
│   ├── v310/               # Python 3.10互換版
│   └── v312/               # Python 3.12専用版
├── test/
│   ├── unit/
│   └── integration/
├── .venv/                  # 仮想環境（複数バージョン対応）
├── pyproject.toml          # プロジェクト設定
└── uv.lock                 # 依存関係ロック
```

## 🎯 使用シーン別ガイド

### シーン1: 日常的な開発作業
- **使用環境**: Python 3.12 (cp312-clipar)
- **参照**: [virtual_environment_rules.md](./virtual_environment_rules.md) - Python 3.12環境（メイン開発）

### シーン2: Python 3.12→3.10 ダウングレード作業
- **使用環境**: Python 3.10 (cp310-clipar)
- **参照**: [downgrade_py312_to_py310_instructions.md](./downgrade_py312_to_py310_instructions.md)
- **関連**: [virtual_environment_rules.md](./virtual_environment_rules.md) - Python 3.10環境（下位互換テスト）

### シーン3: 環境で問題が発生した場合
- **参照**: [troubleshooting_guide.md](./troubleshooting_guide.md)
- **診断スクリプト**: 同ドキュメント内の診断スクリプトを実行

### シーン4: 新しいマシンでのセットアップ
- **参照**: [os_specific_commands.md](./os_specific_commands.md) - 自動化スクリプト例
- **手順**: [virtual_environment_rules.md](./virtual_environment_rules.md) - パターン1: 新規開発者のセットアップ

## 🔧 カスタマイズ指針

これらのドキュメントは`clipar`プロジェクト専用に最適化されていますが、他のプロジェクトに適用する場合の調整ポイント：

1. **プロジェクト名**: `clipar` → 実際のプロジェクト名
2. **Python要件**: `>=3.10` → プロジェクトの要件
3. **依存関係**: `pyproject.toml`の設定に合わせる
4. **ディレクトリ構造**: プロジェクト固有の構造に合わせる

## 📞 サポート

問題が発生した場合：

1. **まず確認**: [troubleshooting_guide.md](./troubleshooting_guide.md)
2. **診断実行**: 診断スクリプトを実行して環境状態を確認
3. **段階的解決**: 問題に応じて適切なドキュメントの解決方法を実行
4. **完全リセット**: 解決しない場合は完全リセット手順を実行

---

**最終更新**: 2025年10月6日
**バージョン**: 1.0.0
**対象プロジェクト**: clipar v0.2.0