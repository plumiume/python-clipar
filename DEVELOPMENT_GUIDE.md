# 📚 開発・管理ドキュメント

cliparプロジェクトの開発・管理に関する詳細なドキュメントは `instructions/` フォルダに格納されています。

## 🎯 すぐに始めたい方

**👉 [instructions/virtual_environment_docs_index.md](./instructions/virtual_environment_docs_index.md)**

このファイルから始めることで、必要なドキュメントにすぐにアクセスできます。

## 📁 ドキュメント構成

```
instructions/
├── README.md                                    # このフォルダの案内
├── virtual_environment_docs_index.md          # 📋 全体インデックス（まずはここから）
├── virtual_environment_rules.md               # 🏗️ 仮想環境管理の標準ルール
├── os_specific_commands.md                     # 💻 OS別コマンドリファレンス
├── troubleshooting_guide.md                   # 🛠️ トラブルシューティングガイド
└── downgrade_py312_to_py310_instructions.md   # 🔄 Python 3.12→3.10 ダウングレード指示書
```

## ⚡ クイックスタート

### 新規開発者セットアップ
```bash
# 仮想環境作成
uv venv .venv/{YOUR_MACHINE}@{YOUR_USER}/cp312-clipar --python 3.12

# 有効化（Windows PowerShell）
.venv\{YOUR_MACHINE}@{YOUR_USER}\cp312-clipar\Scripts\Activate.ps1

# 依存関係インストール
uv pip install -e ".[dev]"
```

### Python 3.12→3.10 ダウングレード作業
```bash
# Python 3.10環境作成
uv venv .venv/{YOUR_MACHINE}@{YOUR_USER}/cp310-clipar --python 3.10

# 環境有効化後、詳細は下記指示書を参照：
# instructions/downgrade_py312_to_py310_instructions.md
```

## 🆘 問題が発生した場合

**[instructions/troubleshooting_guide.md](./instructions/troubleshooting_guide.md)** に包括的な解決方法が記載されています。

---

**最終更新**: 2025年10月6日