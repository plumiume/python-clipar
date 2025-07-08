# Clipar プロジェクト テストスイート

このディレクトリには、`src/clipar` パッケージのテストが含まれています。

## ディレクトリ構造

```
test/
├── unit/                    # ユニットテスト
│   ├── conftest.py         # pytest設定
│   ├── test_basewrapper.py
│   ├── test_class_ast.py
│   ├── test_decorator.py
│   ├── test_groupwrapper.py
│   ├── test_init.py
│   └── test_namespacewrapper.py
├── README.md               # このファイル
├── requirements.txt        # テスト依存関係
└── run_tests.py           # テスト実行スクリプト
```

## ユニットテストファイル一覧

- `unit/test_basewrapper.py` - `basewrapper.py` の基本機能テスト
- `unit/test_class_ast.py` - `class_ast.py` のAST解析機能テスト
- `unit/test_decorator.py` - `decorator.py` のデコレータ機能テスト
- `unit/test_namespacewrapper.py` - `namespacewrapper.py` の名前空間ラッパーテスト
- `unit/test_groupwrapper.py` - `groupwrapper.py` のグループラッパーテスト
- `unit/test_init.py` - `__init__.py` のパッケージインポートテスト

## セットアップ

### 必要な依存関係をインストール

```bash
pip install pytest
```

または requirements.txt を使用：

```bash
pip install -r requirements.txt
```

## テストの実行方法

### 全テストを実行

```bash
# スクリプトを使用
python run_tests.py

# または直接pytest (ユニットテストのみ)
pytest unit/ -v

# または全テストディレクトリ
pytest . -v
```

### 個別のテストファイルを実行

```bash
pytest unit/test_basewrapper.py -v
pytest unit/test_class_ast.py -v
pytest unit/test_decorator.py -v
pytest unit/test_namespacewrapper.py -v
pytest unit/test_groupwrapper.py -v
pytest unit/test_init.py -v
```

### 特定のテストクラスまたはメソッドを実行

```bash
pytest unit/test_basewrapper.py::TestBaseWrapper -v
pytest unit/test_basewrapper.py::TestBaseWrapper::test_init -v
```

## テスト構成

### テスト対象

各テストファイルは以下の内容をカバーしています：

1. **基本機能テスト** - クラスの初期化、メソッドの動作確認
2. **エラーハンドリングテスト** - 例外処理の確認
3. **統合テスト** - 複数のコンポーネント間の相互作用
4. **エッジケーステスト** - 境界条件での動作確認

### モックの使用

テストでは `unittest.mock` を使用して：
- 外部依存関係の分離
- 副作用のない単体テスト
- 特定の条件下での動作確認

## テスト結果の見方

### 成功時

```
====== test session starts ======
collected 50 items

test_basewrapper.py::TestBaseWrapper::test_init PASSED
test_basewrapper.py::TestBaseWrapper::test_get_descriptor PASSED
...
====== 50 passed in 2.34s ======
```

### 失敗時

```
====== FAILURES ======
______ TestClass.test_method ______

    def test_method(self):
>       assert expected == actual
E       AssertionError: expected != actual

test_file.py:123: AssertionError
```

## トラブルシューティング

### よくある問題

1. **インポートエラー**
   - `src` ディレクトリがPythonパスに含まれているか確認
   - `conftest.py` が正しく設定されているか確認

2. **モジュールが見つからない**
   - ワーキングディレクトリがプロジェクトルートにあるか確認
   - パッケージの `__init__.py` ファイルが存在するか確認

3. **型エラー**
   - Pylanceまたはmypyを使用して型チェックを実行
   - 型ヒントが正しく設定されているか確認

## カバレッジ測定（オプション）

テストカバレッジを測定する場合：

```bash
pip install pytest-cov
pytest unit/ --cov=src/clipar --cov-report=html
```

カバレッジレポートは `htmlcov/index.html` で確認できます。

## 継続的インテグレーション

このテストスイートはCI/CDパイプラインで使用できます：

```yaml
# GitHub Actions例
- name: Run tests
  run: |
    pip install pytest
    cd test
    python run_tests.py
```
