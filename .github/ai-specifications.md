# AI Agent Specifications for Clipar Project

## プロジェクト概要

**Clipar** は、型注釈とデコレータを使用してCLIアプリケーションを構築するためのモダンなPythonライブラリです。argparseのボイラープレートコードを排除し、型安全性を確保しながら宣言的にCLIを定義できます。

### 主要特徴
- 🎯 型駆動: Python型注釈でCLI引数を定義
- 🎨 デコレータベース: シンプルな`@namespace`と`@group`デコレータ
- 🔧 自動パース: 型ヒントに基づく自動引数解析
- 📦 ネストグループ: ネストした引数グループのサポート
- 🚀 簡単統合: argparseワークフローのドロップイン置換
- ✅ 型安全: mypy/pylanceによる完全な型チェックサポート

## アーキテクチャ概要

### 並列実装戦略
Cliparは異なるPythonバージョンの互換性を確保するため、バージョン別の並列実装を採用:

```
src/clipar/
├── __init__.py              # バージョン選択エントリポイント
├── entities.py              # 共通エンティティのre-export
├── v310/                    # Python 3.10/3.11対応
│   ├── decorator.py         # TypeVarベースの実装
│   ├── basewrapper.py
│   ├── namespacewrapper.py
│   ├── groupwrapper.py
│   ├── class_ast.py
│   └── mixin.py
└── v312/                    # Python 3.12+対応
    ├── decorator.py         # 新しいジェネリック構文対応
    ├── basewrapper.py
    ├── namespacewrapper.py
    ├── groupwrapper.py
    ├── class_ast.py
    ├── help_formatter.py
    └── mixin.py
```

### バージョン選択メカニズム
`src/clipar/__init__.py`が実行時に`sys.version_info`を判定:
- Python 3.12+ → `v312/`から実装をインポート
- Python 3.10/3.11 → `v310/`から実装をインポート

## 開発ガイドライン

### 必須原則

1. **並列実装の整合性維持**
   - 公開APIの変更時は必ず両バージョン（v310, v312）を同時更新
   - テストも両バージョンに対応したものを作成

2. **型安全性の確保**
   - 全てのパブリック関数・メソッドに型注釈を付与
   - mypyでの型チェックを必須とする

3. **パッケージ管理**
   - `uv`を使用（`pip`系コマンド禁止）
   - 依存関係追加: `uv add <package>`
   - 開発依存: `uv add --dev <package>`

### ヘルプテキストパターン
フィールド直後の文字列リテラルでヘルプを定義（AST解析で自動抽出）:

```python
@namespace
class Config:
    input_file: str
    "Path to the input data file (required)"
    
    workers: int = 4
    "Number of parallel workers"
```

### NotSelectedの使用
未設定オプションの検出にはsentinel値`NotSelected`を使用:

```python
from clipar import NotSelected

config = Config.parse_args()
if config.optional_arg is NotSelected:
    print("オプション引数が指定されていません")
```

## テスト戦略

### 環境別テスト実行
```powershell
# Python 3.10環境
venv\cp310\Scripts\activate
python -m pytest -q test/unit/v310
python -m pytest -q test/integration/v310

# Python 3.12環境  
venv\cp312\Scripts\activate
python -m pytest -q test/unit/v312
python -m pytest -q test/integration/v312
```

### テスト構造
```
test/
├── conftest.py                    # 共通フィクスチャ
├── test_import_compatibility.py  # インポート互換性テスト
├── unit/
│   ├── v310/                     # Python 3.10/3.11用ユニットテスト
│   └── v312/                     # Python 3.12+用ユニットテスト
└── integration/
    ├── v310/                     # Python 3.10/3.11用統合テスト
    └── v312/                     # Python 3.12+用統合テスト
```

## 主要コンポーネント仕様

### デコレータ (`decorator.py`)
- `@namespace`: トップレベルCLI名前空間を定義
- `@group`: 引数グループを定義（階層オプション生成）
- `@mutually_exclusive_group`: 排他的グループを定義

### ベースラッパー (`basewrapper.py`)
- `BaseWrapper`: 全ラッパークラスの基底
- `NotSelected`: 未設定オプションのsentinel値
- 型変換ロジック（自動的に適切な型変換関数を選択）

### AST解析 (`class_ast.py`)
- `ClassAstHolder`: クラス定義のAST解析
- フィールド直後の文字列リテラルからヘルプテキストを自動抽出
- 型ヒント情報の抽出と処理

### 名前空間ラッパー (`namespacewrapper.py`)
- トップレベルCLI名前空間の実装
- `ArgumentParser`オプションの管理
- `parse_args()`メソッドの実装

### グループラッパー (`groupwrapper.py`)
- 引数グループの実装（`--database-host`のような階層オプション）
- ネストしたグループ構造のサポート

## 品質保証

### チェック項目
- [ ] 両バージョン（v310, v312）での API整合性
- [ ] 型注釈の完全性（mypy --strict通過）
- [ ] 適切な環境でのテスト実行
- [ ] ドキュメントとコードの同期
- [ ] パフォーマンステスト（大規模CLI定義）

### 自動化可能な検証
- GitHub Actionsでの複数Python版テスト
- mypyによる型チェック
- pytestによるユニット・統合テスト
- カバレッジ測定（pytest-cov）

## よくある問題とその解決策

### Q: v310とv312で実装が分かれている理由は？
A: Python 3.12で導入された新ジェネリック構文(`class Foo[T]:`)は旧バージョンと互換性がないため。最適化された実装を各バージョン用に提供。

### Q: AST解析でヘルプテキストを抽出する理由は？
A: デコレータ引数ではなく、コードの可読性を保ちながら型注釈に近い場所にヘルプを記述できるため。

### Q: NotSelectedとNoneの使い分けは？
A: `None`は明示的な値、`NotSelected`は未設定状態を表す。混同すると実行時エラーの原因となる。

## 関連ドキュメント

- [詳細開発ガイド](./.github/copilot-instructions.md)
- [テスト仕様書](../test/test.copilot-instructions.md)
- [API リファレンス](../docs/html/index.html)
- [クイックスタート](../README.md)