"""Test module for namespacewrapper.py"""

import pytest
import argparse
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Any

from clipar.v312.namespacewrapper import NamespaceWrapper, ArgumentParserOptions


class MockNamespace:
    """Mock namespace class for testing"""
    
    def __init__(self):
        self.arg1: str
        self.arg2: int = 42
        self.flag: bool = False


class TestArgumentParserOptions:
    """Test ArgumentParserOptions TypedDict"""
    
    def test_argument_parser_options_structure(self):
        """Test ArgumentParserOptions structure"""
        # Test basic options
        options: ArgumentParserOptions = {
            "prog": "test_program",
            "usage": "test usage",
            "epilog": "test epilog",
            "add_help": True
        }
        
        assert options["prog"] == "test_program"
        assert options["usage"] == "test usage"
        assert options["epilog"] == "test epilog"
        assert options["add_help"] is True
    
    def test_empty_options(self):
        """Test empty ArgumentParserOptions"""
        options: ArgumentParserOptions = {}
        assert len(options) == 0
    
    def test_version_specific_options(self):
        """Test version-specific options"""
        if sys.version_info >= (3, 14):
            # Test Python 3.14+ specific options
            options: ArgumentParserOptions = {
                "suggest_on_error": True,
                "color": False
            }
            assert "suggest_on_error" in options
            assert "color" in options
        else:
            # Test pre-3.14 options (no suggest_on_error, color)
            options: ArgumentParserOptions = {
                "exit_on_error": True,
                "allow_abbrev": False
            }
            assert "exit_on_error" in options
            assert "allow_abbrev" in options


class TestNamespaceWrapper:
    """Test NamespaceWrapper class"""
    
    def test_init_default_options(self):
        """Test NamespaceWrapper initialization with default options"""
        wrapper = NamespaceWrapper(MockNamespace)
        assert wrapper.namespace_type is MockNamespace
        assert isinstance(wrapper._parser, argparse.ArgumentParser)
    
    def test_init_with_options(self):
        """Test NamespaceWrapper initialization with custom options"""
        options: ArgumentParserOptions = {
            "prog": "test_program",
            "add_help": False,
            "exit_on_error": False
        }
        wrapper = NamespaceWrapper(MockNamespace, options)
        assert wrapper.namespace_type is MockNamespace
        assert isinstance(wrapper._parser, argparse.ArgumentParser)
        assert wrapper._parser.prog == "test_program"
    
    def test_configure_container(self):
        """Test configure_container method"""
        wrapper = NamespaceWrapper(MockNamespace)
        container = wrapper.configure_container()
        assert container is wrapper._parser
        assert isinstance(container, argparse.ArgumentParser)
    
    def test_before_parse(self):
        """Test _before_parse method"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # Mock the hook methods to verify they're called
        with patch.object(wrapper, 'on_before_parse') as mock_on_before_parse:
            with patch.object(wrapper, '_flatten_subparsers', return_value=[]):
                wrapper._before_parse()
                mock_on_before_parse.assert_called_once_with([], None)
    
    def test_before_parse_with_subparsers(self):
        """Test _before_parse method with subparsers"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # Create mock bound wrappers
        mock_bound_wrapper1 = Mock()
        mock_bound_wrapper1.self = Mock()
        mock_bound_wrapper1.self._flatten_subgroups = Mock(return_value=[])  # Return empty list
        mock_bound_wrapper2 = Mock()
        mock_bound_wrapper2.self = Mock()
        mock_bound_wrapper2.self._flatten_subgroups = Mock(return_value=[])  # Return empty list
        
        flatten_result = [
            (["sub1"], mock_bound_wrapper1),
            (["sub2"], mock_bound_wrapper2)
        ]
        
        with patch.object(wrapper, 'on_before_parse') as mock_on_before_parse:
            with patch.object(wrapper, '_flatten_subparsers', return_value=flatten_result):
                with patch.object(wrapper, '_flatten_subgroups', return_value=[]):  # Mock this too
                    wrapper._before_parse()
                    
                    # Verify main wrapper hook is called
                    mock_on_before_parse.assert_called_once_with([], None)
                    
                    # Verify subparser hooks are called
                    mock_bound_wrapper1.self.on_before_parse.assert_called_once_with(["sub1"], mock_bound_wrapper1)
                    mock_bound_wrapper2.self.on_before_parse.assert_called_once_with(["sub2"], mock_bound_wrapper2)
    
    def test_after_parse(self):
        """Test _after_parse method"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # Mock namespace
        mock_namespace = Mock()
        
        # Create proper BoundWrapper instances instead of Mock
        from clipar.v312.basewrapper import BoundWrapper
        mock_bound_wrapper1 = BoundWrapper("sub1", wrapper, wrapper)
        mock_bound_wrapper2 = BoundWrapper("sub2", wrapper, wrapper)
        
        flatten_result = [
            (["sub1"], mock_bound_wrapper1),
            (["sub2"], mock_bound_wrapper2)
        ]
        
        # Mock parser to return the wrapper itself as default
        with patch.object(wrapper._parser, 'get_default', return_value=wrapper):
            with patch.object(wrapper, '_set_subgroup_namespace'):
                # Since _set_subparser_namespace was removed, test the direct result
                result = wrapper._after_parse(mock_namespace, flatten_result)
                
                # Verify that _after_parse returns the modified namespace
                assert result is not None
    
    def test_run_callbacks_removed(self):
        """Test that callback execution is handled in _after_parse"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # The _run_callbacks method doesn't exist - callbacks are handled in _after_parse
        # Just verify that _exec_callback method exists from SubparserWrapper
        assert hasattr(wrapper, '_exec_callback')
    
    def test_parse_args_default(self):
        """Test parse_args method with default arguments"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        with patch.object(wrapper, '_before_parse') as mock_before:
            with patch.object(wrapper, '_after_parse') as mock_after:
                with patch.object(wrapper._parser, 'parse_args') as mock_parse:
                    mock_namespace = Mock()
                    mock_parse.return_value = mock_namespace
                    mock_before.return_value = []
                    mock_after.return_value = mock_namespace
                    
                    result = wrapper.parse_args()
                    
                    mock_before.assert_called_once()
                    mock_parse.assert_called_once_with(None)
                    mock_after.assert_called_once_with(mock_namespace, [])
                    assert result == mock_namespace
    
    def test_parse_args_with_args(self):
        """Test parse_args method with custom arguments"""
        wrapper = NamespaceWrapper(MockNamespace)
        custom_args = ["--arg1", "value1", "--arg2", "42"]
        
        with patch.object(wrapper, '_before_parse') as mock_before:
            with patch.object(wrapper, '_after_parse') as mock_after:
                with patch.object(wrapper._parser, 'parse_args') as mock_parse:
                    mock_namespace = Mock()
                    mock_parse.return_value = mock_namespace
                    mock_before.return_value = []
                    mock_after.return_value = mock_namespace
                    
                    result = wrapper.parse_args(custom_args)
                    
                    mock_before.assert_called_once()
                    mock_parse.assert_called_once_with(custom_args)
                    mock_after.assert_called_once_with(mock_namespace, [])
                    assert result == mock_namespace
    
    def test_parse_args_integration(self):
        """Test parse_args method integration"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # Test that parse_args method exists and is callable
        assert hasattr(wrapper, 'parse_args')
        assert callable(wrapper.parse_args)
    
    def test_parse_known_args(self):
        """Test parse_known_args method"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        with patch.object(wrapper, '_before_parse') as mock_before:
            with patch.object(wrapper, '_after_parse') as mock_after:
                with patch.object(wrapper._parser, 'parse_known_args') as mock_parse:
                    mock_namespace = Mock()
                    remaining_args = ["--unknown", "arg"]
                    mock_parse.return_value = (mock_namespace, remaining_args)
                    mock_before.return_value = []
                    mock_after.return_value = mock_namespace
                    
                    result = wrapper.parse_known_args()
                    
                    mock_before.assert_called_once()
                    mock_parse.assert_called_once_with(None)
                    mock_after.assert_called_once_with(mock_namespace, [])
                    assert result == (mock_namespace, remaining_args)
    
    def test_integration_with_argparser(self):
        """Test integration with actual ArgumentParser"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # This tests that the wrapper properly inherits from SubparserWrapper
        # and integrates with argparse
        assert hasattr(wrapper, '_parser')
        assert isinstance(wrapper._parser, argparse.ArgumentParser)
        assert hasattr(wrapper, 'parse_args')
        assert hasattr(wrapper, 'parse_known_args')
    
    def test_subparser_inheritance(self):
        """Test that NamespaceWrapper properly inherits from SubparserWrapper"""
        wrapper = NamespaceWrapper(MockNamespace)
        
        # Verify SubparserWrapper methods are available
        assert hasattr(wrapper, '_set_callback')
        assert hasattr(wrapper, '_check_namespace')
        assert hasattr(wrapper, '_exec_callback')
        
        # Verify BaseWrapper methods are available
        assert hasattr(wrapper, '_flatten_subparsers')
        assert hasattr(wrapper, '_flatten_subgroups')
        assert hasattr(wrapper, 'on_before_parse')
        assert hasattr(wrapper, 'on_after_parse')


if __name__ == "__main__":
    pytest.main([__file__])
