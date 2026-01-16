"""
Combos Module - Reports Package

Contains report generators:
- HTMLReportGenerator: Generate HTML analysis reports
- PromptGenerator: Generate Claude prompts for AI review
"""

from .html_generator import HTMLReportGenerator
from .prompt_generator import PromptGenerator

__all__ = [
    "HTMLReportGenerator",
    "PromptGenerator",
]
