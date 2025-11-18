# AI Agent Documentation Index

このディレクトリには、AIエージェントがCliparプロジェクトで効率的に作業を行うための包括的なドキュメント群が含まれています。

## ドキュメント構成

### 📋 基本仕様書
| ドキュメント | 用途 | 対象読者 |
|-------------|------|----------|
| [ai-specifications.md](./ai-specifications.md) | プロジェクト概要・アーキテクチャ・基本ガイドライン | 全AIエージェント |
| [copilot-instructions.md](./copilot-instructions.md) | 開発ルール・具体的手順・アンチパターン | 開発作業を行うエージェント |

### 🔧 技術仕様書  
| ドキュメント | 用途 | 対象読者 |
|-------------|------|----------|
| [api-reference.md](./api-reference.md) | 内部API詳細・使用例・バージョン差異 | コード生成・変更を行うエージェント |
| [architecture.md](./architecture.md) | 設計思想・技術的判断・実装戦略 | アーキテクチャ理解が必要なエージェント |
| [code-quality.md](./code-quality.md) | 品質基準・静的解析・コーディング規約 | 品質保証を行うエージェント |

### 🛠️ 開発プロセス
| ドキュメント | 用途 | 対象読者 |
|-------------|------|----------|  
| [development-workflow.md](./development-workflow.md) | 開発フロー・環境管理・デバッグ手順 | 開発作業全般を行うエージェント |
| [testing-strategy.md](./testing-strategy.md) | テスト戦略・品質保証・CI/CD | テスト作成・実行を行うエージェント |

## 効率的な利用方法

### 🚀 初回プロジェクト参加時

1. **[ai-specifications.md](./ai-specifications.md)** を最初に読む
   - プロジェクト全体像の把握
   - 並列実装戦略の理解
   - 基本的な開発ルールの確認

2. **[copilot-instructions.md](./copilot-instructions.md)** で詳細ルールを確認
   - コーディング規約
   - テスト実行方法
   - よくあるトラブルシューティング

### 🔍 作業別推奨読み順

#### 新機能開発時
```
ai-specifications.md → api-reference.md → development-workflow.md → testing-strategy.md
```

#### バグ修正時
```
copilot-instructions.md → development-workflow.md → api-reference.md
```

#### アーキテクチャ変更時
```
architecture.md → ai-specifications.md → api-reference.md → testing-strategy.md
```

#### テスト作成時
```
testing-strategy.md → api-reference.md → development-workflow.md
```

#### コード品質保証時
```
code-quality.md → development-workflow.md → testing-strategy.md
```

## クイックリファレンス

### 🔑 重要コマンド

```powershell
# 環境確認
python --version

# Python 3.10テスト
venv\cp310\Scripts\Activate.ps1
python -m pytest test/unit/v310/ -v

# Python 3.12テスト  
venv\cp312\Scripts\Activate.ps1
python -m pytest test/unit/v312/ -v

# パッケージ追加
uv add <package>
uv add --dev <dev-package>
```

### 📁 重要ディレクトリ

```
src/clipar/
├── __init__.py           # バージョン選択ロジック（重要）
├── entities.py           # 統一エクスポート
├── v310/                 # Python 3.10/3.11対応
└── v312/                 # Python 3.12+対応

test/
├── unit/v310/           # Python 3.10/3.11用テスト
├── unit/v312/           # Python 3.12+用テスト
├── integration/v310/    # 統合テスト
└── integration/v312/    # 統合テスト
```

### ⚠️ 必須注意事項

1. **並列実装の整合性**
   - v310とv312両方への変更が必須
   - 片側のみの更新は実行時エラーの原因

2. **環境とテストの対応**
   - Python 3.10/3.11 → v310テスト
   - Python 3.12+ → v312テスト
   - 不適切な環境での実行は失敗の原因

3. **パッケージ管理**
   - `uv`コマンドのみ使用
   - `pip`系コマンドは禁止

## トラブルシューティング

### 💥 よくある問題

| 問題 | 原因 | 解決策 | 参照ドキュメント |
|------|------|--------|------------------|
| テスト失敗 | Python環境不整合 | 適切な環境に切り替え | [development-workflow.md](./development-workflow.md) |
| インポートエラー | バージョン実装不整合 | 両バージョン同期 | [copilot-instructions.md](./copilot-instructions.md) |
| ヘルプテキスト未表示 | AST解析失敗 | フィールド直後配置 | [api-reference.md](./api-reference.md) |
| 型チェックエラー | ジェネリック構文混同 | バージョン適切使用 | [architecture.md](./architecture.md) |

### 🔧 デバッグヒント

```python
# AST解析確認
from clipar.v310.class_ast import ClassAstHolder
holder = ClassAstHolder(YourClass)
print(holder.help_texts)

# 型検出確認
from clipar.v310.namespacewrapper import NamespaceWrapper  
wrapper = NamespaceWrapper(YourClass)
field_type, is_optional = wrapper._detect_type("field", annotation)
```

## 更新とメンテナンス

### 📝 ドキュメント更新ルール

- **API変更時**: `api-reference.md`を必ず更新
- **新機能追加時**: 該当するすべてのドキュメントを更新  
- **バグ修正時**: `development-workflow.md`のトラブルシューティングを更新
- **テスト追加時**: `testing-strategy.md`に新しいパターンを記録

### 🔄 定期レビュー項目

- [ ] ドキュメントとコードの同期
- [ ] リンクの有効性確認
- [ ] 例示コードの動作確認
- [ ] パフォーマンスベンチマークの更新

## 関連リソース

### 📚 外部リンク
- [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [argparse Documentation](https://docs.python.org/3/library/argparse.html)
- [AST Module Documentation](https://docs.python.org/3/library/ast.html)

### 🏠 プロジェクト内リソース
- [メインREADME](../README.md) - 基本的な使用方法
- [テスト仕様詳細](../test/test.copilot-instructions.md) - テスト固有の詳細
- [Sphinx文档](../docs/html/index.html) - 自動生成API文書
- [使用例](../examples/) - 実践的な使用例

---

## 📧 フィードバック

ドキュメントの改善提案や不明な点があれば、以下の方法でフィードバックをお願いします：

1. **Issue作成**: プロジェクトのGitHubリポジトリにIssueを作成
2. **直接編集**: ドキュメントファイルを直接編集してPRを作成  
3. **議論**: プロジェクトの議論フォーラムで話題を提起

適切なドキュメンテーションにより、AIエージェントがより効率的にプロジェクトに貢献できることを目指しています。