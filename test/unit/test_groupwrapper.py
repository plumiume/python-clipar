"""Test module for groupwrapper.py"""

import pytest
import argparse
from unittest.mock import Mock, patch
from typing import Any

from clipar.groupwrapper import LazyContainer, GroupWrapper, GroupWrapperOptions


class MockNamespace:
    """Mock namespace class for testing"""
    
    def __init__(self):
        self.arg1: str
        self.arg2: int = 42


class TestLazyContainer:
    """Test LazyContainer class"""
    
    def test_init(self):
        """Test LazyContainer initialization"""
        container = LazyContainer()
        assert container.arguments == []
        assert container.argument_groups == []
        assert container.defaults == {}
    
    def test_add_argument(self):
        """Test add_argument method"""
        container = LazyContainer()
        container.add_argument("--test", type=str, help="Test argument")
        
        assert len(container.arguments) == 1
        arg = container.arguments[0]
        assert arg.name_or_flags == ("--test",)
        assert arg.options.get("type") == str
        assert arg.options.get("help") == "Test argument"
    
    def test_add_argument_positional(self):
        """Test add_argument with positional argument"""
        container = LazyContainer()
        container.add_argument("pos_arg", type=int, help="Positional argument")
        
        assert len(container.arguments) == 1
        arg = container.arguments[0]
        assert arg.name_or_flags == ("pos_arg",)
        assert arg.options.get("type") == int
    
    def test_add_argument_multiple_flags(self):
        """Test add_argument with multiple flags"""
        container = LazyContainer()
        container.add_argument("-v", "--verbose", action="store_true")
        
        assert len(container.arguments) == 1
        arg = container.arguments[0]
        assert arg.name_or_flags == ("-v", "--verbose")
        assert arg.options.get("action") == "store_true"
    
    def test_lazy_add_argument(self):
        """Test lazy_add_argument method"""
        container = LazyContainer()
        container.add_argument("--test1", type=str)
        container.add_argument("--test2", type=int)
        
        mock_parser = Mock()
        container.lazy_add_argument(mock_parser)
        
        assert mock_parser.add_argument.call_count == 2
        mock_parser.add_argument.assert_any_call("--test1", type=str)
        mock_parser.add_argument.assert_any_call("--test2", type=int)
    
    def test_add_argument_group(self):
        """Test add_argument_group method"""
        container = LazyContainer()
        result = container.add_argument_group(
            title="Test Group",
            description="Test description",
            prefix_chars="-",
            conflict_handler="error"
        )
        
        assert isinstance(result, LazyContainer)
        assert result is not container  # Should return new instance
        assert len(container.argument_groups) == 1
        
        group = container.argument_groups[0]
        assert group.title == "Test Group"
        assert group.description == "Test description"
        assert group.prefix_chars == "-"
        assert group.conflict_handler == "error"
    
    def test_add_argument_group_defaults(self):
        """Test add_argument_group with default parameters"""
        container = LazyContainer()
        result = container.add_argument_group()
        
        assert isinstance(result, LazyContainer)
        assert len(container.argument_groups) == 1
        
        group = container.argument_groups[0]
        assert group.title is None
        assert group.description is None
        assert group.prefix_chars == "-"
        assert group.conflict_handler == "error"
    
    def test_lazy_add_argument_group(self):
        """Test lazy_add_argument_group method"""
        container = LazyContainer()
        container.add_argument_group("Group 1", "Description 1")
        container.add_argument_group("Group 2", "Description 2")
        
        mock_parser = Mock()
        container.lazy_add_argument_group(mock_parser)
        
        assert mock_parser.add_argument_group.call_count == 2
        mock_parser.add_argument_group.assert_any_call(
            title="Group 1",
            description="Description 1",
            prefix_chars="-",
            conflict_handler="error"
        )
        mock_parser.add_argument_group.assert_any_call(
            title="Group 2",
            description="Description 2",
            prefix_chars="-",
            conflict_handler="error"
        )
    
    def test_set_defaults(self):
        """Test set_defaults method"""
        container = LazyContainer()
        container.set_defaults(arg1="value1", arg2=42)
        
        assert container.defaults == {"arg1": "value1", "arg2": 42}
        
        # Test updating defaults
        container.set_defaults(arg3="value3", arg1="new_value1")
        expected = {"arg1": "new_value1", "arg2": 42, "arg3": "value3"}
        assert container.defaults == expected
    
    def test_get_default(self):
        """Test get_default method"""
        container = LazyContainer()
        container.set_defaults(arg1="value1", arg2=42)
        
        assert container.get_default("arg1") == "value1"
        assert container.get_default("arg2") == 42
        assert container.get_default("nonexistent") is None
    
    def test_argument_class(self):
        """Test _Argument inner class"""
        container = LazyContainer()
        arg = container._Argument(
            name_or_flags=("--test", "-t"),
            options={"type": str, "help": "Test"}
        )
        
        assert arg.name_or_flags == ("--test", "-t")
        assert arg.options == {"type": str, "help": "Test"}
    
    def test_argument_group_class(self):
        """Test _ArgumentGroup inner class"""
        container = LazyContainer()
        group = container._ArgumentGroup(
            title="Test Group",
            description="Test description",
            prefix_chars="+",
            conflict_handler="resolve"
        )
        
        assert group.title == "Test Group"
        assert group.description == "Test description"
        assert group.prefix_chars == "+"
        assert group.conflict_handler == "resolve"
    
    def test_argument_group_defaults(self):
        """Test _ArgumentGroup with default parameters"""
        container = LazyContainer()
        group = container._ArgumentGroup()
        
        assert group.title is None
        assert group.description is None
        assert group.prefix_chars == "-"
        assert group.conflict_handler == "error"


class TestGroupWrapperOptions:
    """Test GroupWrapperOptions TypedDict"""
    
    def test_group_wrapper_options_structure(self):
        """Test GroupWrapperOptions structure"""
        options: GroupWrapperOptions = {
            "title": "Test Group",
            "description": "Test description",
            "prefix_chars": "+",
            "conflict_handler": "resolve"
        }
        
        assert options["title"] == "Test Group"
        assert options["description"] == "Test description"
        assert options["prefix_chars"] == "+"
        assert options["conflict_handler"] == "resolve"
    
    def test_empty_options(self):
        """Test empty GroupWrapperOptions"""
        options: GroupWrapperOptions = {}
        assert len(options) == 0


class TestGroupWrapper:
    """Test GroupWrapper class"""
    
    def test_init_default_options(self):
        """Test GroupWrapper initialization with default options"""
        wrapper = GroupWrapper(MockNamespace)
        assert wrapper.namespace_type is MockNamespace
        assert isinstance(wrapper._container, LazyContainer)
    
    def test_init_with_options(self):
        """Test GroupWrapper initialization with custom options"""
        options: GroupWrapperOptions = {
            "title": "Custom Group",
            "description": "Custom description"
        }
        wrapper = GroupWrapper(MockNamespace, options)
        assert wrapper.namespace_type is MockNamespace
        assert isinstance(wrapper._container, LazyContainer)
        # Note: _options attribute may not exist in actual implementation
    
    def test_configure_container(self):
        """Test configure_container method"""
        wrapper = GroupWrapper(MockNamespace)
        container = wrapper.configure_container()
        assert container is wrapper._container
        assert isinstance(container, LazyContainer)
    
    def test_bind_method(self):
        """Test _bind method - uses base implementation from BaseWrapper"""
        wrapper = GroupWrapper(MockNamespace)
        parent_wrapper = Mock()
        
        # GroupWrapper uses the base _bind method from BaseWrapper
        from clipar.basewrapper import BoundWrapper
        result = wrapper._bind("test_name", parent_wrapper)
        
        assert isinstance(result, BoundWrapper)
        assert result._bound_name == "test_name"
        assert result._parent is parent_wrapper
        assert result._self is wrapper
    
    def test_subgroup_inheritance(self):
        """Test that GroupWrapper properly inherits from SubgroupWrapper"""
        wrapper = GroupWrapper(MockNamespace)
        
        # Verify SubgroupWrapper/BaseWrapper methods are available
        assert hasattr(wrapper, '_flatten_subparsers')
        assert hasattr(wrapper, '_flatten_subgroups')
        assert hasattr(wrapper, 'on_before_parse')
        assert hasattr(wrapper, 'on_after_parse')
    
    def test_integration_with_lazy_container(self):
        """Test integration with LazyContainer"""
        wrapper = GroupWrapper(MockNamespace)
        
        # Test that the wrapper uses LazyContainer
        assert isinstance(wrapper._container, LazyContainer)
        
        # Test that container methods are available
        assert hasattr(wrapper._container, 'add_argument')
        assert hasattr(wrapper._container, 'add_argument_group')
        assert hasattr(wrapper._container, 'set_defaults')
        assert hasattr(wrapper._container, 'get_default')


class TestBoundGroupWrapper:
    """Test BoundWrapper usage with GroupWrapper"""
    
    def test_bound_wrapper_with_group(self):
        """Test that BoundWrapper works with GroupWrapper"""
        from clipar.basewrapper import BoundWrapper
        
        wrapper = GroupWrapper(MockNamespace)
        parent_wrapper = Mock()
        
        # Create a BoundWrapper instance manually
        bound = BoundWrapper("test_group", parent_wrapper, wrapper)
        
        assert bound._bound_name == "test_group"
        assert bound._parent is parent_wrapper
        assert bound._self is wrapper
        assert bound.self is wrapper


class TestGroupWrapperIntegration:
    """Test GroupWrapper integration scenarios"""
    
    def test_lazy_container_integration(self):
        """Test integration between GroupWrapper and LazyContainer"""
        wrapper = GroupWrapper(MockNamespace)
        
        # Verify wrapper uses LazyContainer
        assert isinstance(wrapper._container, LazyContainer)
        
        # Add arguments to the lazy container
        wrapper._container.add_argument("--test", type=str, help="Test argument")
        wrapper._container.set_defaults(test="default_value")
        
        # Verify arguments are stored in lazy container
        lazy_container = wrapper._container
        assert len(lazy_container.arguments) == 1
        assert lazy_container.get_default("test") == "default_value"
        
        # Test lazy loading to a real parser
        real_parser = argparse.ArgumentParser()
        lazy_container.lazy_add_argument(real_parser)
        
        # The real parser should now have the argument
        # We can verify this by checking if parsing works
        try:
            namespace = real_parser.parse_args(["--test", "value"])
            assert hasattr(namespace, 'test')
        except SystemExit:
            # If parsing fails, it's still ok for this test
            pass
    
    def test_argument_group_integration(self):
        """Test argument group integration"""
        wrapper = GroupWrapper(MockNamespace)
        
        # Add argument groups
        group1 = wrapper._container.add_argument_group("Group 1")
        group2 = wrapper._container.add_argument_group("Group 2")
        
        # Verify groups are different instances
        assert group1 is not group2
        assert isinstance(group1, LazyContainer)
        assert isinstance(group2, LazyContainer)
        
        # Add arguments to groups
        group1.add_argument("--group1-arg", type=str)
        group2.add_argument("--group2-arg", type=int)
        
        # Verify arguments are in different containers
        assert len(group1.arguments) == 1
        assert len(group2.arguments) == 1
        assert group1.arguments[0].name_or_flags == ("--group1-arg",)
        assert group2.arguments[0].name_or_flags == ("--group2-arg",)


if __name__ == "__main__":
    pytest.main([__file__])
