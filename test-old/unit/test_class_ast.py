"""Test module for class_ast.py"""

import pytest
import ast
import textwrap
from unittest.mock import Mock, patch

from clipar.v312.class_ast import ClassAstHolder


class MockClass:
    """Mock class for testing ClassAstHolder"""
    
    def __init__(self):
        self.arg1: str
        "Documentation for arg1"
        self.arg2: int = 42
        "Documentation for arg2"
        self.arg3 = "default"


class TestClassAstHolder:
    """Test ClassAstHolder class"""
    
    def test_init(self):
        """Test ClassAstHolder initialization"""
        holder = ClassAstHolder(MockClass)
        assert holder.cls is MockClass
        assert isinstance(holder.classdef, ast.ClassDef)
        assert holder.classdef.name == "MockClass"
    
    def test_get_class_code_success(self):
        """Test _get_class_code method with valid class"""
        holder = ClassAstHolder(MockClass)
        code = holder._get_class_code(MockClass)
        assert isinstance(code, str)
        assert "class MockClass" in code
        assert "arg1: str" in code
    
    def test_get_class_code_os_error(self):
        """Test _get_class_code method with OSError"""
        holder = ClassAstHolder(MockClass)
        
        with patch('inspect.getsource', side_effect=OSError("File not found")):
            with pytest.raises(RuntimeError, match="Could not retrieve source code"):
                holder._get_class_code(MockClass)
    
    def test_get_class_code_unexpected_error(self):
        """Test _get_class_code method with unexpected error"""
        holder = ClassAstHolder(MockClass)
        
        with patch('inspect.getsource', side_effect=ValueError("Unexpected")):
            with pytest.raises(RuntimeError, match="Unexpected error while retrieving"):
                holder._get_class_code(MockClass)
    
    def test_get_ast_tree_success(self):
        """Test _get_ast_tree method with valid code"""
        holder = ClassAstHolder(MockClass)
        code = "class TestClass:\n    pass"
        tree = holder._get_ast_tree(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.ClassDef)
    
    def test_get_ast_tree_syntax_error(self):
        """Test _get_ast_tree method with syntax error"""
        holder = ClassAstHolder(MockClass)
        invalid_code = "class TestClass\n    pass"  # Missing colon
        
        with pytest.raises(SyntaxError, match="Syntax error in class code"):
            holder._get_ast_tree(invalid_code)
    
    def test_get_ast_tree_unexpected_error(self):
        """Test _get_ast_tree method with unexpected error"""
        holder = ClassAstHolder(MockClass)
        
        with patch('ast.parse', side_effect=ValueError("Unexpected")):
            with pytest.raises(RuntimeError, match="Unexpected error while parsing"):
                holder._get_ast_tree("class Test: pass")
    
    def test_get_classdef_from_tree_success(self):
        """Test _get_classdef_from_tree method with valid tree"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("class TestClass:\n    pass")
        classdef = holder._get_classdef_from_tree(tree)
        assert isinstance(classdef, ast.ClassDef)
        assert classdef.name == "TestClass"
    
    def test_get_classdef_from_tree_empty(self):
        """Test _get_classdef_from_tree method with empty tree"""
        holder = ClassAstHolder(MockClass)
        tree = ast.Module(body=[], type_ignores=[])
        
        with pytest.raises(RuntimeError, match="No class definition found"):
            holder._get_classdef_from_tree(tree)
    
    def test_get_classdef_from_tree_not_class(self):
        """Test _get_classdef_from_tree method with non-class definition"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("def test(): pass")
        
        with pytest.raises(TypeError, match="does not contain a class definition"):
            holder._get_classdef_from_tree(tree)
    
    def test_get_annassign_target_name_success(self):
        """Test _get_annassign_target_name method with valid assignment"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("arg: str")
        assign = tree.body[0]
        name = holder._get_annassign_target_name(assign)
        assert name == "arg"
    
    def test_get_annassign_target_name_invalid(self):
        """Test _get_annassign_target_name method with invalid node"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("def test(): pass")
        func_def = tree.body[0]
        name = holder._get_annassign_target_name(func_def)
        assert name is None
    
    def test_get_assign_target_name_success(self):
        """Test _get_assign_target_name method with valid assignment"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("arg = 42")
        assign = tree.body[0]
        name = holder._get_assign_target_name(assign)
        assert name == "arg"
    
    def test_get_assign_target_name_multiple_targets(self):
        """Test _get_assign_target_name method with multiple targets"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("a, b = 1, 2")
        assign = tree.body[0]
        name = holder._get_assign_target_name(assign)
        assert name is None
    
    def test_get_target_name(self):
        """Test _get_target_name method"""
        holder = ClassAstHolder(MockClass)
        
        # Test with annotated assignment
        tree = ast.parse("arg: str")
        assign = tree.body[0]
        name = holder._get_target_name(assign)
        assert name == "arg"
        
        # Test with regular assignment
        tree = ast.parse("arg = 42")
        assign = tree.body[0]
        name = holder._get_target_name(assign)
        assert name == "arg"
        
        # Test with function definition
        tree = ast.parse("def test(): pass")
        func_def = tree.body[0]
        name = holder._get_target_name(func_def)
        assert name is None
    
    def test_get_str_constant_expr_success(self):
        """Test _get_str_constant_expr method with valid string expression"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("'test string'")
        expr = tree.body[0]
        string_value = holder._get_str_constant_expr(expr)
        assert string_value == "test string"
    
    def test_get_str_constant_expr_not_string(self):
        """Test _get_str_constant_expr method with non-string constant"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("42")
        expr = tree.body[0]
        string_value = holder._get_str_constant_expr(expr)
        assert string_value is None
    
    def test_get_str_constant_expr_not_expr(self):
        """Test _get_str_constant_expr method with non-expression node"""
        holder = ClassAstHolder(MockClass)
        tree = ast.parse("def test(): pass")
        func_def = tree.body[0]
        string_value = holder._get_str_constant_expr(func_def)
        assert string_value is None
    
    def test_get_assign_docs(self):
        """Test get_assign_docs method"""
        # Create a mock class with proper structure
        code = textwrap.dedent('''
        class TestClass:
            arg1: str
            "Documentation for arg1"
            arg2: int = 42
            "Documentation for arg2"
            arg3 = "default"
        ''').strip()
        
        with patch.object(ClassAstHolder, '_get_class_code', return_value=code):
            holder = ClassAstHolder(MockClass)
            docs = holder.get_assign_docs()
            
            assert "arg1" in docs
            assert docs["arg1"] == "Documentation for arg1"
            assert "arg2" in docs
            assert docs["arg2"] == "Documentation for arg2"
    
    def test_get_assign_orders(self):
        """Test get_assign_orders method"""
        # Create a mock class with proper structure
        code = textwrap.dedent('''
        class TestClass:
            arg1: str
            arg2: int = 42
            arg3 = "default"
        ''').strip()
        
        with patch.object(ClassAstHolder, '_get_class_code', return_value=code):
            holder = ClassAstHolder(MockClass)
            orders = holder.get_orders()
            
            assert "arg1" in orders
            assert "arg2" in orders
            assert "arg3" in orders
            assert orders["arg1"] < orders["arg2"] < orders["arg3"]
    
    def test_get_assign_infos(self):
        """Test get_assign_infos method"""
        # Create a mock class with proper structure
        code = textwrap.dedent('''
        class TestClass:
            arg1: str
            "Documentation for arg1"
            arg2: int = 42
            "Documentation for arg2"
            arg3 = "default"
        ''').strip()
        
        with patch.object(ClassAstHolder, '_get_class_code', return_value=code):
            holder = ClassAstHolder(MockClass)
            infos = holder.get_assign_infos()
            
            assert "arg1" in infos
            assert infos["arg1"].doc == "Documentation for arg1"
            assert isinstance(infos["arg1"].order, int)
            
            assert "arg2" in infos
            assert infos["arg2"].doc == "Documentation for arg2"
            assert isinstance(infos["arg2"].order, int)
            
            assert "arg3" in infos
            assert infos["arg3"].doc is None  # No documentation
            assert isinstance(infos["arg3"].order, int)
            
            # Verify ordering
            assert infos["arg1"].order < infos["arg2"].order < infos["arg3"].order
    
    def test_var_info_named_tuple(self):
        """Test _VarInfo named tuple"""
        holder = ClassAstHolder(MockClass)
        var_info = holder._VarInfo(doc="test doc", order=1)
        
        assert var_info.doc == "test doc"
        assert var_info.order == 1
        assert len(var_info) == 2


if __name__ == "__main__":
    pytest.main([__file__])
