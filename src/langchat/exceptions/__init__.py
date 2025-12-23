# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""
Compatibility module.

`UnsupportedFileTypeError` now lives in `langchat.utils.exceptions`.
This namespace stays to avoid breaking existing imports:
  - from langchat.exceptions import UnsupportedFileTypeError
"""

from langchat.utils.exceptions import UnsupportedFileTypeError

__all__ = ["UnsupportedFileTypeError"]


