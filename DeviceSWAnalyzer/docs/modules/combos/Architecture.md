# Combos Module - Architecture

> **Version:** 1.1
> **Status:** Ready for Implementation
> **Last Updated:** January 2025
> **Change:** Added Knowledge-Based Reasoning approach

---

## 1. Overview

The Combos module analyzes Carrier Aggregation (CA) and Dual Connectivity (DC) combinations from multiple data sources to identify discrepancies between what's defined in RFC, what's built in the RRC table (0xB826), and what's advertised to the network via UE Capability.

### 1.1 Combo Types Supported

| Type | Description | Primary Use |
|------|-------------|-------------|
| **LTE CA** | LTE Carrier Aggregation (2-6 CC) | Intra/Inter-band CA |
| **NRCA** | NR Carrier Aggregation | FR1/FR2 aggregation |
| **EN-DC** | E-UTRA NR Dual Connectivity | NSA (4G anchor + 5G) |
| **NR-DC** | NR Dual Connectivity | FR1 + FR2 aggregation |

### 1.2 Three-Source Comparison Model with Knowledge-Based Reasoning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              THREE-SOURCE COMPARISON WITH KNOWLEDGE-BASED REASONING          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                           DATA SOURCES (Facts)                               │
│    ┌──────────┐      ┌──────────────┐      ┌─────────────────┐              │
│    │   RFC    │      │    0xB826    │      │  UE Capability  │              │
│    │  (XML)   │      │ (QXDM Log)   │      │   (ASN.1 XML)   │              │
│    │          │      │              │      │                 │              │
│    │ "Should  │      │  "What's     │      │  "What Device   │              │
│    │  Build"  │      │   Built"     │      │   Advertises"   │              │
│    └────┬─────┘      └──────┬───────┘      └────────┬────────┘              │
│         │                   │                       │                        │
│         └─────────┬─────────┴───────────┬──────────┘                        │
│                   │                     │                                    │
│                   ▼                     ▼                                    │
│         ┌─────────────────┐   ┌─────────────────┐                           │
│         │  RFC vs 0xB826  │   │ 0xB826 vs UECap │                           │
│         │   Comparison    │   │   Comparison    │                           │
│         └────────┬────────┘   └────────┬────────┘                           │
│                  │                     │                                     │
│                  └──────────┬──────────┘                                    │
│                             │                                                │
│                             ▼                                                │
│                  ┌─────────────────────┐                                    │
│                  │    DISCREPANCIES    │                                    │
│                  │   (Raw Findings)    │                                    │
│                  └──────────┬──────────┘                                    │
│                             │                                                │
│  ┌──────────────────────────┼──────────────────────────┐                    │
│  │                          ▼                          │                    │
│  │              KNOWLEDGE BASE (Context)               │                    │
│  │  ┌─────────────────┐    ┌─────────────────────┐    │                    │
│  │  │ Band Restriction│    │   Carrier Policy    │    │                    │
│  │  │     Files       │    │      Files          │    │                    │
│  │  │                 │    │                     │    │                    │
│  │  │ - Regional      │    │ - Carrier X reqs    │    │                    │
│  │  │ - Regulatory    │    │ - Market variants   │    │                    │
│  │  │ - HW variants   │    │ - Business rules    │    │                    │
│  │  └────────┬────────┘    └──────────┬──────────┘    │                    │
│  │           │                        │               │                    │
│  │           └───────────┬────────────┘               │                    │
│  │                       ▼                            │                    │
│  │            ┌─────────────────────┐                 │                    │
│  │            │   REASONING ENGINE  │                 │                    │
│  │            │  "WHY is it missing"│                 │                    │
│  │            └─────────────────────┘                 │                    │
│  └────────────────────────┬───────────────────────────┘                    │
│                           │                                                 │
│                           ▼                                                 │
│                ┌───────────────────────┐                                   │
│                │    ANALYSIS REPORT    │                                   │
│                │  - Discrepancy + WHY  │                                   │
│                │  - Context & Reasoning│                                   │
│                │  - AI Recommendations │                                   │
│                └───────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Knowledge-Based Reasoning Concept

The module uses a **two-layer approach**:

| Layer | Purpose | Sources |
|-------|---------|---------|
| **Data Layer** (Facts) | WHAT is different | RFC, 0xB826, UE Capability |
| **Knowledge Layer** (Context) | WHY it's different | Band Restrictions, Carrier Policy |

**Key Insight**: UE Capability is the source of truth for supported bands. Knowledge files don't filter - they **explain discrepancies**.

```
Example Flow:
─────────────
Discrepancy Found: Combo 66A-n71A in RFC but NOT in UE Capability

Step 1: Check Band Restriction File
        → "Band 71 restricted in APAC region"

Step 2: Check Carrier Policy
        → "Carrier X does not require Band 71"

Step 3: Generate Reasoned Output
        → "Combo 66A-n71A missing"
        → REASON: "Band 71 restricted (APAC regional restriction)"
        → SEVERITY: Low (expected behavior)
```

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMBOS MODULE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         WEB LAYER (Flask)                            │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌───────────┐  │    │
│  │  │   Upload    │  │   Analyze    │  │   Results   │  │  Download │  │    │
│  │  │   Route     │  │   Route      │  │   Route     │  │   Route   │  │    │
│  │  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └─────┬─────┘  │    │
│  └─────────┼────────────────┼─────────────────┼────────────────┼───────┘    │
│            │                │                 │                │            │
│  ┌─────────┼────────────────┼─────────────────┼────────────────┼───────┐    │
│  │         ▼                ▼                 ▼                ▼       │    │
│  │                      ORCHESTRATOR                                   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │                  CombosOrchestrator                          │  │    │
│  │  │  - Coordinates parsing, analysis, and report generation      │  │    │
│  │  │  - Loads knowledge base for reasoning                        │  │    │
│  │  │  - Manages analysis pipeline                                 │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │                    PARSER LAYER │                                    │   │
│  │  ┌──────────────┐  ┌────────────┴───┐  ┌──────────────┐            │   │
│  │  │  RFC Parser  │  │  QXDM Parser   │  │ UECap Parser │            │   │
│  │  │              │  │                │  │              │            │   │
│  │  │ - LTE CA     │  │ - 0xB826 logs  │  │ - ASN.1 XML  │            │   │
│  │  │ - NRCA       │  │ - Text/ISLOG   │  │ - MRDC/EUTRA │            │   │
│  │  │ - ENDC       │  │ - Hex decode   │  │ - Bands/BCS  │            │   │
│  │  │ - NRDC       │  │                │  │ - Bands list │            │   │
│  │  └──────┬───────┘  └───────┬────────┘  └──────┬───────┘            │   │
│  │         │                  │                  │                     │   │
│  │  ┌──────┴──────────────────┴──────────────────┴──────┐             │   │
│  │  │               EFS Parser (P2)                      │             │   │
│  │  │  - prune_ca_combos (text)                         │             │   │
│  │  │  - ca_disable (binary)                            │             │   │
│  │  │  - cap_control_nrca_* (binary)                    │             │   │
│  │  └───────────────────────────────────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │                    ANALYZER LAYER                                    │   │
│  │                                 ▼                                    │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    CombosAnalyzer                            │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │   │
│  │  │  │ Normalizer  │  │  Comparator │  │  Discrepancy Finder │  │   │   │
│  │  │  │             │  │             │  │                     │  │   │   │
│  │  │  │ - Band sort │  │ - Set ops   │  │ - Missing combos    │  │   │   │
│  │  │  │ - BCS norm  │  │ - Matching  │  │ - Extra combos      │  │   │   │
│  │  │  │ - Format    │  │ - Scoring   │  │ - BCS mismatch      │  │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │               KNOWLEDGE BASE LAYER (Context & Reasoning)            │   │
│  │                                 ▼                                    │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    KnowledgeBase                             │   │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐                 │   │   │
│  │  │  │ Band Restriction │  │  Carrier Policy  │                 │   │   │
│  │  │  │     Loader       │  │     Loader       │                 │   │   │
│  │  │  │                  │  │                  │                 │   │   │
│  │  │  │ - Regional rules │  │ - Carrier reqs   │                 │   │   │
│  │  │  │ - Regulatory     │  │ - Market config  │                 │   │   │
│  │  │  │ - HW variants    │  │ - Business rules │                 │   │   │
│  │  │  └────────┬─────────┘  └────────┬─────────┘                 │   │   │
│  │  │           └───────────┬─────────┘                           │   │   │
│  │  │                       ▼                                     │   │   │
│  │  │           ┌─────────────────────┐                           │   │   │
│  │  │           │   ReasoningEngine   │                           │   │   │
│  │  │           │  - Match discrepancy│                           │   │   │
│  │  │           │  - Lookup context   │                           │   │   │
│  │  │           │  - Explain WHY      │                           │   │   │
│  │  │           │  - Assign severity  │                           │   │   │
│  │  │           └─────────────────────┘                           │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │                    REPORT LAYER │                                    │   │
│  │                                 ▼                                    │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                  CombosReportGenerator                       │   │   │
│  │  │  - HTML report with summary tables                           │   │   │
│  │  │  - Discrepancy + Reasoning display                           │   │   │
│  │  │  - Claude prompt with context for AI review                  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Structure

```
src/
├── modules/
│   └── combos/
│       ├── __init__.py
│       ├── orchestrator.py          # CombosOrchestrator - main entry point
│       ├── models.py                # Data classes and enums
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── rfc_parser.py        # Parse RFC XML for all combo types
│       │   ├── qxdm_parser.py       # Parse 0xB826 from QXDM logs
│       │   ├── uecap_parser.py      # Parse UE Capability XML
│       │   └── efs_parser.py        # Parse EFS files (P2)
│       │
│       ├── analyzers/
│       │   ├── __init__.py
│       │   ├── combos_analyzer.py   # Core comparison logic
│       │   ├── normalizer.py        # Combo normalization utilities
│       │   └── comparator.py        # Set comparison operations
│       │
│       ├── knowledge/               # Knowledge Base Layer (P2)
│       │   ├── __init__.py
│       │   ├── knowledge_base.py    # Main knowledge base manager
│       │   ├── band_restrictions.py # Band restriction loader
│       │   ├── carrier_policy.py    # Carrier policy loader
│       │   └── reasoning_engine.py  # Reasoning engine for WHY
│       │
│       └── reports/
│           ├── __init__.py
│           ├── html_generator.py    # HTML report generation
│           ├── prompt_generator.py  # Claude prompt generation
│           └── templates/
│               └── combos_report.html
│
├── web/
│   └── routes/
│       └── combos.py                # Flask blueprint for combos
│
templates/
└── combos/
    ├── upload.html                  # File upload interface
    └── results.html                 # Results display

knowledge_library/                   # Shared knowledge files
└── combos/
    ├── band_restrictions/
    │   ├── regional_apac.yaml       # APAC region restrictions
    │   ├── regional_emea.yaml       # EMEA region restrictions
    │   ├── regional_na.yaml         # North America restrictions
    │   └── hw_variants.yaml         # Hardware variant restrictions
    │
    └── carrier_policies/
        ├── verizon.yaml             # Verizon-specific requirements
        ├── att.yaml                 # AT&T-specific requirements
        ├── tmobile.yaml             # T-Mobile requirements
        └── generic.yaml             # Generic/default policy
```

---

## 4. Core Data Structures

### 4.1 Enums

```python
from enum import Enum, auto

class ComboType(Enum):
    """Type of carrier aggregation or dual connectivity combo."""
    LTE_CA = auto()      # LTE Carrier Aggregation
    NRCA = auto()        # NR Carrier Aggregation
    ENDC = auto()        # E-UTRA NR Dual Connectivity (NSA)
    NRDC = auto()        # NR Dual Connectivity

class DataSource(Enum):
    """Source of combo data."""
    RFC = auto()         # RFC XML definition
    RRC_TABLE = auto()   # 0xB826 built RRC table
    UE_CAP = auto()      # UE Capability advertisement
    EFS = auto()         # EFS pruning/disable files
    RFPD = auto()        # RFPD envelope validation

class DiscrepancyType(Enum):
    """Type of discrepancy found between sources."""
    MISSING_IN_RRC = auto()      # In RFC but not in 0xB826
    MISSING_IN_UECAP = auto()    # In 0xB826 but not in UE Cap
    EXTRA_IN_RRC = auto()        # In 0xB826 but not in RFC
    BCS_MISMATCH = auto()        # Band combo exists but BCS differs
    PRUNED_BY_EFS = auto()       # Disabled by EFS file
    ENVELOPE_FILTERED = auto()   # Filtered by RF envelope
```

### 4.2 Data Classes

```python
from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict

@dataclass
class BandComponent:
    """Single band component in a combo."""
    band: int                    # Band number (e.g., 66, 77)
    band_class: str              # Bandwidth class (A, B, C, etc.)
    mimo_layers: Optional[int] = None  # MIMO layers (2, 4)
    is_nr: bool = False          # True if NR band, False if LTE

    def __hash__(self):
        return hash((self.band, self.band_class, self.is_nr))

    def __str__(self):
        prefix = "n" if self.is_nr else ""
        return f"{prefix}{self.band}{self.band_class}"


@dataclass
class Combo:
    """A carrier aggregation or dual connectivity combination."""
    combo_type: ComboType
    components: List[BandComponent]
    bcs: Optional[Set[int]] = None       # Bandwidth Combination Set
    fallback_list: List[int] = field(default_factory=list)
    source: Optional[DataSource] = None
    raw_string: Optional[str] = None     # Original string representation

    @property
    def normalized_key(self) -> str:
        """Generate normalized key for comparison (bands sorted)."""
        sorted_components = sorted(
            self.components,
            key=lambda c: (not c.is_nr, c.band, c.band_class)
        )
        return "-".join(str(c) for c in sorted_components)

    def __hash__(self):
        return hash(self.normalized_key)


@dataclass
class ComboSet:
    """Collection of combos from a single source."""
    source: DataSource
    combo_type: ComboType
    combos: Dict[str, Combo] = field(default_factory=dict)  # key: normalized_key

    def add(self, combo: Combo):
        self.combos[combo.normalized_key] = combo

    def __len__(self):
        return len(self.combos)

    def keys(self) -> Set[str]:
        return set(self.combos.keys())


@dataclass
class Discrepancy:
    """A discrepancy found between two sources."""
    discrepancy_type: DiscrepancyType
    combo: Combo
    source_a: DataSource
    source_b: DataSource
    details: Optional[str] = None
    reason: Optional['ReasoningResult'] = None  # Knowledge-based reasoning


@dataclass
class ReasoningResult:
    """Result from the reasoning engine explaining WHY a discrepancy exists."""
    has_explanation: bool = False
    reason_type: Optional[str] = None      # "regional", "carrier", "regulatory", "hw_variant"
    explanation: Optional[str] = None       # Human-readable explanation
    source_file: Optional[str] = None       # Which knowledge file provided this
    severity: str = "unknown"               # "expected", "low", "medium", "high", "critical"
    recommended_action: Optional[str] = None


@dataclass
class ComparisonResult:
    """Result of comparing two ComboSets."""
    source_a: DataSource
    source_b: DataSource
    combo_type: ComboType
    common: Set[str]              # Keys present in both
    only_in_a: Set[str]           # Keys only in source A
    only_in_b: Set[str]           # Keys only in source B
    bcs_mismatches: List[Discrepancy] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result for all combo types."""
    timestamp: str
    input_files: Dict[str, str]   # source -> filename

    # Parsed combo sets
    rfc_combos: Dict[ComboType, ComboSet] = field(default_factory=dict)
    rrc_combos: Dict[ComboType, ComboSet] = field(default_factory=dict)
    uecap_combos: Dict[ComboType, ComboSet] = field(default_factory=dict)

    # Comparison results
    rfc_vs_rrc: Dict[ComboType, ComparisonResult] = field(default_factory=dict)
    rrc_vs_uecap: Dict[ComboType, ComparisonResult] = field(default_factory=dict)

    # All discrepancies
    discrepancies: List[Discrepancy] = field(default_factory=list)

    # Summary statistics
    summary: Dict[str, any] = field(default_factory=dict)
```

### 4.3 Knowledge Base Data Structures

```python
@dataclass
class BandRestriction:
    """A band restriction rule from knowledge base."""
    band: int                          # Band number (e.g., 71)
    restriction_type: str              # "regional", "regulatory", "hw_variant"
    regions: List[str] = field(default_factory=list)  # ["APAC", "EMEA"]
    reason: str = ""                   # "Not certified in region"
    source_file: str = ""              # "regional_apac.yaml"


@dataclass
class ComboRestriction:
    """A specific combo restriction from knowledge base."""
    combo_key: str                     # Normalized combo key "66A-n71A"
    restriction_type: str              # "regional", "carrier", "regulatory"
    reason: str = ""
    source_file: str = ""


@dataclass
class CarrierRequirement:
    """Carrier-specific combo requirements."""
    carrier_name: str                  # "Verizon", "AT&T"
    required_combos: Set[str] = field(default_factory=set)
    optional_combos: Set[str] = field(default_factory=set)
    excluded_combos: Set[str] = field(default_factory=set)
    notes: Dict[str, str] = field(default_factory=dict)  # combo -> note


@dataclass
class KnowledgeBaseContext:
    """Aggregated knowledge base context for reasoning."""
    band_restrictions: Dict[int, List[BandRestriction]] = field(default_factory=dict)
    combo_restrictions: Dict[str, List[ComboRestriction]] = field(default_factory=dict)
    carrier_requirements: Dict[str, CarrierRequirement] = field(default_factory=dict)
    active_carrier: Optional[str] = None  # Currently selected carrier
    active_region: Optional[str] = None   # Currently selected region
```

---

## 5. Parser Specifications

### 5.1 RFC Parser (`rfc_parser.py`)

Parses RFC XML files to extract combo definitions.

```python
class RFCParser:
    """Parse RFC XML files for combo definitions."""

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse RFC XML and return combo sets by type.

        Expected XML structure:
        <rfc>
          <ca_combos>
            <combo bands="1A-3A-7A" bcs="0,1,2" />
          </ca_combos>
          <endc_combos>
            <combo lte="66A" nr="n77A" bcs="0" />
          </endc_combos>
          ...
        </rfc>
        """
        pass

    def _parse_lte_ca(self, element) -> List[Combo]:
        """Parse LTE CA combo definitions."""
        pass

    def _parse_endc(self, element) -> List[Combo]:
        """Parse EN-DC combo definitions."""
        pass

    def _parse_nrca(self, element) -> List[Combo]:
        """Parse NR CA combo definitions."""
        pass
```

**Key RFC XML Paths:**
- LTE CA: `//ca_combos/combo` or `//lte_ca_combos`
- EN-DC: `//endc_combos/combo` or `//mrdc_combos`
- NRCA: `//nrca_combos/combo`

### 5.2 QXDM Parser (`qxdm_parser.py`)

Parses 0xB826 logs from QXDM text/ISLOG files.

```python
class QXDMParser:
    """Parse QXDM 0xB826 logs for RRC table combos."""

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse 0xB826 log and return combo sets.

        Supports formats:
        - QXDM text export (.txt)
        - ISLOG format (.isf converted to text)
        - HDFV viewer export
        """
        pass

    def _parse_eutra_ca(self, log_content: str) -> ComboSet:
        """Parse E-UTRA (LTE) CA combos from 0xB826."""
        # Look for pattern: eutra-CA: 1A-3A-7A BCS=[0,1,2]
        pass

    def _parse_endc(self, log_content: str) -> ComboSet:
        """Parse EN-DC combos from 0xB826."""
        # Look for pattern: DC_1A_n77A BCS=0 FB=1,2,3
        pass

    def _parse_nr_combos(self, log_content: str) -> ComboSet:
        """Parse NR CA and NR-DC combos."""
        pass
```

**Log Patterns to Match:**
```
# LTE CA pattern
eutra-CA: ([0-9]+[A-Z]-)+[0-9]+[A-Z]\s+BCS=\[([0-9,]+)\]

# EN-DC pattern
DC_([0-9]+[A-Z])_(n[0-9]+[A-Z])\s+BCS=([0-9]+)\s+FB=([0-9,]+)

# Total counts
supportedBandCombinationList: (\d+) items
```

### 5.3 UE Capability Parser (`uecap_parser.py`)

Parses ASN.1 XML exports of UE Capability.

```python
class UECapParser:
    """Parse UE Capability ASN.1 XML exports."""

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse UE Capability XML.

        Expected XML structure matches 3GPP ASN.1 definitions:
        - EUTRA-Capability for LTE CA
        - UE-MRDC-Capability for EN-DC/NR-DC
        - UE-NR-Capability for NR CA
        """
        pass

    def _parse_eutra_capability(self, root) -> ComboSet:
        """Parse supportedBandCombination-r10/r11/r13."""
        pass

    def _parse_mrdc_capability(self, root) -> ComboSet:
        """Parse supportedBandCombinationList in UE-MRDC-Capability."""
        pass
```

**XML Paths:**
```xml
<!-- LTE CA -->
<rf-Parameters-v1020>
  <supportedBandCombination-r10>
    <BandCombinationParameters-r10>
      <bandParametersDL-r10><!-- bands --></bandParametersDL-r10>
    </BandCombinationParameters-r10>
  </supportedBandCombination-r10>
</rf-Parameters-v1020>

<!-- EN-DC (MRDC) -->
<supportedBandCombinationList>
  <BandCombination>
    <bandList>
      <BandParameters><!-- band, class, mimo --></BandParameters>
    </bandList>
  </BandCombination>
</supportedBandCombinationList>
```

### 5.4 EFS Parser (`efs_parser.py`) - P2

Parses EFS files that control combo pruning/disabling.

```python
class EFSParser:
    """Parse EFS files for combo control settings (Phase 2)."""

    def parse_prune_ca_combos(self, file_path: str) -> Set[str]:
        """
        Parse prune_ca_combos text file.

        Format: [Band][Class]-[Band][Class]-[BCS];
        Example: 1A-3A-0;1A-3A-1;7A-20A-0;

        Returns: Set of pruned combo keys
        """
        pass

    def parse_ca_disable(self, file_path: str) -> bool:
        """
        Parse ca_disable binary file.

        Format: Single byte - 0x00 (enabled) or 0x01 (disabled)
        Returns: True if CA is disabled
        """
        pass

    def parse_cap_control(self, file_path: str) -> Dict[str, bool]:
        """
        Parse cap_control_* binary files for NRCA/NRDC.

        Format: Binary 0x00/0x01
        Returns: Dict of capability -> enabled status
        """
        pass
```

**EFS File Locations:**
```
/nv/item_files/modem/lte/rrc/cap/prune_ca_combos
/nv/item_files/modem/lte/rrc/cap/ca_disable
/nv/item_files/modem/lte/rrc/cap/disable_4l_per_band
/nv/item_files/modem/nr5g/rrc/cap_control_nrca_enabled
/nv/item_files/modem/nr5g/rrc/cap_control_nrdc_enabled
```

---

## 6. Analyzer Specification

### 6.1 Normalizer (`normalizer.py`)

```python
class ComboNormalizer:
    """Normalize combos for consistent comparison."""

    def normalize_combo(self, combo: Combo) -> Combo:
        """
        Normalize a combo for comparison:
        1. Sort bands (LTE first, then NR; ascending by band number)
        2. Standardize band class notation (A, B, C)
        3. Normalize BCS representation
        """
        pass

    def normalize_band_string(self, band_str: str) -> str:
        """
        Normalize band string format.

        Examples:
        - "B1A" -> "1A"
        - "n77A" -> "n77A"
        - "1_A" -> "1A"
        """
        pass

    def normalize_bcs(self, bcs: any) -> Set[int]:
        """
        Normalize BCS to set of integers.

        Inputs handled:
        - "0,1,2" -> {0, 1, 2}
        - [0, 1, 2] -> {0, 1, 2}
        - "0" -> {0}
        - None -> empty set
        """
        pass
```

### 6.2 Comparator (`comparator.py`)

```python
class ComboComparator:
    """Compare combo sets from different sources."""

    def compare(self, set_a: ComboSet, set_b: ComboSet) -> ComparisonResult:
        """
        Compare two combo sets and identify differences.

        Returns ComparisonResult with:
        - common: combos in both sets
        - only_in_a: combos only in set A
        - only_in_b: combos only in set B
        - bcs_mismatches: same combo but different BCS
        """
        pass

    def find_bcs_mismatches(
        self,
        set_a: ComboSet,
        set_b: ComboSet,
        common_keys: Set[str]
    ) -> List[Discrepancy]:
        """Find combos with matching bands but different BCS."""
        pass
```

### 6.3 Main Analyzer (`combos_analyzer.py`)

```python
class CombosAnalyzer:
    """Main analyzer that orchestrates all comparisons."""

    def __init__(self):
        self.normalizer = ComboNormalizer()
        self.comparator = ComboComparator()

    def analyze(
        self,
        rfc_combos: Dict[ComboType, ComboSet],
        rrc_combos: Dict[ComboType, ComboSet],
        uecap_combos: Optional[Dict[ComboType, ComboSet]] = None,
        efs_pruned: Optional[Set[str]] = None
    ) -> AnalysisResult:
        """
        Perform complete analysis across all sources.

        Analysis flow:
        1. Normalize all combo sets
        2. Compare RFC vs 0xB826 for each combo type
        3. Compare 0xB826 vs UE Cap (if provided)
        4. Check for EFS pruning (if provided)
        5. Generate discrepancy list
        6. Calculate summary statistics
        """
        pass

    def _categorize_discrepancies(
        self,
        comparison: ComparisonResult
    ) -> List[Discrepancy]:
        """Convert comparison result to discrepancy list."""
        pass

    def _calculate_summary(self, result: AnalysisResult) -> Dict:
        """Calculate summary statistics."""
        return {
            'total_rfc_combos': sum(len(cs) for cs in result.rfc_combos.values()),
            'total_rrc_combos': sum(len(cs) for cs in result.rrc_combos.values()),
            'total_discrepancies': len(result.discrepancies),
            'missing_in_rrc': len([d for d in result.discrepancies
                                   if d.discrepancy_type == DiscrepancyType.MISSING_IN_RRC]),
            'extra_in_rrc': len([d for d in result.discrepancies
                                 if d.discrepancy_type == DiscrepancyType.EXTRA_IN_RRC]),
            # ... more stats
        }
```

---

## 7. Knowledge Base & Reasoning Engine

### 7.1 Knowledge Base File Formats

**Band Restriction File (YAML):**
```yaml
# knowledge_library/combos/band_restrictions/regional_apac.yaml
name: "APAC Regional Restrictions"
version: "1.0"
region: "APAC"

band_restrictions:
  - band: 71
    reason: "Band 71 not certified for APAC market"
    restriction_type: "regional"

  - band: 14
    reason: "FirstNet band - US only"
    restriction_type: "regulatory"

combo_restrictions:
  - combo: "66A-71A"
    reason: "Band 71 not available in APAC"

notes: "Applied to APAC region builds"
```

**Carrier Policy File (YAML):**
```yaml
# knowledge_library/combos/carrier_policies/verizon.yaml
name: "Verizon US Requirements"
version: "2024.1"
carrier: "Verizon"
market: "US"

required_combos:
  - "2A-4A-66A"
  - "66A-n77A"
  - "2A-66A-n77A"

optional_combos:
  - "5A-66A"

excluded_combos:
  - "71A-n71A"   # T-Mobile bands

combo_notes:
  "66A-n77A": "Primary EN-DC combo for C-Band"
  "2A-4A-66A": "Legacy LTE CA - still required"

notes: "Based on Verizon certification requirements 2024"
```

### 7.2 Knowledge Base Loader (`knowledge_base.py`)

```python
class KnowledgeBase:
    """Load and manage knowledge base files."""

    def __init__(self, kb_path: str = "knowledge_library/combos"):
        self.kb_path = kb_path
        self.context = KnowledgeBaseContext()

    def load(
        self,
        region: Optional[str] = None,
        carrier: Optional[str] = None
    ) -> KnowledgeBaseContext:
        """
        Load knowledge base files based on region and carrier.

        Args:
            region: Optional region filter ("APAC", "EMEA", "NA")
            carrier: Optional carrier filter ("Verizon", "AT&T")

        Returns:
            KnowledgeBaseContext with loaded rules
        """
        self._load_band_restrictions(region)
        self._load_carrier_policies(carrier)
        self.context.active_region = region
        self.context.active_carrier = carrier
        return self.context

    def _load_band_restrictions(self, region: Optional[str]):
        """Load band restriction YAML files."""
        pass

    def _load_carrier_policies(self, carrier: Optional[str]):
        """Load carrier policy YAML files."""
        pass
```

### 7.3 Reasoning Engine (`reasoning_engine.py`)

```python
class ReasoningEngine:
    """
    Reasoning engine that explains WHY discrepancies exist.

    This does NOT filter - it provides CONTEXT and EXPLANATION.
    """

    def __init__(self, knowledge_base: KnowledgeBaseContext):
        self.kb = knowledge_base

    def explain_discrepancy(self, discrepancy: Discrepancy) -> ReasoningResult:
        """
        Attempt to explain why a discrepancy exists.

        Checks in order:
        1. Band restrictions (is any band in combo restricted?)
        2. Combo restrictions (is this specific combo restricted?)
        3. Carrier requirements (does carrier exclude this?)
        4. Return "unknown" if no explanation found

        Args:
            discrepancy: The discrepancy to explain

        Returns:
            ReasoningResult with explanation or "unknown"
        """
        # Extract bands from combo
        bands = [c.band for c in discrepancy.combo.components]

        # Step 1: Check band restrictions
        for band in bands:
            if band in self.kb.band_restrictions:
                restrictions = self.kb.band_restrictions[band]
                for r in restrictions:
                    if self._matches_context(r):
                        return ReasoningResult(
                            has_explanation=True,
                            reason_type=r.restriction_type,
                            explanation=f"Band {band}: {r.reason}",
                            source_file=r.source_file,
                            severity=self._calculate_severity(r, discrepancy),
                            recommended_action=self._get_recommendation(r)
                        )

        # Step 2: Check combo restrictions
        combo_key = discrepancy.combo.normalized_key
        if combo_key in self.kb.combo_restrictions:
            r = self.kb.combo_restrictions[combo_key][0]
            return ReasoningResult(
                has_explanation=True,
                reason_type=r.restriction_type,
                explanation=r.reason,
                source_file=r.source_file,
                severity="expected",
                recommended_action="No action - expected restriction"
            )

        # Step 3: Check carrier requirements
        if self.kb.active_carrier:
            carrier_req = self.kb.carrier_requirements.get(self.kb.active_carrier)
            if carrier_req:
                if combo_key in carrier_req.excluded_combos:
                    return ReasoningResult(
                        has_explanation=True,
                        reason_type="carrier",
                        explanation=f"Excluded by {self.kb.active_carrier} policy",
                        source_file=f"{self.kb.active_carrier.lower()}.yaml",
                        severity="expected",
                        recommended_action="No action - carrier exclusion"
                    )

        # No explanation found
        return ReasoningResult(
            has_explanation=False,
            severity="high",
            recommended_action="Investigate - unexpected discrepancy"
        )

    def _calculate_severity(
        self,
        restriction: BandRestriction,
        discrepancy: Discrepancy
    ) -> str:
        """
        Calculate severity based on restriction type and discrepancy.

        - expected: Known restriction, no issue
        - low: Minor, informational
        - medium: Should be reviewed
        - high: Potential configuration error
        - critical: Likely bug or misconfiguration
        """
        if restriction.restriction_type in ["regional", "regulatory"]:
            return "expected"
        elif restriction.restriction_type == "hw_variant":
            return "low"
        return "medium"

    def _get_recommendation(self, restriction: BandRestriction) -> str:
        """Generate recommendation based on restriction type."""
        recommendations = {
            "regional": "No action - regional restriction as designed",
            "regulatory": "No action - regulatory compliance",
            "hw_variant": "Verify hardware variant matches build config",
            "carrier": "Verify carrier requirements are current"
        }
        return recommendations.get(restriction.restriction_type, "Review manually")

    def enrich_discrepancies(
        self,
        discrepancies: List[Discrepancy]
    ) -> List[Discrepancy]:
        """Add reasoning to all discrepancies."""
        for d in discrepancies:
            d.reason = self.explain_discrepancy(d)
        return discrepancies
```

### 7.4 Severity Classification

| Severity | Meaning | Action Required |
|----------|---------|-----------------|
| **expected** | Discrepancy is known and intentional | None |
| **low** | Minor, informational only | Optional review |
| **medium** | Should be reviewed but not blocking | Review recommended |
| **high** | Potential configuration error | Investigation required |
| **critical** | Likely bug or serious misconfiguration | Immediate attention |

---

## 8. Report Generation

### 8.1 HTML Report Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Combos Analysis Report</title>
    <style>/* Styling */</style>
</head>
<body>
    <!-- Header with timestamp and file info -->
    <header>
        <h1>Combos Analysis Report</h1>
        <div class="metadata">...</div>
    </header>

    <!-- Summary Dashboard -->
    <section id="summary">
        <div class="stat-card">RFC Combos: X</div>
        <div class="stat-card">RRC Combos: Y</div>
        <div class="stat-card">Discrepancies: Z</div>
    </section>

    <!-- By Combo Type Tabs -->
    <section id="combo-types">
        <div class="tab" data-type="lte-ca">LTE CA</div>
        <div class="tab" data-type="endc">EN-DC</div>
        <div class="tab" data-type="nrca">NR CA</div>
        <div class="tab" data-type="nrdc">NR-DC</div>
    </section>

    <!-- Comparison Tables -->
    <section id="rfc-vs-rrc">
        <h2>RFC vs 0xB826 Comparison</h2>
        <table class="comparison-table">
            <tr class="match">...</tr>
            <tr class="missing">...</tr>
            <tr class="extra">...</tr>
        </table>
    </section>

    <!-- Discrepancy Details -->
    <section id="discrepancies">
        <h2>Discrepancies</h2>
        <div class="discrepancy missing-in-rrc">...</div>
        <div class="discrepancy bcs-mismatch">...</div>
    </section>

    <!-- AI Review Section (populated by Claude) -->
    <section id="ai-review" class="hidden">
        <h2>AI Expert Review</h2>
        <div id="claude-analysis"></div>
    </section>
</body>
</html>
```

### 8.2 Claude Prompt Generation

```python
class PromptGenerator:
    """Generate Claude analysis prompt."""

    def generate(self, result: AnalysisResult) -> str:
        """
        Generate prompt for Claude expert review.

        Includes:
        - Summary statistics
        - List of discrepancies
        - Request for analysis and recommendations
        """
        prompt = f"""
You are an RF engineer expert analyzing CA/DC combo configurations.

## Analysis Summary
- RFC defines {result.summary['total_rfc_combos']} combos
- RRC table has {result.summary['total_rrc_combos']} combos
- Found {result.summary['total_discrepancies']} discrepancies

## Discrepancies Found
{self._format_discrepancies(result.discrepancies)}

## Your Task
1. Analyze each discrepancy and explain potential causes
2. Prioritize issues by severity (Critical/High/Medium/Low)
3. Provide specific recommendations to resolve each issue
4. Flag any combos that may indicate configuration errors

Format your response with clear sections and bullet points.
"""
        return prompt
```

---

## 8. Web Routes (`combos.py`)

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

combos_bp = Blueprint('combos', __name__, url_prefix='/combos')

@combos_bp.route('/')
def upload():
    """Display file upload form."""
    return render_template('combos/upload.html')


@combos_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Process uploaded files and run analysis.

    Expected files:
    - rfc_file: RFC XML (required)
    - qxdm_file: 0xB826 log (required)
    - uecap_file: UE Capability XML (optional)
    - efs_files: EFS files (optional, P2)
    """
    # Validate required files
    if 'rfc_file' not in request.files or 'qxdm_file' not in request.files:
        flash('RFC and QXDM files are required', 'error')
        return redirect(url_for('combos.upload'))

    # Save uploaded files
    # ...

    # Run orchestrator
    orchestrator = CombosOrchestrator()
    result = orchestrator.analyze(
        rfc_path=rfc_path,
        qxdm_path=qxdm_path,
        uecap_path=uecap_path  # Optional
    )

    # Generate reports
    html_report = orchestrator.generate_html_report(result)
    prompt_file = orchestrator.generate_prompt(result)

    return render_template(
        'combos/results.html',
        result=result,
        html_report=html_report,
        prompt_file=prompt_file
    )


@combos_bp.route('/download/<filename>')
def download(filename):
    """Download generated report."""
    safe_filename = secure_filename(filename)
    file_path = os.path.join(current_app.config['OUTPUT_FOLDER'], safe_filename)

    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('combos.upload'))

    return send_file(file_path, as_attachment=True)


@combos_bp.route('/ai-review', methods=['POST'])
def ai_review():
    """Execute Claude CLI for AI expert review."""
    # Similar to bands module implementation
    pass
```

---

## 9. Orchestrator (`orchestrator.py`)

```python
class CombosOrchestrator:
    """Main orchestrator coordinating parsing, analysis, and reporting."""

    def __init__(self):
        self.rfc_parser = RFCParser()
        self.qxdm_parser = QXDMParser()
        self.uecap_parser = UECapParser()
        self.efs_parser = EFSParser()
        self.analyzer = CombosAnalyzer()
        self.html_generator = HTMLGenerator()
        self.prompt_generator = PromptGenerator()

    def analyze(
        self,
        rfc_path: str,
        qxdm_path: str,
        uecap_path: Optional[str] = None,
        efs_paths: Optional[Dict[str, str]] = None
    ) -> AnalysisResult:
        """
        Run complete analysis pipeline.

        Steps:
        1. Parse RFC XML
        2. Parse QXDM 0xB826 log
        3. Parse UE Capability (if provided)
        4. Parse EFS files (if provided)
        5. Run analyzer
        6. Return result
        """
        # Parse all sources
        rfc_combos = self.rfc_parser.parse(rfc_path)
        rrc_combos = self.qxdm_parser.parse(qxdm_path)

        uecap_combos = None
        if uecap_path:
            uecap_combos = self.uecap_parser.parse(uecap_path)

        efs_pruned = None
        if efs_paths:
            efs_pruned = self._parse_efs_files(efs_paths)

        # Run analysis
        result = self.analyzer.analyze(
            rfc_combos=rfc_combos,
            rrc_combos=rrc_combos,
            uecap_combos=uecap_combos,
            efs_pruned=efs_pruned
        )

        return result

    def generate_html_report(self, result: AnalysisResult) -> str:
        """Generate HTML report and return filename."""
        return self.html_generator.generate(result)

    def generate_prompt(self, result: AnalysisResult) -> str:
        """Generate Claude prompt and return filename."""
        return self.prompt_generator.generate(result)
```

---

## 10. Implementation Phases

### Phase 0 (P0) - Core Infrastructure
| Task | Description | Priority |
|------|-------------|----------|
| Data models | Implement all dataclasses and enums | Critical |
| RFC parser | Parse combo definitions from RFC XML | Critical |
| QXDM parser | Parse 0xB826 logs | Critical |
| Basic analyzer | RFC vs 0xB826 comparison | Critical |
| HTML report | Basic report generation | Critical |
| Web routes | Upload and analyze endpoints | Critical |

### Phase 1 (P1) - Enhanced Analysis
| Task | Description | Priority |
|------|-------------|----------|
| UE Cap parser | Parse ASN.1 XML capability | High |
| Three-source comparison | Full RFC -> 0xB826 -> UECap flow | High |
| Claude integration | AI expert review | High |
| RFPD integration | Envelope validation data | Medium |
| Enhanced reporting | Detailed discrepancy breakdown | Medium |

### Phase 2 (P2) - Knowledge-Based Reasoning & Advanced Features
| Task | Description | Priority |
|------|-------------|----------|
| Knowledge Base | Band restrictions & carrier policy loaders | Medium |
| Reasoning Engine | Explain WHY discrepancies exist | Medium |
| EFS parser | Parse prune_ca_combos, ca_disable | Medium |
| EFS analysis | Show EFS impact on combos | Medium |

**Note**: Knowledge Base provides CONTEXT for reasoning, not filtering. UE Capability remains the source of truth for supported bands.

**Note**: DUT Automation (QPST/PCAT) is intentionally NOT part of Combos module - it will be a separate module.

---

## 11. Dependencies

### Python Packages
```
lxml>=4.9.0          # XML parsing
defusedxml>=0.7.1    # Secure XML parsing
jinja2>=3.1.0        # HTML templating
flask>=2.3.0         # Web framework (existing)
```

### Internal Dependencies
```
src/modules/combos/
├── models.py        <- No dependencies
├── parsers/         <- Depends on models.py
├── analyzers/       <- Depends on models.py, parsers/
├── reports/         <- Depends on models.py, analyzers/
└── orchestrator.py  <- Depends on all above
```

---

## 12. Testing Strategy

### Unit Tests
```
tests/unit/combos/
├── test_models.py           # Data class tests
├── test_rfc_parser.py       # RFC parsing tests
├── test_qxdm_parser.py      # QXDM parsing tests
├── test_normalizer.py       # Normalization tests
├── test_comparator.py       # Comparison logic tests
└── test_analyzer.py         # Full analysis tests
```

### Integration Tests
```
tests/integration/combos/
├── test_full_pipeline.py    # End-to-end tests
├── test_web_routes.py       # Flask route tests
└── test_report_generation.py
```

### Test Data
```
tests/fixtures/combos/
├── sample_rfc.xml           # Sample RFC file
├── sample_0xB826.txt        # Sample QXDM log
├── sample_uecap.xml         # Sample UE Capability
└── expected_results/        # Expected analysis outputs
```

---

## 13. Related Documents

- [Requirements.md](./Requirements.md) - Module requirements
- [CA_ENDC_NRDC_NRCA_research_document.md](../../CA_ENDC_NRDC_NRCA_research_document.md) - Technical research
- [Combos_Module_Requirements.md](../../Combos_Module_Requirements.md) - Detailed requirements
- [Overall_Architecture.md](../../Overall_Architecture.md) - System architecture
- [Qualcomm 80-NU834-1](../../../knowledge_library/Qualcomm_Docs/80-NU834-1_REV_A_Application_Note__EFS_to_Control_Ca-Supported_Band_Combinations.pdf) - EFS Control reference

---

## 14. Control Mechanisms Reference

### 14.1 LTE CA Control (via EFS)
```
Location: /nv/item_files/modem/lte/rrc/cap/
Files:
- prune_ca_combos  : Text file, format "[Band][Class]-...-[BCS];"
- ca_disable       : Binary (0x01 = disabled)
- disable_4l_per_band : Disable 4-layer MIMO per band
```

### 14.2 NRCA/NR-DC Control (via EFS)
```
Location: /nv/item_files/modem/nr5g/rrc/
Files:
- cap_control_nrca_enabled  : Binary (0x00/0x01)
- cap_control_nrdc_enabled  : Binary (0x00/0x01)
```

### 14.3 EN-DC Control (NOT via EFS)
```
EN-DC is controlled by:
- Policyman XML rules
- RFC (Radio Frequency Configuration)
- MCFG (Modem Configuration)

NOT controlled by EFS pruning files.
```

---

*Document Version: 1.1 | Ready for Implementation Review*
*Change: Added Knowledge-Based Reasoning approach (Section 1.3, 7)*
