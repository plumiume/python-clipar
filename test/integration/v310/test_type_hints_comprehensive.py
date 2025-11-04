"""Comprehensive type hints integration tests for optional arguments (v310)

This test suite covers all possible type hint patterns for optional arguments,
with one argument per test class for clear isolation and debugging.

Note: Uses typing module syntax compatible with Python 3.10/3.11.
"""

from typing import Literal, Optional, Union, List, Tuple
from clipar import namespace


class TestBasicTypes:
    """Test basic built-in types"""

    def test_str_optional(self):
        """Test optional str argument"""
        @namespace
        class Config:
            name: str = "default"
        
        result = Config.parse_args([])
        assert result.name == "default"
        
        result = Config.parse_args(["--name", "custom"])
        assert result.name == "custom"

    def test_int_optional(self):
        """Test optional int argument"""
        @namespace
        class Config:
            count: int = 10
        
        result = Config.parse_args([])
        assert result.count == 10
        
        result = Config.parse_args(["--count", "25"])
        assert result.count == 25

    def test_float_optional(self):
        """Test optional float argument"""
        @namespace
        class Config:
            rate: float = 1.5
        
        result = Config.parse_args([])
        assert result.rate == 1.5
        
        result = Config.parse_args(["--rate", "2.7"])
        assert result.rate == 2.7

    def test_bool_optional_false_default(self):
        """Test optional bool argument with False default (store_true)"""
        @namespace
        class Config:
            verbose: bool = False
        
        result = Config.parse_args([])
        assert result.verbose is False
        
        result = Config.parse_args(["--verbose"])
        assert result.verbose is True

    def test_bool_optional_true_default(self):
        """Test optional bool argument with True default (store_false)"""
        @namespace
        class Config:
            quiet: bool = True
        
        result = Config.parse_args([])
        assert result.quiet is True
        
        result = Config.parse_args(["--quiet"])
        assert result.quiet is False


class TestLiteralTypes:
    """Test Literal type hints"""

    def test_literal_str(self):
        """Test Literal with string values"""
        @namespace
        class Config:
            mode: Literal["fast", "slow", "balanced"] = "balanced"
        
        result = Config.parse_args([])
        assert result.mode == "balanced"
        
        result = Config.parse_args(["--mode", "fast"])
        assert result.mode == "fast"

    def test_literal_int(self):
        """Test Literal with integer values"""
        @namespace
        class Config:
            level: Literal[1, 2, 3, 4, 5] = 3
        
        result = Config.parse_args([])
        assert result.level == 3
        
        result = Config.parse_args(["--level", "5"])
        assert result.level == 5


class TestUnionTypes:
    """Test Union type hints (using Union[] for Python 3.10)"""

    def test_union_str_int(self):
        """Test Union[str, int]"""
        @namespace
        class Config:
            value: Union[str, int] = "default"
        
        result = Config.parse_args([])
        assert result.value == "default"
        
        result = Config.parse_args(["--value", "text"])
        assert result.value == "text"

    def test_union_int_float(self):
        """Test Union[int, float]"""
        @namespace
        class Config:
            threshold: Union[int, float] = 10
        
        result = Config.parse_args([])
        assert result.threshold == 10
        
        result = Config.parse_args(["--threshold", "15"])
        assert result.threshold == 15

    def test_union_three_types(self):
        """Test union with three types"""
        @namespace
        class Config:
            value: Union[int, float, str] = 42
        
        result = Config.parse_args([])
        assert result.value == 42
        
        result = Config.parse_args(["--value", "text"])
        assert result.value == "text"


class TestUnionWithLiteral:
    """Test Union combined with Literal"""

    def test_union_int_literal_str(self):
        """Test Union[int, Literal[str values]]"""
        @namespace
        class Config:
            size: Union[int, Literal["small", "large"]] = "small"
        
        result = Config.parse_args([])
        assert result.size == "small"
        
        result = Config.parse_args(["--size", "100"])
        assert result.size == 100
        
        result = Config.parse_args(["--size", "large"])
        assert result.size == "large"

    # TODO: Union types are processed in order of appearance. When str appears first,
    # it successfully converts any string, preventing subsequent types from being tried.
    # For numeric string conversion, place specific types (int, Literal) before str.
    def test_union_str_literal_int(self):
        """Test Union[str, Literal[int values]]"""
        @namespace
        class Config:
            port: Union[str, Literal[80, 443, 8080]] = 80
        
        result = Config.parse_args([])
        assert result.port == 80
        
        result = Config.parse_args(["--port", "custom"])
        assert result.port == "custom"
        
        # Note: str type is tried first, so "443" remains string
        result = Config.parse_args(["--port", "443"])
        assert result.port == "443"

    def test_union_type_order_int_before_str(self):
        """Test Union[int, str] - int is tried first"""
        @namespace
        class Config:
            value: Union[int, str] = 42
        
        result = Config.parse_args([])
        assert result.value == 42
        
        # Numeric string converts to int
        result = Config.parse_args(["--value", "123"])
        assert result.value == 123
        assert isinstance(result.value, int)
        
        # Non-numeric string converts to str
        result = Config.parse_args(["--value", "text"])
        assert result.value == "text"
        assert isinstance(result.value, str)

    def test_union_type_order_str_before_int(self):
        """Test Union[str, int] - str is tried first and always succeeds"""
        @namespace
        class Config:
            value: Union[str, int] = "default"
        
        result = Config.parse_args([])
        assert result.value == "default"
        
        # str is tried first, so "123" remains string
        result = Config.parse_args(["--value", "123"])
        assert result.value == "123"
        assert isinstance(result.value, str)
        
        result = Config.parse_args(["--value", "text"])
        assert result.value == "text"
        assert isinstance(result.value, str)


class TestOptionalTypes:
    """Test Optional type hints (Optional[T] = Union[T, None])"""

    def test_optional_str(self):
        """Test Optional[str]"""
        @namespace
        class Config:
            name: Optional[str] = None
        
        result = Config.parse_args([])
        assert result.name is None
        
        result = Config.parse_args(["--name", "value"])
        assert result.name == "value"

    def test_optional_int(self):
        """Test Optional[int]"""
        @namespace
        class Config:
            count: Optional[int] = None
        
        result = Config.parse_args([])
        assert result.count is None
        
        result = Config.parse_args(["--count", "42"])
        assert result.count == 42

    def test_optional_with_non_none_default(self):
        """Test Optional with non-None default value"""
        @namespace
        class Config:
            timeout: Optional[float] = 30.0
        
        result = Config.parse_args([])
        assert result.timeout == 30.0
        
        result = Config.parse_args(["--timeout", "60.5"])
        assert result.timeout == 60.5


class TestSequenceTypes:
    """Test sequence type hints (List, Tuple from typing)"""

    def test_list_str(self):
        """Test List[str] with default"""
        @namespace
        class Config:
            files: List[str] = []
        
        result = Config.parse_args([])
        assert result.files == []
        
        result = Config.parse_args(["--files", "a.txt", "b.txt", "c.txt"])
        assert result.files == ["a.txt", "b.txt", "c.txt"]

    def test_list_int(self):
        """Test List[int] with default"""
        @namespace
        class Config:
            numbers: List[int] = [1, 2, 3]
        
        result = Config.parse_args([])
        assert result.numbers == [1, 2, 3]
        
        result = Config.parse_args(["--numbers", "10", "20", "30"])
        assert result.numbers == [10, 20, 30]

    def test_tuple_ellipsis_str(self):
        """Test Tuple[str, ...] (variable length)"""
        @namespace
        class Config:
            tags: Tuple[str, ...] = ()
        
        result = Config.parse_args([])
        assert result.tags == ()
        
        # Note: argparse returns list for nargs='*', not tuple
        result = Config.parse_args(["--tags", "tag1", "tag2", "tag3"])
        assert result.tags == ["tag1", "tag2", "tag3"]

    def test_tuple_ellipsis_int(self):
        """Test Tuple[int, ...] (variable length)"""
        @namespace
        class Config:
            values: Tuple[int, ...] = (1, 2)
        
        result = Config.parse_args([])
        assert result.values == (1, 2)
        
        # Note: argparse returns list for nargs='*', not tuple
        result = Config.parse_args(["--values", "5", "10", "15"])
        assert result.values == [5, 10, 15]


class TestFixedTupleTypes:
    """Test fixed-length tuple type hints"""

    def test_tuple_two_elements(self):
        """Test Tuple[str, int] (fixed 2 elements)"""
        @namespace
        class Config:
            pair: Tuple[str, int] = ("default", 0)
        
        result = Config.parse_args([])
        assert result.pair == ("default", 0)
        
        # Note: argparse returns list for nargs=N, not tuple
        result = Config.parse_args(["--pair", "name", "42"])
        assert result.pair == ["name", 42]

    def test_tuple_three_elements(self):
        """Test Tuple[int, str, float] (fixed 3 elements)"""
        @namespace
        class Config:
            triple: Tuple[int, str, float] = (1, "x", 1.0)
        
        result = Config.parse_args([])
        assert result.triple == (1, "x", 1.0)
        
        # Note: argparse returns list for nargs=N, not tuple
        result = Config.parse_args(["--triple", "10", "test", "2.5"])
        assert result.triple == [10, "test", 2.5]

    def test_tuple_four_elements(self):
        """Test Tuple[str, str, int, float] (fixed 4 elements)"""
        @namespace
        class Config:
            quad: Tuple[str, str, int, float] = ("a", "b", 1, 1.0)
        
        result = Config.parse_args([])
        assert result.quad == ("a", "b", 1, 1.0)
        
        # Note: argparse returns list for nargs=N, not tuple
        result = Config.parse_args(["--quad", "x", "y", "5", "3.14"])
        assert result.quad == ["x", "y", 5, 3.14]


class TestComplexUnionTypes:
    """Test complex union type combinations"""

    def test_union_multiple_literals(self):
        """Test union of multiple Literal types"""
        @namespace
        class Config:
            mode: Union[Literal["a", "b"], Literal["c", "d"]] = "a"
        
        result = Config.parse_args([])
        assert result.mode == "a"
        
        result = Config.parse_args(["--mode", "c"])
        assert result.mode == "c"

    def test_union_literal_many_values(self):
        """Test Literal with many values (> 5)"""
        @namespace
        class Config:
            choice: Literal["opt1", "opt2", "opt3", "opt4", "opt5", "opt6"] = "opt1"
        
        result = Config.parse_args([])
        assert result.choice == "opt1"
        
        result = Config.parse_args(["--choice", "opt6"])
        assert result.choice == "opt6"

    def test_union_int_str_literal(self):
        """Test complex union: Union[int, str, Literal values]"""
        @namespace
        class Config:
            value: Union[int, str, Literal["auto", "max"]] = "auto"
        
        result = Config.parse_args([])
        assert result.value == "auto"
        
        result = Config.parse_args(["--value", "100"])
        assert result.value == 100
        
        result = Config.parse_args(["--value", "max"])
        assert result.value == "max"


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_list_default(self):
        """Test List with empty default"""
        @namespace
        class Config:
            items: List[str] = []
        
        result = Config.parse_args([])
        assert result.items == []

    def test_empty_tuple_default(self):
        """Test Tuple with empty default"""
        @namespace
        class Config:
            items: Tuple[str, ...] = ()
        
        result = Config.parse_args([])
        assert result.items == ()

    def test_single_element_list(self):
        """Test List with single element"""
        @namespace
        class Config:
            files: List[str] = ["default.txt"]
        
        result = Config.parse_args([])
        assert result.files == ["default.txt"]
        
        result = Config.parse_args(["--files", "single.txt"])
        assert result.files == ["single.txt"]

    def test_literal_single_value(self):
        """Test Literal with single value"""
        @namespace
        class Config:
            constant: Literal["only_option"] = "only_option"
        
        result = Config.parse_args([])
        assert result.constant == "only_option"
        
        result = Config.parse_args(["--constant", "only_option"])
        assert result.constant == "only_option"


class TestMixedTypesInSequences:
    """Test sequences with union element types"""

    def test_list_union_elements(self):
        """Test List[Union[int, str]] - elements can be int or str"""
        @namespace
        class Config:
            mixed: List[Union[int, str]] = []
        
        result = Config.parse_args([])
        assert result.mixed == []
        
        result = Config.parse_args(["--mixed", "text", "123", "more"])
        # Note: argparse will try to convert, behavior depends on type function
        assert len(result.mixed) == 3

    def test_tuple_ellipsis_union(self):
        """Test Tuple[Union[int, str], ...] - variable length with union type"""
        @namespace
        class Config:
            values: Tuple[Union[int, str], ...] = ()
        
        result = Config.parse_args([])
        assert result.values == ()
