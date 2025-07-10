from typing import Self, Unpack, TypedDict
import argparse

from .basewrapper import BoundWrapper, AddArgumentOptions, ArgumentContainerProtocol, SubgroupWrapper

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
            prefix_chars: str = '-',
            conflict_handler: str = 'error'
            ):
            self.title = title
            self.description = description
            self.prefix_chars = prefix_chars
            self.conflict_handler = conflict_handler

    arguments: list[_Argument]
    argument_groups: list[_ArgumentGroup]
    defaults: dict[str, object]

    def __init__(self):
        self.arguments = []
        self.argument_groups = []
        self.defaults = {}

    def add_argument(
        self,
        *name_or_flags: str,
        **kwargs: Unpack[AddArgumentOptions]
        ):
        self.arguments.append(self._Argument(
            name_or_flags=name_or_flags,
            options=kwargs
        ))

    def lazy_add_argument(self, parser: ArgumentContainerProtocol):
        for lazy_arg in self.arguments:
            parser.add_argument(*lazy_arg.name_or_flags, **lazy_arg.options)

    def add_argument_group(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        prefix_chars: str = '-',
        conflict_handler: str = 'error'
        ) -> Self:
        argument_group = self._ArgumentGroup(
            title=title,
            description=description,
            prefix_chars=prefix_chars,
            conflict_handler=conflict_handler
        )
        lazy_container = self.__class__()
        self.argument_groups.append(argument_group)
        return lazy_container

    def lazy_add_argument_group(
        self,
        parser: ArgumentContainerProtocol
        ):
        for lazy_group in self.argument_groups:
            parser.add_argument_group(
                title=lazy_group.title,
                description=lazy_group.description,
                prefix_chars=lazy_group.prefix_chars,
                conflict_handler=lazy_group.conflict_handler
            )

    def set_defaults(self, **kwargs):
        self.defaults.update(kwargs)

    def get_default(self, dest: str) -> object:
        return self.defaults.get(dest, None)

class GroupWrapperOptions(TypedDict, total=False):
    title: str | None
    description: str | None
    prefix_chars: str
    conflict_handler: str

class GroupWrapper[NS](SubgroupWrapper[NS]):

    def __init__(
        self,
        namespace_type: type[NS],
        parser_options: GroupWrapperOptions = {}
        ):

        self._lazy_container = LazyContainer()
        self._parser_options = GroupWrapperOptions(
            title=namespace_type.__name__,
            description=self.__doc__,
        ) | parser_options

        super().__init__(namespace_type)

    def configure_container(self) -> LazyContainer:
        return self._lazy_container

    def on_before_parse(
        self,
        bound_name: list[str],
        bound_wrapper: BoundWrapper | None
        ):
        if bound_wrapper is None: # Never
            raise ValueError("bound_wrapper must not be None for GroupWrapper")

        parent_container = bound_wrapper._parent._container

        if not isinstance(parent_container, argparse.ArgumentParser): # Never
            raise TypeError(
                f"Expected ArgumentContainerProtocol, got {type(parent_container).__name__}."
            )

        argument_group = parent_container.add_argument_group(
            title=self._parser_options.get("title"),
            description=self._parser_options.get("description"),
            prefix_chars=self._parser_options.get("prefix_chars", '-'),
            conflict_handler=self._parser_options.get("conflict_handler", 'error')
        )
        
        self._lazy_container.lazy_add_argument(argument_group)
        self._lazy_container.lazy_add_argument_group(argument_group)
