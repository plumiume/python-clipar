API リファレンス
================

.. toctree::
   :maxdepth: 2

   modules

モジュール概要
--------------

clipar パッケージの主要なモジュールとクラス：

.. autosummary::
   :toctree: generated
   :recursive:

   clipar

主要な機能
----------

デコレータ
~~~~~~~~~~

.. currentmodule:: clipar

.. autosummary::
   namespace
   group

エンティティ
~~~~~~~~~~~~

.. autosummary::
   clipar.entities

バージョン別実装
----------------

clipar は Python のバージョンに応じて最適化された実装を提供します：

* **v310**: Python 3.10/3.11 向け実装
* **v312**: Python 3.12+ 向け実装

実装は実行時に自動的に選択されるため、ユーザーが意識する必要はありません。
