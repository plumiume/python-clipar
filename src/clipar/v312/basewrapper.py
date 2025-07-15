import abc
from typing import (
    overload, Self, Protocol, runtime_checkable, Any,
    Callable, Literal, Union,
    Iterable, Sequence,
    TypedDict, Unpack,
    TypeGuard, Final,
)
from types import UnionType
from enum import Enum

from itertools import chain
import argparse

from .class_ast import ClassAstHolder

Literalizable = str | int | float | bool | None

def _return_bool(value: bool) -> bool:
    return value

def _append_list[T](target: list[T], *args: T) -> list[T]:
    target.extend(args)
    return target

class _NotSelectedType:
    def __bool__(self) -> Literal[False]:
        return False
    def __getattr__(self, name: str):
        return NotSelectedType.I

class NotSelectedType(Enum):
    I = _NotSelectedType()
    "A singleton instance representing a value that is not selected or set."
    def __repr__(self) -> str:
        return "NotSelected"
    def __bool__(self) -> Literal[False]:
        return False
    def __getattr__(self, name: str):
        return NotSelectedType.I
NotSelected: Final = NotSelectedType.I

class AddArgumentOptions(TypedDict, total=False):
    action: str | type[argparse.Action]
    nargs: int | Literal['?', '*', '+'] | None
    const: object
    default: object
    type: Callable[[str], Any] | argparse.FileType | str
    choices: Iterable | None
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
    def set_defaults(self, **kwargs):...
    def get_default(self, dest: str) -> object:...

@runtime_checkable
class SupportsOriginAndArgs(Protocol):
    __origin__: 'type | SupportsOriginAndArgs'
    __args__: tuple

class BaseWrapper[NS](abc.ABC):

    def __init__(self, namespace_type: type[NS]):
        self.namespace_type = namespace_type
        self._subparsers: dict[str, 'BoundWrapper'] = {}
        self._subgroups: dict[str, 'BoundWrapper'] = {}
        self._arg_names: set[str] = set()

        self._container = self.configure_container()
        self._init_container(self._container, namespace_type)

    @overload
    def __get__(
        self,
        instance: 'WrapperHolder | type | None',
        owner: type | None = None
        ) -> Self:...
    @overload
    def __get__(
        self,
        instance: object,
        owner: type | None = None
        ) -> NS | Literal[NotSelectedType.I]: ...
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
    def T(self) -> type[NS]:
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
        namespace_type: type[NS]
        ):

        assign_infos = ClassAstHolder(namespace_type).get_assign_infos()

        for assign_name, assign_info in assign_infos.items():

            in_annotations = assign_name in namespace_type.__annotations__
            in_dict = assign_name in namespace_type.__dict__
            default = namespace_type.__dict__.get(assign_name, None)

            if isinstance(default, type):
                raise TypeError(
                    f"Assign name '{assign_name}' cannot be a type, "
                    f"it must be an instance or a default value."
                )

            elif in_dict and isinstance(default, SubparserWrapper | SubgroupWrapper):
                self._add_wrapper(
                    container,
                    assign_name,
                    default
                )

            elif in_annotations and in_dict:
                self._arg_names.add(assign_name)
                self._add_opt(
                    container,
                    assign_name,
                    namespace_type.__annotations__[assign_name],
                    default,
                    assign_info.doc,
                )

            elif in_annotations:
                self._arg_names.add(assign_name)
                self._add_req(
                    container,
                    assign_name,
                    namespace_type.__annotations__[assign_name],
                    assign_info.doc,
                )

            elif in_dict:
                self._arg_names.add(assign_name)
                self._add_opt(
                    container,
                    assign_name,
                    type(default),
                    default,
                    assign_info.doc,
                )

            else: # Never
                raise ValueError(
                    f"Assign name '{assign_name}' not found in annotations or dict."
                )

    def _add_wrapper(
        self,
        container: ArgumentContainerProtocol, # for compatibility, not used
        name: str,
        wrapper: 'SubparserWrapper | SubgroupWrapper'
        ):

        wrapper.on_before_bind(name, self)

        bound_wrapper = wrapper._bind(name, self)

        if isinstance(wrapper, SubparserWrapper):
            self._subparsers[name] = bound_wrapper
        elif isinstance(wrapper, SubgroupWrapper):
            self._subgroups[name] = bound_wrapper
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
        annotation: type | SupportsOriginAndArgs,
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
        annotation: type | SupportsOriginAndArgs,
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

        container.add_argument(
            name_or_flag,
            action=action,
            help=doc,
            dest=name,
            default=default,
            **parse_result,
        )

    def _parse_annotation(
        self,
        annotation: UnionType | type | SupportsOriginAndArgs
        ) -> _ParseAnnotationResult:

        if (
            isinstance(annotation, SupportsOriginAndArgs)
            and isinstance(annotation.__origin__, type)
            and issubclass(annotation.__origin__, Sequence)
            ):

            splited_annotation = annotation.__args__

            if issubclass(annotation.__origin__, tuple):
                if ... in annotation.__args__:
                    nargs = '*'
                else:
                    nargs = len(annotation.__args__)

            else:
                nargs = '*'

        elif isinstance(annotation, UnionType):
            splited_annotation = annotation.__args__
            nargs = '*'

        else:
            splited_annotation = (annotation, )
            nargs = None

        flatten_union_and_literal = self._flatten_union_and_literal(splited_annotation)

        pick_choices_is_required = [
            all(
                not isinstance(ann, type | SupportsOriginAndArgs)
                for ann in literals
            )
            for literals in flatten_union_and_literal.values()
        ]

        if all(pick_choices_is_required):
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
                pick_choices_is_required
            )

        return self._ParseAnnotationResult(
            nargs=nargs,
            type=type_,
            choices=choices
        )

    def _flatten_union_and_literal(
        self,
        annotations: tuple[UnionType | type | SupportsOriginAndArgs, ...]
        ) -> dict[
            type | SupportsOriginAndArgs,
            list[type | SupportsOriginAndArgs | Literalizable]
        ]:

        union_args = list(chain.from_iterable(
            ann.__args__
            if isinstance(ann, UnionType)
            else ann.__args__
            if isinstance(ann, SupportsOriginAndArgs) and ann.__origin__ is Union
            else (ann, )
            for ann in annotations
        ))

        literal_args = list(chain.from_iterable(
            ann.__args__
            if isinstance(ann, SupportsOriginAndArgs) and ann.__origin__ is Literal
            else [ann]
            for ann in union_args
        ))

        ret: dict[
            type | SupportsOriginAndArgs,
            list[type | SupportsOriginAndArgs | Literalizable]
        ] = {
            ann: [ann]
            for ann in literal_args
            if isinstance(ann, type | SupportsOriginAndArgs)
        }

        for ann in literal_args:
            if not isinstance(ann, Literalizable):
                continue
            ret.setdefault(type(ann), []).append(ann)

        return ret

    def _multi_type_builder(
        self,
        flatten_union_and_literal: dict[
            type | SupportsOriginAndArgs,
            list[type | SupportsOriginAndArgs | Literalizable]
        ],
        pick_choices_is_required: list[bool]
        ):

        def type_impl(value: str) -> object:

                zipped = zip(
                    flatten_union_and_literal.keys(),
                    flatten_union_and_literal.values(),
                    pick_choices_is_required
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
        annotation: type | SupportsOriginAndArgs
        ) -> type:

        tmp = annotation
        while isinstance(tmp, SupportsOriginAndArgs):
            tmp = tmp.__origin__
        if not isinstance(tmp, type):
            raise TypeError(
                f"Annotation {annotation} is not a type."
            )
        return tmp

    def _flatten_subparsers(self) -> list[tuple[list[str], 'BoundWrapper']]:

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

    def _flatten_subgroups(self) -> list[tuple[list[str], 'BoundWrapper']]:

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

    def on_before_bind(self, bound_name: str, wrapper: 'BaseWrapper'):
        pass
    def on_after_bind(self, bound_name: str, wrapper: 'BaseWrapper'):
        pass

    def on_before_parse(self, bound_names: list[str], bound_wrapper: 'BoundWrapper | None'):
        pass
    def on_after_parse(self, bound_names: list[str], bound_wrapper: 'BoundWrapper | None'):
        pass

    def _bind(self, name: str, parent: 'BaseWrapper') -> 'BoundWrapper':
        return BoundWrapper(name, parent, self)

class SubparserWrapper[NS](BaseWrapper[NS], abc.ABC):
    def __init__(
        self,
        namespace_type: type[NS]
        ):
        super().__init__(namespace_type)
        self._container.set_defaults(_clipar_wrapper=self)
        self._callback: Callable[[NS], object] | None = None

    def _set_callback(
        self,
        callback: Callable[[NS], object]
        ):
        self._callback = callback

    def _check_namespace(self, namespace: object) -> TypeGuard[NS]:
        return all(
            hasattr(namespace, attr)
            for attr in self._arg_names
        )

    def _exec_callback(self, namespace: object) -> object:

        if self._callback is None:
            return

        if self._check_namespace(namespace):
            return self._callback(namespace)

class SubgroupWrapper[NS](BaseWrapper[NS], abc.ABC):
    pass

class WrapperHolder[W: BaseWrapper]: pass

class BoundWrapper[W: BaseWrapper](WrapperHolder[W]):

    def __init__(self, name: str, parent_wrapper: BaseWrapper, self_wrapper: W):
        self._bound_name = name
        self._parent = parent_wrapper
        self._self = self_wrapper

    @property
    def self(self_) -> BaseWrapper:
        return self_._self
