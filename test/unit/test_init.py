"""Test module for __init__.py"""

import pytest

def test_imports():
    """Test that main exports can be imported"""
    from clipar import NotSelected, namespace, group
    
    # Test that NotSelected is available
    assert NotSelected is not None
    
    # Test that decorators are callable
    assert callable(namespace)
    assert callable(group)


def test_notselected_import():
    """Test NotSelected import specifically"""
    from clipar import NotSelected
    from clipar.basewrapper import NotSelected as BaseNotSelected
    
    # Should be the same object
    assert NotSelected is BaseNotSelected


def test_namespace_decorator_import():
    """Test namespace decorator import"""
    from clipar import namespace
    from clipar.decorator import namespace as DecoratorNamespace
    
    # Should be the same function
    assert namespace is DecoratorNamespace


def test_group_decorator_import():
    """Test group decorator import"""
    from clipar import group
    from clipar.decorator import group as DecoratorGroup
    
    # Should be the same function
    assert group is DecoratorGroup


def test_package_structure():
    """Test basic package structure"""
    import clipar
    
    # Test that the package has the expected attributes
    assert hasattr(clipar, 'NotSelected')
    assert hasattr(clipar, 'namespace')
    assert hasattr(clipar, 'group')


class MockNamespace:
    """Mock namespace for testing decorators"""
    arg: str


def test_namespace_decorator_functionality():
    """Test that imported namespace decorator works"""
    from clipar import namespace
    
    # Test that decorator can be applied
    try:
        decorated = namespace(MockNamespace)
        assert decorated is not None
    except Exception as e:
        # If there are import issues, that's what we're testing for
        pytest.fail(f"Namespace decorator failed: {e}")


def test_group_decorator_functionality():
    """Test that imported group decorator works"""
    from clipar import group
    
    # Test that decorator can be applied
    try:
        decorated = group(MockNamespace)
        assert decorated is not None
    except Exception as e:
        # If there are import issues, that's what we're testing for
        pytest.fail(f"Group decorator failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
