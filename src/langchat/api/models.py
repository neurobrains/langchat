"""
Pydantic models for API requests and responses.
"""

from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for chat queries"""

    query: str
    userId: str
    domain: str
    image: Optional[str] = None
