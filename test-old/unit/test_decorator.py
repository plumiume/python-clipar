"""Test module for decorator.py"""

import pytest
from unittest.mock import Mock, patch
from typing import Any

from clipar.v312.decorator import NamespaceWithOptions, namespace, group


class MockNamespace:
    """Mock namespace class for testing"""
    
    def __init__(self):
        self.arg1: str
        self.arg2: int = 42


class TestNamespaceWithOptions:
    """Test NamespaceWithOptions class"""
    
    def test_init(self):
        """Test NamespaceWithOptions initialization"""
        options: Any = {"prog": "test_prog", "add_help": False}
        nwo = NamespaceWithOptions(options)
        assert nwo.options == options
    
    def test_call_with_namespace_type(self):
        """Test __call__ with namespace type"""
        options: Any = {"prog": "test_prog"}
        nwo = NamespaceWithOptions(options)
        
        with patch('clipar.v312.decorator.NamespaceWrapper') as mock_wrapper_class:
            # NamespaceWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            result = nwo(MockNamespace)
            
            # Verify the __getitem__ was called (for generic type)
            mock_wrapper_class.__getitem__.assert_called_once()
            # The method passes {} as options, not self.options
            mock_instance.assert_called_once_with(MockNamespace, {})
            assert result == mock_instance.return_value
    
    def test_call_without_namespace_type(self):
        """Test __call__ without namespace type"""
        initial_options: Any = {"prog": "test_prog"}
        nwo = NamespaceWithOptions(initial_options)
        
        # Use only compatible options
        result = nwo(prog="new_prog", add_help=False)
        
        assert isinstance(result, NamespaceWithOptions)
        assert "prog" in result.options
        assert "add_help" in result.options
    
    def test_call_with_none_and_options(self):
        """Test __call__ with None and additional options"""
        initial_options: Any = {"prog": "test_prog"}
        nwo = NamespaceWithOptions(initial_options)
        
        # Test the actual behavior based on the overloads
        result = nwo(epilog="End message")
        
        assert isinstance(result, NamespaceWithOptions)
        assert "epilog" in result.options


class TestNamespaceDecorator:
    """Test namespace decorator function"""
    
    def test_namespace_call_with_type(self):
        """Test namespace decorator with type"""
        with patch('clipar.v312.decorator.NamespaceWrapper') as mock_wrapper_class:
            # NamespaceWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            result = namespace(MockNamespace)
            
            # Verify the __getitem__ was called (for generic type)
            mock_wrapper_class.__getitem__.assert_called_once()
            # Verify the instance was called with correct args
            mock_instance.assert_called_once_with(MockNamespace, {})
            assert result == mock_instance.return_value
    
    def test_namespace_call_with_options(self):
        """Test namespace decorator with options"""
        options = {"prog": "test_program", "add_help": False}
        result = namespace(**options)
        
        assert isinstance(result, NamespaceWithOptions)
        assert result.options == options
    
    def test_namespace_call_without_args(self):
        """Test namespace decorator without arguments"""
        result = namespace()
        
        assert isinstance(result, NamespaceWithOptions)
        assert result.options == {}
    
    def test_namespace_as_decorator(self):
        """Test namespace used as decorator"""
        with patch('clipar.v312.decorator.NamespaceWrapper') as mock_wrapper_class:
            # NamespaceWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            @namespace
            class TestNamespace:
                arg: str
            
            # Verify the __getitem__ was called (for generic type)
            mock_wrapper_class.__getitem__.assert_called_once()
            # Verify the instance was called, checking the args
            args, kwargs = mock_instance.call_args
            assert args[1] == {}  # Second argument should be empty dict
            assert hasattr(args[0], '__name__')  # First argument should be a class
    
    def test_namespace_as_decorator_with_options(self):
        """Test namespace used as decorator with options"""
        with patch('clipar.v312.decorator.NamespaceWrapper') as mock_wrapper_class:
            # NamespaceWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            @namespace(prog="test_prog")
            class TestNamespace:
                arg: str
            
            # namespace(prog="test_prog") returns NamespaceWithOptions
            # which when called with TestNamespace returns the wrapper
            mock_wrapper_class.__getitem__.assert_called_once()
            mock_instance.assert_called_once()


class GroupWithOptions:
    """Mock GroupWithOptions for testing"""
    
    def __init__(self, options):
        self.options = options
    
    def __call__(self, namespace_type=None, /, **options):
        if namespace_type is not None:
            # Return mock GroupWrapper
            from unittest.mock import Mock
            return Mock()
        else:
            # Return new GroupWithOptions with updated options
            new_options = {**self.options, **options}
            return GroupWithOptions(new_options)


class TestGroupDecorator:
    """Test group decorator function"""
    
    def test_group_call_with_type(self):
        """Test group decorator with type"""
        with patch('clipar.v312.decorator.GroupWrapper') as mock_wrapper_class:
            # GroupWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            result = group(MockNamespace)
            
            # Verify the __getitem__ was called (for generic type)
            mock_wrapper_class.__getitem__.assert_called_once()
            # Verify the instance was called with correct args
            mock_instance.assert_called_once_with(MockNamespace, {})
            assert result == mock_instance.return_value
    
    def test_group_call_with_options(self):
        """Test group decorator with options"""
        options = {"title": "Test Group", "description": "Test description"}

        with patch('clipar.v312.decorator.GroupWithOptions') as mock_group_options:
            mock_instance = Mock()
            mock_group_options.return_value = mock_instance
            
            result = group(**options)
            
            mock_group_options.assert_called_once_with(options)
            assert result == mock_instance
    
    def test_group_call_without_args(self):
        """Test group decorator without arguments"""
        with patch('clipar.v312.decorator.GroupWithOptions') as mock_group_options:
            mock_instance = Mock()
            mock_group_options.return_value = mock_instance
            
            result = group()
            
            mock_group_options.assert_called_once_with({})
            assert result == mock_instance
    
    def test_group_as_decorator(self):
        """Test group used as decorator"""
        with patch('clipar.v312.decorator.GroupWrapper') as mock_wrapper_class:
            # GroupWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            @group
            class TestGroup:
                arg: str
            
            # Verify the __getitem__ was called (for generic type)
            mock_wrapper_class.__getitem__.assert_called_once()
            # Verify the instance was called, checking the args
            args, kwargs = mock_instance.call_args
            assert args[1] == {}  # Second argument should be empty dict
            assert hasattr(args[0], '__name__')  # First argument should be a class
    
    def test_group_as_decorator_with_options(self):
        """Test group used as decorator with options"""
        with patch('clipar.v312.decorator.GroupWrapper') as mock_wrapper_class:
            # GroupWrapper[NS] calls __getitem__ then the result
            mock_instance = Mock()
            mock_wrapper_class.__getitem__.return_value = mock_instance
            
            @group(title="Test Group")
            class TestGroup:
                arg: str
            
            # group(title="Test Group") returns GroupWithOptions
            # which when called with TestGroup returns the wrapper
            mock_wrapper_class.__getitem__.assert_called_once()
            mock_instance.assert_called_once()


class TestDecoratorIntegration:
    """Test decorator integration"""
    
    def test_namespace_and_group_imports(self):
        """Test that namespace and group can be imported"""
        # This test ensures the decorators are properly exposed
        assert callable(namespace)
        assert callable(group)
    
    def test_namespace_options_validation(self):
        """Test namespace options validation"""
        # Test with valid options using Any to avoid type issues
        valid_options: Any = {
            "prog": "test_program", 
            "add_help": True
        }
        
        result = namespace(**valid_options)
        assert isinstance(result, NamespaceWithOptions)
        assert "prog" in result.options
        assert "add_help" in result.options
    
    def test_group_options_validation(self):
        """Test group options validation"""
        # Test with valid options using Any to avoid type issues
        valid_options: Any = {
            "title": "Test Group",
            "description": "Test description"
        }

        with patch('clipar.v312.decorator.GroupWithOptions') as mock_group_options:
            mock_instance = Mock()
            mock_group_options.return_value = mock_instance
            
            result = group(**valid_options)
            
            mock_group_options.assert_called_once()
            assert result == mock_instance


if __name__ == "__main__":
    pytest.main([__file__])
