"""
argparse.HelpFormatter の内部API を含む日本語docstring付き型スタブファイル

このファイルは CliparHelpFormatter の実装のために、
argparse.HelpFormatter の内部メソッドとAPI構造を理解するための参考資料として作成されています。
"""

from __future__ import annotations
from typing import Any, Callable, Iterable, Pattern
from argparse import Action
from argparse import _MutuallyExclusiveGroup # type: ignore


class HelpFormatter:
    """ヘルプメッセージとusageメッセージの生成を行うフォーマッター
    
    このクラス名のみがパブリックAPIとして扱われ、
    提供されるメソッドはすべて実装詳細として扱われる。
    """

    # インスタンス変数
    _prog: str
    _indent_increment: int
    _max_help_position: int
    _width: int
    _current_indent: int
    _level: int
    _action_max_length: int
    _root_section: HelpFormatter._Section
    _current_section: HelpFormatter._Section
    _whitespace_matcher: Pattern[str]
    _long_break_matcher: Pattern[str]

    def __init__(self,
                 prog: str,
                 indent_increment: int = 2,
                 max_help_position: int = 24,
                 width: int | None = None) -> None:
        """HelpFormatterを初期化
        
        Args:
            prog: プログラム名
            indent_increment: インデントの増分（デフォルト: 2）
            max_help_position: ヘルプテキストの最大開始位置（デフォルト: 24）
            width: 出力幅（デフォルト: 自動検出）
        """
        ...

    # ===============================
    # セクションとインデントのメソッド
    # ===============================
    
    def _indent(self) -> None:
        """現在のインデントレベルを1段階深くする"""
        ...

    def _dedent(self) -> None:
        """現在のインデントレベルを1段階浅くする"""
        ...

    class _Section:
        """ヘルプメッセージの1つのセクションを表す内部クラス"""
        
        formatter: HelpFormatter
        parent: HelpFormatter._Section | None
        heading: str | None
        items: list[tuple[Callable[..., str], Iterable[Any]]]
        
        def __init__(self, formatter: HelpFormatter, parent: HelpFormatter._Section | None, heading: str | None = None) -> None:
            """セクションを初期化
            
            Args:
                formatter: 親となるHelpFormatterインスタンス
                parent: 親セクション（Noneの場合はルートセクション）
                heading: セクションの見出し
            """
            ...

        def format_help(self) -> str:
            """このセクションのヘルプテキストをフォーマットして返す"""
            ...

    def _add_item(self, func: Callable[..., str], args: Iterable[Any]) -> None:
        """現在のセクションにアイテムを追加"""
        ...

    # ========================
    # メッセージ構築メソッド
    # ========================
    
    def start_section(self, heading: str | None) -> None:
        """新しいセクションを開始"""
        ...

    def end_section(self) -> None:
        """現在のセクションを終了し、親セクションに戻る"""
        ...

    def add_text(self, text: str | None) -> None:
        """セクションにテキストを追加"""
        ...

    def add_usage(self, usage: str | None, actions: Iterable[Action], groups: Iterable[_MutuallyExclusiveGroup], prefix: str | None = None) -> None:
        """usageセクションを追加"""
        ...

    def add_argument(self, action: Action) -> None:
        """引数の情報をヘルプに追加"""
        ...

    def add_arguments(self, actions: Iterable[Action]) -> None:
        """複数の引数を一度に追加"""
        ...

    # =======================
    # ヘルプフォーマットメソッド
    # =======================
    
    def format_help(self) -> str:
        """完全なヘルプメッセージを生成して返す"""
        ...

    def _join_parts(self, part_strings: Iterable[str]) -> str:
        """文字列の部分を結合（空文字列とSUPPRESSは除外）"""
        ...

    def _format_usage(self, usage: str | None, actions: Iterable[Action], groups: Iterable[_MutuallyExclusiveGroup], prefix: str | None) -> str:
        """usageメッセージをフォーマット"""
        ...

    def _format_actions_usage(self, actions: Iterable[Action], groups: Iterable[_MutuallyExclusiveGroup]) -> str:
        """アクションのusage部分をフォーマット"""
        ...

    def _format_text(self, text: str) -> str:
        """通常のテキストをフォーマット"""
        ...

    def _format_action(self, action: Action) -> str:
        """単一のアクション（引数）のヘルプをフォーマット
        
        これは CliparHelpFormatter で最も重要にオーバーライドするメソッド
        """
        ...

    def _format_action_invocation(self, action: Action) -> str:
        """アクションの呼び出し形式（名前とmetavar）をフォーマット
        
        これは CliparHelpFormatter で重要にオーバーライドするメソッド
        positional と optional で処理が分かれる
        """
        ...

    def _metavar_formatter(self, action: Action, default_metavar: str) -> Callable[[int], tuple[str, ...]]:
        """metavar（引数の値を表すプレースホルダー）のフォーマッターを返す
        
        これは CliparHelpFormatter で最も重要にオーバーライドするメソッド
        ここで型情報やリテラル情報の表示を制御する
        """
        ...

    def _format_args(self, action: Action, default_metavar: str) -> str:
        """アクションの引数部分をフォーマット（nargs考慮）"""
        ...

    def _expand_help(self, action: Action) -> str:
        """ヘルプテキスト内の変数を展開"""
        ...

    def _iter_indented_subactions(self, action: Action) -> Iterable[Any]:
        """インデントされたサブアクションを反復処理"""
        ...

    def _split_lines(self, text: str, width: int) -> list[str]:
        """指定された幅でテキストを行に分割"""
        ...

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """テキストを指定された幅とインデントで埋める"""
        ...

    def _get_help_string(self, action: Action) -> str | None:
        """アクションのヘルプ文字列を取得"""
        ...

    def _get_default_metavar_for_optional(self, action: Action) -> str:
        """オプション引数のデフォルトmetavarを取得"""
        ...

    def _get_default_metavar_for_positional(self, action: Action) -> str:
        """位置引数のデフォルトmetavarを取得"""
        ...


# 他のフォーマッタークラス（参考用）

class RawDescriptionHelpFormatter(HelpFormatter):
    """説明文のフォーマットを保持するヘルプフォーマッター"""
    
    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """テキストを指定された幅とインデントで埋める（オーバーライド）
        
        呼び出し元の内部API:
        - _format_text() -> _fill_text()
        - _format_action() -> _expand_help() -> _fill_text()（間接的）
        """
        ...


class RawTextHelpFormatter(RawDescriptionHelpFormatter):
    """すべてのヘルプテキストのフォーマットを保持するヘルプフォーマッター"""
    
    def _split_lines(self, text: str, width: int) -> list[str]:
        """指定された幅でテキストを行に分割（オーバーライド）
        
        呼び出し元の内部API:
        - _format_action() -> _expand_help() -> _split_lines()
        - _fill_text() -> textwrap.wrap() の代替として使用
        """
        ...


class ArgumentDefaultsHelpFormatter(HelpFormatter):
    """引数のデフォルト値をヘルプに追加するヘルプフォーマッター"""
    
    def _get_help_string(self, action: Any) -> str | None:
        """アクションのヘルプ文字列を取得（オーバーライド）
        
        呼び出し元の内部API:
        - _format_action() -> _expand_help() -> _get_help_string()
        - add_argument() -> _format_action() -> _expand_help() -> _get_help_string()
        """
        ...


class MetavarTypeHelpFormatter(HelpFormatter):
    """引数の'type'をデフォルトのmetavar値として使用するヘルプフォーマッター"""
    
    def _get_default_metavar_for_optional(self, action: Any) -> str:
        """オプション引数のデフォルトmetavarを取得（オーバーライド）
        
        呼び出し元の内部API:
        - _format_action_invocation() -> _format_args() -> _metavar_formatter() -> _get_default_metavar_for_optional()
        """
        ...

    def _get_default_metavar_for_positional(self, action: Any) -> str:
        """位置引数のデフォルトmetavarを取得（オーバーライド）
        
        呼び出し元の内部API:
        - _format_action_invocation() -> _metavar_formatter() -> _get_default_metavar_for_positional()
        """
        ...