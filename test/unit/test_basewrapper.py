"""Test module for basewrapper.py"""

import pytest
import argparse
from typing import Literal
from unittest.mock import Mock, MagicMock

from clipar.basewrapper import (
    BaseWrapper, SubparserWrapper, SubgroupWrapper, BoundWrapper,
    NotSelected, NotSelectedType, _return_bool, _append_list,
    AddArgumentOptions, ArgumentContainerProtocol,
    SupportsOriginAndArgs
)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_return_bool(self):
        """Test _return_bool function"""
        assert _return_bool(True) is True
        assert _return_bool(False) is False
    
    def test_append_list(self):
        """Test _append_list function"""
        target = [1, 2]
        result = _append_list(target, 3, 4)
        assert result == [1, 2, 3, 4]
        assert target is result  # Same object should be returned


class TestNotSelectedType:
    """Test NotSelectedType and NotSelected enum"""
    
    def test_not_selected_singleton(self):
        """Test NotSelected singleton"""
        assert NotSelected is NotSelectedType.I
        assert isinstance(NotSelected.value, type(NotSelectedType.I.value))


class MockNamespace:
    """Mock namespace class for testing"""
    
    def __init__(self):
        self.arg1: str
        self.arg2: int = 42
        self.flag: bool = False


class ConcreteWrapper(BaseWrapper[MockNamespace]):
    """Concrete implementation of BaseWrapper for testing"""
    
    def configure_container(self) -> ArgumentContainerProtocol:
        return Mock(spec=ArgumentContainerProtocol)


class TestBaseWrapper:
    """Test BaseWrapper class"""
    
    def test_init(self):
        """Test BaseWrapper initialization"""
        wrapper = ConcreteWrapper(MockNamespace)
        assert wrapper.namespace_type is MockNamespace
        assert isinstance(wrapper._subparsers, dict)
        assert isinstance(wrapper._subgroups, dict)
        assert isinstance(wrapper._arg_names, set)
        assert wrapper._container is not None
    
    def test_namespace_type_property(self):
        """Test T property"""
        wrapper = ConcreteWrapper(MockNamespace)
        assert wrapper.T is MockNamespace
    
    def test_get_descriptor_with_none_instance(self):
        """Test __get__ method with None instance"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper.__get__(None, None)
        assert result is wrapper
    
    def test_get_descriptor_with_type_instance(self):
        """Test __get__ method with type instance"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper.__get__(type, None)
        assert result is wrapper
    
    def test_get_descriptor_with_object_instance(self):
        """Test __get__ method with object instance"""
        wrapper = ConcreteWrapper(MockNamespace)
        obj = object()
        result = wrapper.__get__(obj, None)
        assert result is NotSelected
    
    def test_update_container(self):
        """Test update_container method"""
        wrapper = ConcreteWrapper(MockNamespace)
        new_container = Mock(spec=ArgumentContainerProtocol)
        wrapper.update_container(new_container)
        assert wrapper._container is new_container
    
    def test_parse_annotation_basic_type(self):
        """Test _parse_annotation with basic type"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper._parse_annotation(int)
        assert 'type' in result
        assert result['type'] is int
        assert result.get('nargs') is None
    
    def test_parse_annotation_literal(self):
        """Test _parse_annotation with Literal type"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper._parse_annotation(Literal['a', 'b'])
        assert 'choices' in result
        assert result['choices'] is not None
        assert set(result['choices']) == {'a', 'b'}
    
    def test_flatten_union_and_literal(self):
        """Test _flatten_union_and_literal method"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper._flatten_union_and_literal((int, str))
        assert int in result
        assert str in result
        assert result[int] == [int]
        assert result[str] == [str]
    
    def test_get_type_from_type_or_generic_alias(self):
        """Test _get_type_from_type_or_generic_alias method"""
        wrapper = ConcreteWrapper(MockNamespace)
        assert wrapper._get_type_from_type_or_generic_alias(int) is int
        assert wrapper._get_type_from_type_or_generic_alias(str) is str
    
    def test_flatten_subparsers_empty(self):
        """Test _flatten_subparsers with empty subparsers"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper._flatten_subparsers()
        assert result == []
    
    def test_flatten_subgroups_empty(self):
        """Test _flatten_subgroups with empty subgroups"""
        wrapper = ConcreteWrapper(MockNamespace)
        result = wrapper._flatten_subgroups()
        assert result == []
    
    def test_bind(self):
        """Test _bind method"""
        wrapper = ConcreteWrapper(MockNamespace)
        parent_wrapper = ConcreteWrapper(MockNamespace)
        bound = wrapper._bind("test", parent_wrapper)
        assert isinstance(bound, BoundWrapper)
        assert bound._bound_name == "test"
        assert bound._parent is parent_wrapper
        assert bound._self is wrapper
    
    def test_hook_methods(self):
        """Test hook methods don't raise errors"""
        wrapper = ConcreteWrapper(MockNamespace)
        bound = BoundWrapper("test", wrapper, wrapper)
        
        # These should not raise exceptions
        wrapper.on_after_bind(bound)
        wrapper.on_before_parse(["test"], bound)
        wrapper.on_after_parse(["test"], bound)


class MockSubparserWrapper(SubparserWrapper[MockNamespace]):
    """Mock SubparserWrapper for testing"""
    
    def configure_container(self) -> ArgumentContainerProtocol:
        mock_container = Mock(spec=ArgumentContainerProtocol)
        mock_container.set_defaults = Mock()
        return mock_container


class TestSubparserWrapper:
    """Test SubparserWrapper class"""
    
    def test_init(self):
        """Test SubparserWrapper initialization"""
        wrapper = MockSubparserWrapper(MockNamespace)
        assert wrapper.namespace_type is MockNamespace
        assert wrapper._callback is None
        # Just verify that the container has the set_defaults method
        assert hasattr(wrapper._container, 'set_defaults')
    
    def test_set_callback(self):
        """Test _set_callback method"""
        wrapper = MockSubparserWrapper(MockNamespace)
        callback = lambda x: x
        wrapper._set_callback(callback)
        assert wrapper._callback is callback
    
    def test_check_namespace_valid(self):
        """Test _check_namespace with valid namespace"""
        wrapper = MockSubparserWrapper(MockNamespace)
        wrapper._arg_names = {'arg1', 'arg2'}
        
        namespace = Mock()
        namespace.arg1 = "test"
        namespace.arg2 = 42
        
        assert wrapper._check_namespace(namespace) is True
    
    def test_check_namespace_invalid(self):
        """Test _check_namespace with invalid namespace"""
        wrapper = MockSubparserWrapper(MockNamespace)
        wrapper._arg_names = {'arg1', 'arg2'}
        
        namespace = Mock(spec=[])  # Empty spec means no attributes
        
        assert wrapper._check_namespace(namespace) is False
    
    def test_exec_callback_none(self):
        """Test _exec_callback with None callback"""
        wrapper = MockSubparserWrapper(MockNamespace)
        namespace = Mock()
        result = wrapper._exec_callback(namespace)
        assert result is None
    
    def test_exec_callback_valid_namespace(self):
        """Test _exec_callback with valid namespace"""
        wrapper = MockSubparserWrapper(MockNamespace)
        wrapper._arg_names = {'arg1'}
        
        expected_result = "callback_result"
        callback = Mock(return_value=expected_result)
        wrapper._set_callback(callback)
        
        namespace = Mock()
        namespace.arg1 = "test"
        
        result = wrapper._exec_callback(namespace)
        assert result == expected_result
        callback.assert_called_once_with(namespace)


class MockSubgroupWrapper(SubgroupWrapper[MockNamespace]):
    """Mock SubgroupWrapper for testing"""
    
    def configure_container(self) -> ArgumentContainerProtocol:
        return Mock(spec=ArgumentContainerProtocol)


class TestSubgroupWrapper:
    """Test SubgroupWrapper class"""
    
    def test_init(self):
        """Test SubgroupWrapper initialization"""
        wrapper = MockSubgroupWrapper(MockNamespace)
        assert wrapper.namespace_type is MockNamespace


class TestBoundWrapper:
    """Test BoundWrapper class"""
    
    def test_init(self):
        """Test BoundWrapper initialization"""
        parent = ConcreteWrapper(MockNamespace)
        self_wrapper = ConcreteWrapper(MockNamespace)
        bound = BoundWrapper("test_name", parent, self_wrapper)
        
        assert bound._bound_name == "test_name"
        assert bound._parent is parent
        assert bound._self is self_wrapper
    
    def test_self_property(self):
        """Test self property"""
        parent = ConcreteWrapper(MockNamespace)
        self_wrapper = ConcreteWrapper(MockNamespace)
        bound = BoundWrapper("test_name", parent, self_wrapper)
        
        assert bound.self is self_wrapper


class TestArgumentContainerProtocol:
    """Test ArgumentContainerProtocol"""
    
    def test_protocol_compliance(self):
        """Test that argparse.ArgumentParser has required methods"""
        parser = argparse.ArgumentParser()
        assert hasattr(parser, 'add_argument')
        assert hasattr(parser, 'add_argument_group')
        assert hasattr(parser, 'set_defaults')
        assert hasattr(parser, 'get_default')


class TestSupportsOriginAndArgs:
    """Test SupportsOriginAndArgs protocol"""
    
    def test_protocol_compliance(self):
        """Test protocol compliance with typing constructs"""
        from typing import List, Dict
        
        # These should implement the protocol
        list_type = List[int]
        dict_type = Dict[str, int]
        
        if hasattr(list_type, '__origin__') and hasattr(list_type, '__args__'):
            assert isinstance(list_type, SupportsOriginAndArgs)
        if hasattr(dict_type, '__origin__') and hasattr(dict_type, '__args__'):
            assert isinstance(dict_type, SupportsOriginAndArgs)


if __name__ == "__main__":
    pytest.main([__file__])
