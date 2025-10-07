from typing import Any, TypedDict

def _is_dunder(name: str) -> bool:
    return name.startswith('__') and name.endswith('__') and len(name) > 4

class _CliparMixinDict(TypedDict):
    _repr_lock: bool
    command: str | None

class _MetaMixin(type):

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        obj = super().__call__(*args, **kwargs)
        assert isinstance(obj, BaseMixin)
        obj.clipar_mixin_dict = _CliparMixinDict(
            _repr_lock=False,
            command=None
        )

class BaseMixin(metaclass=_MetaMixin):
    clipar_mixin_dict: _CliparMixinDict

class ReprMixin(BaseMixin):
    """A mixin class that provides a custom __repr__ method for better object representation.
    
    This mixin automatically generates a string representation of the object by displaying
    all non-dunder attributes and their values. It includes protection against infinite
    recursion through a lock mechanism.
    """

    def __repr__(self):

        if self.clipar_mixin_dict['_repr_lock']:
            return f'{self.__class__.__name__}(...)'

        self.clipar_mixin_dict['_repr_lock'] = True

        exception = None
        try:
            ret = (
                f'{self.__class__.__name__}('
            ) + ' '.join(
                f'{attrname}={repr(getattr(self, attrname))}'
                for attrname in dir(self)
                if not _is_dunder(attrname)
            ) + (
                ')'
            )
        except Exception as e:
            exception = e
            ret = f'{self.__class__.__name__}(error: {e})'
        finally:
            self.clipar_mixin_dict['_repr_lock'] = False

        if exception:
            raise exception

        return ret

class CommandMixin(BaseMixin):
    """A mixin class that provides command storage and retrieval functionality.
    
    This mixin allows objects to store and access a command string through
    a property interface, managing the command state in the clipar_mixin_dict.
    """

    @property
    def command(self) -> str | None:
        """Get the stored command string."""
        return self.clipar_mixin_dict['command']
