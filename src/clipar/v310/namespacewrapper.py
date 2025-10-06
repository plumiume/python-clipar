from typing import (
    Any,
    Sequence,
    Callable,
    TypedDict,
    TypeVar
)
from argparse import (
    _SubParsersAction, # pyright: ignore[reportPrivateUsage]
)
import argparse
import argcomplete
from .basewrapper import BaseWrapper, SubparserWrapper, SubgroupWrapper, BoundWrapper

_NS = TypeVar('_NS')
_R = TypeVar('_R')

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

class NamespaceWrapper(SubparserWrapper[_NS]):

    def __init__(
        self,
        namespace_type: type[_NS],
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

    def _before_parse(self):

        self.on_before_parse([], None)

        flatten_subparsers = self._flatten_subparsers()

        for bound_names, bound_wrapper in flatten_subparsers:
            bound_wrapper.self.on_before_parse(bound_names, bound_wrapper)

            flatten_subgroups = bound_wrapper.self._flatten_subgroups()

            for subgroup_names, subgroup_wrapper in flatten_subgroups:
                new_names = subgroup_names + bound_names
                subgroup_wrapper.self.on_before_parse(new_names, subgroup_wrapper)

        flatten_subgroups = self._flatten_subgroups()
        for subgroup_names, subgroup_wrapper in flatten_subgroups:
            subgroup_wrapper.self.on_before_parse(subgroup_names, subgroup_wrapper)

        argcomplete.autocomplete(self._parser)

        return flatten_subparsers

    def _after_parse(
        self,
        argparse_namespace: argparse.Namespace,
        flatten_subparsers: list[tuple[list[str], BoundWrapper[Any]]],
        ) -> _NS:

        leaf_wrapper: SubparserWrapper[Any] = getattr(argparse_namespace, '_clipar_wrapper')
        leaf_name: str | None = getattr(argparse_namespace, '_clipar_leaf_name', None)

        bound_names = []

        if self is not leaf_wrapper:
            
            for bound_names, bound_wrapper in flatten_subparsers:
                if (
                    bound_names
                    and bound_names[0] == leaf_name
                    and bound_wrapper.self is leaf_wrapper
                    ):
                    break

            if not bound_names:
                raise ValueError(
                    f"Leaf wrapper not found in the flattened subparsers."
                    f" ( flatten_subparsers: {flatten_subparsers} )"
                )

        leaf_namespace = leaf_wrapper.namespace_type()

        self._set_subgroup_namespace(
            leaf_wrapper._subgroups,
            argparse_namespace,
            leaf_namespace,
            bound_names,
        )

        self._set_args(
            leaf_wrapper,
            argparse_namespace,
            leaf_namespace,
        )

        result_namespace = self._set_subparser_namespace(
            flatten_subparsers,
            argparse_namespace,
            leaf_namespace,
            bound_names,
        )

        leaf_wrapper._exec_callback(leaf_namespace)

        return result_namespace

    def _set_args(
        self,
        wrapper: BaseWrapper[Any],
        argparse_namespace: argparse.Namespace,
        target_namespace: object,
        ):

        for attr_name in wrapper._arg_names:
            attr_value = getattr(argparse_namespace, attr_name)
            setattr(target_namespace, attr_name, attr_value)

    def _set_subgroup_namespace(
        self,
        subgroups: 'dict[str, BoundWrapper[Any]]',
        argparse_namespace: argparse.Namespace,
        target_namespace: object,
        names: list[str],
        ):

        for bound_name, bound_wrapper in subgroups.items():
            child_wrapper = bound_wrapper.self
            child_namespace = child_wrapper.namespace_type()
            setattr(target_namespace, bound_name, child_namespace)

            new_names = names + [bound_name]

            self._set_subgroup_namespace(
                child_wrapper._subgroups,
                argparse_namespace,
                names=new_names,
                target_namespace=child_namespace,
            )

            self._set_args(
                child_wrapper,
                argparse_namespace,
                child_namespace,
            )

            bound_wrapper.self.on_after_parse(new_names, bound_wrapper)

    def _set_subparser_namespace(
        self,
        flatten_subparsers: list[tuple[list[str], BoundWrapper[SubparserWrapper[Any]]]],
        argparse_namespace: argparse.Namespace,
        leaf_namespace: object,
        names: list[str],
        ) -> _NS:

        # [----bind_by----]
        # [leaf, ..., root]
        #       [..., root]
        #            [root]
        # begin = -bound[0].length to -1

        current_namespace = leaf_namespace

        for begin in range(-len(names), 0):

            for bound_names, bound_wrapper in flatten_subparsers:

                if bound_names == names[begin:]:

                    parent_namespace = bound_wrapper.parent.namespace_type()

                    setattr(parent_namespace, bound_wrapper.bound_name, current_namespace)
                    self._set_args(
                        bound_wrapper.parent,
                        argparse_namespace,
                        parent_namespace,
                    )

                    bound_wrapper.self.on_after_parse(bound_names, bound_wrapper)
                    current_namespace = parent_namespace

        if isinstance(current_namespace, self.namespace_type):
            return current_namespace

        raise ValueError(
            f"Current namespace {current_namespace} is not an instance of the expected "
            f"namespace type {self.namespace_type}."
        )


    def parse_args(self, args: list[str] | None = None) -> _NS:
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
        flatten_subparsers = self._before_parse()
        namespace = self._parser.parse_args(args)
        return self._after_parse(namespace, flatten_subparsers)

    def parse_known_args(self, args: list[str] | None = None) -> tuple[_NS, list[str]]:
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
        flatten_subparsers = self._before_parse()
        namespace, unknown_args = self._parser.parse_known_args(args)
        return (
            self._after_parse(namespace, flatten_subparsers),
            unknown_args
        )

    def parse_intermixed_args(self, args: list[str] | None = None) -> _NS:
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
        flatten_subparsers = self._before_parse()
        namespace = self._parser.parse_intermixed_args(args)
        return self._after_parse(namespace, flatten_subparsers)


    def parse_known_intermixed_args(self, args: list[str] | None = None) -> tuple[_NS, list[str]]:
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
        flatten_subparsers = self._before_parse()
        namespace, unknown_args = self._parser.parse_known_intermixed_args(args)
        return (
            self._after_parse(namespace, flatten_subparsers),
            unknown_args
        )

    def callback(
        self,
        func: Callable[[_NS], _R]
        ) -> Callable[[_NS], _R]:
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