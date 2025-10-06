def _is_dunder(name: str) -> bool:
    return name.startswith('__') and name.endswith('__') and len(name) > 4

class ReprMixin:

    def __repr__(self):

        if self.__repr__.__dict__.get('lock'):
            return f'{self.__class__.__name__}<...>'

        self.__repr__.__dict__['lock'] = True

        exception = None
        try:
            ret = (
                f'{self.__class__.__name__}<'
            ) + ' '.join(
                f'{attrname}={repr(getattr(self, attrname))}'
                for attrname in dir(self)
                if not _is_dunder(attrname)
            ) + (
                '>'
            )
        except Exception as e:
            exception = e
            ret = f'{self.__class__.__name__}<error: {e}>'
        finally:
            self.__repr__.__dict__['lock'] = False

        if exception:
            raise exception

        return ret
