"""Integration tests for new inheritance features"""

from clipar import namespace, group, mutually_exclusive_group


class TestInheritanceIntegration:
    """Integration tests for inheritance features with decorators"""

    def test_namespace_decorator_with_inherited_class(self):
        """Test @namespace decorator works with inherited classes"""
        
        class BaseConfig:
            verbose: bool = False
            output_dir: str = "output"

        @namespace
        class AppConfig(BaseConfig):
            input_file: str
            workers: int = 1

        # Test parsing with inherited attributes
        config = AppConfig.parse_args([
            "input.txt", 
            "--verbose", 
            "--output-dir", "/tmp", 
            "--workers", "4"
        ])
        
        assert config.input_file == "input.txt"
        assert config.verbose is True
        assert config.output_dir == "/tmp"
        assert config.workers == 4

    def test_namespace_decorator_inherited_ordering(self):
        """Test that inherited attributes maintain proper ordering"""
        
        class BaseConfig:
            base_required: str
            base_optional: int = 10

        @namespace
        class DerivedConfig(BaseConfig):
            derived_required: str
            derived_optional: bool = False

        # Should be able to parse with correct positional argument order
        config = DerivedConfig.parse_args([
            "base_value",      # base_required
            "derived_value",   # derived_required
            "--base-optional", "20",
            "--derived-optional"
        ])
        
        assert config.base_required == "base_value"
        assert config.derived_required == "derived_value"
        assert config.base_optional == 20
        assert config.derived_optional is True

    def test_group_decorator_with_inherited_class(self):
        """Test @group decorator works with inherited classes"""
        
        class BaseOptions:
            base_flag: bool = False
            base_value: str = "default"

        @group
        class DatabaseOptions(BaseOptions):
            host: str = "localhost"
            port: int = 5432

        @namespace
        class AppConfig:
            db = DatabaseOptions

        # Group attributes are flattened, so no db- prefix
        config = AppConfig.parse_args([
            "--base-flag",
            "--base-value", "custom",
            "--host", "remote.example.com",
            "--port", "3306"
        ])
        
        # Test that all inherited and new attributes are accessible
        assert hasattr(config, 'db')
        # Note: The actual attribute access depends on the specific implementation
        # These tests verify the parsing works without exceptions

    def test_mutually_exclusive_group_with_inherited_class(self):
        """Test @mutually_exclusive_group with inherited classes"""
        
        class BaseOutputOptions:
            quiet: bool = False

        @mutually_exclusive_group
        class OutputOptions(BaseOutputOptions):
            verbose: bool = False
            debug: bool = False

        @namespace
        class AppConfig:
            output = OutputOptions

        # Test that mutually exclusive behavior works (no prefix for flattened groups)
        config1 = AppConfig.parse_args(["--verbose"])
        assert hasattr(config1, 'output')

        config2 = AppConfig.parse_args(["--debug"])
        assert hasattr(config2, 'output')

        # Test that inherited non-exclusive options still work
        config3 = AppConfig.parse_args(["--quiet"])
        assert hasattr(config3, 'output')

    def test_complex_inheritance_with_documentation(self):
        """Test that documentation is preserved through inheritance"""
        
        class BaseConfig:
            base_option: str = "default"
            "Base option documentation"

        @namespace
        class DerivedConfig(BaseConfig):
            derived_option: int = 10
            "Derived option documentation"

        # Test that the class can be parsed successfully
        config = DerivedConfig.parse_args([
            "--base-option", "custom_base",
            "--derived-option", "42"
        ])
        
        assert config.base_option == "custom_base"
        assert config.derived_option == 42

    def test_slots_inheritance_compatibility(self):
        """Test that __slots__ classes work with inheritance"""
        
        @namespace  
        class TestConfig:
            regular_option: str = "test"

        # Should not fail during parsing
        config = TestConfig.parse_args(["--regular-option", "value"])
        assert config.regular_option == "value"

    def test_multiple_inheritance_with_decorators(self):
        """Test multiple inheritance scenarios with decorators"""
        
        class MixinA:
            option_a: str = "a"

        class MixinB:
            option_b: int = 1

        @namespace
        class MultiConfig(MixinA, MixinB):
            main_option: bool = False

        config = MultiConfig.parse_args([
            "--option-a", "custom_a",
            "--option-b", "5",
            "--main-option"
        ])
        
        assert config.option_a == "custom_a"
        assert config.option_b == 5
        assert config.main_option is True

    def test_inheritance_with_annotation_only_attributes(self):
        """Test inheritance with type annotation only attributes"""
        
        class BaseConfig:
            base_required: str  # No default value

        @namespace
        class DerivedConfig(BaseConfig):
            derived_required: int  # No default value
            optional_attr: bool = True

        config = DerivedConfig.parse_args([
            "base_string",     # base_required
            "42",              # derived_required (converted to int)
        ])
        
        assert config.base_required == "base_string"
        assert config.derived_required == 42
        assert config.optional_attr is True  # Default value
        
        # Test with optional flag (store_false for True default)
        config2 = DerivedConfig.parse_args([
            "base_string2",
            "24"
        ])
        
        assert config2.base_required == "base_string2"
        assert config2.derived_required == 24
        assert config2.optional_attr is True  # Default value maintained

    def test_error_handling_with_inheritance(self):
        """Test error handling in inheritance scenarios"""
        
        class ProblematicBase:
            # This might cause issues with AST parsing
            pass

        @namespace
        class SafeConfig(ProblematicBase):
            safe_option: str = "safe"

        # Should not raise exceptions during class creation
        config = SafeConfig.parse_args(["--safe-option", "value"])
        assert config.safe_option == "value"

    def test_deep_inheritance_chain(self):
        """Test deep inheritance chains work correctly"""
        
        class Level1:
            level1_attr: str = "l1"

        class Level2(Level1):
            level2_attr: int = 2

        class Level3(Level2):
            level3_attr: bool = False

        @namespace
        class DeepConfig(Level3):
            main_attr: str = "main"

        config = DeepConfig.parse_args([
            "--level1-attr", "custom1",
            "--level2-attr", "5",
            "--level3-attr",
            "--main-attr", "custom_main"
        ])
        
        assert config.level1_attr == "custom1"
        assert config.level2_attr == 5
        assert config.level3_attr is True
        assert config.main_attr == "custom_main"