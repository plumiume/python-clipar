クイックスタート
================

基本的な使い方
--------------

clipar を使用すると、Pythonのクラスと型注釈を使って簡単にCLIを定義できます。

シンプルな例
~~~~~~~~~~~~

.. code-block:: python

   from clipar import namespace

   @namespace
   class CLI:
       verbose: bool = False
       "詳細出力を有効にする"

       name: str = "World"
       "挨拶する名前"

   if __name__ == "__main__":
       args = CLI.parse_args()
       if args.verbose:
           print(f"詳細モードで実行中...")
       print(f"Hello, {args.name}!")

実行例：

.. code-block:: bash

   $ python script.py --name Alice
   Hello, Alice!

   $ python script.py --verbose --name Bob
   詳細モードで実行中...
   Hello, Bob!

ヘルプメッセージの追加
----------------------

フィールドの直後に文字列リテラルを置くことで、ヘルプメッセージを追加できます：

.. code-block:: python

   @namespace
   class CLI:
       output: str = "output.txt"
       "出力ファイルのパス"

       force: bool = False
       "既存のファイルを上書きする"

グループ化されたオプション
--------------------------

関連するオプションをグループ化できます：

.. code-block:: python

   from clipar import namespace, group

   @namespace
   class CLI:
       @group
       class Database:
           host: str = "localhost"
           "データベースホスト"

           port: int = 5432
           "データベースポート"

       verbose: bool = False

   if __name__ == "__main__":
       args = CLI.parse_args()
       print(f"Database: {args.Database.host}:{args.Database.port}")

複数のバージョンサポート
------------------------

clipar は Python 3.10/3.11 と 3.12+ の両方をサポートしています。
適切な実装が実行時に自動的に選択されます。

次のステップ
------------

詳細なAPI仕様については :doc:`api/index` を参照してください。
