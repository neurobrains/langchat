# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Flashrank reranker provider."""

from langchat.reranker.flashrank_adapter import FlashrankRerankAdapter


class Flashrank(FlashrankRerankAdapter):
    """
    Flashrank reranker provider.

    Fast, local reranking using ONNX models.
    """
    pass


__all__ = ["Flashrank"]


# Backward compatibility
FlashrankProvider = Flashrank

