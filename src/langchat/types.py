# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Public types returned by the LangChat SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class ChatResponse:
    """Typed response returned by :meth:`LangChat.chat`.

    Attributes:
        text: The assistant's reply text.
        user_id: The user identifier that was passed to :meth:`~LangChat.chat`.
        domain: The domain that was passed to :meth:`~LangChat.chat`.
        status: ``"success"`` or ``"error"``.
        response_time: Wall-clock seconds the request took.
        timestamp: ISO-8601 timestamp of when the response was generated.
        error: Error message when ``status == "error"``, otherwise ``None``.

    Examples::

        response = await lc.chat("Hello", user_id="alice")

        print(response.text)           # the answer
        print(response.response_time)  # e.g. 1.23
        if response:                   # True when status == "success"
            ...
    """

    text: str
    user_id: str
    domain: str
    status: Literal["success", "error"]
    response_time: float
    timestamp: str
    error: str | None = None

    def __bool__(self) -> bool:
        """Return ``True`` when the response succeeded."""
        return self.status == "success"

    def __str__(self) -> str:
        return self.text


__all__ = ["ChatResponse"]
