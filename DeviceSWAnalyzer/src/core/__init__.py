"""
Band Combos Analyzer - Core Package

This package contains the core analysis logic:
- BandTracer: Traces bands through filtering stages
- BandAnalyzer: Coordinates parsing and analysis
- PromptGenerator: Generates prompt.txt for Claude CLI
"""

from .band_tracer import BandTracer, BandTraceResult, BandStatus, FinalStatus
from .analyzer import BandAnalyzer, AnalysisInput, AnalysisResult, AnalysisSummary, run_analysis
from .prompt_generator import PromptGenerator, generate_prompt

__all__ = [
    'BandTracer', 'BandTraceResult', 'BandStatus', 'FinalStatus',
    'BandAnalyzer', 'AnalysisInput', 'AnalysisResult', 'AnalysisSummary', 'run_analysis',
    'PromptGenerator', 'generate_prompt',
]
