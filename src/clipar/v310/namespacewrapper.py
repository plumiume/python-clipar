import sys
from typing import (
    Callable, TypeVar, Union, Type, Generic,
    TypedDict,
)
from itertools import chain 
import argparse
import argcomplete
from .basewrapper import BaseWrapper, SubparserWrapper, BoundWrapper

if sys.version_info >= (3, 14):
    class ArgumentParserOptions(TypedDict, total=False):
        prog: Union[str, None]
        "The name of the program (default: sys.argv[0])"
        usage: Union[str, None]
        "A usage message to display when the program is run with no arguments."
        # description: Union[str, None]
        # "A description of the program to display before the argument help."
        # use namespace_type.__doc__
        epilog: Union[str, None]
        "A message to display after the argument help."
        # parents: Sequence[argparse.ArgumentParser]
        # "A list of ArgumentParser objects whose arguments should be added to this parser."
        # not used
        formatter_class: argparse._FormatterClass
        "The class used to format the help output."
        prefix_chars: str
        "The set of characters that prefix optional arguments (default: '-')"
        fromfile_prefix_chars: Union[str, None]
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
        suggest_on_error: bool
        "Whether to suggest similar options on error (default: False)"
        color: bool
        "Whether to use color in the help output (default: False)"

else:
    class ArgumentParserOptions(TypedDict, total=False):
        prog: Union[str, None]
        "The name of the program (default: sys.argv[0])"
        usage: Union[str, None]
        "A usage message to display when the program is run with no arguments."
        # description: Union[str, None]
        # "A description of the program to display before the argument help."
        # use namespace_type.__doc__
        epilog: Union[str, None]
        "A message to display after the argument help."
        # parents: Sequence[argparse.ArgumentParser]
        # "A list of ArgumentParser objects whose arguments should be added to this parser."
        # not used
        formatter_class: Type[argparse.HelpFormatter]
        "The class used to format the help output."
        prefix_chars: str
        "The set of characters that prefix optional arguments (default: '-')"
        fromfile_prefix_chars: Union[str, None]
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

NS = TypeVar('NS')

class NamespaceWrapper(SubparserWrapper[NS]):

    def __init__(
        self,
        namespace_type: Type[NS],
        parser_options: ArgumentParserOptions = {}
        ):

        self._parser = argparse.ArgumentParser(**parser_options)
        super().__init__(namespace_type)

    def configure_container(self) -> argparse.ArgumentParser:
        return self._parser

    def _before_parse(self):

        self.on_before_parse([], None)

        flatten_subparsers = self._flatten_subparsers()

        for bound_names, bound_wrapper in flatten_subparsers:
            bound_wrapper.self.on_before_parse(bound_names, bound_wrapper)

            flatten_subgroups = bound_wrapper.self._flatten_subgroups()

            for subgroup_names, subgroup_wrapper in flatten_subgroups:
                new_names = bound_names + subgroup_names
                subgroup_wrapper.self.on_before_parse(new_names, subgroup_wrapper)

        flatten_subgroups = self._flatten_subgroups()
        for subgroup_names, subgroup_wrapper in flatten_subgroups:
            subgroup_wrapper.self.on_before_parse(subgroup_names, subgroup_wrapper)

        argcomplete.autocomplete(self._parser)

        return flatten_subparsers

    def _after_parse(
        self,
        current_namespace: object,
        flatten_subparsers: list[tuple[list[str], BoundWrapper]],
        ) -> NS:

        leaf_wrapper: SubparserWrapper = self._parser.get_default('_clipar_wrapper')

        if leaf_wrapper is self:
            bound_names = []
            wrapper = self

        else:
            bound = None
            for bound in flatten_subparsers:
                if bound[1]._self is leaf_wrapper:
                    break

            if bound is None:
                raise ValueError(
                    f"Leaf wrapper not found in the flattened subparsers."
                    f" ( flatten_subparsers: {flatten_subparsers} )"
                )

            bound_names = bound[0]
            wrapper = bound[1].self

        self._set_subgroup_namespace(
            wrapper._subgroups,
            current_namespace,
            bound_names,
        )

        self._set_subparser_namespace(
            flatten_subparsers,
            current_namespace,
            bound_names,
        )

        leaf_wrapper._exec_callback(current_namespace)

        return self._set_current_namespace(current_namespace)

    def _set_subgroup_namespace(
        self,
        subgroups: dict[str, BoundWrapper],
        source_namespace: object,
        names: list[str],
        target_namespace: Union[object, None] = None,
        ):

        if target_namespace is None:
            target_namespace = source_namespace

        for bound_name, bound_wrapper in subgroups.items():
            child_wrapper = bound_wrapper.self
            child_namespace = child_wrapper.namespace_type()
            setattr(target_namespace, bound_name, child_namespace)

            new_names = names + [bound_name]

            self._set_subgroup_namespace(
                child_wrapper._subgroups,
                source_namespace,
                names=new_names,
                target_namespace=child_namespace,
            )

            for attr_name in child_wrapper._arg_names:
                if hasattr(source_namespace, attr_name):
                    attr_value = getattr(source_namespace, attr_name)
                    delattr(source_namespace, attr_name)
                    setattr(child_namespace, attr_name, attr_value)

            bound_wrapper.self.on_after_parse(new_names, bound_wrapper)


    def _set_subparser_namespace(
        self,
        flatten_subparsers: list[tuple[list[str], BoundWrapper]],
        current_namespace: object,
        names: list[str],
        ):

        # [----bind_by----]
        # [leaf, ..., root]
        #       [..., root]
        #            [root]
        # begin = bound[0].length to -1
        for begin in range(-len(names), 0):
            for bound_names, bound_wrapper in flatten_subparsers:

                if bound_names == names[begin:]:

                    parent_namespace = bound_wrapper.self.namespace_type()
                    setattr(parent_namespace, bound_wrapper._bound_name, current_namespace)
                    current_namespace = parent_namespace

                    bound_wrapper.self.on_after_parse(bound_names, bound_wrapper)

                    break

    def _set_current_namespace(
        self,
        current_namespace: object
        ) -> NS:

        result_namespace = self.namespace_type()
        for attr_name in chain(self._arg_names, self._subgroups):
            attr_value = getattr(current_namespace, attr_name)
            delattr(current_namespace, attr_name)
            setattr(result_namespace, attr_name, attr_value)

        return result_namespace


    def parse_args(self, args: Union[list[str], None] = None) -> NS:
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

    def parse_known_args(self, args: Union[list[str], None] = None) -> tuple[NS, list[str]]:
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

    def parse_intermixed_args(self, args: Union[list[str], None] = None) -> NS:
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


    def parse_known_intermixed_args(self, args: Union[list[str], None] = None) -> tuple[NS, list[str]]:
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

    R = TypeVar('R')
    
    def callback(
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
