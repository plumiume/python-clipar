"""
Core entities module for clipar CLI library.

Copyright (c) 2025 Clipar Contributors
SPDX-License-Identifier: MIT

This module provides version-specific imports for the main wrapper classes
used to create command-line interfaces from Python classes. The appropriate
implementation is selected based on the Python version at runtime.
"""

import sys

# Import version-appropriate implementations based on Python version
if sys.version_info >= (3, 12):
    # Use Python 3.12+ implementation with new generic syntax
    from .v312.basewrapper import BaseWrapper
    from .v312.namespacewrapper import NamespaceWrapper
    from .v312.groupwrapper import GroupWrapper
elif sys.version_info >= (3, 10):
    # Use Python 3.10/3.11 implementation with legacy generic syntax
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
