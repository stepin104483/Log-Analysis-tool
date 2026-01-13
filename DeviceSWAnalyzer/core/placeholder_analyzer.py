"""
Placeholder Analyzer Base Class

Base class for modules that are not yet implemented (coming soon).
"""

from typing import List
from .base_analyzer import BaseAnalyzer, AnalysisInput, AnalysisResult, InputFieldConfig


class PlaceholderAnalyzer(BaseAnalyzer):
    """
    Base class for coming soon modules.

    Provides default implementations that return "not implemented" status.
    Subclasses only need to define module metadata.
    """

    @property
    def status(self) -> str:
        return "coming_soon"

    @property
    def input_fields(self) -> List[InputFieldConfig]:
        return []

    @property
    def supports_ai_review(self) -> bool:
        return False

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        return AnalysisResult(
            success=False,
            module_id=self.module_id,
            cli_output=f"{self.display_name} is coming soon!",
            errors=[f"Module '{self.module_id}' is not yet implemented"]
        )

    def generate_prompt(self, result: AnalysisResult) -> str:
        return ""
