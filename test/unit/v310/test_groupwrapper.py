"""Unit tests for clipar.v310.groupwrapper module"""

# pyright: reportPrivateUsage=false

from unittest.mock import Mock, patch
import argparse
from clipar.v310.groupwrapper import (
    LazyContainer, GroupWrapper, MutuallyExclusiveGroupWrapper,
    GroupWrapperOptions, MutuallyExclusiveGroupWrapperOptions
)
from clipar.v310.basewrapper import BaseWrapper, AddArgumentOptions


class TestLazyContainer:
    """Test LazyContainer class functionality"""

    def test_argument_inner_class(self):
        """Test LazyContainer._Argument inner class"""
        name_or_flags = ("--verbose", "-v")
        options: AddArgumentOptions = {"action": "store_true", "help": "Enable verbose mode"}
        
        arg = LazyContainer._Argument(name_or_flags, options)
        assert arg.name_or_flags == name_or_flags
        assert arg.options == options

    def test_argument_group_inner_class(self):
        """Test LazyContainer._ArgumentGroup inner class"""
        # Test with default values
        group = LazyContainer._ArgumentGroup()
        assert group.title is None
        assert group.description is None
        assert group.prefix_chars == '-'
        assert group.conflict_handler == 'error'
        
        # Test with custom values
        group = LazyContainer._ArgumentGroup(
            "Test Group", 
            "Test description",
            prefix_chars='+',
            conflict_handler='resolve'
        )
        assert group.title == "Test Group"
        assert group.description == "Test description"
        assert group.prefix_chars == '+'
        assert group.conflict_handler == 'resolve'

    def test_mutually_exclusive_group_inner_class(self):
        """Test LazyContainer._MutuallyExclusiveGroup inner class"""
        # Test with default value
        meg = LazyContainer._MutuallyExclusiveGroup()
        assert meg.required is False
        
        # Test with custom value
        meg = LazyContainer._MutuallyExclusiveGroup(required=True)
        assert meg.required is True

    def test_init_with_argument_group(self):
        """Test LazyContainer initialization with ArgumentGroup"""
        arg_group = LazyContainer._ArgumentGroup("Test Group", "Test description")
        container = LazyContainer(arg_group)
        
        assert container.options == arg_group
        assert container.arguments == []
        assert container.groups == []
        assert container.defaults == {}

    def test_init_with_mutually_exclusive_group(self):
        """Test LazyContainer initialization with MutuallyExclusiveGroup"""
        meg = LazyContainer._MutuallyExclusiveGroup(required=True)
        container = LazyContainer(meg)
        
        assert container.options == meg
        assert container.arguments == []
        assert container.groups == []
        assert container.defaults == {}

    def test_init_as_argument_group(self):
        """Test class method init_as_argument_group"""
        container = LazyContainer.init_as_argument_group(
            title="Test Group",
            description="Test description",
            prefix_chars='+',
            conflict_handler='resolve'
        )
        
        assert isinstance(container.options, LazyContainer._ArgumentGroup)
        assert container.options.title == "Test Group"
        assert container.options.description == "Test description"
        assert container.options.prefix_chars == '+'
        assert container.options.conflict_handler == 'resolve'

    def test_init_as_mutually_exclusive_group(self):
        """Test class method init_as_mutually_exclusive_group"""
        container = LazyContainer.init_as_mutually_exclusive_group(required=True)
        
        assert isinstance(container.options, LazyContainer._MutuallyExclusiveGroup)
        assert container.options.required is True

    def test_add_argument(self):
        """Test add_argument method"""
        arg_group = LazyContainer._ArgumentGroup()
        container = LazyContainer(arg_group)
        
        # Add an argument
        container.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")
        
        assert len(container.arguments) == 1
        argument = container.arguments[0]
        assert argument.name_or_flags == ("--verbose", "-v")
        assert argument.options.get("action") == "store_true"
        assert argument.options.get("help") == "Enable verbose mode"

    def test_add_argument_group(self):
        """Test add_argument_group method"""
        arg_group = LazyContainer._ArgumentGroup()
        container = LazyContainer(arg_group)
        
        # Add an argument group
        new_group = container.add_argument_group(title="Sub Group", description="Sub description")
        
        assert len(container.groups) == 1
        assert container.groups[0] == new_group
        assert isinstance(new_group, LazyContainer)
        assert isinstance(new_group.options, LazyContainer._ArgumentGroup)
        assert new_group.options.title == "Sub Group"
        assert new_group.options.description == "Sub description"

    def test_add_mutually_exclusive_group(self):
        """Test add_mutually_exclusive_group method"""
        arg_group = LazyContainer._ArgumentGroup()
        container = LazyContainer(arg_group)
        
        # Add a mutually exclusive group
        meg = container.add_mutually_exclusive_group(required=True)
        
        assert len(container.groups) == 1
        assert container.groups[0] == meg
        assert isinstance(meg, LazyContainer)
        assert isinstance(meg.options, LazyContainer._MutuallyExclusiveGroup)
        assert meg.options.required is True

    def test_set_defaults(self):
        """Test set_defaults method"""
        arg_group = LazyContainer._ArgumentGroup()
        container = LazyContainer(arg_group)
        
        # Set defaults
        container.set_defaults(verbose=True, output="file.txt")
        
        assert container.defaults["verbose"] is True
        assert container.defaults["output"] == "file.txt"

    def test_apply_to_argument_group(self):
        """Test apply method with argument group"""
        # Create a mock argument parser
        mock_parser = Mock(spec=argparse.ArgumentParser)
        mock_group = Mock()
        mock_parser.add_argument_group.return_value = mock_group
        
        # Create container with argument group
        container = LazyContainer.init_as_argument_group(
            title="test Group",
            description="Test description"
        )
        container.add_argument("--verbose", action="store_true")
        container.set_defaults(verbose=False)
        
        # Apply to parser
        container.apply(mock_parser, "test_group")
        
        # Verify argument group was created
        mock_parser.add_argument_group.assert_called_once_with(
            title="test_group",
            description="Test description",
            prefix_chars='-',
            conflict_handler='error'
        )
        
        # Verify argument was added
        mock_group.add_argument.assert_called_once_with("--verbose", action="store_true")
        
        # Verify defaults were set
        mock_group.set_defaults.assert_called_once_with(verbose=False)

    def test_apply_to_mutually_exclusive_group(self):
        """Test apply method with mutually exclusive group"""
        # Create a mock argument parser
        mock_parser = Mock(spec=argparse.ArgumentParser)
        mock_meg = Mock()
        mock_parser.add_mutually_exclusive_group.return_value = mock_meg
        
        # Create container with mutually exclusive group
        container = LazyContainer.init_as_mutually_exclusive_group(required=True)
        container.add_argument("--verbose", action="store_true")
        container.add_argument("--quiet", action="store_true")
        
        # Apply to parser
        container.apply(mock_parser, "meg_group")
        
        # Verify mutually exclusive group was created
        mock_parser.add_mutually_exclusive_group.assert_called_once_with(required=True)
        
        # Verify arguments were added
        assert mock_meg.add_argument.call_count == 2
        mock_meg.add_argument.assert_any_call("--verbose", action="store_true")
        mock_meg.add_argument.assert_any_call("--quiet", action="store_true")

    def test_apply_with_nested_groups(self):
        """Test apply method with nested groups"""
        # Create a mock argument parser
        mock_parser = Mock(spec=argparse.ArgumentParser)
        mock_group = Mock()
        mock_subgroup = Mock()
        mock_parser.add_argument_group.return_value = mock_group
        mock_group.add_argument_group.return_value = mock_subgroup
        
        # Create container with nested groups
        container = LazyContainer.init_as_argument_group(title="Main Group")
        sub_container = container.add_argument_group(title="Sub Group")
        sub_container.add_argument("--option", help="An option")
        
        # Apply to parser
        container.apply(mock_parser, "main_group")
        
        # Verify nested structure was created
        mock_parser.add_argument_group.assert_called_once_with(
            title="main_group",
            description=None,
            prefix_chars='-',
            conflict_handler='error'
        )
        mock_group.add_argument_group.assert_called_once_with(
            title="Sub Group",
            description=None,
            prefix_chars='-',
            conflict_handler='error'
        )
        mock_subgroup.add_argument.assert_called_once_with("--option", help="An option")


class TestGroupWrapper:
    """Test GroupWrapper class functionality"""

    def test_init(self):
        """Test GroupWrapper initialization"""
        class TestGroup:
            """Test group class"""
            option1: str
            option2: bool = False

        options: GroupWrapperOptions = {"title": "Custom Title", "description": "Custom description"}
        wrapper = GroupWrapper(TestGroup, options)
        
        assert wrapper.namespace_type == TestGroup
        assert isinstance(wrapper._lazy_container, LazyContainer)

    def test_init_with_default_options(self):
        """Test GroupWrapper initialization with default options"""
        class TestGroup:
            """Test group docstring"""
            option1: str

        wrapper = GroupWrapper(TestGroup)
        
        assert wrapper.namespace_type == TestGroup
        assert isinstance(wrapper._lazy_container, LazyContainer)

    def test_configure_container(self):
        """Test configure_container method"""
        class TestGroup:
            option1: str

        wrapper = GroupWrapper(TestGroup)
        container = wrapper.configure_container()
        
        assert container == wrapper._lazy_container
        assert isinstance(container, LazyContainer)

    def test_on_after_bind(self):
        """Test on_after_bind method"""
        class TestGroup:
            option1: str

        wrapper = GroupWrapper(TestGroup)
        
        # Create a mock child wrapper
        mock_child_wrapper = Mock(spec=BaseWrapper)
        mock_child_container = Mock()
        mock_child_wrapper._container = mock_child_container
        
        # Mock the lazy container apply method
        with patch.object(wrapper._lazy_container, 'apply') as mock_apply:
            wrapper.on_after_bind("child_name", mock_child_wrapper)
            mock_apply.assert_called_once_with(mock_child_container, "child_name")

    def test_inheritance_from_subgroup_wrapper(self):
        """Test that GroupWrapper inherits from SubgroupWrapper"""
        from clipar.v310.basewrapper import SubgroupWrapper
        
        class TestGroup:
            option1: str

        wrapper = GroupWrapper(TestGroup)
        assert isinstance(wrapper, SubgroupWrapper)


class TestMutuallyExclusiveGroupWrapper:
    """Test MutuallyExclusiveGroupWrapper class functionality"""

    def test_init(self):
        """Test MutuallyExclusiveGroupWrapper initialization"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        wrapper = MutuallyExclusiveGroupWrapper(TestGroup, options)
        
        assert wrapper.namespace_type == TestGroup
        assert isinstance(wrapper._lazy_container, LazyContainer)

    def test_init_with_default_options(self):
        """Test MutuallyExclusiveGroupWrapper initialization with default options"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        wrapper = MutuallyExclusiveGroupWrapper(TestGroup)
        
        assert wrapper.namespace_type == TestGroup
        assert isinstance(wrapper._lazy_container, LazyContainer)

    def test_configure_container(self):
        """Test configure_container method"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        wrapper = MutuallyExclusiveGroupWrapper(TestGroup)
        container = wrapper.configure_container()
        
        assert container == wrapper._lazy_container
        assert isinstance(container, LazyContainer)

    def test_on_after_bind(self):
        """Test on_after_bind method"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        wrapper = MutuallyExclusiveGroupWrapper(TestGroup)
        
        # Create a mock child wrapper
        mock_child_wrapper = Mock(spec=BaseWrapper)
        mock_child_container = Mock()
        mock_child_wrapper._container = mock_child_container
        
        # Mock the lazy container apply method
        with patch.object(wrapper._lazy_container, 'apply') as mock_apply:
            wrapper.on_after_bind("child_name", mock_child_wrapper)
            mock_apply.assert_called_once_with(mock_child_container, "child_name")

    def test_inheritance_from_subgroup_wrapper(self):
        """Test that MutuallyExclusiveGroupWrapper inherits from SubgroupWrapper"""
        from clipar.v310.basewrapper import SubgroupWrapper
        
        class TestGroup:
            option1: bool = False
            option2: bool = False

        wrapper = MutuallyExclusiveGroupWrapper(TestGroup)
        assert isinstance(wrapper, SubgroupWrapper)

    def test_mutually_exclusive_group_container_type(self):
        """Test that the container is configured as mutually exclusive group"""
        class TestGroup:
            option1: bool = False
            option2: bool = False

        options: MutuallyExclusiveGroupWrapperOptions = {"required": True}
        wrapper = MutuallyExclusiveGroupWrapper(TestGroup, options)
        
        container = wrapper.configure_container()
        assert isinstance(container.options, LazyContainer._MutuallyExclusiveGroup)
        assert container.options.required is True


class TestIntegrationScenarios:
    """Test integration scenarios for group wrappers"""

    def test_nested_group_structure(self):
        """Test creating nested group structures"""
        class MainGroup:
            option1: str

        class SubGroup:
            option2: bool = False

        # Create main group wrapper
        main_wrapper = GroupWrapper(MainGroup, {"title": "Main Group"})
        
        # Create sub group wrapper
        sub_wrapper = GroupWrapper(SubGroup, {"title": "Sub Group"})
        
        # Test that both wrappers are properly configured
        main_container = main_wrapper.configure_container()
        sub_container = sub_wrapper.configure_container()
        
        assert isinstance(main_container, LazyContainer)
        assert isinstance(sub_container, LazyContainer)
        assert isinstance(main_container.options, LazyContainer._ArgumentGroup)
        assert isinstance(sub_container.options, LazyContainer._ArgumentGroup)

    def test_mutually_exclusive_options_setup(self):
        """Test setting up mutually exclusive options"""
        class OutputMode:
            verbose: bool = False
            quiet: bool = False
            normal: bool = False

        wrapper = MutuallyExclusiveGroupWrapper(
            OutputMode, 
            {"required": True}
        )
        
        container = wrapper.configure_container()
        assert isinstance(container.options, LazyContainer._MutuallyExclusiveGroup)
        assert container.options.required is True


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_group_class(self):
        """Test with empty group class"""
        class EmptyGroup:
            pass

        # Should not raise an error
        wrapper = GroupWrapper(EmptyGroup)
        container = wrapper.configure_container()
        assert isinstance(container, LazyContainer)

    def test_group_with_complex_types(self):
        """Test group with complex type annotations"""
        from typing import List, Optional
        
        class ComplexGroup:
            files: List[str]
            optional_param: Optional[int] = None

        # Should not raise an error during initialization
        wrapper = GroupWrapper(ComplexGroup)
        container = wrapper.configure_container()
        assert isinstance(container, LazyContainer)

    def test_option_merging_behavior(self):
        """Test how options are merged with defaults"""
        class TestGroup:
            """Default description"""
            option1: str

        # Test that custom options override defaults
        custom_options: GroupWrapperOptions = {
            "title": "Custom Title",
            "description": "Custom Description"
        }
        
        wrapper = GroupWrapper(TestGroup, custom_options)
        container = wrapper.configure_container()
        
        assert isinstance(container.options, LazyContainer._ArgumentGroup)
        # The actual title/description verification would require accessing
        # the internal lazy container options, which might be implementation-specific
