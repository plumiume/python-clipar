"""Unit tests for clipar.v310.mixin module"""

# pyright: reportPrivateUsage=false

import pytest
from typing import Any
from clipar.v310.mixin import _is_dunder, ReprMixin


class TestIsDunderFunction:
    """Test _is_dunder utility function"""

    def test_is_dunder_valid_dunder_names(self):
        """Test _is_dunder with valid dunder method names"""
        assert _is_dunder("__init__") is True
        assert _is_dunder("__str__") is True
        assert _is_dunder("__repr__") is True
        assert _is_dunder("__len__") is True
        assert _is_dunder("__getitem__") is True
        assert _is_dunder("__setitem__") is True
        assert _is_dunder("__call__") is True

    def test_is_dunder_invalid_dunder_names(self):
        """Test _is_dunder with invalid dunder method names"""
        # Too short (4 or fewer characters)
        assert _is_dunder("__") is False
        assert _is_dunder("___") is False
        assert _is_dunder("____") is False
        
        # Missing leading underscores
        assert _is_dunder("init__") is False
        assert _is_dunder("_init__") is False
        
        # Missing trailing underscores
        assert _is_dunder("__init") is False
        assert _is_dunder("__init_") is False
        
        # Regular method names
        assert _is_dunder("method") is False
        assert _is_dunder("_private") is False
        assert _is_dunder("_private_") is False

    def test_is_dunder_edge_cases(self):
        """Test _is_dunder with edge cases"""
        # Empty string
        assert _is_dunder("") is False
        
        # Just underscores (exactly 4 characters)
        assert _is_dunder("____") is False
        
        # 5 underscores (minimum valid length)
        assert _is_dunder("_____") is True
        
        # Mixed characters with proper dunder format
        assert _is_dunder("__abc__") is True
        assert _is_dunder("__123__") is True
        assert _is_dunder("__a_b__") is True

    def test_is_dunder_with_numbers_and_special_chars(self):
        """Test _is_dunder with numbers and special characters"""
        assert _is_dunder("__version__") is True
        assert _is_dunder("__file__") is True
        assert _is_dunder("__name__") is True
        assert _is_dunder("__doc__") is True
        assert _is_dunder("__dict__") is True


class TestReprMixin:
    """Test ReprMixin class functionality"""

    def test_basic_repr_functionality(self):
        """Test basic __repr__ functionality"""
        class TestClass(ReprMixin):
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = 42
                self.attr3 = True

        obj = TestClass()
        repr_str = repr(obj)
        
        # Should contain class name
        assert "TestClass<" in repr_str
        assert repr_str.endswith(">")
        
        # Should contain attribute names and values
        assert "attr1='value1'" in repr_str
        assert "attr2=42" in repr_str
        assert "attr3=True" in repr_str

    def test_repr_excludes_dunder_methods(self):
        """Test that __repr__ excludes dunder methods"""
        class TestClass(ReprMixin):
            def __init__(self):
                self.public_attr = "public"
        
        obj = TestClass()
        repr_str = repr(obj)
        
        # Should not contain dunder attributes
        assert "__init__" not in repr_str
        assert "__class__" not in repr_str
        assert "__dict__" not in repr_str
        assert "__repr__" not in repr_str
        
        # Should contain public attributes
        assert "public_attr='public'" in repr_str

    def test_repr_with_private_attributes(self):
        """Test __repr__ with private attributes (single underscore)"""
        class TestClass(ReprMixin):
            def __init__(self):
                self.public = "public_value"
                self._private = "private_value"
        
        obj = TestClass()
        repr_str = repr(obj)
        
        # Should contain both public and private attributes
        assert "public='public_value'" in repr_str
        assert "_private='private_value'" in repr_str

    def test_repr_with_no_attributes(self):
        """Test __repr__ with class that has no custom attributes"""
        class EmptyClass(ReprMixin):
            pass
        
        obj = EmptyClass()
        repr_str = repr(obj)
        
        # Should still show class name with angle brackets
        assert repr_str.startswith("EmptyClass<")
        assert repr_str.endswith(">")

    def test_repr_with_methods(self):
        """Test __repr__ with class that has methods"""
        class TestClassWithMethods(ReprMixin):
            def __init__(self):
                self.attr = "value"
            
            def public_method(self):
                return "method result"
            
            def _private_method(self):
                return "private method result"
        
        obj = TestClassWithMethods()
        repr_str = repr(obj)
        
        # Should contain attributes
        assert "attr='value'" in repr_str
        
        # Should contain method names (as they're not dunder)
        assert "public_method=" in repr_str
        assert "_private_method=" in repr_str

    def test_repr_with_property(self):
        """Test __repr__ with properties"""
        class TestClassWithProperty(ReprMixin):
            def __init__(self):
                self._value = "internal"
            
            @property
            def computed_value(self):
                return f"computed_{self._value}"
        
        obj = TestClassWithProperty()
        repr_str = repr(obj)
        
        # Should contain the internal attribute
        assert "_value='internal'" in repr_str
        
        # Should contain the property (computed at repr time)
        assert "computed_value='computed_internal'" in repr_str

    def test_repr_with_complex_attribute_values(self):
        """Test __repr__ with complex attribute values"""

        def callable_attr(x: int) -> int:
            return x + 1

        class TestClass(ReprMixin):
            def __init__(self):
                self.string_attr = "test string"
                self.list_attr = [1, 2, 3]
                self.dict_attr = {"key": "value"}
                self.none_attr = None
                self.callable_attr = callable_attr
        
        obj = TestClass()
        repr_str = repr(obj)
        
        # Should properly represent different types
        assert "string_attr='test string'" in repr_str
        assert "list_attr=[1, 2, 3]" in repr_str
        assert "dict_attr={'key': 'value'}" in repr_str
        assert "none_attr=None" in repr_str
        assert "callable_attr=" in repr_str  # Lambda will have some representation

    def test_repr_attribute_ordering(self):
        """Test that attributes appear in dir() order"""
        class OrderedClass(ReprMixin):
            def __init__(self):
                # Set attributes in specific order
                self.z_attr = "z"
                self.a_attr = "a"
                self.m_attr = "m"
        
        obj = OrderedClass()
        repr_str = repr(obj)
        
        # The exact order depends on dir() implementation
        # Just verify all attributes are present
        assert "z_attr='z'" in repr_str
        assert "a_attr='a'" in repr_str
        assert "m_attr='m'" in repr_str

    def test_repr_with_inheritance(self):
        """Test __repr__ with inherited attributes"""
        class BaseClass:
            def __init__(self):
                self.base_attr = "base_value"
        
        class DerivedClass(BaseClass, ReprMixin):
            def __init__(self):
                super().__init__()
                self.derived_attr = "derived_value"
        
        obj = DerivedClass()
        repr_str = repr(obj)
        
        # Should contain both base and derived attributes
        assert "base_attr='base_value'" in repr_str
        assert "derived_attr='derived_value'" in repr_str
        assert "DerivedClass<" in repr_str

    def test_repr_with_descriptor_attributes(self):
        """Test __repr__ with descriptor attributes"""
        class TestDescriptor:
            def __get__(self, obj: Any, objtype: Any = None):
                return "descriptor_value"
        
        class TestClass(ReprMixin):
            descriptor_attr = TestDescriptor()
            
            def __init__(self):
                self.normal_attr = "normal_value"
        
        obj = TestClass()
        repr_str = repr(obj)
        
        # Should contain both normal and descriptor attributes
        assert "normal_attr='normal_value'" in repr_str
        assert "descriptor_attr='descriptor_value'" in repr_str


class TestIntegrationScenarios:
    """Test integration scenarios for mixin usage"""

    def test_multiple_inheritance_with_repr_mixin(self):
        """Test ReprMixin with multiple inheritance"""
        class Mixin1:
            def __init__(self):
                self.mixin1_attr = "mixin1"
        
        class Mixin2:
            def __init__(self):
                self.mixin2_attr = "mixin2"
        
        class CombinedClass(Mixin1, Mixin2, ReprMixin):
            def __init__(self):
                Mixin1.__init__(self)
                Mixin2.__init__(self)
                self.own_attr = "own"
        
        obj = CombinedClass()
        repr_str = repr(obj)
        
        # Should contain attributes from all mixins
        assert "mixin1_attr='mixin1'" in repr_str
        assert "mixin2_attr='mixin2'" in repr_str
        assert "own_attr='own'" in repr_str

    def test_repr_mixin_with_slots(self):
        """Test ReprMixin with __slots__"""
        class SlottedClass(ReprMixin):
            __slots__ = ['slot_attr1', 'slot_attr2']
            
            def __init__(self):
                self.slot_attr1 = "slot1"
                self.slot_attr2 = "slot2"
        
        obj = SlottedClass()
        repr_str = repr(obj)
        
        # Should work with slotted classes
        assert "SlottedClass<" in repr_str
        assert "slot_attr1='slot1'" in repr_str
        assert "slot_attr2='slot2'" in repr_str


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_repr_with_exception_raising_attribute(self):
        """Test __repr__ when attribute access raises exception"""
        class ProblematicClass(ReprMixin):
            def __init__(self):
                self.normal_attr = "normal"
            
            @property
            def problematic_attr(self):
                raise ValueError("Cannot access this attribute")
        
        obj = ProblematicClass()
        
        # __repr__ should raise the exception when attribute access fails
        with pytest.raises(ValueError, match="Cannot access this attribute"):
            repr(obj)

    def test_repr_with_recursive_structure(self):
        """Test __repr__ with potentially recursive structures"""
        class RecursiveClass(ReprMixin):
            def __init__(self):
                self.normal_attr = "value"
                self.self_ref = self  # Self-reference
        
        obj = RecursiveClass()
        
        # Should handle self-reference without infinite recursion
        repr_str = repr(obj)
        assert "RecursiveClass<" in repr_str
        assert "normal_attr='value'" in repr_str
        # self_ref will show as object representation
