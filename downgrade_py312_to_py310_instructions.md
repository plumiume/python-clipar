# Python 3.12 → 3.10 ダウングレード指示書 (Claude Sonnet用)

## 概要
`src/clipar/v312/` フォルダ内の全てのPythonファイルをPython 3.10互換に変更する。
主な変更点はジェネリック構文、型注釈、インポートの修正。

## 変更対象ファイル
- `src/clipar/v312/basewrapper.py`
- `src/clipar/v312/class_ast.py`
- `src/clipar/v312/decorator.py`
- `src/clipar/v312/groupwrapper.py`
- `src/clipar/v312/mixin.py`
- `src/clipar/v312/namespacewrapper.py`

## 変更ルール

### 1. ジェネリック構文の変更

**変更前 (Python 3.12+):**
```python
class MyClass[T]:
    pass

def function[T](param: T) -> T:
    pass
```

**変更後 (Python 3.10):**
```python
from typing import TypeVar, Generic

_T = TypeVar('_T')

class MyClass(Generic[_T]):
    pass

def function(param: _T) -> _T:
    pass
```

### 2. 具体的な変更パターン

#### A. クラス定義
```python
# 変更前
class NamespaceWrapper[NS](SubparserWrapper[NS]):

# 変更後
from typing import TypeVar, Generic
_NS = TypeVar('_NS')
class NamespaceWrapper(SubparserWrapper[_NS], Generic[_NS]):
```

#### B. 関数定義
```python
# 変更前
def _append_list[T](target: list[T], *args: T) -> list[T]:

# 変更後
_T = TypeVar('_T')
def _append_list(target: list[_T], *args: _T) -> list[_T]:
```

#### C. メソッド定義
```python
# 変更前
def callback[R](self, func: Callable[[NS], R]) -> Callable[[NS], R]:

# 変更後
_R = TypeVar('_R')
def callback(self, func: Callable[[_NS], _R]) -> Callable[[_NS], _R]:
```

#### D. bound制約付きTypeVar
```python
# 変更前
class Container[T: BaseType]:
    def process[U: AnotherType](self, item: U) -> T:
        pass

# 変更後
_T = TypeVar('_T', bound=BaseType)
_U = TypeVar('_U', bound=AnotherType)

class Container(Generic[_T]):
    def process(self, item: _U) -> _T:
        pass
```

#### E. 複数制約付きTypeVar
```python
# 変更前
def handle[T: (str, int, float)](value: T) -> T:
    pass

# 変更後
_T = TypeVar('_T', str, int, float)  # str, int, floatのいずれか
def handle(value: _T) -> _T:
    pass
```

### 3. インポートの統一

**各ファイルの先頭に追加すべきインポート:**
```python
from typing import TypeVar, Generic
from typing_extensions import Self

# 必要に応じて追加するTypeVar（プライベート変数として定義）
_NS = TypeVar('_NS')
_CLS = TypeVar('_CLS')
_T = TypeVar('_T')
_R = TypeVar('_R')
_U = TypeVar('_U')
_W = TypeVar('_W')

# bound制約付きの例
_T_BOUND = TypeVar('_T_BOUND', bound=SomeBaseClass)
_T_CHOICES = TypeVar('_T_CHOICES', str, int, float)  # 複数制約
```

### TypeVar命名規則
- **プライベート変数として定義**: `NS` → `_NS`, `T` → `_T`
- **理由**: TypeVarはモジュール内でのみ使用し、外部に公開する必要がないため
- **既存コードとの整合性**: `v310` フォルダで既に `_NS`, `_T` 等を使用している場合はそれに合わせる

### TypeVarのbound制約構文
- **変更前**: `class Foo[T: SomeType]` または `def func[T: SomeType]`
- **変更後**: `_T = TypeVar('_T', bound=SomeType)` + `class Foo(Generic[_T])`
- **制約の種類**:
  - `bound=`: 上限境界（そのタイプまたはサブタイプ）
  - 複数制約: `TypeVar('_T', str, int)` （指定した型のいずれか）

### 4. 特定ファイルの変更点

#### `namespacewrapper.py`
- `class NamespaceWrapper[NS]` → `class NamespaceWrapper(SubparserWrapper[_NS])`
- `def callback[R]` → `def callback` + `_R = TypeVar('_R')`

#### `class_ast.py`
- `class ClassAstHolder[CLS]` → `class ClassAstHolder(Generic[_CLS])`
- `_CLS = TypeVar('_CLS')` を追加

#### `basewrapper.py`
- `def _append_list[T]` → `def _append_list` + `_T = TypeVar('_T')`
- 既存のTypeVarと重複しないよう注意（既に `_T` が定義されている場合は再利用）

#### `decorator.py`
- ジェネリック関数の変更
- TypeVarの重複確認

#### `groupwrapper.py`
- 既にPython 3.10互換のため変更不要の可能性

#### `mixin.py`
- 既にPython 3.10互換のため変更不要の可能性

### 5. 変更手順

1. **仮想環境の準備**
   - Python 3.10の仮想環境を作成・有効化
   - 依存関係のインストール

2. **ファイル単位で変更**
   - 1つのファイルを完全に変更してからテスト
   - 変更前にバックアップを取る

3. **インポートの追加**
   - 必要なTypeVarを先頭で定義
   - 既存のインポートと重複しないよう確認

4. **構文の変更**
   - ジェネリック構文を順次変更
   - 型注釈の整合性を確認

5. **動作確認**
   - 各ファイル変更後に構文エラーがないか確認（仮想環境内で）
   - 型チェッカー（pyright/mypy）での確認（仮想環境内で）

### 6. 注意事項

#### A. TypeVarの重複回避
```python
# 同じファイル内で重複定義しない
_T = TypeVar('_T')  # 既存
_U = TypeVar('_U')  # 新規追加時は別名使用

# bound制約が異なる場合は別名を使用
_T = TypeVar('_T')  # 制約なし
_T_BOUND = TypeVar('_T_BOUND', bound=BaseClass)  # bound制約あり
```

#### B. 継承関係の確認
```python
# 変更前
class NamespaceWrapper[NS](SubparserWrapper[NS]):

# 変更後（継承とGenericの順序に注意）
class NamespaceWrapper(SubparserWrapper[_NS], Generic[_NS]):
# または
class NamespaceWrapper(SubparserWrapper[_NS]):  # 既にGeneric[_NS]が含まれている場合
```

#### C. 既存のTypeVarとの整合性
- `v310` フォルダの対応するファイルと同じTypeVar名を使用（`_NS`, `_T` 等）
- プライベート変数として統一: `NS` → `_NS`, `T` → `_T`, `CLS` → `_CLS`
- 一意性を保つため、必要に応じて `_NS1`, `_NS2` 等の番号付きサフィックスを使用

### 7. 検証方法

#### A. 仮想環境の確認
```bash
# 仮想環境が有効化されているか確認
which python  # Linux/macOS
where python  # Windows

# Python バージョンの確認
python --version  # Python 3.10.x であることを確認
```

#### B. 構文チェック
```bash
# 仮想環境内で実行
python -m py_compile src/clipar/v312/filename.py
```

#### C. 型チェック
```bash
# 仮想環境内で実行
pyright src/clipar/v312/
```

#### D. インポートテスト
```python
# 仮想環境内のPythonで確認
# 各モジュールが正しくインポートできるか確認
from src.clipar.v312.namespacewrapper import NamespaceWrapper
```

### 8. 完了確認チェックリスト

- [ ] Python 3.10の仮想環境が作成・有効化されている
- [ ] 依存関係が仮想環境内にインストールされている  
- [ ] 全ファイルでジェネリック構文 `[T]` が除去されている
- [ ] 必要なTypeVarがプライベート変数として定義されている（`_T`, `_NS`, `_CLS` 等）
- [ ] bound制約構文 `[T: BaseType]` が `TypeVar('_T', bound=BaseType)` に変換されている
- [ ] 複数制約構文が適切に `TypeVar('_T', Type1, Type2)` 形式に変換されている
- [ ] インポートが正しく追加されている
- [ ] 構文エラーがない（仮想環境内で確認）
- [ ] 型チェッカーでエラーがない（仮想環境内で確認）
- [ ] 既存の機能が保持されている
- [ ] TypeVar命名規則が統一されている（アンダースコアプレフィックス）

## 仮想環境の設定と管理

### 仮想環境の作成と有効化
**全てのコマンド実行前に仮想環境を有効にすること**

#### 1. 仮想環境の確認と作成
```bash
# 仮想環境の存在確認
ls .venv/

# 仮想環境がない場合、uvで作成
# パス形式: {projectroot}/.venv/{user}@{machine}/{python_version_like_cp312}-{projectname}
# 例: .venv/user@computer/cp310-clipar
uv venv .venv/{user}@{machine}/cp310-clipar --python 3.10

# または現在のユーザー・マシン情報を自動取得
uv venv .venv/$(whoami)@$(hostname)/cp310-clipar --python 3.10
```

#### 2. 仮想環境の有効化
```bash
# Windows (PowerShell)
.venv\{user}@{machine}\cp310-clipar\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\{user}@{machine}\cp310-clipar\Scripts\activate.bat

# Linux/macOS
source .venv/{user}@{machine}/cp310-clipar/bin/activate
```

#### 3. 依存関係のインストール
```bash
# pyproject.tomlから依存関係をインストール
uv pip install -e .

# 開発用依存関係も含める場合
uv pip install -e ".[dev]"
```

## 実行コマンド例

```bash
# 1. 仮想環境の有効化（必須）
# Windows PowerShell:
.venv\{user}@{machine}\cp310-clipar\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/{user}@{machine}/cp310-clipar/bin/activate

# 2. 現在のブランチで作業
git status

# 3. 変更後のファイル確認
git diff src/clipar/v312/

# 4. テスト実行
python -m pytest test/ -v

# 5. 型チェック
pyright src/clipar/v312/
```

## トラブルシューティング

### よくある問題
1. **TypeVarの重複定義**: 同じ名前のTypeVarが複数回定義されている
2. **継承順序の問題**: `Generic[T]` の位置が不適切
3. **インポート漏れ**: 必要な `typing` モジュールのインポートが不足
4. **bound制約の見落とし**: `[T: BaseType]` 構文のbound制約が適切に変換されていない
5. **複数制約の構文エラー**: `TypeVar('T', bound=A, bound=B)` のような不正な記述

### 解決方法
1. **仮想環境の確認**: Python 3.10環境が正しく有効化されているか確認
2. ファイル全体でTypeVarの一意性を確認
3. 継承関係を慎重に確認
4. 必要なインポートを先頭に追加
5. bound制約は `bound=` パラメータで指定
6. 複数制約は `TypeVar('T', Type1, Type2, Type3)` の形式で指定

---

**注意**: この指示書に従って変更する際は、必ず段階的に進め、各ファイルの変更後に動作確認を行ってください。