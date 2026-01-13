"""
Base Analyzer Abstract Class

All analysis modules must inherit from BaseAnalyzer and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class InputFieldConfig:
    """Configuration for a single input field."""
    name: str
    label: str
    file_types: List[str]  # e.g., ['.xml', '.txt']
    patterns: List[str]  # Auto-detection patterns e.g., ['*rfc*.xml']
    required: bool = False
    description: str = ""


@dataclass
class AnalysisInput:
    """Generic container for analysis inputs."""
    files: Dict[str, str] = field(default_factory=dict)  # name -> filepath
    parameters: Dict[str, Any] = field(default_factory=dict)  # Additional params
    kb_files: List[str] = field(default_factory=list)  # Knowledge base files


@dataclass
class AnalysisResult:
    """Generic container for analysis results."""
    success: bool
    module_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    summary: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    cli_output: str = ""
    html_report_path: Optional[str] = None
    prompt_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseAnalyzer(ABC):
    """
    Abstract base class for all analysis modules.

    All analysis modules must inherit from this class and implement
    the required abstract methods.
    """

    @property
    @abstractmethod
    def module_id(self) -> str:
        """
        Unique identifier for the module.
        Used in URLs, file paths, and configuration.
        Example: 'bands', 'combos', 'ims'
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable name shown in the UI.
        Example: 'Band Analysis', 'CA/ENDC Combos'
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Brief description of what this module does.
        Shown on the dashboard and help pages.
        """
        pass

    @property
    def icon(self) -> str:
        """
        Icon identifier for the UI (optional).
        Default: 'default'
        """
        return "default"

    @property
    def status(self) -> str:
        """
        Module status: 'active', 'coming_soon', 'beta', 'deprecated'
        """
        return "coming_soon"

    @property
    def version(self) -> str:
        """Module version string."""
        return "1.0.0"

    @property
    @abstractmethod
    def input_fields(self) -> List[InputFieldConfig]:
        """
        Define the input fields for this module.
        Returns a list of InputFieldConfig objects.
        """
        pass

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        """
        Define additional parameters (text inputs, checkboxes, etc.)
        Override in subclass if needed.
        """
        return []

    @property
    def supports_ai_review(self) -> bool:
        """Whether this module supports AI expert review."""
        return True

    @abstractmethod
    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        """
        Run the analysis on the provided inputs.

        Args:
            inputs: AnalysisInput containing file paths and parameters

        Returns:
            AnalysisResult with analysis outcome
        """
        pass

    @abstractmethod
    def generate_prompt(self, result: AnalysisResult) -> str:
        """
        Generate a prompt for Claude AI review.

        Args:
            result: The analysis result to generate prompt for

        Returns:
            String prompt for Claude
        """
        pass

    def generate_html_report(self, result: AnalysisResult, output_path: str) -> str:
        """
        Generate an HTML report for the analysis.
        Override in subclass for custom reports.

        Args:
            result: The analysis result
            output_path: Path to save the HTML report

        Returns:
            Path to the generated report
        """
        # Default implementation - can be overridden
        raise NotImplementedError("Subclass must implement generate_html_report")

    def validate_inputs(self, inputs: AnalysisInput) -> List[str]:
        """
        Validate the inputs before analysis.

        Args:
            inputs: The inputs to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check required fields
        for field_config in self.input_fields:
            if field_config.required and field_config.name not in inputs.files:
                errors.append(f"Required field '{field_config.label}' is missing")

        return errors

    def detect_file_type(self, filename: str) -> Optional[str]:
        """
        Auto-detect which input field a file belongs to based on patterns.

        Args:
            filename: The filename to check

        Returns:
            Field name if matched, None otherwise
        """
        import fnmatch

        lower_filename = filename.lower()

        for field_config in self.input_fields:
            for pattern in field_config.patterns:
                if fnmatch.fnmatch(lower_filename, pattern.lower()):
                    return field_config.name

        return None

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information as a dictionary."""
        return {
            'module_id': self.module_id,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'status': self.status,
            'version': self.version,
            'supports_ai_review': self.supports_ai_review,
            'input_fields': [
                {
                    'name': f.name,
                    'label': f.label,
                    'file_types': f.file_types,
                    'patterns': f.patterns,
                    'required': f.required,
                    'description': f.description,
                }
                for f in self.input_fields
            ],
            'parameters': self.parameters,
        }
