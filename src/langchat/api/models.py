# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for chat queries"""

    query: str
    userId: str
    platform: str
    image: str | None = None
