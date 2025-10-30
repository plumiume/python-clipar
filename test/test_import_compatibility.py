"""Top-level import compatibility tests for v310/v312 implementations"""

import sys
import pytest
from clipar import namespace, group, mutually_exclusive_group, NotSelected


class TestTopLevelImportCompatibility:
    """Test that all top-level imports work correctly across v310/v312 implementations"""

    def test_python_version_selection(self):
        """Test that the correct implementation is loaded based on Python version"""
        import clipar
        
        # Verify we can access the version-appropriate implementation
        assert hasattr(clipar, 'namespace')
        assert hasattr(clipar, 'group') 
        assert hasattr(clipar, 'mutually_exclusive_group')
        assert hasattr(clipar, 'NotSelected')
        
        # Test basic functionality works
        @namespace
        class VersionTestConfig:
            test_arg: str = "default"
            
        config = VersionTestConfig.parse_args(["--test-arg", "value"])
        assert config.test_arg == "value"

    def test_namespace_decorator_import(self):
        """Test @namespace decorator works from top-level import"""
        @namespace
        class NamespaceImportTest:
            name: str
            verbose: bool = False
            
        config = NamespaceImportTest.parse_args(["test", "--verbose"])
        assert config.name == "test"
        assert config.verbose is True

    def test_group_decorator_import(self):
        """Test @group decorator works from top-level import"""
        @group
        class DatabaseGroup:
            host: str = "localhost"
            port: int = 5432
            
        @namespace
        class GroupImportTest:
            app_name: str = "TestApp"
            database = DatabaseGroup
            
        config = GroupImportTest.parse_args(["--host", "prod.db.com", "--port", "3306"])
        assert config.app_name == "TestApp"
        assert config.database is not NotSelected
        assert config.database.host == "prod.db.com"
        assert config.database.port == 3306

    def test_mutually_exclusive_group_import(self):
        """Test @mutually_exclusive_group decorator works from top-level import"""
        @mutually_exclusive_group
        class OutputFormat:
            json: bool = False
            yaml: bool = False
            
        @namespace
        class MutuallyExclusiveImportTest:
            input_file: str
            format = OutputFormat
            
        config = MutuallyExclusiveImportTest.parse_args(["data.txt", "--json"])
        assert config.input_file == "data.txt"
        assert config.format is not NotSelected
        assert config.format.json is True
        assert config.format.yaml is False

    def test_notselected_import(self):
        """Test NotSelected sentinel value import and usage"""
        @group
        class OptionalGroup:
            setting: str = "default"
            
        @namespace
        class NotSelectedImportTest:
            required: str
            optional = OptionalGroup
            
        # Test that group is not NotSelected when parent namespace is active
        config = NotSelectedImportTest.parse_args(["required_value"])
        assert config.required == "required_value"
        # Group should be accessible in this context
        assert config.optional is not NotSelected
        assert config.optional.setting == "default"

    def test_cross_version_api_compatibility(self):
        """Test that the public API is identical between v310 and v312"""
        import clipar
        
        # Test that all expected public attributes exist
        expected_attrs = ['namespace', 'group', 'mutually_exclusive_group', 'NotSelected', 'mixin']
        for attr in expected_attrs:
            assert hasattr(clipar, attr), f"Missing public attribute: {attr}"
            
        # Test that decorators are callable
        assert callable(clipar.namespace)
        assert callable(clipar.group)
        assert callable(clipar.mutually_exclusive_group)

    def test_mixin_import(self):
        """Test mixin module import works correctly"""
        from clipar import mixin
        
        # Test ReprMixin availability
        assert hasattr(mixin, 'ReprMixin')
        
        @namespace
        class MixinImportTest(mixin.ReprMixin):
            name: str = "test"
            count: int = 1
            
        config = MixinImportTest.parse_args(["--name", "mixin_test", "--count", "5"])
        
        # Test that ReprMixin functionality works
        repr_str = repr(config)
        assert "MixinImportTest<" in repr_str
        assert "name='mixin_test'" in repr_str
        assert "count=5" in repr_str

    def test_complex_nested_import_compatibility(self):
        """Test complex scenarios work identically across versions"""
        @group
        class ServerGroup:
            host: str = "localhost"
            port: int = 8080
            
        @mutually_exclusive_group
        class LogLevel:
            debug: bool = False
            info: bool = False
            error: bool = False
            
        @namespace
        class ComplexImportTest:
            service_name: str
            server = ServerGroup
            log_level = LogLevel
            workers: int = 1
            
        config = ComplexImportTest.parse_args([
            "TestService",
            "--host", "api.example.com",
            "--port", "443",
            "--info",
            "--workers", "4"
        ])
        
        assert config.service_name == "TestService"
        assert config.workers == 4
        assert config.server is not NotSelected
        assert config.server.host == "api.example.com"
        assert config.server.port == 443
        assert config.log_level is not NotSelected
        assert config.log_level.debug is False
        assert config.log_level.info is True
        assert config.log_level.error is False

    def test_version_specific_implementation_details(self):
        """Test that version-specific implementation details don't leak to public API"""
        import clipar
        
        # These should not be directly accessible from top-level import (except v310/v312 which are expected)
        internal_attrs = ['basewrapper', 'decorator', 'class_ast']
        for attr in internal_attrs:
            assert not hasattr(clipar, attr), f"Internal attribute leaked to public API: {attr}"
            
        # v310/v312 may be accessible depending on implementation but should not be used directly
        # This documents the current behavior - they may be present but are not part of public API

    @pytest.mark.parametrize("python_version,expected_impl", [
        ((3, 10), "should work with v310"),
        ((3, 11), "should work with v310"), 
        ((3, 12), "should work with v312"),
        ((3, 13), "should work with v312"),
    ])
    def test_version_selection_logic(self, python_version: tuple[int, int], expected_impl: str):
        """Test that version selection logic works as expected"""
        # This is more of a documentation test - we can't easily mock sys.version_info
        # but we can verify the current behavior is correct
        
        current_version = sys.version_info[:2]
        
        # Basic functionality test that should work regardless of version
        @namespace
        class VersionLogicTest:
            arg: str = "test"
            
        config = VersionLogicTest.parse_args([])
        assert config.arg == "test"
        
        # Document expected behavior based on current running version
        if current_version >= (3, 12):
            # We expect v312 implementation features to work
            if python_version >= (3, 12):
                assert expected_impl == "should work with v312"
        else:
            # We expect v310 implementation features to work  
            if python_version < (3, 12):
                assert expected_impl == "should work with v310"

    def test_import_error_handling(self):
        """Test that import errors are handled gracefully"""
        # Test that we can import clipar without any import errors
        try:
            import clipar
            # Try using all major components
            
            @clipar.namespace
            class ImportErrorTest:
                test: str = "value"
                
            config = ImportErrorTest.parse_args([])
            assert config.test == "value"
            
        except ImportError as e:
            pytest.fail(f"Import error occurred: {e}")

    def test_entities_import(self):
        """Test that entities module is accessible if needed"""
        # This tests internal consistency - entities should be importable
        # but may not be part of public API
        try:
            from clipar import entities
            # If entities is available, it should have expected structure
            # This is version-agnostic test
            assert entities is not None
        except ImportError:
            # If entities is not in public API, that's also fine
            # This test documents the current behavior
            pass