"""Pytest configuration for clipar tests"""

import pytest
import sys
from pathlib import Path

# Add the src directory to Python path so tests can import modules
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_args():
    """Sample command line arguments for testing"""
    return ["--verbose", "--output", "test.txt", "--count", "5"]


@pytest.fixture
def complex_args():
    """Complex command line arguments with subcommands"""
    return ["process", "--input", "data.csv", "--format", "json", "--verbose"]
