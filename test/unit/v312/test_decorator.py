"""Unit tests for clipar.v312.decorator module"""

from clipar.v312.decorator import (
    NamespaceWithOptions, GroupWithOptions, MutuallyExclusiveGroupWithOptions,
    namespace, group, mutually_exclusive_group
)
from clipar.v312.namespacewrapper import NamespaceWrapper, ArgumentParserOptions
from clipar.v312.groupwrapper import (
    GroupWrapper, MutuallyExclusiveGroupWrapper, 
    GroupWrapperOptions, MutuallyExclusiveGroupWrapperOptions
)


class TestNamespaceWithOptions:
    """Test NamespaceWithOptions class functionality"""

    def test_init(self):
        """Test initialization of NamespaceWithOptions"""
        options: ArgumentParserOptions = {"prog": "test_prog", "add_help": False}
        namespace_options = NamespaceWithOptions(options)
        assert namespace_options.options == options

    def test_call_with_namespace_type(self):
        """Test calling with a namespace type returns NamespaceWrapper"""
        class TestNamespace:
            pass

        options: ArgumentParserOptions = {"prog": "test_prog"}
        namespace_options = NamespaceWithOptions(options)
        
        result = namespace_options(TestNamespace)
        assert isinstance(result, NamespaceWrapper)
        assert result.namespace_type == TestNamespace

    def test_call_without_namespace_type(self):
        """Test calling without namespace type returns new NamespaceWithOptions"""
        options: ArgumentParserOptions = {"prog": "test_prog"}
        namespace_options = NamespaceWithOptions(options)
        
        result = namespace_options(add_help=False)
        
        assert isinstance(result, NamespaceWithOptions)
        expected_options = options.copy()
        expected_options["add_help"] = False
        assert result.options == expected_options

    def test_call_with_none_namespace_type(self):
        """Test calling with None namespace type returns new NamespaceWithOptions"""
        options: ArgumentParserOptions = {"prog": "test_prog"}
        namespace_options = NamespaceWithOptions(options)
        
        result = namespace_options(None, add_help=False)
        
        assert isinstance(result, NamespaceWithOptions)
        expected_options = options.copy()
        expected_options["add_help"] = False
        assert result.options == expected_options

    def test_call_overloads(self):
        """Test that both overloads work correctly"""
        class TestNamespace:
            arg1: str
            arg2: int = 10

        options: ArgumentParserOptions = {"prog": "test_prog"}
        namespace_options = NamespaceWithOptions(options)
        
        # Test first overload (with namespace type)
        wrapper = namespace_options(TestNamespace)
        assert isinstance(wrapper, NamespaceWrapper)
        
        # Test second overload (without namespace type)
        new_options_obj = namespace_options(add_help=False)
        assert isinstance(new_options_obj, NamespaceWithOptions)

    def test_empty_options(self):
        """Test with empty options dictionary"""
        options: ArgumentParserOptions = {}
        namespace_options = NamespaceWithOptions(options)
        assert namespace_options.options == {}

    def test_options_merging(self):
        """Test that options are properly merged"""
        initial_options: ArgumentParserOptions = {"prog": "test", "add_help": True}
        namespace_options = NamespaceWithOptions(initial_options)
        
        result = namespace_options(epilog="Test epilog", add_help=False)
        
        expected: ArgumentParserOptions = {"prog": "test", "add_help": False, "epilog": "Test epilog"}
        assert result.options == expected


class TestGroupWithOptions:
    """Test GroupWithOptions class functionality"""

    def test_init(self):
        """Test initialization of GroupWithOptions"""
        options: GroupWrapperOptions = {"title": "test_group", "description": "Test description"}
        group_options = GroupWithOptions(options)
        assert group_options.options == options

    def test_call_with_namespace_type(self):
        """Test calling with a namespace type returns GroupWrapper"""
        class TestGroup:
            pass

        options: GroupWrapperOptions = {"title": "test_group"}
        group_options = GroupWithOptions(options)
        
        result = group_options(TestGroup)
        assert isinstance(result, GroupWrapper)
        assert result.namespace_type == TestGroup

    def test_call_without_namespace_type(self):
        """Test calling without namespace type returns new GroupWithOptions"""
        options: GroupWrapperOptions = {"title": "test_group"}
        group_options = GroupWithOptions(options)
        
        result = group_options(description="New description")
        
        assert isinstance(result, GroupWithOptions)
        expected_options = options.copy()
        expected_options["description"] = "New description"
        assert result.options == expected_options

    def test_call_with_none_namespace_type(self):
        """Test calling with None namespace type returns new GroupWithOptions"""
        options: GroupWrapperOptions = {"title": "test_group"}
        group_options = GroupWithOptions(options)
        
        result = group_options(None, description="New description")
        
        assert isinstance(result, GroupWithOptions)
        expected_options = options.copy()
        expected_options["description"] = "New description"
        assert result.options == expected_options

    def test_empty_options(self):
        """Test with empty options dictionary"""
        options: GroupWrapperOptions = {}
        group_options = GroupWithOptions(options)
        assert group_options.options == {}

    def test_options_merging(self):
        """Test that options are properly merged"""
        initial_options: GroupWrapperOptions = {"title": "group1"}
        group_options = GroupWithOptions(initial_options)
        
        result = group_options(description="Test description")
        
        expected: GroupWrapperOptions = {"title": "group1", "description": "Test description"}
        assert result.options == expected


class TestMutuallyExclusiveGroupWithOptions:
    """Test MutuallyExclusiveGroupWithOptions class functionality"""

    def test_init(self):
        """Test initialization of MutuallyExclusiveGroupWithOptions"""
        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        meg_options = MutuallyExclusiveGroupWithOptions(options)
        assert meg_options.options == options

    def test_call_with_namespace_type(self):
        """Test calling with a namespace type returns MutuallyExclusiveGroupWrapper"""
        class TestGroup:
            pass

        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        meg_options = MutuallyExclusiveGroupWithOptions(options)
        
        result = meg_options(TestGroup)
        assert isinstance(result, MutuallyExclusiveGroupWrapper)
        assert result.namespace_type == TestGroup

    def test_call_without_namespace_type(self):
        """Test calling without namespace type returns new MutuallyExclusiveGroupWithOptions"""
        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        meg_options = MutuallyExclusiveGroupWithOptions(options)
        
        result = meg_options(required=False)
        
        assert isinstance(result, MutuallyExclusiveGroupWithOptions)
        expected_options = options.copy()
        expected_options["required"] = False
        assert result.options == expected_options

    def test_call_with_none_namespace_type(self):
        """Test calling with None namespace type returns new MutuallyExclusiveGroupWithOptions"""
        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        meg_options = MutuallyExclusiveGroupWithOptions(options)
        
        result = meg_options(None, required=False)
        
        assert isinstance(result, MutuallyExclusiveGroupWithOptions)
        expected_options = options.copy()
        expected_options["required"] = False
        assert result.options == expected_options

    def test_empty_options(self):
        """Test with empty options dictionary"""
        options: MutuallyExclusiveGroupWrapperOptions = {}
        meg_options = MutuallyExclusiveGroupWithOptions(options)
        assert meg_options.options == {}

    def test_options_merging(self):
        """Test that options are properly merged"""
        initial_options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        meg_options = MutuallyExclusiveGroupWithOptions(initial_options)
        
        result = meg_options(required=False)
        
        expected: MutuallyExclusiveGroupWrapperOptions = {"required": False}
        assert result.options == expected


class TestDecoratorConstants:
    """Test the module-level decorator constants"""

    def test_namespace_constant(self):
        """Test that namespace constant is callable"""
        assert callable(namespace)
        
        # Test that it can be called with options
        result = namespace(prog="test")
        assert isinstance(result, NamespaceWithOptions)

    def test_group_constant(self):
        """Test that group constant is callable"""
        assert callable(group)
        
        # Test that it can be called with options
        result = group(title="test_group")
        assert isinstance(result, GroupWithOptions)

    def test_mutually_exclusive_group_constant(self):
        """Test that mutually_exclusive_group constant is callable"""
        assert callable(mutually_exclusive_group)
        
        # Test that it can be called with options
        result = mutually_exclusive_group(required=True)
        assert isinstance(result, MutuallyExclusiveGroupWithOptions)

    def test_namespace_with_class(self):
        """Test using namespace decorator with a class"""
        class TestNamespace:
            arg1: str
            arg2: int = 10

        wrapper = namespace(TestNamespace)
        assert isinstance(wrapper, NamespaceWrapper)
        assert wrapper.namespace_type == TestNamespace

    def test_group_with_class(self):
        """Test using group decorator with a class"""
        class TestGroup:
            arg1: str
            arg2: bool = False

        wrapper = group(TestGroup)
        assert isinstance(wrapper, GroupWrapper)
        assert wrapper.namespace_type == TestGroup

    def test_mutually_exclusive_group_with_class(self):
        """Test using mutually_exclusive_group decorator with a class"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        wrapper = mutually_exclusive_group(TestGroup)
        assert isinstance(wrapper, MutuallyExclusiveGroupWrapper)
        assert wrapper.namespace_type == TestGroup


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple decorators"""

    def test_chained_namespace_options(self):
        """Test chaining namespace options"""
        # Start with base options
        base_namespace = namespace(prog="myapp")
        
        # Add more options
        configured_namespace = base_namespace(add_help=False, epilog="Example usage")
        
        # Finally apply to a class
        class Config:
            verbose: bool = False
            output: str = "output.txt"
        
        wrapper = configured_namespace(Config)
        assert isinstance(wrapper, NamespaceWrapper)
        assert wrapper.namespace_type == Config

    def test_chained_group_options(self):
        """Test chaining group options"""
        # Start with base options
        base_group = group(title="Input Options")
        
        # Add more options
        configured_group = base_group(description="Options for input processing")
        
        # Finally apply to a class
        class InputGroup:
            input_file: str
            format: str = "json"
        
        wrapper = configured_group(InputGroup)
        assert isinstance(wrapper, GroupWrapper)
        assert wrapper.namespace_type == InputGroup

    def test_chained_mutually_exclusive_group_options(self):
        """Test chaining mutually exclusive group options"""
        # Start with base options
        base_meg = mutually_exclusive_group(required=True)
        
        # Modify options
        configured_meg = base_meg(required=False)
        
        # Finally apply to a class
        class OutputMode:
            verbose: bool = False
            quiet: bool = False
        
        wrapper = configured_meg(OutputMode)
        assert isinstance(wrapper, MutuallyExclusiveGroupWrapper)
        assert wrapper.namespace_type == OutputMode


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_namespace_with_invalid_options(self):
        """Test namespace with various option types"""
        # This should work - options are just passed through
        options: ArgumentParserOptions = {"prog": "test", "add_help": True}
        namespace_obj = NamespaceWithOptions(options)
        assert namespace_obj.options == options

    def test_empty_class_decoration(self):
        """Test decorating empty classes"""
        class EmptyNamespace:
            pass
        
        class EmptyGroup:
            pass
        
        ns_wrapper = namespace(EmptyNamespace)
        group_wrapper = group(EmptyGroup)
        meg_wrapper = mutually_exclusive_group(EmptyGroup)
        
        assert isinstance(ns_wrapper, NamespaceWrapper)
        assert isinstance(group_wrapper, GroupWrapper)
        assert isinstance(meg_wrapper, MutuallyExclusiveGroupWrapper)

    def test_options_mutation_safety(self):
        """Test that original options are not mutated"""
        original_options: ArgumentParserOptions = {"prog": "test", "add_help": True}
        namespace_obj = NamespaceWithOptions(original_options)
        
        # Creating new instance with additional options
        new_obj = namespace_obj(epilog="New epilog")
        
        # Original options should be unchanged
        assert original_options == {"prog": "test", "add_help": True}
        assert "epilog" not in original_options
        
        # New object should have merged options
        expected: ArgumentParserOptions = {"prog": "test", "add_help": True, "epilog": "New epilog"}
        assert new_obj.options == expected


class TestBoolTypeOptimization:
    """Test bool type flag optimization in different scenarios"""

    def test_bool_with_default_false(self):
        """Test bool type with default=False becomes store_true flag"""
        @namespace
        class ConfigWithBoolFalse:
            verbose: bool = False
        
        # Test that --verbose flag works without requiring an argument
        config = ConfigWithBoolFalse.parse_args(['--verbose'])
        assert config.verbose is True
        
        # Test default value
        config_default = ConfigWithBoolFalse.parse_args([])
        assert config_default.verbose is False

    def test_bool_with_default_true(self):
        """Test bool type with default=True becomes store_false flag"""
        @namespace
        class ConfigWithBoolTrue:
            debug: bool = True
        
        # Test that --debug flag works without requiring an argument
        config = ConfigWithBoolTrue.parse_args(['--debug'])
        assert config.debug is False
        
        # Test default value
        config_default = ConfigWithBoolTrue.parse_args([])
        assert config_default.debug is True

    # TODO: test_bool_without_default - Future improvement needed
    # Currently, bool type parsing from string has issues:
    # Python's bool() converts any non-empty string to True
    # Need custom parsing logic to handle 'False', '0', etc.

    def test_multiple_bool_flags(self):
        """Test multiple bool flags in the same namespace"""
        @namespace
        class ConfigWithMultipleBools:
            verbose: bool = False
            debug: bool = False
            quiet: bool = True
        
        # Test combination of flags
        config = ConfigWithMultipleBools.parse_args(['--verbose', '--quiet'])
        assert config.verbose is True
        assert config.debug is False
        assert config.quiet is False

    def test_bool_flag_with_other_types(self):
        """Test bool flags work correctly alongside other argument types"""
        @namespace
        class MixedTypeConfig:
            name: str = "default"
            verbose: bool = False
            count: int = 1
        
        # Test bool flag with other arguments
        config = MixedTypeConfig.parse_args([
            '--name', 'test',
            '--verbose',
            '--count', '5'
        ])
        assert config.name == 'test'
        assert config.verbose is True
        assert config.count == 5

    def test_bool_positional_argument(self):
        """Test bool type as positional argument with proper string conversion."""
        @namespace
        class ConfigWithBoolPositional:
            enabled: bool
        
        # Test 'true' conversion
        config = ConfigWithBoolPositional.parse_args(['true'])
        assert config.enabled is True
        
        # Test 'false' conversion
        config = ConfigWithBoolPositional.parse_args(['false'])
        assert config.enabled is False
        
        # Test '1' conversion
        config = ConfigWithBoolPositional.parse_args(['1'])
        assert config.enabled is True
        
        # Test '0' conversion
        config = ConfigWithBoolPositional.parse_args(['0'])
        assert config.enabled is False
        
        # Test case-insensitive
        config = ConfigWithBoolPositional.parse_args(['TRUE'])
        assert config.enabled is True
        
        config = ConfigWithBoolPositional.parse_args(['FALSE'])
        assert config.enabled is False
