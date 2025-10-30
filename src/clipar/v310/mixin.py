"""
Mixin classes providing additional functionality for CLI namespace objects.

This module contains utility mixins that can be inherited by namespace classes
to add extra functionality like improved string representation.
"""

def _is_dunder(name: str) -> bool:
    """Check if attribute name is a dunder (double underscore) method."""
    return name.startswith('__') and name.endswith('__') and len(name) > 4

class ReprMixin:
    """
    Mixin class providing improved string representation for namespace objects.
    
    Provides a detailed __repr__ method that shows all non-dunder attributes
    and their values. Includes protection against infinite recursion.
    
    Example:
        @namespace  
        class Config(ReprMixin):
            verbose: bool = False
            count: int = 1
            
        config = Config.parse_args()
        print(repr(config))  # Config<verbose=False count=1>
    """

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
