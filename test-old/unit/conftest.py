"""Pytest configuration and test runner"""

import pytest
import sys
from pathlib import Path

# Add the src directory to Python path so tests can import modules
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_all_modules():
    """Test that all main modules can be imported"""
    try:
        import clipar.v312.basewrapper
        import clipar.v312.class_ast
        import clipar.v312.decorator
        import clipar.v312.namespacewrapper
        import clipar.v312.groupwrapper
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


if __name__ == "__main__":
    # Run all tests
    pytest.main([
        "test_basewrapper.py",
        "test_class_ast.py", 
        "test_decorator.py",
        "test_namespacewrapper.py",
        "test_groupwrapper.py",
        "test_init.py",
        "-v"
    ])
