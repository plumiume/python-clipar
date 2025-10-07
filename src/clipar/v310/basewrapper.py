# pyright: reportUnnecessaryIsInstance=false
import abc
from typing import (
    overload, Protocol, runtime_checkable, Any,
    Callable, Literal, Union,
    Iterable, Sequence,
    TypedDict, TypeGuard, Final,
    get_type_hints, get_args, get_origin,
    TypeVar, Generic,
)
from typing_extensions import Self, Unpack
from types import UnionType, EllipsisType, NoneType
from enum import Enum

from itertools import chain
import argparse

from .class_ast import ClassAstHolder
from .mixin import BaseMixin

# TypeVar definitions for Python 3.10 compatibility
_NS = TypeVar('_NS')
_T = TypeVar('_T')
_W = TypeVar('_W', bound='BaseWrapper[Any]', covariant=True)

Location = list[str]
OnParseHookArgs = tuple[Location, 'BoundWrapper[BaseWrapper[Any]]']
Literalizable = str | int | float | bool | NoneType
OBJECT_ATTRS = set(dir(object))
MIXIN_ATTRIBUTES = set(dir(BaseMixin))
MIXIN_ANNOTATIONS = get_type_hints(BaseMixin)

def _return_bool(value: bool) -> bool:
    return value

def _append_list(target: list[_T], *args: _T) -> list[_T]:
    target.extend(args)
    return target

def _get_attr_names(cls: type) -> Iterable[str]:
    for base in reversed(cls.mro()):
        if hasattr(base, '__slots__'):
            yield from getattr(base, '__slots__')
        if hasattr(base, '__dict__'):
            yield from getattr(base, '__dict__')

class _NotSelectedType:
    def __bool__(self) -> Literal[False]:
        return False
    def __getattr__(self, name: str) -> 'Literal[NotSelectedType.I]':
        try:
            return NotSelectedType.I
        except NameError as e:
            raise AttributeError() from e

class NotSelectedType(Enum):
    I = _NotSelectedType()
    "A singleton instance representing a value that is not selected or set."
    def __repr__(self) -> str:
        return "NotSelected"
    def __bool__(self) -> Literal[False]:
        return False
    def __getattr__(self, name: str) -> 'Literal[NotSelectedType.I]':
        try:
            return NotSelectedType.I
        except NameError as e:
            raise AttributeError() from e
NotSelected: Final = NotSelectedType.I

class AddArgumentOptions(TypedDict, total=False):
    action: str | type[argparse.Action]
    nargs: int | Literal['?', '*', '+'] | None
    const: object
    default: object
    type: Callable[[str], object] | argparse.FileType | str
    choices: Iterable[object] | None
    required: bool
    help: str | None
    metavar: str | tuple[str, ...] | None
    dest: str | None
    version: str

@runtime_checkable
class ArgumentContainerProtocol(Protocol):
    def add_argument(
        self,
        *name_or_flags: str,
        **kwargs: Unpack[AddArgumentOptions]
        ) -> Any:...
    def add_argument_group(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        prefix_chars: str = '-',
        conflict_handler: str = 'error'
        ) -> 'ArgumentContainerProtocol':...
    def add_mutually_exclusive_group(
        self,
        *,
        required: bool = False
        ) -> 'ArgumentContainerProtocol':...
    def set_defaults(self, **kwargs: Any):...
    def get_default(self, dest: str) -> object:...

@runtime_checkable
class GenericAliasLike(Protocol):
    __args__: tuple['GenericAliasLike | type | None', ...] | tuple[Any, EllipsisType]
    __origin__: Any

class BaseWrapper(abc.ABC, Generic[_NS]):

    def __init__(self, namespace_type: type[_NS]):
        self.namespace_type = namespace_type
        self._subparsers: dict[str, 'BoundWrapper[SubparserWrapper[Any]]'] = {}
        self._subgroups: dict[str, 'BoundWrapper[SubgroupWrapper[Any]]'] = {}
        self._arg_names: set[str] = set()

        self._container = self.configure_container()
        self._init_container(self._container, namespace_type)

    @overload
    def __get__(
        self,
        instance: 'WrapperHolder[Any] | type | None',
        owner: type | None = None
        ) -> Self:...
    @overload
    def __get__(
        self,
        instance: object,
        owner: type | None = None
        ) -> _NS | Literal[NotSelectedType.I]: ...
    def __get__(
        self,
        instance: type | object | None,
        owner: type | None = None
        ):

        if instance is None or isinstance(instance, WrapperHolder | type):
            return self

        if _return_bool(False):
            return self.namespace_type()
        else:
            return NotSelected

    @property
    def T(self) -> type[_NS]:
        "The type of the namespace class wrapped by this BaseWrapper."
        return self.namespace_type

    @abc.abstractmethod
    def configure_container(self) -> ArgumentContainerProtocol:
        raise NotImplementedError(
            "Subclasses must implement configure_container method."
        )

    def update_container(self, container: ArgumentContainerProtocol):
        self._container = container

    def _init_container(
        self,
        container: ArgumentContainerProtocol,
        namespace_type: type[_NS]
        ):

        assign_infos: dict[str, ClassAstHolder.VarInfo] = {}
        try:
            # assign_infos = ClassAstHolder(namespace_type).get_assign_infos()
            for base in reversed(namespace_type.mro()):
                assign_infos.update(
                    ClassAstHolder(base).get_assign_infos()
                )
        except (OSError, TypeError, SyntaxError, RuntimeError):
            pass

        annotations = get_type_hints(namespace_type)
        attrnames = list(_get_attr_names(namespace_type))

        ordered_attrnames = [
            *(
                a for a in annotations
                if a not in attrnames
                and a not in MIXIN_ANNOTATIONS
            ),
            *(
                a for a in attrnames
                if a not in MIXIN_ATTRIBUTES
                and not a.startswith('_')
            )
        ]

        for attr_key in ordered_attrnames:

            in_annotations = attr_key in annotations
            in_dict = attr_key in attrnames
            default: Any | None = getattr(namespace_type, attr_key, None)
            var_info = assign_infos.get(attr_key, None)
            doc = var_info.doc if var_info else None

            if isinstance(default, type):
                raise TypeError(
                    f"Assign name '{attr_key}' cannot be a type, "
                    f"it must be an instance or a default value."
                )

            elif in_dict and isinstance(default, SubparserWrapper | SubgroupWrapper):
                self._add_wrapper(
                    container=container,
                    name=attr_key,
                    wrapper=default # pyright: ignore[reportUnknownArgumentType]
                )

            elif in_dict:
                self._arg_names.add(attr_key)
                self._add_opt(
                    container=container,
                    name=attr_key,
                    annotation=annotations.get(attr_key, type(default)),
                    default=default,
                    doc=doc,
                )

            elif in_annotations:
                self._arg_names.add(attr_key)
                self._add_req(
                    container=container,
                    name=attr_key,
                    annotation=annotations[attr_key],
                    doc=doc,
                )

            else: # Never
                raise ValueError(
                    f"Assign name '{attr_key}' not found in annotations or dict."
                )

    def _add_wrapper(
        self,
        container: ArgumentContainerProtocol, # for compatibility, not used
        name: str,
        wrapper: 'SubparserWrapper[Any] | SubgroupWrapper[Any]'
        ):

        wrapper.on_before_bind(name, self)

        if isinstance(wrapper, SubparserWrapper):
            self._subparsers[name] = wrapper._bind(name, self)
        elif isinstance(wrapper, SubgroupWrapper):
            self._subgroups[name] = wrapper._bind(name, self)
        else:
            raise TypeError(
                f"Wrapper must be either SubparserWrapper or SubgroupWrapper, "
                f"got {type(wrapper).__name__}."
            )

        wrapper.on_after_bind(name, self)

    class _ParseAnnotationResult(TypedDict, total=False):
        nargs: int | Literal['?', '*', '+'] | None
        type: Callable[[str], object]
        choices: Sequence[object] | None

    def _add_req(
        self,
        container: ArgumentContainerProtocol,
        name: str,
        annotation: type | UnionType | GenericAliasLike,
        doc: str | None
        ):

        parse_result = self._parse_annotation(annotation)

        container.add_argument(
            name,
            help=doc,
            **parse_result
        )

    def _add_opt(
        self,
        container: ArgumentContainerProtocol,
        name: str,
        annotation: GenericAliasLike | type,
        default: object,
        doc: str | None
        ):

        name_or_flag = '--' + name.replace('_', '-')

        parse_result = self._parse_annotation(annotation)

        type_ = parse_result.get('type', None)
        if isinstance(type_, type) and issubclass(type_, bool):
            action = 'store_false' if default else 'store_true'
            parse_result = self._ParseAnnotationResult()
        else:
            action = 'store'

        action = container.add_argument(
            name_or_flag,
            action=action,
            help=doc,
            dest=name,
            default=default,
            **parse_result,
        )

    def _parse_annotation(
        self,
        annotation: GenericAliasLike | UnionType | type
        ) -> _ParseAnnotationResult:

        nargs, annotation_args = self._determine_nargs_and_generic_args(annotation)

        flatten_union_and_literal = self._flatten_union_and_literal(annotation_args)

        pick_choices_are_required = [
            all(
                isinstance(ann, Literalizable)
                for ann in literals
            )
            for literals in flatten_union_and_literal.values()
        ]

        if all(pick_choices_are_required):
            choices = list(chain.from_iterable(
                flatten_union_and_literal.values()
            ))
        else:
            choices = None

        if len(flatten_union_and_literal) == 1:
            ann = next(iter(flatten_union_and_literal.keys()))
            type_ = self._get_type_from_type_or_generic_alias(ann)

        else:
            type_ = self._multi_type_builder(
                flatten_union_and_literal,
                pick_choices_are_required
            )

        return self._ParseAnnotationResult(
            nargs=nargs,
            type=type_,
            choices=choices
        )

    def _determine_nargs_and_generic_args(
        self,
        annotation: GenericAliasLike | UnionType | type
        ) -> tuple[
            int | Literal['?', '*', '+'] | None,
            tuple[GenericAliasLike | type | None, ...]
        ]:

        tp_origin = get_origin(annotation)
        tp_args = get_args(annotation)

        if isinstance(annotation, type):
            return None, (annotation, )

        if isinstance(annotation, UnionType):
            return None, tp_args

        if tp_origin in (Literal, Union):
            return None, tp_args

        if not isinstance(tp_origin, type):
            raise TypeError(
                f"Annotation {annotation} has invalid origin {tp_origin}."
            )

        no_ellipsis_args = tuple(a for a in tp_args if a is not ...)

        if ... in tp_args:
            return '*', no_ellipsis_args

        if issubclass(tp_origin, tuple):
            return len(no_ellipsis_args), no_ellipsis_args

        if issubclass(tp_origin, Sequence):
            return '*', no_ellipsis_args

        return None, (annotation, )

    def _flatten_union_and_literal(
        self,
        annotations: tuple[GenericAliasLike | UnionType | type | None, ...]
        ) -> dict[
            GenericAliasLike | type,
            list[GenericAliasLike | type | Literalizable]
        ]:

        union_args = list(chain.from_iterable(
            ann.__args__
            if isinstance(ann, UnionType)
            else ann.__args__
            if isinstance(ann, GenericAliasLike) and ann.__origin__ is Union
            else (ann, )
            for ann in annotations
        ))

        literal_args = list(chain.from_iterable(
            ann.__args__
            if isinstance(ann, GenericAliasLike) and ann.__origin__ is Literal
            else [ann]
            for ann in union_args
        ))

        ret: dict[
            type | GenericAliasLike,
            list[type | GenericAliasLike | Literalizable]
        ] = {
            ann: [ann]
            for ann in literal_args
            if isinstance(ann, type | GenericAliasLike)
        }

        for ann in literal_args:
            if isinstance(ann, Literalizable):
                ret.setdefault(type(ann), []).append(ann)

        return ret

    def _multi_type_builder(
        self,
        flatten_union_and_literal: dict[
            type |  GenericAliasLike,
            list[type |  GenericAliasLike | Literalizable]
        ],
        pick_choices_are_required: list[bool]
        ):

        def type_impl(value: str) -> object:

                zipped = zip(
                    flatten_union_and_literal.keys(),
                    flatten_union_and_literal.values(),
                    pick_choices_are_required
                )
                for ann, literals, pick_choices in zipped:

                    type_ = self._get_type_from_type_or_generic_alias(ann)

                    try:
                        inst = type_(value)
                    except (ValueError, TypeError):
                        continue

                    if pick_choices and inst not in literals:
                        raise ValueError(
                            f"Value '{value}' is not in choices {literals}."
                        )

                    return inst

                raise ValueError(
                    f"Cannot convert value '{value}' to any of the types: "
                    f"{', '.join(str(ann) for ann in flatten_union_and_literal.keys())}."
                )
        return type_impl

    def _get_type_from_type_or_generic_alias(
        self,
        annotation: GenericAliasLike | type
        ) -> type:

        tmp = annotation
        while isinstance(tmp, GenericAliasLike):
            tmp = tmp.__origin__
        if not isinstance(tmp, type):
            raise TypeError(
                f"Annotation {annotation} is not a type."
            )
        return tmp

    def _flatten_subparsers(self) -> list[tuple[list[str], 'BoundWrapper[SubparserWrapper[Any]]']]:

        return list(chain.from_iterable(
            chain(
                (
                    ([name], bound_wrapper),
                ),
                (
                    (_append_list(child_names, name), child_bound_wrapper)
                    for child_names, child_bound_wrapper
                    in bound_wrapper.self._flatten_subparsers()
                )
            )
            for name, bound_wrapper in self._subparsers.items()
        ))

    def _flatten_subgroups(self) -> list[tuple[list[str], 'BoundWrapper[SubgroupWrapper[Any]]']]:

        return list(chain.from_iterable(
            chain(
                (
                    ([name], bound_wrapper),
                ),
                (
                    (_append_list(child_names, name), child_bound_wrapper)
                    for child_names, child_bound_wrapper
                    in bound_wrapper.self._flatten_subgroups()
                )
            )
            for name, bound_wrapper in self._subgroups.items()
        ))

    def _bind(self, name: str, parent: 'BaseWrapper[Any]') -> 'BoundWrapper[Self]':
        return BoundWrapper(name, parent, self)

    ## Hooks

    def on_before_bind(self, bound_name: str, wrapper: 'BaseWrapper[Any]'):
        pass
    def on_after_bind(self, bound_name: str, wrapper: 'BaseWrapper[Any]'):
        pass

    def on_before_parse(self, location: Location, bound_wrapper: 'BoundWrapper[BaseWrapper[Any]] | None'):
        pass
    def on_after_parse(self, location: Location, bound_wrapper: 'BoundWrapper[BaseWrapper[Any]] | None'):
        pass

    ## Public API

    def add_wrapper(
        self,
        name: str,
        wrapper: 'SubparserWrapper[Any] | SubgroupWrapper[Any]'
        ):

        """
        Dynamically add a wrapper to create nested command structures.
        
        This method enables runtime construction of nested CLI structures by adding
        subparser or subgroup wrappers to the current container. It's primarily used
        to build complex configurations combining namespace, group, and mutually
        exclusive group decorators.
        
        Args:
            name: The identifier for the wrapper. This becomes the subcommand name
                for subparsers or the group identifier for subgroups.
            wrapper: The wrapper instance to add. Must be either a SubparserWrapper
                (e.g., from @namespace decorator) or SubgroupWrapper (e.g., from 
                @group or @mutually_exclusive_group decorators).
        
        Raises:
            TypeError: If the wrapper type is not SubparserWrapper or SubgroupWrapper.
        
        Note:
            - Calls binding hooks (on_before_bind, on_after_bind) during registration
            - Creates a BoundWrapper instance to manage the relationship
            - Enables aliasing by allowing the same wrapper to be added with different names
            - For @namespace wrappers: Creates independent subcommands where only the
              selected subcommand becomes active (others remain NotSelected)
            - For @group/@mutually_exclusive_group wrappers: All arguments are flattened
              to the top level, and aliasing may cause argument name conflicts
        
        Example:
            ```python
            # Add a database configuration group
            database_group = GroupWrapper(DatabaseConfig) 
            main_wrapper.add_wrapper("database", database_group)
            
            # Add subcommand for nested namespace
            config_ns = NamespaceWrapper(ConfigNamespace)
            main_wrapper.add_wrapper("config", config_ns)
            
            # Create alias (works for namespaces, may conflict for groups)
            main_wrapper.add_wrapper("cfg", config_ns)
            ```
        """

        self._add_wrapper(self._container, name, wrapper)

class SubparserWrapper(BaseWrapper[_NS], abc.ABC, Generic[_NS]):
    def __init__(
        self,
        namespace_type: type[_NS]
        ):
        super().__init__(namespace_type)
        self._container.set_defaults(_clipar_wrapper=self)
        self._callback: Callable[[_NS], object] | None = None

    def _set_callback(
        self,
        callback: Callable[[_NS], object]
        ):
        self._callback = callback

    def _check_namespace(self, namespace: object) -> TypeGuard[_NS]:
        return all(
            hasattr(namespace, attr)
            for attr in self._arg_names
        )

    def _exec_callback(self, namespace: object) -> object:

        if self._callback is None:
            return

        if self._check_namespace(namespace):
            return self._callback(namespace)

class SubgroupWrapper(BaseWrapper[_NS], abc.ABC, Generic[_NS]):
    pass

class WrapperHolder(Generic[_W]): pass

class BoundWrapper(WrapperHolder[_W], Generic[_W]):

    def __init__(self, name: str, parent_wrapper: BaseWrapper[Any], self_wrapper: _W):
        self._bound_name = name
        self._parent = parent_wrapper
        self._self = self_wrapper

    @property
    def bound_name(self) -> str:
        return self._bound_name

    @property
    def parent(self) -> BaseWrapper[Any]:
        return self._parent

    @property
    def self(self_) -> _W:
        return self_._self
