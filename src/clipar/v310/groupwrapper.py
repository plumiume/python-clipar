from typing import Any, TypedDict, TypeVar
from typing_extensions import Unpack

from .basewrapper import BaseWrapper, AddArgumentOptions, ArgumentContainerProtocol, SubgroupWrapper

_NS = TypeVar('_NS')

class LazyContainer(ArgumentContainerProtocol):

    class _Argument:
        def __init__(
            self,
            name_or_flags: tuple[str, ...],
            options: AddArgumentOptions
            ):
            self.name_or_flags = name_or_flags
            self.options = options

    class _ArgumentGroup:
        def __init__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            prefix_chars: str = '-',
            conflict_handler: str = 'error'
            ):
            self.title = title
            self.description = description
            self.prefix_chars = prefix_chars
            self.conflict_handler = conflict_handler

    class _MutuallyExclusiveGroup:
        def __init__(self, required: bool = False):
            self.required = required

    def __init__(
        self,
        options: _ArgumentGroup | _MutuallyExclusiveGroup
        ):
        self.options = options
        self.arguments: list[LazyContainer._Argument] = []
        self.groups: list[LazyContainer] = []
        self.defaults: dict[str, object] = {}

    @classmethod
    def init_as_argument_group(
        cls,
        title: str | None = None,
        description: str | None = None,
        *,
        prefix_chars: str = '-',
        conflict_handler: str = 'error'
        ) -> 'LazyContainer':
        return cls(cls._ArgumentGroup(
            title=title,
            description=description,
            prefix_chars=prefix_chars,
            conflict_handler=conflict_handler
        ))

    @classmethod
    def init_as_mutually_exclusive_group(
        cls,
        *,
        required: bool = False
        ) -> 'LazyContainer':
        return cls(cls._MutuallyExclusiveGroup(
            required=required
        ))

    def add_argument(
        self,
        *name_or_flags: str,
        **kwargs: Unpack[AddArgumentOptions]
        ):
        self.arguments.append(self._Argument(
            name_or_flags=name_or_flags,
            options=kwargs
        ))

    def add_argument_group(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        prefix_chars: str = '-',
        conflict_handler: str = 'error'
        ) -> 'LazyContainer':

        lazy_container = LazyContainer(
            self._ArgumentGroup(
                title=title,
                description=description,
                prefix_chars=prefix_chars,
                conflict_handler=conflict_handler
            )
        )

        self.groups.append(lazy_container)

        return lazy_container

    def add_mutually_exclusive_group(
        self,
        *,
        required: bool = False
        ) -> ArgumentContainerProtocol:

        lazy_container = LazyContainer(
            self._MutuallyExclusiveGroup(
                required=required
            )
        )

        self.groups.append(lazy_container)

        return lazy_container

    def apply(
        self,
        container: ArgumentContainerProtocol,
        title: str | None = None,
        ):

        self._apply_impl(
            supports_add_argument_group=container,
            supports_add_mutually_exclusive_group=container,
            title=title
        )

    def _apply_impl(
        self,
        supports_add_argument_group: ArgumentContainerProtocol,
        supports_add_mutually_exclusive_group: ArgumentContainerProtocol | None,
        title: str | None = None,
        ):

        supports_ameg_group = None

        if isinstance(self.options, self._ArgumentGroup):
            supports_aa_group = supports_add_argument_group.add_argument_group(
                title=(
                    self.options.title
                    if title is None
                    else title
                ),
                description=self.options.description,
                prefix_chars=self.options.prefix_chars,
                conflict_handler=self.options.conflict_handler
            )
            supports_ameg_group = supports_aa_group

        elif isinstance(self.options, self._MutuallyExclusiveGroup): # pyright: ignore[reportUnnecessaryIsInstance]

            if supports_add_mutually_exclusive_group is None:
                raise TypeError(
                    "The bound target does not support add_mutually_exclusive_group"
                )
            
            supports_aa_group = supports_add_mutually_exclusive_group.add_mutually_exclusive_group(
                required=self.options.required
            )

        else:
            raise TypeError(
                f"Unsupported lazy container options type: {type(self.options)}"
            )

        supports_aa_group.set_defaults(**self.defaults)

        for arg in self.arguments:
            supports_aa_group.add_argument(*arg.name_or_flags, **arg.options)

        for lazy_container in self.groups:

            lazy_container._apply_impl(
                supports_aa_group, 
                supports_ameg_group
            )

    def set_defaults(self, **kwargs: Any):
        self.defaults.update(kwargs)

    def get_default(self, dest: str) -> object:
        return self.defaults.get(dest, None)

class GroupWrapperOptions(TypedDict, total=False):
    title: str | None
    "Title of the argument group, displayed in help output."
    description: str | None
    "Description of the argument group, displayed in help output."
    prefix_chars: str
    "Prefix characters for the argument group, default is '-'"
    conflict_handler: str
    "Conflict handler for the argument group, default is 'error'"

class GroupWrapper(SubgroupWrapper[_NS]):

    def __init__(
        self,
        namespace_type: type[_NS],
        options: GroupWrapperOptions = {}
        ):

        lazy_container_options = GroupWrapperOptions(
            title=namespace_type.__name__,
            description=self.__doc__,
        )

        self._lazy_container = LazyContainer.init_as_argument_group(
            **(lazy_container_options | options)
        )

        super().__init__(namespace_type)

    def configure_container(self) -> LazyContainer:
        return self._lazy_container

    def on_after_bind(self, bound_name: str, wrapper: BaseWrapper[Any]):
        self._lazy_container.apply(wrapper._container, bound_name)

class MutuallyExclusiveGroupWrapperOptions(TypedDict, total=False):
    required: bool
    "Whether the mutually exclusive group is required, default is False"

class MutuallyExclusiveGroupWrapper(SubgroupWrapper[_NS]):

    def __init__(
        self,
        namespace_type: type[_NS],
        options: MutuallyExclusiveGroupWrapperOptions = {}
        ):

        self._lazy_container = LazyContainer.init_as_mutually_exclusive_group(
            **options
        )

        super().__init__(namespace_type)

    def configure_container(self) -> LazyContainer:
        return self._lazy_container

    def on_after_bind(self, bound_name: str, wrapper: BaseWrapper[Any]):
        self._lazy_container.apply(wrapper._container, bound_name)
