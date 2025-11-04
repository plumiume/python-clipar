.. clipar documentation master file

clipar ドキュメント
===================

**clipar** は、Python の型注釈とクラスデコレータを使って CLI を定義する軽量ライブラリです。

.. toctree::
   :maxdepth: 2
   :caption: 目次:

   installation
   quickstart
   api/index

特徴
----

* 型注釈ベースのCLI定義
* Python 3.10+ および 3.12+ のサポート
* シンプルで直感的なAPI
* ネストされたコマンドグループのサポート

インストール
------------

.. code-block:: bash

   pip install clipar

クイックスタート
----------------

.. code-block:: python

   from clipar import namespace

   @namespace
   class CLI:
       verbose: bool = False
       "詳細出力を有効にする"

       count: int = 1
       "実行回数"

   if __name__ == "__main__":
       args = CLI.parse_args()
       print(f"Verbose: {args.verbose}, Count: {args.count}")

インデックスと検索
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
