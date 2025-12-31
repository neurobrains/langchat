# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.


class UnsupportedFileTypeError(Exception):
    """
    Exception raised when a file type is not supported.

    This exception is used when document loaders cannot process
    a given file type.
    """

    pass
