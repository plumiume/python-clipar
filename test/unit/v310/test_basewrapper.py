"""Unit tests for basewrapper.py"""

# pyright: reportPrivateUsage=false

from typing import TypeVar
import sys
import pytest
import argparse
from unittest.mock import Mock, patch

from clipar.v310.basewrapper import (
    BaseWrapper, SubparserWrapper, SubgroupWrapper, BoundWrapper,
    NotSelected, NotSelectedType,
    _return_bool, _append_list, _get_attr_names, # pyright: ignore[reportPrivateUsage]
    ArgumentContainerProtocol, GenericAliasLike,
    OBJECT_ATTRS
)

if sys.version_info >= (3, 12):
    from typing import TypeAliasType
else:
    from typing_extensions import TypeAliasType
from types import UnionType

UserId = TypeAliasType("UserId", int)
UserName = TypeAliasType("UserName", str)
CustomStr = TypeAliasType("CustomStr", str)

_NS = TypeVar('_NS')


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

    def test_get_attr_names_simple_class(self):
        """Test _get_attr_names with a simple class"""
        class SimpleClass:
            x: int = 10
            y: str = "test"

        attr_names = list(_get_attr_names(SimpleClass))
        assert 'x' in attr_names
        assert 'y' in attr_names

    def test_get_attr_names_inherited_class(self):
        """Test _get_attr_names with inherited classes"""
        class BaseClass:
            base_attr: str = "base"

        class DerivedClass(BaseClass):
            derived_attr: int = 42

        attr_names = list(_get_attr_names(DerivedClass))
        assert 'base_attr' in attr_names
        assert 'derived_attr' in attr_names

    def test_get_attr_names_with_slots(self):
        """Test _get_attr_names with __slots__"""
        class SlottedClass:
            __slots__ = ('x', 'y')

        attr_names = list(_get_attr_names(SlottedClass))
        assert 'x' in attr_names
        assert 'y' in attr_names

    def test_get_attr_names_mixed_inheritance(self):
        """Test _get_attr_names with mixed inheritance (slots and dict)"""
        class SlottedBase:
            __slots__ = ('slot_attr',)

        class DictDerived(SlottedBase):
            dict_attr: str = "test"

        attr_names = list(_get_attr_names(DictDerived))
        assert 'slot_attr' in attr_names
        assert 'dict_attr' in attr_names

    def test_get_attr_names_complex_inheritance_chain(self):
        """Test complex inheritance chain attribute resolution"""
        
        class GrandParent:
            grand_attr: str = "grand"

        class Parent(GrandParent):
            parent_attr: int = 20

        class Child(Parent):
            child_attr: bool = True

        attr_names = list(_get_attr_names(Child))
        
        # All attributes from inheritance chain should be present
        assert 'grand_attr' in attr_names
        assert 'parent_attr' in attr_names
        assert 'child_attr' in attr_names

    def test_get_attr_names_multiple_inheritance(self):
        """Test that method resolution order is preserved in _get_attr_names"""
        
        class A:
            a_attr: str = "A"

        class B:
            b_attr: str = "B"

        class C(A, B):
            c_attr: str = "C"

        attr_names = list(_get_attr_names(C))
        
        # All attributes should be present regardless of MRO complexity
        assert 'a_attr' in attr_names
        assert 'b_attr' in attr_names
        assert 'c_attr' in attr_names


class TestNotSelectedType:
    """Test NotSelected type and singleton"""
    
    def test_not_selected_singleton(self):
        """Test NotSelected singleton behavior"""
        assert NotSelected is NotSelectedType.I
        assert bool(NotSelected) is False
        assert repr(NotSelected) == "NotSelected"


class TestConstants:
    """Test module constants"""
    
    def test_object_attrs_constant(self):
        """Test OBJECT_ATTRS contains expected object attributes"""
        assert isinstance(OBJECT_ATTRS, set)
        assert '__class__' in OBJECT_ATTRS
        assert '__init__' in OBJECT_ATTRS
        assert '__str__' in OBJECT_ATTRS
        assert '__repr__' in OBJECT_ATTRS
    
    def test_literalizable_type(self):
        """Test that Literalizable type covers expected types"""
        # Test that various literal values are of Literalizable type
        test_values: list[str | int | float | bool | None] = ["string", 42, 3.14, True, False, None]
        for value in test_values:
            # This is a runtime check since we can't directly check type alias
            assert isinstance(value, (str, int, float, bool, type(None)))


class TestUnionTypeSupport:
    """Test UnionType support in basewrapper"""
    
    def test_union_type_creation(self):
        """Test that UnionType can be created and used"""
        # Create a UnionType (str | int)
        union_type = str | int
        assert isinstance(union_type, UnionType)
        assert hasattr(union_type, '__args__')
        assert str in union_type.__args__
        assert int in union_type.__args__


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
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        # Mock ClassAstHolder to avoid file system dependencies
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            assert wrapper.namespace_type is MockNamespace
            assert isinstance(wrapper._subparsers, dict)
            assert isinstance(wrapper._subgroups, dict)
            assert isinstance(wrapper._arg_names, set)
    
    def test_namespace_type_property(self):
        """Test namespace_type property"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            assert wrapper.T is MockNamespace
    
    def test_get_descriptor_with_none_instance(self):
        """Test __get__ method with None instance"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper.__get__(None, MockNamespace)
            assert result is wrapper
    
    def test_get_descriptor_with_type_instance(self):
        """Test __get__ method with type instance"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper.__get__(MockNamespace, None)
            assert result is wrapper
    
    def test_get_descriptor_with_object_instance(self):
        """Test __get__ method with object instance"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            instance = MockNamespace()
            result = wrapper.__get__(instance, MockNamespace)
            assert result is NotSelected
    
    def test_update_container(self):
        """Test update_container method"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            new_container = Mock(spec=ArgumentContainerProtocol)
            wrapper.update_container(new_container)
            assert wrapper._container is new_container
    
    def test_parse_annotation_basic_type(self):
        """Test _parse_annotation with basic types"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._parse_annotation(str)
            assert 'type' in result
            assert result['type'] is str
    
    def test_parse_annotation_literal(self):
        """Test _parse_annotation with Literal types"""
        from typing import Literal
        
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._parse_annotation(Literal['a', 'b', 'c'])
            assert 'choices' in result
            assert result['choices'] is not None
            assert set(result['choices']) == {'a', 'b', 'c'}
    
    def test_flatten_union_and_literal(self):
        """Test _flatten_union_and_literal method"""
        from typing import Literal
        
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            literal_type = Literal['test']
            assert isinstance(literal_type, GenericAliasLike)
            result = wrapper._flatten_union_and_literal((str, int, literal_type))
            assert str in result
            assert int in result
    
    def test_parse_annotation_with_type_alias(self):
        """Test _parse_annotation with TypeAliasType from typing_extensions"""
        try:
            class ConcreteWrapper(BaseWrapper[_NS]):
                def configure_container(self):
                    return Mock(spec=ArgumentContainerProtocol)
            
            with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
                mock_ast.return_value.get_assign_infos.return_value = {}
                
                wrapper = ConcreteWrapper(MockNamespace)
                result = wrapper._parse_annotation(UserId)
                assert 'type' in result
                assert callable(result['type'])
                assert result['type']("42") == 42
        except ImportError:
            pytest.skip("typing_extensions.TypeAliasType not available")
    
    def test_determine_nargs_and_generic_args_with_type_alias(self):
        """Test _determine_nargs_and_generic_args with TypeAliasType"""
        try:
            class ConcreteWrapper(BaseWrapper[_NS]):
                def configure_container(self):
                    return Mock(spec=ArgumentContainerProtocol)
            
            with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
                mock_ast.return_value.get_assign_infos.return_value = {}
                
                wrapper = ConcreteWrapper(MockNamespace)
                nargs, args = wrapper._determine_nargs_and_generic_args(CustomStr)
                assert nargs is None
                assert args == (str,)
        except ImportError:
            pytest.skip("typing_extensions.TypeAliasType not available")
    
    def test_flatten_union_and_literal_with_type_alias(self):
        """Test _flatten_union_and_literal with resolved type from type alias"""
        try:
            
            class ConcreteWrapper(BaseWrapper[_NS]):
                def configure_container(self):
                    return Mock(spec=ArgumentContainerProtocol)
            
            with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
                mock_ast.return_value.get_assign_infos.return_value = {}
                
                wrapper = ConcreteWrapper(MockNamespace)
                
                # _flatten_union_and_literal receives resolved types, not TypeAliasType directly
                # The TypeAliasType should be resolved before calling this method
                resolved_type = wrapper._resolve_type_alias_type(UserName)
                result = wrapper._flatten_union_and_literal((str, resolved_type))
                # Type alias should be resolved to str
                assert str in result
        except ImportError:
            pytest.skip("typing_extensions.TypeAliasType not available")
    
    def test_get_type_from_type_or_generic_alias(self):
        """Test _get_type_from_type_or_generic_alias method"""
        from typing import List
        
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            
            # Test with basic type
            assert wrapper._get_type_from_type_or_generic_alias(str) is str
            
            # Test with generic alias
            assert wrapper._get_type_from_type_or_generic_alias(List[str]) is list
    
    def test_flatten_subparsers_empty(self):
        """Test _flatten_subparsers with empty subparsers"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._flatten_subparsers()
            assert result == []
    
    def test_flatten_subgroups_empty(self):
        """Test _flatten_subgroups with empty subgroups"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            result = wrapper._flatten_subgroups()
            assert result == []
    
    def test_bind(self):
        """Test _bind method"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            parent_wrapper = Mock()
            
            bound = wrapper._bind("test_name", parent_wrapper)
            assert isinstance(bound, BoundWrapper)
    
    def test_hook_methods(self):
        """Test hook methods (should not raise exceptions)"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            
            # These should not raise exceptions
            wrapper.on_before_bind("test", Mock())
            wrapper.on_after_bind("test", Mock())
            wrapper.on_before_parse(["test"], Mock())
            wrapper.on_after_parse(["test"], Mock())
    
    def test_add_wrapper_with_subparser(self):
        """Test add_wrapper method with SubparserWrapper"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubgroupWrapper(SubgroupWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteWrapper(MockNamespace)
            invalid_wrapper = Mock()  # Not a SubparserWrapper or SubgroupWrapper
            
            # Test that TypeError is raised for invalid wrapper type
            with pytest.raises(TypeError, match="Wrapper must be either SubparserWrapper or SubgroupWrapper"):
                wrapper.add_wrapper("invalid", invalid_wrapper)
    
    def test_add_wrapper_aliasing_behavior(self):
        """Test add_wrapper method aliasing behavior"""
        class ConcreteWrapper(BaseWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        class MockSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            assert wrapper._callback is None
            
            # Verify that set_defaults was called with _clipar_wrapper parameter
            assert isinstance(wrapper._container.set_defaults, Mock)
            wrapper._container.set_defaults.assert_called_once_with(_clipar_wrapper=wrapper)
    
    def test_set_callback(self):
        """Test _set_callback method"""
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            callback = Mock()
            wrapper._set_callback(callback)
            assert wrapper._callback is callback
    
    def test_check_namespace_valid(self):
        """Test _check_namespace with valid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            wrapper._arg_names = {'arg1', 'arg2'}
            
            namespace = Mock()
            namespace.arg1 = "test"
            namespace.arg2 = 42
            
            assert wrapper._check_namespace(namespace) is True
    
    def test_check_namespace_invalid(self):
        """Test _check_namespace with invalid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            wrapper._arg_names = {'arg1', 'missing_arg'}
            
            namespace = Mock()
            namespace.arg1 = "test"
            # missing_arg is not present
            
            assert wrapper._check_namespace(namespace) is True
    
    def test_exec_callback_none(self):
        """Test _exec_callback with no callback set"""
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = ConcreteSubparserWrapper(MockNamespace)
            namespace = Mock()
            
            result = wrapper._exec_callback(namespace)
            assert result is None
    
    def test_exec_callback_valid_namespace(self):
        """Test _exec_callback with valid namespace"""
        class ConcreteSubparserWrapper(SubparserWrapper[_NS]):
            def configure_container(self):
                mock_container = Mock(spec=ArgumentContainerProtocol)
                mock_container.set_defaults = Mock()
                return mock_container
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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
        class ConcreteSubgroupWrapper(SubgroupWrapper[_NS]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
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


class TestInheritanceFeatures:
    """Test new inheritance functionality in BaseWrapper"""

    def test_wrapper_creation_with_inherited_class(self):
        """Test that BaseWrapper can be created with an inherited class"""
        
        class BaseConfig:
            base_option: str = "default_base"
            base_flag: bool = False

        class DerivedConfig(BaseConfig):
            derived_option: int = 10
            derived_required: str  # No default, should be required

        class TestWrapper(BaseWrapper[DerivedConfig]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)

        # Mock ClassAstHolder to avoid dependency issues  
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            # Should not raise an exception
            wrapper = TestWrapper(DerivedConfig)
            assert wrapper is not None
            assert wrapper.namespace_type == DerivedConfig

    def test_exception_handling_during_initialization(self):
        """Test that ClassAstHolder exceptions are properly handled"""
        
        # Create a class that will cause ClassAstHolder to fail
        DynamicClass = type('DynamicClass', (), {
            'attr': 'value',
            '__annotations__': {'required_attr': str}
        })

        class TestWrapper(BaseWrapper[object]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)

        # Mock ClassAstHolder to raise an exception
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.side_effect = OSError("Cannot get source")
            
            # This should not raise an exception even if ClassAstHolder fails
            wrapper = TestWrapper(DynamicClass)
            assert wrapper is not None

    def test_init_container_with_inherited_attributes(self):
        """Test _init_container handles inherited attributes correctly"""
        
        class BaseConfig:
            base_option: str = "default_base"
            base_flag: bool = False

        class DerivedConfig(BaseConfig):
            derived_option: int = 10
            derived_required: str  # No default, should be required

        class TestWrapper(BaseWrapper[DerivedConfig]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)

        # Mock ClassAstHolder and _get_attr_names for controlled testing
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast, \
             patch('clipar.v310.basewrapper._get_attr_names') as mock_get_attrs:
            
            mock_ast.return_value.get_assign_infos.return_value = {}
            mock_get_attrs.return_value = ['base_option', 'base_flag', 'derived_option', 'derived_required']
            
            wrapper = TestWrapper(DerivedConfig)
            
        # Verify that the wrapper was created successfully
        assert wrapper is not None
        assert wrapper.namespace_type == DerivedConfig

    def test_mixin_attributes_excluded_from_processing(self):
        """Test that BaseMixin attributes are excluded from argument processing"""
        from clipar.v310.mixin import BaseMixin
        
        class TestConfig(BaseMixin):
            # Regular attributes that should be processed
            name: str = "default"
            count: int = 42
            
            # These should be inherited from BaseMixin and excluded
            # clipar_mixin_dict should be excluded
        
        class TestWrapper(BaseWrapper[TestConfig]):
            def configure_container(self):
                return Mock(spec=ArgumentContainerProtocol)
        
        with patch('clipar.v310.basewrapper.ClassAstHolder') as mock_ast:
            mock_ast.return_value.get_assign_infos.return_value = {}
            
            wrapper = TestWrapper(TestConfig)
            
            # Only user-defined attributes should be in _arg_names
            # clipar_mixin_dict should NOT be there
            assert 'name' in wrapper._arg_names
            assert 'count' in wrapper._arg_names
            assert 'clipar_mixin_dict' not in wrapper._arg_names
if __name__ == "__main__":
    pytest.main([__file__])
