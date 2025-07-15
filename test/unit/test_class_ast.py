"""Unit tests for clipar.v312.class_ast module"""

import pytest
import ast
import textwrap
from unittest.mock import patch, MagicMock
from clipar.v312.class_ast import ClassAstHolder


class TestClassAstHolder:
    """Test ClassAstHolder class functionality"""

    @pytest.fixture
    def sample_class(self):
        """Sample class for testing"""
        class SampleClass:
            """Sample class for testing"""
            var1: str
            "Documentation for var1"
            
            var2: int = 10
            "Documentation for var2"
            
            var3 = "default"
            
            class NestedClass:
                pass
                
            def method(self):
                pass
        
        return SampleClass

    @pytest.fixture
    def class_holder(self, sample_class):
        """ClassAstHolder instance for testing"""
        return ClassAstHolder(sample_class)

    def test_init_success(self, sample_class):
        """Test successful initialization of ClassAstHolder"""
        holder = ClassAstHolder(sample_class)
        assert holder.cls == sample_class
        assert isinstance(holder.classdef, ast.ClassDef)
        assert holder.classdef.name == "SampleClass"

    def test_get_class_code_success(self, sample_class):
        """Test successful extraction of class source code"""
        holder = ClassAstHolder(sample_class)
        code = holder._get_class_code(sample_class)
        assert "class SampleClass:" in code
        assert "var1: str" in code
        assert "var2: int = 10" in code

    def test_get_class_code_os_error(self):
        """Test handling of OSError when getting class code"""
        # Create a holder with a valid class first
        class TestClass:
            pass
        
        holder = ClassAstHolder(TestClass)
        
        # Then test with built-in class that should raise TypeError
        with pytest.raises(TypeError, match="Could not retrieve source code"):
            holder._get_class_code(str)

    @patch('inspect.getsource')
    def test_get_class_code_unexpected_error(self, mock_getsource):
        """Test handling of unexpected errors when getting class code"""
        class TestClass:
            pass
        
        # First call will succeed (for constructor), second call will fail
        mock_getsource.side_effect = [
            "class TestClass:\n    pass",  # Success for constructor
            ValueError("Unexpected error")  # Failure for test
        ]
            
        holder = ClassAstHolder(TestClass)
        
        with pytest.raises(RuntimeError, match="Unexpected error while retrieving source code"):
            holder._get_class_code(TestClass)

    def test_get_ast_tree_success(self, class_holder):
        """Test successful AST tree generation"""
        code = "class TestClass:\n    pass"
        tree = class_holder._get_ast_tree(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.ClassDef)

    def test_get_ast_tree_syntax_error(self, class_holder):
        """Test handling of syntax errors in code"""
        invalid_code = "class TestClass\n    pass"  # Missing colon
        
        with pytest.raises(SyntaxError, match="Syntax error in class code"):
            class_holder._get_ast_tree(invalid_code)

    @patch('ast.parse')
    def test_get_ast_tree_unexpected_error(self, mock_parse, class_holder):
        """Test handling of unexpected errors when parsing AST"""
        mock_parse.side_effect = ValueError("Unexpected parse error")
        
        with pytest.raises(RuntimeError, match="Unexpected error while parsing class code"):
            class_holder._get_ast_tree("class TestClass: pass")

    def test_get_classdef_from_tree_success(self, class_holder):
        """Test successful extraction of ClassDef from AST tree"""
        tree = ast.parse("class TestClass:\n    pass")
        classdef = class_holder._get_classdef_from_tree(tree)
        assert isinstance(classdef, ast.ClassDef)
        assert classdef.name == "TestClass"

    def test_get_classdef_from_tree_empty_body(self, class_holder):
        """Test handling of empty AST body"""
        tree = ast.Module(body=[], type_ignores=[])
        
        with pytest.raises(RuntimeError, match="No class definition found"):
            class_holder._get_classdef_from_tree(tree)

    def test_get_classdef_from_tree_not_classdef(self, class_holder):
        """Test handling of non-ClassDef nodes"""
        tree = ast.parse("def function(): pass")
        
        with pytest.raises(TypeError, match="does not contain a class definition"):
            class_holder._get_classdef_from_tree(tree)

    def test_get_classdef_name_success(self, class_holder):
        """Test successful extraction of class name"""
        classdef = ast.ClassDef(name="TestClass", bases=[], keywords=[], 
                               decorator_list=[], body=[], type_params=[])
        result = class_holder._get_classdef_name(classdef)
        assert result == "TestClass"

    def test_get_classdef_name_not_classdef(self, class_holder):
        """Test handling of non-ClassDef nodes"""
        funcdef = ast.FunctionDef(name="test_func", args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], 
            kw_defaults=[], vararg=None, kwarg=None), body=[], 
            decorator_list=[], returns=None, type_params=[])
        result = class_holder._get_classdef_name(funcdef)
        assert result is None

    def test_get_annassign_target_name_success(self, class_holder):
        """Test successful extraction of annotated assignment target name"""
        target = ast.Name(id="var1", ctx=ast.Store())
        annotation = ast.Name(id="str", ctx=ast.Load())
        annassign = ast.AnnAssign(target=target, annotation=annotation, value=None, simple=1)
        
        result = class_holder._get_annassign_target_name(annassign)
        assert result == "var1"

    def test_get_annassign_target_name_not_annassign(self, class_holder):
        """Test handling of non-AnnAssign nodes"""
        assign = ast.Assign(targets=[], value=ast.Constant(value=1))
        result = class_holder._get_annassign_target_name(assign)
        assert result is None

    def test_get_annassign_target_name_complex_target(self, class_holder):
        """Test handling of complex target (not Name)"""
        target = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), 
                              attr="var1", ctx=ast.Store())
        annotation = ast.Name(id="str", ctx=ast.Load())
        annassign = ast.AnnAssign(target=target, annotation=annotation, value=None, simple=1)
        
        result = class_holder._get_annassign_target_name(annassign)
        assert result is None

    def test_get_assign_target_name_success(self, class_holder):
        """Test successful extraction of assignment target name"""
        target = ast.Name(id="var1", ctx=ast.Store())
        assign = ast.Assign(targets=[target], value=ast.Constant(value=1))
        
        result = class_holder._get_assign_target_name(assign)
        assert result == "var1"

    def test_get_assign_target_name_multiple_targets(self, class_holder):
        """Test handling of multiple assignment targets"""
        target1 = ast.Name(id="var1", ctx=ast.Store())
        target2 = ast.Name(id="var2", ctx=ast.Store())
        assign = ast.Assign(targets=[target1, target2], value=ast.Constant(value=1))
        
        result = class_holder._get_assign_target_name(assign)
        assert result is None

    def test_get_assign_target_name_complex_target(self, class_holder):
        """Test handling of complex target (not Name)"""
        target = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), 
                              attr="var1", ctx=ast.Store())
        assign = ast.Assign(targets=[target], value=ast.Constant(value=1))
        
        result = class_holder._get_assign_target_name(assign)
        assert result is None

    def test_get_target_name_annassign(self, class_holder):
        """Test _get_target_name with annotated assignment"""
        target = ast.Name(id="var1", ctx=ast.Store())
        annotation = ast.Name(id="str", ctx=ast.Load())
        annassign = ast.AnnAssign(target=target, annotation=annotation, value=None, simple=1)
        
        result = class_holder._get_target_name(annassign)
        assert result == "var1"

    def test_get_target_name_assign(self, class_holder):
        """Test _get_target_name with regular assignment"""
        target = ast.Name(id="var1", ctx=ast.Store())
        assign = ast.Assign(targets=[target], value=ast.Constant(value=1))
        
        result = class_holder._get_target_name(assign)
        assert result == "var1"

    def test_get_target_name_none(self, class_holder):
        """Test _get_target_name with neither assignment type"""
        funcdef = ast.FunctionDef(name="test_func", args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], 
            kw_defaults=[], vararg=None, kwarg=None), body=[], 
            decorator_list=[], returns=None, type_params=[])
        
        result = class_holder._get_target_name(funcdef)
        assert result is None

    def test_get_str_constant_expr_success(self, class_holder):
        """Test successful extraction of string constant from expression"""
        constant = ast.Constant(value="test string")
        expr = ast.Expr(value=constant)
        
        result = class_holder._get_str_constant_expr(expr)
        assert result == "test string"

    def test_get_str_constant_expr_not_expr(self, class_holder):
        """Test handling of non-Expr nodes"""
        assign = ast.Assign(targets=[], value=ast.Constant(value="test"))
        result = class_holder._get_str_constant_expr(assign)
        assert result is None

    def test_get_str_constant_expr_not_constant(self, class_holder):
        """Test handling of non-Constant expression values"""
        name = ast.Name(id="var", ctx=ast.Load())
        expr = ast.Expr(value=name)
        
        result = class_holder._get_str_constant_expr(expr)
        assert result is None

    def test_get_str_constant_expr_not_string(self, class_holder):
        """Test handling of non-string constants"""
        constant = ast.Constant(value=42)
        expr = ast.Expr(value=constant)
        
        result = class_holder._get_str_constant_expr(expr)
        assert result is None

    def test_get_assign_docs(self, class_holder):
        """Test extraction of assignment documentation"""
        docs = class_holder.get_assign_docs()
        assert isinstance(docs, dict)
        assert "var1" in docs
        assert docs["var1"] == "Documentation for var1"
        assert "var2" in docs
        assert docs["var2"] == "Documentation for var2"

    def test_get_orders(self, class_holder):
        """Test extraction of declaration order"""
        orders = class_holder.get_orders()
        assert isinstance(orders, dict)
        assert "var1" in orders
        assert "var2" in orders
        assert "var3" in orders
        assert "NestedClass" in orders
        assert orders["var1"] < orders["var2"]
        assert orders["var2"] < orders["var3"]

    def test_get_assign_infos(self, class_holder):
        """Test extraction of combined assignment information"""
        infos = class_holder.get_assign_infos()
        assert isinstance(infos, dict)
        
        # Check var1
        assert "var1" in infos
        var1_info = infos["var1"]
        assert var1_info.doc == "Documentation for var1"
        assert isinstance(var1_info.order, int)
        
        # Check var2
        assert "var2" in infos
        var2_info = infos["var2"]
        assert var2_info.doc == "Documentation for var2"
        assert isinstance(var2_info.order, int)
        
        # Check order relationship
        assert var1_info.order < var2_info.order

    def test_varinfo_namedtuple(self, class_holder):
        """Test _VarInfo NamedTuple functionality"""
        info = class_holder._VarInfo(doc="test doc", order=1)
        assert info.doc == "test doc"
        assert info.order == 1
        assert len(info) == 2
        assert tuple(info) == ("test doc", 1)


class TestClassAstHolderEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_class(self):
        """Test handling of empty class"""
        class EmptyClass:
            pass
        
        holder = ClassAstHolder(EmptyClass)
        docs = holder.get_assign_docs()
        orders = holder.get_orders()
        infos = holder.get_assign_infos()
        
        assert isinstance(docs, dict)
        assert isinstance(orders, dict)
        assert isinstance(infos, dict)

    def test_class_with_only_methods(self):
        """Test handling of class with only methods"""
        class MethodOnlyClass:
            def method1(self):
                pass
            
            def method2(self):
                pass
        
        holder = ClassAstHolder(MethodOnlyClass)
        docs = holder.get_assign_docs()
        orders = holder.get_orders()
        infos = holder.get_assign_infos()
        
        assert len(docs) == 0
        assert len(orders) == 0
        assert len(infos) == 0

    def test_class_with_complex_assignments(self):
        """Test handling of complex assignment patterns"""
        class ComplexClass:
            # Tuple assignment (should be ignored)
            # a, b = 1, 2  # This would be complex to test
            
            # Simple assignment
            simple_var = "value"
            "Documentation for simple_var"
        
        holder = ClassAstHolder(ComplexClass)
        docs = holder.get_assign_docs()
        
        # Only simple_var should be captured
        assert "simple_var" in docs
        assert docs["simple_var"] == "Documentation for simple_var"
