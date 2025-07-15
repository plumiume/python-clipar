from typing import overload, Self, Unpack, Final

from .namespacewrapper import NamespaceWrapper, ArgumentParserOptions as NamespaceOptions
from .groupwrapper import (
    GroupWrapper, GroupWrapperOptions as GroupOptions,
    MutuallyExclusiveGroupWrapper, MutuallyExclusiveGroupWrapperOptions as MutuallyExclusiveGroupWrapperOptions
)

class NamespaceWithOptions:

    def __init__(
        self,
        options: NamespaceOptions
        ):
        self.options = options

    @overload
    def __call__[NS](
        self,
        namespace_type: type[NS],
        /
        ) -> NamespaceWrapper[NS]: ...
    @overload
    def __call__(
        self,
        namespace_type: None = None,
        /,
        **options: Unpack[NamespaceOptions],
        ) -> Self: ...
    def __call__[NS](
        self,
        namespace_type: type[NS] | None = None,
        /,
        **options: Unpack[NamespaceOptions]
        ):
        """
        Create a new NamespaceWrapper instance or modify options for future use.
        
        This method serves dual purposes: when called with a namespace class type,
        it returns a configured NamespaceWrapper for immediate use. When called
        without a type (or with None), it returns a new NamespaceWithOptions
        instance with updated configuration options for later application.

        Args:
            namespace_type (`type[NS] | None`): The type of the namespace class to be wrapped.
                If None, returns a new NamespaceWithOptions with updated options.

            prog (`str | None`): The name of the program (default: sys.argv[0]).
                This appears in help messages and error messages.
            
            usage (`str | None`): A usage message to display when the program is run 
                with no arguments or when help is requested.
            
            epilog (`str | None`): A message to display after the argument help.
                Useful for additional information or examples.
            
            formatter_class (`argparse._FormatterClass`): The class used to format 
                the help output. Controls how help text is displayed.
            
            prefix_chars (`str`): The set of characters that prefix optional arguments 
                (default: '-'). For example, '--option' or '+option'.
            
            fromfile_prefix_chars (`str | None`): Characters that prefix files containing 
                additional arguments (default: None). When set, allows reading arguments 
                from files.
            
            conflict_handler (`str`): The strategy for resolving conflicts between 
                argument names (default: 'error'). Can be 'error' or 'resolve'.
            
            add_help (`bool`): Whether to add a default help argument (default: True).
                When True, automatically adds -h/--help options.
            
            allow_abbrev (`bool`): Whether to allow abbreviations of long options 
                (default: True). When True, '--verb' can match '--verbose'.
            
            exit_on_error (`bool`): Whether to exit on error (default: True).
                When False, raises SystemExit instead of calling sys.exit().
            
            suggest_on_error (`bool`): Whether to suggest similar options on error 
                (default: False). Available in Python 3.14+.
            
            color (`bool`): Whether to use color in the help output (default: False).
                Available in Python 3.14+.

        Returns:
            overload1 (`NamespaceWrapper[NS]`): If namespace_type is provided,
                returns a configured NamespaceWrapper. Otherwise, returns a new
                NamespaceWithOptions with updated options.

            overload2 (`NamespaceWithOptions`): If namespace_type is None,
                returns a new NamespaceWithOptions with the combined options.

        Examples:
            Basic usage with immediate namespace creation:
            
            ```python
            from clipar import namespace
            
            @namespace
            class Config:
                verbose: bool = False
                output: str = 'output.txt'
            
            # Parse command line arguments
            config = Config.parse_args(['--verbose', '--output', 'result.txt'])
            # config.verbose == True
            # config.output == 'result.txt'
            ```

            Creating a namespace with custom options:
            
            ```python
            # Configure parser options before applying to namespace
            custom_namespace = namespace(
                prog='my-tool',
                description='A tool for processing files',
                epilog='Visit https://example.com for more info'
            )
            
            @custom_namespace
            class MyTool:
                input_file: str
                threads: int = 4
            
            tool = MyTool.parse_args(['data.txt', '--threads', '8'])
            ```

            Chaining options for reusable configurations:
            
            ```python
            import argparse
            
            # Create a base configuration
            base_config = namespace(
                formatter_class=argparse.RawDescriptionHelpFormatter,
                prefix_chars='-+'
            )
            
            # Extend with additional options
            tool_config = base_config(
                prog='advanced-tool',
                add_help=True
            )
            
            @tool_config
            class AdvancedTool:
                mode: str = 'auto'
                quiet: bool = False
            ```

            Using different prefix characters:
            
            ```python
            @namespace(prefix_chars='-+')
            class UnixStyleTool:
                verbose: bool = False  # Can use --verbose or ++verbose
                count: int = 1         # Can use --count or ++count
            ```

            Reading arguments from files:
            
            ```python
            @namespace(fromfile_prefix_chars='@')
            class FileArgsTool:
                config: str = 'default.conf'
            
            # Usage: python tool.py @args.txt
            # where args.txt contains: --config production.conf
            ```

            Custom error handling:
            
            ```python
            @namespace(
                exit_on_error=False,
                conflict_handler='resolve'
            )
            class RobustTool:
                input: str
                output: str = 'out.txt'
            
            try:
                tool = RobustTool.parse_args(['--invalid'])
            except SystemExit as e:
                # Parsing failed
                pass
            ```
        """

        new_options = self.options | options

        if namespace_type is None:
            return NamespaceWithOptions(new_options)

        return NamespaceWrapper[NS](namespace_type, new_options)

class GroupWithOptions:

    def __init__(
        self,
        options: GroupOptions
        ):
        self.options = options

    @overload
    def __call__[NS](
        self,
        namespace_type: type[NS],
        /
        ) -> GroupWrapper[NS]: ...
    @overload
    def __call__(
        self,
        namespace_type: None = None,
        /,
        **options: Unpack[GroupOptions],
        ) -> Self: ...
    def __call__[NS](
        self,
        namespace_type: type[NS] | None = None,
        /,
        **options: Unpack[GroupOptions]
        ):
        """
        Create a new GroupWrapper instance or modify options for future use.
        
        This method configures argument groups for command-line parsing. When called
        with a namespace class type, it wraps the class as an argument group with
        the specified options. When called without a type, it returns a new
        GroupWithOptions instance with updated configuration for later use.

        Args:
            namespace_type (`type[NS] | None`): The type of the namespace class to be wrapped
                as an argument group. If None, returns a new GroupWithOptions with updated options.

            title (`str | None`): The title to display for this argument group in help output.
                If None, no title is displayed for the group.
            
            description (`str | None`): A description to display for this argument group.
                Appears below the title in help output.
            
            prefix_chars (`str`): The set of characters that prefix optional arguments 
                for this group (default: '-'). Inherits from parent if not specified.
            
            conflict_handler (`str`): The strategy for resolving conflicts between 
                argument names within this group (default: 'error'). Can be 'error' or 'resolve'.

        Returns:
            overload1 (`GroupWrapper[NS]`): If namespace_type is provided,
                returns a configured GroupWrapper for immediate use. Otherwise, returns a new
                GroupWithOptions with updated options.

            overload2 (`GroupWithOptions`): If namespace_type is None,
                returns a new GroupWithOptions with the combined options.

        Examples:
            Basic argument group creation with external class definition:
            
            ```python
            from clipar import namespace, group
            
            # Define group class externally (no options)
            @group
            class DatabaseGroup:
                host: str = 'localhost'
                port: int = 5432
                username: str
                password: str
            
            @namespace
            class Config:
                # Main arguments
                input_file: str
                output_file: str = 'output.txt'
                
                # Database connection group
                database: DatabaseGroup
            
            config = Config.parse_args([
                'input.txt', 
                '--host', 'db.example.com',
                '--username', 'admin'
            ])
            # config.database.host == 'db.example.com'
            # config.database.username == 'admin'
            ```

            Using nested group classes within namespace:
            
            ```python
            @namespace
            class ServerConfig:
                # General options
                config_file: str = 'server.conf'
                debug: bool = False
                
                @group
                class Network:
                    host: str = '0.0.0.0'
                    port: int = 8080
                    timeout: float = 30.0
                
                @group
                class Security:
                    auth_token: str
                    enable_ssl: bool = False
                    cert_file: str = 'cert.pem'
                
                # Group instances
                network: Network
                security: Security
            
            config = ServerConfig.parse_args([
                '--host', '192.168.1.100',
                '--port', '9000',
                '--auth-token', 'secret123',
                '--enable-ssl'
            ])
            ```

            Creating groups with custom options:
            
            ```python
            # Define group with title and description
            @group(
                title='Database Options',
                description='Options for database connection'
            )
            class DatabaseGroup:
                host: str = 'localhost'
                port: int = 5432
                username: str
                password: str
            
            @namespace
            class Config:
                input_file: str
                database: DatabaseGroup
            ```

            Using custom options for nested groups:
            
            ```python
            @namespace
            class ServerConfig:
                config_file: str = 'server.conf'
                
                @group(
                    title='Network Settings',
                    description='Configure network-related options'
                )
                class Network:
                    host: str = '0.0.0.0'
                    port: int = 8080
                    timeout: float = 30.0
                
                @group(
                    title='Security Settings',
                    description='Configure security and authentication'
                )
                class Security:
                    auth_token: str
                    enable_ssl: bool = False
                    cert_file: str = 'cert.pem'
                
                network: Network
                security: Security
            ```

            Direct internal class assignment with group decorator:
            
            ```python
            @namespace
            class ApplicationConfig:
                # Main application settings
                app_name: str = 'MyApp'
                version: str = '1.0.0'
                
                # Internal group definition as nested classes (basic usage)
                @group
                class DatabaseSettings:
                    host: str = 'localhost'
                    port: int = 5432
                    name: str = 'myapp_db'
                    ssl_mode: bool = True
                
                @group
                class LoggingSettings:
                    level: str = 'INFO'
                    file: str = 'app.log'
                    rotate: bool = False
                
                # Group assignments
                database: DatabaseSettings
                logging: LoggingSettings
            
            config = ApplicationConfig.parse_args([
                '--host', 'prod-db.example.com',
                '--name', 'production_db',
                '--level', 'DEBUG'
            ])
            # config.database.host == 'prod-db.example.com'
            # config.logging.level == 'DEBUG'
            ```

            Creating reusable group configurations:
            
            ```python
            # Create a base group configuration
            database_group = group(
                title='Database Configuration',
                description='Settings for database connectivity',
                prefix_chars='-+'
            )
            
            # Apply to multiple classes
            @database_group
            class DatabaseConfig:
                host: str = 'localhost'
                port: int = 5432
                ssl_enabled: bool = True
                timeout: float = 10.0
            
            @namespace
            class AppConfig:
                verbose: bool = False
                log_file: str = 'app.log'
                db: DatabaseConfig
            
            @namespace 
            class TestConfig:
                test_mode: bool = True
                db: DatabaseConfig
            ```

            Multiple groups with clear type annotations:
            
            ```python
            @group
            class InputGroup:
                input_file: str
                format: str = 'json'
                encoding: str = 'utf-8'
            
            @group
            class OutputGroup:
                output_file: str = 'output.txt'
                compress: bool = False
                backup: bool = True
            
            @group
            class ProcessingGroup:
                threads: int = 4
                batch_size: int = 1000
                timeout: float = 60.0
            
            @namespace
            class DataProcessor:
                verbose: bool = False
                dry_run: bool = False
                
                input_opts: InputGroup
                output_opts: OutputGroup
                processing_opts: ProcessingGroup
            ```

            Custom conflict handling in groups:
            
            ```python
            @group(
                title='Advanced Options',
                conflict_handler='resolve'
            )
            class AdvancedGroup:
                mode: str = 'auto'
                level: int = 1
                optimize: bool = True
                
            @namespace
            class Tool:
                basic_option: str = 'default'
                config_file: str = 'config.ini'
                advanced: AdvancedGroup
                # If conflicts arise, 'resolve' strategy will handle them
            
            tool = Tool.parse_args(['--mode', 'manual', '--level', '3'])
            # tool.advanced.mode == 'manual'
            # tool.advanced.level == 3
            ```

            Chaining group options for inheritance:
            
            ```python
            # Base group with common settings
            base_group = group(
                description='Base configuration options',
                prefix_chars='-+'
            )
            
            # Extend with specific title
            logging_group = base_group(
                title='Logging Configuration'
            )
            
            @logging_group
            class LoggingConfig:
                log_level: str = 'INFO'
                log_file: str = 'app.log'
                rotate_logs: bool = True
                max_size: int = 10485760  # 10MB
            
            @namespace
            class Application:
                name: str = 'MyApp'
                version: str = '1.0.0'
                logging: LoggingConfig
            ```
        """

        new_options = self.options | options

        if namespace_type is None:
            return GroupWithOptions(new_options)

        return GroupWrapper[NS](namespace_type, new_options)

class MutuallyExclusiveGroupWithOptions:

    def __init__(
        self,
        options: MutuallyExclusiveGroupWrapperOptions
        ):
        self.options = options

    @overload
    def __call__[NS](
        self,
        namespace_type: type[NS],
        /
        ) -> MutuallyExclusiveGroupWrapper[NS]: ...
    @overload
    def __call__(
        self,
        namespace_type: None = None,
        /,
        **options: Unpack[MutuallyExclusiveGroupWrapperOptions],
        ) -> Self: ...
    def __call__[NS](
        self,
        namespace_type: type[NS] | None = None,
        /,
        **options: Unpack[MutuallyExclusiveGroupWrapperOptions]
        ):
        """
        Create a new MutuallyExclusiveGroupWrapper instance or modify options for future use.
        
        This method configures mutually exclusive argument groups for command-line parsing.
        Mutually exclusive groups ensure that only one argument from the group can be
        specified at a time. When called with a namespace class type, it wraps the class
        as a mutually exclusive argument group. When called without a type, it returns
        a new MutuallyExclusiveGroupWithOptions instance with updated configuration.

        Args:
            namespace_type (`type[NS] | None`): The type of the namespace class to be wrapped
                as a mutually exclusive argument group. If None, returns a new 
                MutuallyExclusiveGroupWithOptions with updated options.

            required (`bool`): Whether at least one argument from this mutually exclusive
                group must be specified (default: False). When True, the parser will
                fail if none of the group's arguments are provided.

        Returns:
            overload1 (`MutuallyExclusiveGroupWrapper[NS]`): If namespace_type is provided,
                returns a configured MutuallyExclusiveGroupWrapper for immediate use.

            overload2 (`MutuallyExclusiveGroupWithOptions`): If namespace_type is None,
                returns a new MutuallyExclusiveGroupWithOptions with updated options.

        Examples:
            Basic mutually exclusive group creation:
            
            ```python
            from clipar import namespace, mutually_exclusive_group
            
            @mutually_exclusive_group
            class OutputModeGroup:
                verbose: bool = False
                quiet: bool = False
                silent: bool = False
            
            @namespace
            class Config:
                input_file: str
                output_mode: OutputModeGroup
            
            # Valid usage (only one option from the group)
            config = Config.parse_args(['input.txt', '--verbose'])
            # config.output_mode.verbose == True
            # config.output_mode.quiet == False
            
            # Invalid usage (multiple options from the group would cause an error)
            # Config.parse_args(['input.txt', '--verbose', '--quiet'])  # Error!
            ```

            Required mutually exclusive group:
            
            ```python
            @mutually_exclusive_group(required=True)
            class ActionGroup:
                create: bool = False
                update: bool = False
                delete: bool = False
            
            @namespace
            class DatabaseTool:
                database_url: str
                action: ActionGroup
            
            # Valid usage (one action is required)
            tool = DatabaseTool.parse_args(['--database-url', 'db://localhost', '--create'])
            # tool.action.create == True
            
            # Invalid usage (no action specified would cause an error)
            # DatabaseTool.parse_args(['--database-url', 'db://localhost'])  # Error!
            ```

            Output format selection:
            
            ```python
            @mutually_exclusive_group
            class FormatGroup:
                json_output: bool = False
                xml_output: bool = False
                csv_output: bool = False
                yaml_output: bool = False
            
            @namespace
            class DataConverter:
                input_file: str
                output_file: str = 'output.txt'
                format_options: FormatGroup
            
            converter = DataConverter.parse_args([
                'data.txt',
                '--output-file', 'result.json',
                '--json-output'
            ])
            # converter.format_options.json_output == True
            # All other format options remain False
            ```

            Logging level selection with requirement:
            
            ```python
            @mutually_exclusive_group(required=True)
            class LogLevelGroup:
                debug: bool = False
                info: bool = False
                warning: bool = False
                error: bool = False
            
            @namespace
            class Logger:
                log_file: str = 'app.log'
                log_level: LogLevelGroup
            
            logger = Logger.parse_args(['--log-file', 'debug.log', '--debug'])
            # logger.log_level.debug == True
            # One log level must always be specified
            ```

            Processing mode selection:
            
            ```python
            @mutually_exclusive_group
            class ProcessingModeGroup:
                batch_mode: bool = False
                interactive_mode: bool = False
                daemon_mode: bool = False
            
            @namespace
            class ProcessingTool:
                config_file: str = 'config.ini'
                max_workers: int = 4
                mode: ProcessingModeGroup
            
            tool = ProcessingTool.parse_args([
                '--config-file', 'prod.ini',
                '--max-workers', '8',
                '--batch-mode'
            ])
            # tool.mode.batch_mode == True
            # Other modes remain False
            ```

            Chaining options for reusable configurations:
            
            ```python
            # Create a base configuration
            base_exclusive = mutually_exclusive_group()
            
            # Create a required version
            required_exclusive = base_exclusive(required=True)
            
            @required_exclusive
            class DatabaseActionGroup:
                backup: bool = False
                restore: bool = False
                migrate: bool = False
                reset: bool = False
            
            @namespace
            class DatabaseManager:
                connection_string: str
                timeout: int = 30
                action: DatabaseActionGroup
            
            # One action is required
            manager = DatabaseManager.parse_args([
                '--connection-string', 'db://localhost',
                '--backup'
            ])
            # manager.action.backup == True
            ```

            Complex application with multiple exclusive groups:
            
            ```python
            @mutually_exclusive_group(required=True)
            class OperationGroup:
                encode: bool = False
                decode: bool = False
                validate: bool = False
            
            @mutually_exclusive_group
            class FormatGroup:
                base64: bool = False
                hex: bool = False
                binary: bool = False
            
            @mutually_exclusive_group
            class OutputGroup:
                stdout: bool = False
                file_output: bool = False
                clipboard: bool = False
            
            @namespace
            class Encoder:
                input_data: str
                operation: OperationGroup      # Required: must choose one
                format_opts: FormatGroup       # Optional: can choose one or none
                output_opts: OutputGroup       # Optional: can choose one or none
            
            encoder = Encoder.parse_args([
                'mydata',
                '--encode',        # Required operation
                '--base64',        # Optional format
                '--file-output'    # Optional output method
            ])
            # encoder.operation.encode == True
            # encoder.format_opts.base64 == True
            # encoder.output_opts.file_output == True
            ```

            Verbose/quiet mutually exclusive pattern:
            
            ```python
            @mutually_exclusive_group
            class VerbosityGroup:
                verbose: bool = False
                quiet: bool = False
            
            @namespace
            class Tool:
                input_file: str
                output_file: str = 'output.txt'
                verbosity: VerbosityGroup
            
            # Can be verbose
            tool1 = Tool.parse_args(['input.txt', '--verbose'])
            # tool1.verbosity.verbose == True
            
            # Can be quiet
            tool2 = Tool.parse_args(['input.txt', '--quiet'])
            # tool2.verbosity.quiet == True
            
            # Cannot be both (would cause error)
            # Tool.parse_args(['input.txt', '--verbose', '--quiet'])  # Error!
            ```

            Nested mutually exclusive groups within namespace:
            
            ```python
            @namespace
            class ServerConfig:
                port: int = 8080
                host: str = 'localhost'
                
                @mutually_exclusive_group(required=True)
                class AuthMethod:
                    token_auth: bool = False
                    password_auth: bool = False
                    certificate_auth: bool = False
                
                @mutually_exclusive_group
                class LogDestination:
                    log_to_file: bool = False
                    log_to_stdout: bool = False
                    log_to_syslog: bool = False
                
                auth: AuthMethod
                logging: LogDestination
            
            config = ServerConfig.parse_args([
                '--port', '9090',
                '--token-auth',      # Required auth method
                '--log-to-file'      # Optional log destination
            ])
            # config.auth.token_auth == True
            # config.logging.log_to_file == True
            ```
        """

        new_options = self.options | options

        if namespace_type is None:
            return MutuallyExclusiveGroupWithOptions(new_options)

        return MutuallyExclusiveGroupWrapper[NS](namespace_type, new_options)

namespace: Final = NamespaceWithOptions({}).__call__
group: Final = GroupWithOptions({}).__call__
mutually_exclusive_group: Final = MutuallyExclusiveGroupWithOptions({}).__call__()
