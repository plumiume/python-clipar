"""
Test suite for clipar - a Python CLI argument parsing library.

This module contains comprehensive tests for the clipar library,
covering namespace decorators, group functionality, type parsing,
and various argument configurations.
"""
import pytest
from typing import Literal

# Import clipar components
from clipar import namespace, group, NotSelected
from clipar.namespacewrapper import NamespaceWrapper
from clipar.groupwrapper import GroupWrapper


def test_basic_namespace():
    """Test basic namespace functionality and argument parsing."""
    
    @namespace
    class BasicConfig:
        input_file: str
        verbose: bool = False
        count: int = 1
    
    assert hasattr(BasicConfig, 'parse_args'), "parse_args method should exist"
    assert isinstance(BasicConfig, NamespaceWrapper), "Should be NamespaceWrapper instance"
    
    # Test required positional argument
    @namespace
    class Config:
        filename: str
    
    parsed = Config.parse_args(['test.txt'])
    assert parsed.filename == 'test.txt', f"Filename should be parsed correctly but got {parsed.filename}"

    # Test optional arguments with defaults
    @namespace
    class ConfigWithDefaults:
        verbose: bool = False
        count: int = 5
        name: str = 'default'
    
    # Test defaults
    parsed = ConfigWithDefaults.parse_args([])
    assert parsed.verbose is False, f"Default verbose should be False but got {parsed.verbose}"
    assert parsed.count == 5, f"Default count should be 5 but got {parsed.count}"
    assert parsed.name == 'default', f"Default name should be 'default' but got {parsed.name}"

    # Test overriding defaults
    parsed = ConfigWithDefaults.parse_args(['--verbose', '--count', '10', '--name', 'custom'])
    assert parsed.verbose is True, f"Verbose should be True when set but got {parsed.verbose}"
    assert parsed.count == 10, f"Count should be 10 when set but got {parsed.count}"
    assert parsed.name == 'custom', f"Name should be 'custom' when set but got {parsed.name}"


def test_type_annotations():
    """Test various type annotations and their parsing behavior."""
    
    # Test Literal types
    @namespace
    class ConfigWithLiterals:
        mode: Literal['auto', 'manual', 'batch'] = 'auto'
        level: Literal[1, 2, 3] = 1
    
    parsed = ConfigWithLiterals.parse_args(['--mode', 'manual', '--level', '3'])
    assert parsed.mode == 'manual', f"Mode should be 'manual' but got {parsed.mode}"
    assert parsed.level == 3, f"Level should be 3 but got {parsed.level}"

    # Test list types
    @namespace
    class ConfigWithLists:
        files: list[str] = []
        numbers: list[int] = []
    
    parsed = ConfigWithLists.parse_args([
        '--files', 'file1.txt', 'file2.txt', 'file3.txt',
        '--numbers', '1', '2', '3'
    ])
    assert parsed.files == ['file1.txt', 'file2.txt', 'file3.txt'], f"Files list should match but got {parsed.files}"
    assert parsed.numbers == [1, 2, 3], f"Numbers list should match but got {parsed.numbers}"

    # Test numeric types
    @namespace
    class ConfigWithNumbers:
        count: int = 0
        rate: float = 1.0
        port: int
    
    parsed = ConfigWithNumbers.parse_args(['8080', '--count', '42', '--rate', '2.5'])
    assert parsed.port == 8080, f"Port should be 8080 but got {parsed.port}"
    assert parsed.count == 42, f"Count should be 42 but got {parsed.count}"
    assert parsed.rate == 2.5, f"Rate should be 2.5 but got {parsed.rate}"


def test_groups():
    """Test group functionality and nested argument organization."""
    
    # Test basic group creation
    @group
    class DatabaseGroup:
        host: str = 'localhost'
        port: int = 5432
        username: str
    
    # Use type annotation instead of direct class reference
    @namespace
    class Config:
        verbose: bool = False
        database = DatabaseGroup
    
    parsed = Config.parse_args([
        '--verbose',
        '--host', 'db.example.com',
        '--port', '3306',
        '--username', 'admin'
    ])
    
    assert parsed.verbose is True, f"Verbose should be True but got {parsed.verbose}"
    assert parsed.database is not NotSelected
    assert parsed.database.host == 'db.example.com', f"Database host should match but got {parsed.database.host}"
    assert parsed.database.port == 3306, f"Database port should match but got {parsed.database.port}"
    assert parsed.database.username == 'admin', f"Database username should match but got {parsed.database.username}"


def test_parsing_methods():
    """Test different parsing methods and their behaviors."""
    
    @namespace
    class Config:
        name: str
        verbose: bool = False
    
    # Test parse_args method
    parsed = Config.parse_args(['test', '--verbose'])
    assert parsed.name == 'test', f"Name should be 'test' but got {parsed.name}"
    assert parsed.verbose is True, f"Verbose should be True but got {parsed.verbose}"

    # Test parse_known_args method
    parsed, unknown = Config.parse_known_args([
        'test', '--verbose', '--unknown-flag', 'extra', 'args'
    ])

    assert parsed.name == 'test', f"Name should be 'test' but got {parsed.name}"
    assert parsed.verbose is True, f"Verbose should be True but got {parsed.verbose}"
    assert unknown == ['--unknown-flag', 'extra', 'args'], f"Unknown args should match but got {unknown}"


def test_namespace_options():
    """Test namespace configuration options."""
    
    @namespace(
        prog='test-program',
        epilog='This is a test program.'
    )
    class Config:
        input_file: str
        verbose: bool = False
    
    assert isinstance(Config, NamespaceWrapper), "Should be NamespaceWrapper with options"
    
    # Test namespace options chaining
    base_config = namespace(
        prog='base-program',
        add_help=True
    )
    
    extended_config = base_config(
        epilog='Extended configuration'
    )
    
    @extended_config
    class ConfigChained:
        name: str
        debug: bool = False
    
    assert isinstance(ConfigChained, NamespaceWrapper), "Chained config should work"


def test_callback_functionality():
    """Test callback registration and execution."""
    
    @namespace
    class Config:
        name: str
        verbose: bool = False
    
    callback_called = False
    
    @Config.callback
    def process_config(config):
        nonlocal callback_called
        callback_called = True
        return config
    
    parsed = Config.parse_args(['test'])
    assert callback_called, "Callback should be called"
    assert parsed.name == 'test', f"Name should be 'test' but got {parsed.name}"


def test_not_selected_behavior():
    """Test NotSelected behavior for unselected subcommands."""
    
    # Test that parse methods mention NotSelected behavior in docstrings
    @namespace
    class Config:
        name: str
    
    # Check that docstrings mention NotSelected behavior
    if Config.parse_args.__doc__:
        assert 'NotSelected' in Config.parse_args.__doc__, "parse_args should mention NotSelected"
    if Config.parse_known_args.__doc__:
        assert 'NotSelected' in Config.parse_known_args.__doc__, "parse_known_args should mention NotSelected"


def test_edge_cases():
    """Test edge cases and error conditions."""
    
    # Test empty namespace
    @namespace
    class EmptyConfig:
        pass
    
    parsed = EmptyConfig.parse_args([])
    assert parsed is not None, "Empty config should parse successfully"
    
    # Test only optional arguments
    @namespace
    class OptionalOnlyConfig:
        verbose: bool = False
        debug: bool = False
        level: int = 1
    
    parsed = OptionalOnlyConfig.parse_args([])
    assert parsed.verbose is False, f"Default verbose should be False but got {parsed.verbose}"
    assert parsed.debug is False, f"Default debug should be False but got {parsed.debug}"
    assert parsed.level == 1, f"Default level should be 1 but got {parsed.level}"

    # Test underscore to dash conversion
    @namespace
    class UnderscoreConfig:
        input_file: str = 'default.txt'
        output_dir: str = '/tmp'
    
    parsed = UnderscoreConfig.parse_args(['--input-file', 'test.txt', '--output-dir', '/home'])
    assert parsed.input_file == 'test.txt', f"Input file should be set via dashed argument but got {parsed.input_file}"
    assert parsed.output_dir == '/home', f"Output dir should be set via dashed argument but got {parsed.output_dir}"


def test_docstrings():
    """Test that docstrings are properly formatted and contain required information."""
    
    @namespace
    class Config:
        name: str
    
    # Check that all parse methods have docstrings
    assert Config.parse_args.__doc__ is not None, "parse_args should have docstring"
    assert Config.parse_known_args.__doc__ is not None, "parse_known_args should have docstring"
    assert Config.callback.__doc__ is not None, "callback should have docstring"
    
    # Check docstring contains proper sections
    if Config.parse_args.__doc__:
        parse_args_doc = Config.parse_args.__doc__
        assert 'Args:' in parse_args_doc, "Docstring should contain Args section"
        assert 'Returns:' in parse_args_doc, "Docstring should contain Returns section"
        assert 'Examples:' in parse_args_doc, "Docstring should contain Examples section"
        assert 'Note:' in parse_args_doc, "Docstring should contain Note section"


def test_error_handling():
    """Test error handling and validation."""
    
    # Test missing required argument error
    @namespace(exit_on_error=False)
    class ConfigWithRequired:
        required_file: str
    
    with pytest.raises(SystemExit):
        ConfigWithRequired.parse_args([])


def test_real_world_scenarios():
    """Test realistic usage scenarios."""
    
    # Test file processing tool
    @group
    class InputOptions:
        input_file: str
        encoding: str = 'utf-8'
        format: Literal['json', 'csv', 'xml'] = 'json'
    
    @group
    class OutputOptions:
        output_file: str = 'output.txt'
        compress: bool = False
        backup: bool = True
    
    @namespace
    class FileProcessor:
        verbose: bool = False
        dry_run: bool = False
        threads: int = 4
        
        # Use .T to get the actual type
        input_opts = InputOptions
        output_opts = OutputOptions

    parsed = FileProcessor.parse_args([
        '--verbose',
        '--threads', '8',
        '--input-file', 'data.json',
        '--format', 'csv',
        '--output-file', 'result.csv',
        '--compress'
    ])
    
    assert parsed.verbose is True, "Verbose should be True"
    assert parsed.threads == 8, "Threads should be 8"
    assert parsed.input_opts is not NotSelected, "Input options should not be NotSelected"
    assert parsed.input_opts.input_file == 'data.json', "Input file should match"
    assert parsed.input_opts.format == 'csv', "Format should be csv"
    assert parsed.output_opts is not NotSelected, "Output options should not be NotSelected"
    assert parsed.output_opts.output_file == 'result.csv', "Output file should match"
    assert parsed.output_opts.compress is True, "Compress should be True"


