"""
Combos Module - Data Models

Core data structures for CA/DC combo analysis.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Any


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


@dataclass
class BandComponent:
    """Single band component in a combo."""
    band: int                    # Band number (e.g., 66, 77)
    band_class: str              # Bandwidth class (A, B, C, etc.)
    mimo_layers: Optional[int] = None  # MIMO layers (2, 4)
    is_nr: bool = False          # True if NR band, False if LTE

    def __hash__(self):
        return hash((self.band, self.band_class, self.is_nr))

    def __eq__(self, other):
        if not isinstance(other, BandComponent):
            return False
        return (self.band == other.band and
                self.band_class == other.band_class and
                self.is_nr == other.is_nr)

    def __str__(self):
        prefix = "n" if self.is_nr else ""
        return f"{prefix}{self.band}{self.band_class}"

    def __repr__(self):
        return f"BandComponent({self})"


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
        """
        Generate normalized key for comparison (bands sorted).

        Sort order: LTE bands first (ascending), then NR bands (ascending)
        """
        sorted_components = sorted(
            self.components,
            key=lambda c: (c.is_nr, c.band, c.band_class)
        )
        return "-".join(str(c) for c in sorted_components)

    @property
    def lte_components(self) -> List[BandComponent]:
        """Get only LTE components."""
        return [c for c in self.components if not c.is_nr]

    @property
    def nr_components(self) -> List[BandComponent]:
        """Get only NR components."""
        return [c for c in self.components if c.is_nr]

    @property
    def bands(self) -> Set[int]:
        """Get all band numbers in this combo."""
        return {c.band for c in self.components}

    def __hash__(self):
        return hash(self.normalized_key)

    def __eq__(self, other):
        if not isinstance(other, Combo):
            return False
        return self.normalized_key == other.normalized_key

    def __str__(self):
        return self.normalized_key

    def __repr__(self):
        return f"Combo({self.combo_type.name}: {self.normalized_key})"


@dataclass
class ReasoningResult:
    """Result from the reasoning engine explaining WHY a discrepancy exists."""
    has_explanation: bool = False
    reason_type: Optional[str] = None      # "regional", "carrier", "regulatory", "hw_variant", "efs"
    explanation: Optional[str] = None       # Human-readable explanation
    source_file: Optional[str] = None       # Which knowledge/EFS file provided this
    severity: str = "unknown"               # "expected", "low", "medium", "high", "critical"
    recommended_action: Optional[str] = None

    def __str__(self):
        if self.has_explanation:
            return f"[{self.severity.upper()}] {self.explanation}"
        return "[UNKNOWN] No explanation found"


@dataclass
class Discrepancy:
    """A discrepancy found between two sources."""
    discrepancy_type: DiscrepancyType
    combo: Combo
    source_a: DataSource
    source_b: DataSource
    details: Optional[str] = None
    reason: Optional[ReasoningResult] = None  # Knowledge-based reasoning

    @property
    def severity(self) -> str:
        """Get severity from reasoning or default to 'medium'."""
        if self.reason:
            return self.reason.severity
        return "medium"

    def __str__(self):
        return f"{self.discrepancy_type.name}: {self.combo} ({self.source_a.name} vs {self.source_b.name})"


@dataclass
class ComboSet:
    """Collection of combos from a single source."""
    source: DataSource
    combo_type: ComboType
    combos: Dict[str, Combo] = field(default_factory=dict)  # key: normalized_key

    def add(self, combo: Combo):
        """Add a combo to the set."""
        combo.source = self.source
        self.combos[combo.normalized_key] = combo

    def get(self, key: str) -> Optional[Combo]:
        """Get a combo by its normalized key."""
        return self.combos.get(key)

    def __len__(self):
        return len(self.combos)

    def __contains__(self, key: str):
        return key in self.combos

    def keys(self) -> Set[str]:
        """Get all normalized keys."""
        return set(self.combos.keys())

    def values(self) -> List[Combo]:
        """Get all combos."""
        return list(self.combos.values())

    def __iter__(self):
        return iter(self.combos.values())


@dataclass
class ComparisonResult:
    """Result of comparing two ComboSets."""
    source_a: DataSource
    source_b: DataSource
    combo_type: ComboType
    common: Set[str] = field(default_factory=set)         # Keys present in both
    only_in_a: Set[str] = field(default_factory=set)      # Keys only in source A
    only_in_b: Set[str] = field(default_factory=set)      # Keys only in source B
    bcs_mismatches: List[Discrepancy] = field(default_factory=list)

    @property
    def total_discrepancies(self) -> int:
        """Total number of discrepancies found."""
        return len(self.only_in_a) + len(self.only_in_b) + len(self.bcs_mismatches)

    @property
    def match_percentage(self) -> float:
        """Percentage of combos that match between sources."""
        total = len(self.common) + len(self.only_in_a) + len(self.only_in_b)
        if total == 0:
            return 100.0
        return (len(self.common) / total) * 100


@dataclass
class AnalysisResult:
    """Complete analysis result for all combo types."""
    timestamp: str = ""
    input_files: Dict[str, str] = field(default_factory=dict)   # source -> filename

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
    summary: Dict[str, Any] = field(default_factory=dict)

    def get_discrepancies_by_type(self, disc_type: DiscrepancyType) -> List[Discrepancy]:
        """Get all discrepancies of a specific type."""
        return [d for d in self.discrepancies if d.discrepancy_type == disc_type]

    def get_discrepancies_by_severity(self, severity: str) -> List[Discrepancy]:
        """Get all discrepancies of a specific severity."""
        return [d for d in self.discrepancies if d.severity == severity]

    def get_discrepancies_by_combo_type(self, combo_type: ComboType) -> List[Discrepancy]:
        """Get all discrepancies for a specific combo type."""
        return [d for d in self.discrepancies if d.combo.combo_type == combo_type]


# ============================================================================
# Knowledge Base Data Structures (P2)
# ============================================================================

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
