# Sphinx Documentation

このディレクトリには、clipar のSphinxドキュメントソースが含まれています。

## ディレクトリ構造

```
sphinx/
  ├── source/           # ドキュメントソースファイル（.rst）
  │   ├── conf.py      # Sphinx設定ファイル
  │   ├── index.rst    # メインページ
  │   ├── api/         # APIリファレンス
  │   ├── _static/     # 静的ファイル（CSS、画像など）
  │   └── _templates/  # カスタムテンプレート
  ├── Makefile         # Unix/Linux用ビルドファイル
  ├── make.bat         # Windows用ビルドファイル
  └── build_docs.py    # Pythonビルドスクリプト
```

ビルド後のHTMLは `docs/html/` に出力されます。

## ドキュメントのビルド

### 方法1: Pythonスクリプトを使用（推奨）

```powershell
cd sphinx
uv run python build_docs.py
```

### 方法2: Makefileを使用

Windows (PowerShell):
```powershell
cd sphinx
.\make.bat html
```

Unix/Linux/macOS:
```bash
cd sphinx
make html
```

### 方法3: 直接sphinx-buildを使用

```powershell
cd sphinx
uv run sphinx-build -b html source ../docs/html
```

## ドキュメントの表示

ビルド後、以下のファイルをブラウザで開きます：

```
docs/html/index.html
```

## 設定

ドキュメント設定は `source/conf.py` で管理されています：

- **拡張機能**: autodoc, autosummary, napoleon
- **テーマ**: piccolo-theme
- **言語**: 日本語
- **メタデータ**: importlib.metadataから自動取得

## autosummaryの生成

autosummaryは自動的に生成されますが、手動で生成する場合：

```powershell
cd sphinx
uv run sphinx-autogen source/**/*.rst
```

## クリーンビルド

ビルドキャッシュをクリアしてビルドする場合：

```powershell
# Windows
.\make.bat clean
.\make.bat html

# Unix/Linux/macOS
make clean
make html
```
