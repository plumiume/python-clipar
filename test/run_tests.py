"""
Test runner script for clipar project

This script runs all unit tests for the clipar project using pytest.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests"""
    
    # Get the test directory
    test_dir = Path(__file__).parent
    unit_test_dir = test_dir / "unit"
    
    # Ensure pytest is available
    try:
        import pytest
    except ImportError:
        print("pytest is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        import pytest
    
    # Run pytest with verbose output
    args = [
        str(unit_test_dir / "test_basewrapper.py"),
        str(unit_test_dir / "test_class_ast.py"),
        str(unit_test_dir / "test_decorator.py"),
        str(unit_test_dir / "test_namespacewrapper.py"), 
        str(unit_test_dir / "test_groupwrapper.py"),
        str(unit_test_dir / "test_init.py"),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes"  # Colored output
    ]
    
    print("Running clipar unit tests...")
    print("=" * 50)
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n" + "=" * 50)
        print("All tests passed! ✅")
    else:
        print("\n" + "=" * 50) 
        print("Some tests failed! ❌")
        print(f"Exit code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
