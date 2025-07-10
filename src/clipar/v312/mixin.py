def _is_dunder(name: str) -> bool:
    return name.startswith('__') and name.endswith('__') and len(name) > 4

class ReprMixin:

    def __repr__(self):

        return (
            f'{self.__class__.__name__}< '
        ) + ' '.join(
            f'{attrname}={getattr(self, attrname)!r}'
            for attrname in dir(self)
            if not _is_dunder(attrname)
        ) + (
            ' >'
        )