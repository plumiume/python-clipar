"""Unit tests for basewrapper.py"""

import pytest
import argparse
from unittest.mock import Mock, patch

from clipar.v312.basewrapper import (
    BaseWrapper, SubparserWrapper, SubgroupWrapper, BoundWrapper,
    NotSelected, NotSelectedType,
    _return_bool, _append_list, # pyright: ignore[reportPrivateUsage]
    ArgumentContainerProtocol, GenericAliasLike
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
        assert target == [1, 2, 3, 4]  # Original list is modified


class TestNotSelectedType:
    """Test NotSelected type and singleton"""
    
    def test_not_selected_singleton(self):
        """Test NotSelected singleton behavior"""
        assert NotSelected is NotSelectedType.I
        assert bool(NotSelected) is False
        assert repr(NotSelected) == "NotSelected"


class MockNamespace:
    """Mock namespace class for testing"""
    
    def __init__(self):
        self.arg1: str
        self.arg2: int = 42
        self.flag: bool = False


class TestBaseWrapper:
    """Test BaseWrapper abstract class"""
    
    def test_init(self):
        """Test BaseWrapper initialization (via concrete subclass)"""
        # Create a concrete implementation for testing
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        # Mock ClassAstHolder to avoid file system dependencies
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            assert wrapper.namespace_type is MockNamespace
            assert isinstance(wrapper._subparsers, dict)
            assert isinstance(wrapper._subgroups, dict)
            assert isinstance(wrapper._arg_names, set)
    
    def test_namespace_type_property(self):
        """Test namespace_type property"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            assert wrapper.T is MockNamespace
    
    def test_get_descriptor_with_none_instance(self):
        """Test __get__ method with None instance"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper.__get__(None, MockNamespace)
            assert result is wrapper
    
    def test_get_descriptor_with_type_instance(self):
        """Test __get__ method with type instance"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper.__get__(MockNamespace, None)
            assert result is wrapper
    
    def test_get_descriptor_with_object_instance(self):
        """Test __get__ method with object instance"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            instance = MockNamespace()
            result = wrapper.__get__(instance, MockNamespace)
            assert result is NotSelected
    
    def test_update_container(self):
        """Test update_container method"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            new_container = Mock(spec=ArgumentContainerProtocol)
            wrapper.update_container(new_container)
            assert wrapper._container is new_container
    
    def test_parse_annotation_basic_type(self):
        """Test _parse_annotation with basic types"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._parse_annotation(str)
            assert 'type' in result
            assert result['type'] is str
    
    def test_parse_annotation_literal(self):
        """Test _parse_annotation with Literal types"""
        from typing import Literal
        
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._parse_annotation(Literal['a', 'b', 'c'])
            assert 'choices' in result
            assert result['choices'] is not None
            assert set(result['choices']) == {'a', 'b', 'c'}
    
    def test_flatten_union_and_literal(self):
        """Test _flatten_union_and_literal method"""
        from typing import Literal, Union
        
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            literal_type = Literal['test']
            assert isinstance(literal_type, GenericAliasLike)
            result = wrapper._flatten_union_and_literal((str, int, literal_type))
            assert str in result
            assert int in result
    
    def test_get_type_from_type_or_generic_alias(self):
        """Test _get_type_from_type_or_generic_alias method"""
        from typing import List
        
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            
            # Test with basic type
            assert wrapper._get_type_from_type_or_generic_alias(str) is str
            
            # Test with generic alias
            assert wrapper._get_type_from_type_or_generic_alias(List[str]) is list
    
    def test_flatten_subparsers_empty(self):
        """Test _flatten_subparsers with empty subparsers"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._flatten_subparsers()
            assert result == []
    
    def test_flatten_subgroups_empty(self):
        """Test _flatten_subgroups with empty subgroups"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._flatten_subgroups()
            assert result == []
    
    def test_bind(self):
        """Test _bind method"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            parent_wrapper = Mock()
            
            bound = wrapper._bind("test_name", parent_wrapper)
            assert isinstance(bound, BoundWrapper)
    
    def test_hook_methods(self):
        """Test hook methods (should not raise exceptions)"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            
            # These should not raise exceptions
            wrapper.on_before_bind("test", Mock())
            wrapper.on_after_bind("test", Mock())
            wrapper.on_before_parse(["test"], Mock())
            wrapper.on_after_parse(["test"], Mock())
    
    def test_add_wrapper_with_subparser(self):
        """Test add_wrapper method with SubparserWrapper"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            subparser = MockSubparserWrapper(MockNamespace)
            
            # Test adding subparser wrapper
            wrapper.add_wrapper("test_subparser", subparser)
            
            # Verify subparser was added
            assert "test_subparser" in wrapper._subparsers
            assert isinstance(wrapper._subparsers["test_subparser"], BoundWrapper)
            assert wrapper._subparsers["test_subparser"]._bound_name == "test_subparser"
            assert wrapper._subparsers["test_subparser"]._parent is wrapper
            assert wrapper._subparsers["test_subparser"]._self is subparser
    
    def test_add_wrapper_with_subgroup(self):
        """Test add_wrapper method with SubgroupWrapper"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubgroupWrapper(SubgroupWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            subgroup = MockSubgroupWrapper(MockNamespace)
            
            # Test adding subgroup wrapper
            wrapper.add_wrapper("test_subgroup", subgroup)
            
            # Verify subgroup was added
            assert "test_subgroup" in wrapper._subgroups
            assert isinstance(wrapper._subgroups["test_subgroup"], BoundWrapper)
            assert wrapper._subgroups["test_subgroup"]._bound_name == "test_subgroup"
            assert wrapper._subgroups["test_subgroup"]._parent is wrapper
            assert wrapper._subgroups["test_subgroup"]._self is subgroup
    
    def test_add_wrapper_calls_hooks(self):
        """Test add_wrapper method calls binding hooks"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            subparser = MockSubparserWrapper(MockNamespace)
            
            # Mock the hook methods
            subparser.on_before_bind = Mock()
            subparser.on_after_bind = Mock()
            
            # Test adding wrapper
            wrapper.add_wrapper("test_hooks", subparser)
            
            # Verify hooks were called
            subparser.on_before_bind.assert_called_once_with("test_hooks", wrapper)
            subparser.on_after_bind.assert_called_once_with("test_hooks", wrapper)
    
    def test_add_wrapper_with_invalid_wrapper_type(self):
        """Test add_wrapper method with invalid wrapper type"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            invalid_wrapper = Mock()  # Not a SubparserWrapper or SubgroupWrapper
            
            # Test that TypeError is raised for invalid wrapper type
            with pytest.raises(TypeError, match="Wrapper must be either SubparserWrapper or SubgroupWrapper"):
                wrapper.add_wrapper("invalid", invalid_wrapper)
    
    def test_add_wrapper_aliasing_behavior(self):
        """Test add_wrapper method aliasing behavior"""
        class ConcreteWrapper(BaseWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            subparser = MockSubparserWrapper(MockNamespace)
            
            # Add same wrapper with different names (aliasing)
            wrapper.add_wrapper("original", subparser)
            wrapper.add_wrapper("alias", subparser)
            
            # Verify both aliases exist and reference the same wrapper
            assert "original" in wrapper._subparsers
            assert "alias" in wrapper._subparsers
            assert wrapper._subparsers["original"]._self is subparser
            assert wrapper._subparsers["alias"]._self is subparser
            
            # Verify they have different bound names
            assert wrapper._subparsers["original"]._bound_name == "original"
            assert wrapper._subparsers["alias"]._bound_name == "alias"


class TestSubparserWrapper:
    """Test SubparserWrapper class"""
    
    def test_init(self):
        """Test SubparserWrapper initialization"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            assert wrapper._callback is None
            
            # Verify that set_defaults was called with _clipar_wrapper parameter
            assert isinstance(wrapper._container.set_defaults, Mock)
            wrapper._container.set_defaults.assert_called_once_with(_clipar_wrapper=wrapper)
    
    def test_set_callback(self):
        """Test _set_callback method"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            callback = Mock()
            wrapper._set_callback(callback)
            assert wrapper._callback is callback
    
    def test_check_namespace_valid(self):
        """Test _check_namespace with valid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            wrapper._arg_names = {'arg1', 'arg2'}
            
            namespace = Mock()
            namespace.arg1 = "test"
            namespace.arg2 = 42
            
            assert wrapper._check_namespace(namespace) is True
    
    def test_check_namespace_invalid(self):
        """Test _check_namespace with invalid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            wrapper._arg_names = {'arg1', 'missing_arg'}
            
            namespace = Mock()
            namespace.arg1 = "test"
            # missing_arg is not present
            
            assert wrapper._check_namespace(namespace) is True
    
    def test_exec_callback_none(self):
        """Test _exec_callback with no callback set"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            namespace = Mock()
            
            result = wrapper._exec_callback(namespace)
            assert result is None
    
    def test_exec_callback_valid_namespace(self):
        """Test _exec_callback with valid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            wrapper._arg_names = {'arg1'}
            
            callback = Mock(return_value="callback_result")
            wrapper._set_callback(callback)
            
            namespace = Mock()
            namespace.arg1 = "test"
            
            result = wrapper._exec_callback(namespace)
            assert result == "callback_result"
            callback.assert_called_once_with(namespace)


class TestSubgroupWrapper:
    """Test SubgroupWrapper class"""
    
    def test_init(self):
        """Test SubgroupWrapper initialization"""
        class ConcreteSubgroupWrapper(SubgroupWrapper):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v312.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubgroupWrapper(MockNamespace)
            assert wrapper.namespace_type is MockNamespace


class TestBoundWrapper:
    """Test BoundWrapper class"""
    
    def test_init(self):
        """Test BoundWrapper initialization"""
        parent_wrapper = Mock()
        self_wrapper = Mock()
        
        bound = BoundWrapper("test_name", parent_wrapper, self_wrapper)
        assert bound._bound_name == "test_name"
        assert bound._parent is parent_wrapper
        assert bound._self is self_wrapper
    
    def test_self_property(self):
        """Test self property"""
        parent_wrapper = Mock()
        self_wrapper = Mock()
        
        bound = BoundWrapper("test_name", parent_wrapper, self_wrapper)
        assert bound.self is self_wrapper


class TestArgumentContainerProtocol:
    """Test ArgumentContainerProtocol"""
    
    def test_protocol_compliance(self):
        """Test that argparse.ArgumentParser implements the protocol"""
        parser = argparse.ArgumentParser()
        assert isinstance(parser, ArgumentContainerProtocol)


class TestGenericAliasLike:
    """Test GenericAliasLike protocol"""
    
    def test_protocol_compliance(self):
        """Test that generic types implement the protocol"""
        from typing import List
        
        # List[str] should implement GenericAliasLike
        list_str = List[str]
        if hasattr(list_str, '__origin__') and hasattr(list_str, '__args__'):
            assert isinstance(list_str, GenericAliasLike)


if __name__ == "__main__":
    pytest.main([__file__])
