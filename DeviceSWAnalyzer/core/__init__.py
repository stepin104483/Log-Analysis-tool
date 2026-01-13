"""
Core Framework for Analysis Tool

This module provides the base classes and utilities for building
analysis modules in a plugin-based architecture.
"""

from .base_analyzer import BaseAnalyzer, AnalysisInput, AnalysisResult, InputFieldConfig
from .placeholder_analyzer import PlaceholderAnalyzer
from .module_registry import ModuleRegistry
from .ai_review import AIReviewService
from .file_handler import FileHandler

__all__ = [
    'BaseAnalyzer',
    'PlaceholderAnalyzer',
    'AnalysisInput',
    'AnalysisResult',
    'InputFieldConfig',
    'ModuleRegistry',
    'AIReviewService',
    'FileHandler',
]
