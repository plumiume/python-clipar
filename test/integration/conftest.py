"""Pytest configuration for integration tests"""

import pytest
import sys
from pathlib import Path

# Add the src directory to Python path so tests can import modules
src_path = Path(__file__).parent.parent.parent / "src"
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


@pytest.fixture
def namespace_with_subgroups():
    """Sample namespace class with subgroups for testing"""
    from clipar import namespace, group
    
    @group
    class DatabaseConfig:
        host: str = "localhost"
        port: int = 5432
        username: str = "admin"
    
    @group  
    class LoggingConfig:
        level: str = "INFO"
        file: str = "app.log"
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @namespace
    class AppConfig:
        app_name: str = "MyApp"
        version: str = "1.0.0"
        debug: bool = False
        database = DatabaseConfig
        logging = LoggingConfig
    
    return AppConfig
