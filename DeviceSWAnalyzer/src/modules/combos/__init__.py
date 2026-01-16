"""
Combos Module - CA/DC Combo Analysis

Analyzes Carrier Aggregation (CA) and Dual Connectivity (DC) combinations
from multiple data sources to identify discrepancies.

Supported combo types:
- LTE CA: LTE Carrier Aggregation
- NRCA: NR Carrier Aggregation
- EN-DC: E-UTRA NR Dual Connectivity (NSA)
- NR-DC: NR Dual Connectivity

Three-source comparison:
- RFC (XML): What should be built
- 0xB826 (QXDM): What's actually built
- UE Capability (ASN.1 XML): What device advertises

Usage:
    from modules.combos import CombosOrchestrator, run_analysis

    # Simple usage
    result = run_analysis(rfc_file='rfc.xml', qxdm_file='0xb826.txt')

    # Or with orchestrator
    orchestrator = CombosOrchestrator(output_dir='./output')
    response = orchestrator.analyze(rfc_file='rfc.xml', qxdm_file='0xb826.txt')
"""

from .models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    BandComponent,
    Combo,
    ComboSet,
    Discrepancy,
    ReasoningResult,
    ComparisonResult,
    AnalysisResult,
)

from .orchestrator import CombosOrchestrator, run_analysis
from .analyzers import CombosAnalyzer, Normalizer, Comparator
from .parsers import RFCParser, QXDMParser, UECapParser, EFSParser
from .reports import HTMLReportGenerator, PromptGenerator
from .knowledge import KnowledgeBase, ReasoningEngine

__version__ = "1.1.0"  # P1/P2 implemented
__all__ = [
    # Models
    "ComboType",
    "DataSource",
    "DiscrepancyType",
    "BandComponent",
    "Combo",
    "ComboSet",
    "Discrepancy",
    "ReasoningResult",
    "ComparisonResult",
    "AnalysisResult",
    # Orchestrator
    "CombosOrchestrator",
    "run_analysis",
    # Analyzers
    "CombosAnalyzer",
    "Normalizer",
    "Comparator",
    # Parsers
    "RFCParser",
    "QXDMParser",
    "UECapParser",
    "EFSParser",
    # Reports
    "HTMLReportGenerator",
    "PromptGenerator",
    # Knowledge Base (P2)
    "KnowledgeBase",
    "ReasoningEngine",
]
