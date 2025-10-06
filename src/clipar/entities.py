import sys

if sys.version_info >= (3, 12):
    from .v312.basewrapper import BaseWrapper
    from .v312.namespacewrapper import NamespaceWrapper
    from .v312.groupwrapper import GroupWrapper
elif sys.version_info >= (3, 10):
    from .v310.basewrapper import BaseWrapper
    from .v310.namespacewrapper import NamespaceWrapper
    from .v310.groupwrapper import GroupWrapper
else:
    raise ImportError("clipar requires Python 3.10 or later")

__all__ = [
    "BaseWrapper",
    "NamespaceWrapper",
    "GroupWrapper",
]
