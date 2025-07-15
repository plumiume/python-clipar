from typing import NamedTuple
import itertools
import inspect
import textwrap
import ast

class ClassAstHolder[CLS]:

    def _get_class_code(self, cls: type) -> str:

        try:
            code = inspect.getsource(cls)
        except OSError as e:
            raise OSError(f"Could not retrieve source code for class {cls.__name__}: {e}")
        except TypeError as e:
            raise TypeError(f"Could not retrieve source code for class {cls.__name__}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while retrieving source code for class {cls.__name__}: {e}")

        return textwrap.dedent(code).strip()

    def _get_ast_tree(self, code: str) -> ast.Module:

        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in class code: {e.msg} at line {e.lineno}, column {e.offset}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while parsing class code: {e}")

    def _get_classdef_from_tree(self, tree: ast.Module) -> ast.ClassDef:

        try:
            target = next(iter(tree.body))
        except StopIteration:
            raise RuntimeError("No class definition found in the provided code.")

        if not isinstance(target, ast.ClassDef):
            raise TypeError("The provided code does not contain a class definition.")

        return target

    def __init__(self, cls: type[CLS]):
        self.cls = cls
        code = self._get_class_code(cls)
        tree = self._get_ast_tree(code)
        self.classdef = self._get_classdef_from_tree(tree)


    def _get_classdef_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.ClassDef):
            return node.name
        return None
 
    def _get_annassign_target_name(self, node: ast.AST) -> str | None:

        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            return node.target.id
        return None

    def _get_assign_target_name(self, node: ast.AST) -> str | None:

        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        return None

    def _get_target_name(self, node: ast.AST) -> str | None:
        return (
            self._get_annassign_target_name(node)
            or self._get_assign_target_name(node)
        )

    def _get_str_constant_expr(self, node: ast.AST) -> str | None:

        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
        return None

    def get_assign_docs(self) -> dict[str, str | None]:

        return {
            name: self._get_str_constant_expr(expr)
            for assign, expr in itertools.pairwise(self.classdef.body)
            if (name := self._get_target_name(assign)) is not None
        }

    def get_orders(self) -> dict[str, int]:

        return {
            name: idx for idx, node in enumerate(self.classdef.body)
            if (
                (name := self._get_target_name(node)) is not None
                or (name := self._get_classdef_name(node)) is not None
            )
        }

    class _VarInfo(NamedTuple):
        doc: str | None
        order: int

    def get_assign_infos(self) -> dict[str, _VarInfo]:
        assign_docs = self.get_assign_docs()
        orders = self.get_orders()
        return {
            name: self._VarInfo(
                doc=assign_docs.get(name, None),
                order=orders[name]
            )
            for name in orders
        }