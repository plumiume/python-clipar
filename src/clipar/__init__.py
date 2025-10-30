"""
clipar - A Python library for creating CLI applications using class decorators.

Copyright (c) 2025 Clipar Contributors
SPDX-License-Identifier: MIT

This module provides decorators to transform Python classes into command-line
interfaces using argparse. It supports nested subcommands, argument groups,
and mutually exclusive groups with type-safe parsing.

Main decorators:
    @namespace: Creates a CLI namespace from a class
    @group: Creates an argument group within a namespace  
    @mutually_exclusive_group: Creates mutually exclusive arguments

Example:
    @namespace
    class Config:
        verbose: bool = False
        input_file: str
        
    config = Config.parse_args()
"""

import sys

# Version-specific imports for backward compatibility
if sys.version_info >= (3, 12):
    # Python 3.12+ implementation with new generic syntax
    from .v312.basewrapper import NotSelectedType, NotSelected
    from .v312.decorator import namespace, group, mutually_exclusive_group
    from .v312 import mixin
elif sys.version_info >= (3, 10):
    # Python 3.10/3.11 implementation with legacy generic syntax
    from .v310.basewrapper import NotSelectedType, NotSelected
    from .v310.decorator import namespace, group, mutually_exclusive_group
    from .v310 import mixin
else:
    raise ImportError("clipar requires Python 3.10 or later")

__all__ = [
    "NotSelectedType", "NotSelected",
    "namespace", "group", "mutually_exclusive_group",
    "mixin",
]
