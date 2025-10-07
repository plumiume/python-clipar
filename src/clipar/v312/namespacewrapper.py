import sys
from typing import (
    Any,
    Sequence,
    Callable,
    TypedDict,
)
import argparse
from argparse import (
    _SubParsersAction, # pyright: ignore[reportPrivateUsage]
)
import argcomplete
from .basewrapper import (
    OnParseHookArgs, Location,
    BaseWrapper, SubparserWrapper, SubgroupWrapper,
    BoundWrapper
)
from . import mixin

type ParentSubparserId = int


class ArgumentParserOptions(TypedDict, total=False):
    prog: str | None
    "The name of the program (default: sys.argv[0])"
    usage: str | None
    "A usage message to display when the program is run with no arguments."
    # description: str | None
    # "A description of the program to display before the argument help."
    # use namespace_type.__doc__
    epilog: str | None
    "A message to display after the argument help."
    # parents: Sequence[argparse.ArgumentParser]
    # "A list of ArgumentParser objects whose arguments should be added to this parser."
    # not used
    formatter_class: type[argparse.HelpFormatter]
    "The class used to format the help output."
    prefix_chars: str
    "The set of characters that prefix optional arguments (default: '-')"
    fromfile_prefix_chars: str | None
    "Characters that prefix files containing additional arguments (default: None)"
    # argument_default: Any | None
    # "The default value for arguments (default: None)"
    # not used
    conflict_handler: str
    "The strategy for resolving conflicts between argument names (default: 'error')"
    add_help: bool
    "Whether to add a default help argument (default: True)"
    allow_abbrev: bool
    "Whether to allow abbreviations of long options (default: True)"
    exit_on_error: bool
    "Whether to exit on error (default: True)"
    if sys.version_info >= (3, 14): # pyright: ignore[reportGeneralTypeIssues]
        suggest_on_error: bool
        "Whether to suggest similar options on error (default: False)"
        color: bool
        "Whether to use color in the help output (default: False)"

class SubParserOptions(TypedDict, total=False):
    title: str
    "The title for the subparser group (default: None)"
    metavar: str | None
    "The name to use for the subcommand in help output (default: None)"
    required: bool
    "Whether the subcommand is required (default: False)"

class TrackableSubParsersAction(_SubParsersAction): # pyright: ignore[reportMissingTypeArgument]

    def __init__(
        self,
        option_strings: Sequence[str],
        prog: str,
        parser_class: type[argparse.ArgumentParser],
        dest: str = "==SUPPRESS==",
        required: bool = False,
        help: str | None = None,
        metavar: str | None = None,
        ):

        super().__init__( # pyright: ignore[reportUnknownMemberType]
            option_strings,
            prog,
            parser_class,
            dest,
            required,
            help,
            metavar
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None
        ):

        super().__call__(
            parser,
            namespace,
            values,
            option_string
        )

        if isinstance(values, str) or not isinstance(values, Sequence):
            raise TypeError(f"Expected Sequence, got {type(values)}.")

        parser_name, *_ = values

        command_chain: list[str] | None = getattr(namespace, '_clipar_command_chain', None)
        if command_chain is None:
            command_chain = [parser_name]
            setattr(namespace, '_clipar_command_chain', command_chain)
        else:
            command_chain.append(parser_name)

class NamespaceWrapper[NS](SubparserWrapper[NS]):

    def __init__(
        self,
        namespace_type: type[NS],
        parser_options: ArgumentParserOptions = {},
        subparser_options: SubParserOptions = {},
        ):

        self._parser = argparse.ArgumentParser(**parser_options)
        self._subparser_options = subparser_options
        self._parser_subparsers: TrackableSubParsersAction | None = None
        super().__init__(namespace_type)

    def _get_subparsers(self) -> TrackableSubParsersAction:
        if self._parser_subparsers is None:
            trackable_subparsers_action = self._parser.add_subparsers(
                # dest="_clipar_leaf_name",
                action=TrackableSubParsersAction,
                **self._subparser_options,
            )
            if isinstance(trackable_subparsers_action, TrackableSubParsersAction):
                self._parser_subparsers = trackable_subparsers_action
            else:
                raise TypeError(
                    f"Expected TrackableSubParsersAction, got "
                    f"{type(trackable_subparsers_action)}."
                )
        return self._parser_subparsers

    def configure_container(self) -> argparse.ArgumentParser:
        return self._parser

    def on_after_bind(self, bound_name: str, wrapper: BaseWrapper[Any]):
        if isinstance(wrapper, SubgroupWrapper):
            raise TypeError(
                f"SubgroupWrapper {wrapper} cannot be bound to a NamespaceWrapper."
            )
        if isinstance(wrapper, NamespaceWrapper):
            wrapper._get_subparsers().add_parser( # pyright: ignore[reportUnknownMemberType]
                bound_name,
                parents=[self._parser],
                add_help=False,
            )

    def _before_parse(self) -> list[OnParseHookArgs]:

        recursionlimit = sys.getrecursionlimit()

        self.on_before_parse([], None)

        stack: list[OnParseHookArgs] = [
            *(([name], holder) for name, holder in self._subgroups.items()),
            *(([name], holder) for name, holder in self._subparsers.items())
        ]

        ret: list[OnParseHookArgs] = []

        while stack:

            item = stack.pop()
            ret.append(item)

            location, holder = item

            if len(location) > recursionlimit:
                raise RecursionError(
                    f"Recursion limit exceeded ({recursionlimit}). "
                    f"Possible cyclic reference in namespace definition."
                )

            holder.self.on_before_parse(location, holder)

            stack.extend(
                (location + [name], holder)
                for name, holder in holder.self._subgroups.items()
            )

            stack.extend(
                (location + [name], holder)
                for name, holder in holder.self._subparsers.items()
            )

        argcomplete.autocomplete(self._parser)

        return ret

    def _after_parse(self, namespace: argparse.Namespace, flattens: list[OnParseHookArgs]) -> NS:

        # leaf_wrapper: SubparserWrapper[Any] = getattr(namespace, '_clipar_wrapper')
        command_chain: list[str] = list(reversed(
            getattr(namespace, '_clipar_command_chain', [])
        )) # leaf to root

        ret_ns = self.namespace_type()

        namespace_table: dict[BaseWrapper[Any], tuple[
            Location, BoundWrapper[BaseWrapper[Any]] | None, object, set[str]
        ]] = {
            self: ([], None, ret_ns, self._arg_names)
        }

        for location, holder in flattens:

            if holder.parent not in namespace_table:
                continue

            if isinstance(holder.self, SubparserWrapper):

                if location != command_chain[:len(location)]:
                    continue

            tmp_ns = holder.self.namespace_type()
            _, _, parent_ns, _ = namespace_table[holder.parent]

            setattr(parent_ns, holder.bound_name, tmp_ns)

            # set attribute to mixin
            # if isinstance(any_ns, mixin.AnyMixin):
            #     do something
            if isinstance(parent_ns, mixin.CommandMixin):
                parent_ns.clipar_mixin_dict['command'] = holder.bound_name

            namespace_table[holder.self] = (location, holder, tmp_ns, holder.self._arg_names)

        for location, holder, tmp_ns, arg_names in reversed(namespace_table.values()):

            for a in arg_names:
                setattr(tmp_ns, a, getattr(namespace, a))

            if holder is None:
                self.on_after_parse(location, None)
            else:
                holder.self.on_after_parse(location, holder)

        return ret_ns

    ## Public API

    def parse_args(self, args: list[str] | None = None) -> NS:
        """
        Parse command-line arguments and return the configured namespace object.
        
        This method converts command-line argument strings into a namespace object
        with attributes corresponding to the defined arguments. It performs full
        validation and will exit with an error message if invalid arguments are provided.

        Args:
            args (`list[str] | None`): The list of argument strings to parse.
                If None (default), arguments are taken from sys.argv.

        Returns:
            `NS`: A namespace object containing the parsed arguments as attributes.

        Raises:
            SystemExit: If parsing fails due to invalid arguments, missing required
                arguments, or other parsing errors (unless exit_on_error=False).

        Note:
            Unselected subcommands in the returned NS instance will return `NotSelected`
            when accessed as attributes. This behavior is implemented by BaseWrapper.__get__,
            which returns the NotSelected singleton when the descriptor is accessed on an
            instance that doesn't correspond to the selected subcommand path.

        Examples:
            Basic argument parsing:
            
            ```python
            @namespace
            class Config:
                input_file: str
                verbose: bool = False
            
            # Parse from sys.argv
            config = Config.parse_args()
            
            # Parse specific arguments
            config = Config.parse_args(['data.txt', '--verbose'])
            # config.input_file == 'data.txt'
            # config.verbose == True
            ```
        """
        flattens = self._before_parse()
        namespace = self._parser.parse_args(args)
        return self._after_parse(namespace, flattens)

    def parse_known_args(self, args: list[str] | None = None) -> tuple[NS, list[str]]:
        """
        Parse known command-line arguments and return unrecognized arguments separately.
        
        This method works similarly to parse_args() but does not raise an error for
        unrecognized arguments. Instead, it parses only the known arguments and
        returns both the namespace and a list of unrecognized argument strings.

        Args:
            args (`list[str] | None`): The list of argument strings to parse.
                If None (default), arguments are taken from sys.argv.

        Returns:
            `tuple[NS, list[str]]`: A tuple containing:
                - The namespace object with parsed known arguments
                - A list of unrecognized argument strings

        Note:
            Unselected subcommands in the returned NS instance will return `NotSelected`
            when accessed as attributes. This behavior is implemented by BaseWrapper.__get__,
            which returns the NotSelected singleton when the descriptor is accessed on an
            instance that doesn't correspond to the selected subcommand path.

        Examples:
            Handling mixed known and unknown arguments:
            
            ```python
            @namespace
            class Config:
                input_file: str
                verbose: bool = False
            
            config, unknown = Config.parse_known_args([
                'data.txt', '--verbose', '--unknown-flag', 'extra'
            ])
            # config.input_file == 'data.txt'
            # config.verbose == True
            # unknown == ['--unknown-flag', 'extra']
            ```
        """
        flattens = self._before_parse()
        namespace, unknown_args = self._parser.parse_known_args(args)
        return (self._after_parse(namespace, flattens), unknown_args)

    def parse_intermixed_args(self, args: list[str] | None = None) -> NS:
        """
        Parse arguments allowing positional and optional arguments to be intermixed.
        
        This method allows command-line arguments where optional arguments can appear
        between positional arguments, similar to many Unix commands. However, it has
        limitations and doesn't support all argparse features like subparsers.

        Args:
            args (`list[str] | None`): The list of argument strings to parse.
                If None (default), arguments are taken from sys.argv.

        Returns:
            `NS`: A namespace object containing the parsed arguments as attributes.

        Raises:
            SystemExit: If parsing fails or if unsupported features are used.

        Note:
            Unselected subcommands in the returned NS instance will return `NotSelected`
            when accessed as attributes. This behavior is implemented by BaseWrapper.__get__,
            which returns the NotSelected singleton when the descriptor is accessed on an
            instance that doesn't correspond to the selected subcommand path.

        Examples:
            Intermixed argument parsing:
            
            ```python
            @namespace
            class Config:
                command: str
                files: list[str]
                verbose: bool = False
            
            # Traditional: command files --verbose
            # Intermixed: command --verbose files
            config = Config.parse_intermixed_args([
                'process', '--verbose', 'file1.txt', 'file2.txt'
            ])
            # config.command == 'process'
            # config.verbose == True
            # config.files == ['file1.txt', 'file2.txt']
            ```
        """
        flattens = self._before_parse()
        namespace = self._parser.parse_intermixed_args(args)
        return self._after_parse(namespace, flattens)


    def parse_known_intermixed_args(self, args: list[str] | None = None) -> tuple[NS, list[str]]:
        """
        Parse known intermixed arguments and return unrecognized arguments separately.
        
        This method combines the functionality of parse_known_args() and 
        parse_intermixed_args(), allowing intermixed argument parsing while
        returning unrecognized arguments instead of raising errors.

        Args:
            args (`list[str] | None`): The list of argument strings to parse.
                If None (default), arguments are taken from sys.argv.

        Returns:
            `tuple[NS, list[str]]`: A tuple containing:
                - The namespace object with parsed known arguments
                - A list of unrecognized argument strings

        Note:
            Unselected subcommands in the returned NS instance will return `NotSelected`
            when accessed as attributes. This behavior is implemented by BaseWrapper.__get__,
            which returns the NotSelected singleton when the descriptor is accessed on an
            instance that doesn't correspond to the selected subcommand path.

        Examples:
            Intermixed parsing with unknown arguments:
            
            ```python
            @namespace
            class Config:
                command: str
                verbose: bool = False
            
            config, unknown = Config.parse_known_intermixed_args([
                'process', '--verbose', '--unknown', 'value', 'extra'
            ])
            # config.command == 'process'
            # config.verbose == True
            # unknown == ['--unknown', 'value', 'extra']
            ```
        """
        flattens = self._before_parse()
        namespace, unknown_args = self._parser.parse_known_intermixed_args(args)
        return (self._after_parse(namespace, flattens), unknown_args)

    def callback[R](
        self,
        func: Callable[[NS], R]
        ) -> Callable[[NS], R]:
        """
        Register a callback function to be executed after parsing the namespace.

        This method allows you to specify a function that will be called with the
        parsed namespace as an argument. The function can perform additional processing
        or validation on the namespace object after all arguments have been parsed.

        Args:
            func (`(NS) -> R`): The callback function to register.
            It should accept a single argument of type NS and return a value of type R.

        Returns:
            `(NS) -> R`: The registered callback function.

        Example:
            ```python
            @namespace
            class Config:
                input_file: str
                verbose: bool = False

            @Config.callback
            def post_process(config: Config.T):
                # Delayed import is recommended: import inside the function if needed
                if config.verbose:
                    # Verbose mode enabled. Input file: config.input_file
                    pass
                return config

            config = Config.parse_args()
            # post_process will be called automatically after parsing
            # config is now available
            ```
        """

        self._set_callback(func)
        return func
