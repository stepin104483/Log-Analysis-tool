"""
Combos Module - Knowledge Base Package (P2)

Contains knowledge base components for reasoning:
- KnowledgeBase: Load band restrictions and carrier policies
- ReasoningEngine: Explain WHY discrepancies exist
"""

from .knowledge_base import KnowledgeBase
from .reasoning_engine import ReasoningEngine

__all__ = [
    "KnowledgeBase",
    "ReasoningEngine",
]
