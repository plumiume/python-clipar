import sys

if sys.version_info >= (3, 12):
    from .v312.basewrapper import NotSelectedType, NotSelected
    from .v312.decorator import namespace, group, mutually_exclusive_group
    from .v312 import mixin
elif sys.version_info >= (3, 10):
    from .v310.basewrapper import NotSelectedType, NotSelected
    from .v310.decorator import namespace, group, mutually_exclusive_group
    from .v310 import mixin
else:
    raise ImportError("clipar requires Python 3.10 or later")
