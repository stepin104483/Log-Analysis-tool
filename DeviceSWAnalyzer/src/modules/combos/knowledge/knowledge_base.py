"""
Knowledge Base Loader

Loads and manages knowledge base files for reasoning:
- Band restriction files (regional, regulatory, hw_variant)
- Carrier policy files (carrier-specific requirements)

Knowledge base provides CONTEXT for explaining discrepancies,
not for filtering combos.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    yaml = None

from ..models import (
    BandRestriction,
    ComboRestriction,
    CarrierRequirement,
    KnowledgeBaseContext,
)

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Load and manage knowledge base files for reasoning.

    The knowledge base provides context to explain WHY discrepancies exist,
    not to filter or modify analysis results.
    """

    def __init__(self, kb_path: Optional[str] = None):
        """
        Initialize knowledge base.

        Args:
            kb_path: Path to knowledge base directory.
                     Default: knowledge_library/combos/
        """
        self.kb_path = kb_path
        self.context = KnowledgeBaseContext()
        self._loaded = False
        self._load_errors: List[str] = []

    def load(
        self,
        region: Optional[str] = None,
        carrier: Optional[str] = None,
        kb_files: Optional[List[str]] = None,
    ) -> KnowledgeBaseContext:
        """
        Load knowledge base files.

        Args:
            region: Optional region filter ("APAC", "EMEA", "NA", "LATAM")
            carrier: Optional carrier filter ("Verizon", "AT&T", etc.)
            kb_files: Optional list of specific KB files to load

        Returns:
            KnowledgeBaseContext with loaded rules
        """
        self._load_errors = []
        self.context = KnowledgeBaseContext()
        self.context.active_region = region
        self.context.active_carrier = carrier

        if yaml is None:
            self._load_errors.append("PyYAML not installed - knowledge base disabled")
            logger.warning("PyYAML not installed - knowledge base will be disabled")
            return self.context

        # Load from specific files if provided
        if kb_files:
            for file_path in kb_files:
                self._load_file(file_path)
        elif self.kb_path:
            # Load from kb_path directory
            self._load_from_directory(region, carrier)

        self._loaded = True
        return self.context

    def _load_from_directory(self, region: Optional[str], carrier: Optional[str]):
        """Load knowledge base from directory structure."""
        kb_path = Path(self.kb_path)

        if not kb_path.exists():
            logger.warning(f"Knowledge base path not found: {kb_path}")
            return

        # Load band restrictions
        restrictions_path = kb_path / 'band_restrictions'
        if restrictions_path.exists():
            for yaml_file in restrictions_path.glob('*.yaml'):
                # Filter by region if specified
                if region:
                    filename = yaml_file.stem.lower()
                    if 'regional' in filename and region.lower() not in filename:
                        continue
                self._load_band_restriction_file(yaml_file)

        # Load carrier policies
        policies_path = kb_path / 'carrier_policies'
        if policies_path.exists():
            for yaml_file in policies_path.glob('*.yaml'):
                # Filter by carrier if specified
                if carrier:
                    filename = yaml_file.stem.lower()
                    if carrier.lower() not in filename and filename != 'generic':
                        continue
                self._load_carrier_policy_file(yaml_file)

    def _load_file(self, file_path: str):
        """Load a single knowledge base file."""
        path = Path(file_path)

        if not path.exists():
            self._load_errors.append(f"File not found: {file_path}")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                return

            # Determine file type and load accordingly
            if 'band_restrictions' in data or 'combo_restrictions' in data:
                self._process_restriction_data(data, str(path))
            elif 'required_combos' in data or 'carrier' in data:
                self._process_carrier_data(data, str(path))
            else:
                # Try to auto-detect
                self._process_generic_data(data, str(path))

        except yaml.YAMLError as e:
            self._load_errors.append(f"YAML parse error in {file_path}: {e}")
        except Exception as e:
            self._load_errors.append(f"Error loading {file_path}: {e}")

    def _load_band_restriction_file(self, file_path: Path):
        """Load a band restriction YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data:
                self._process_restriction_data(data, str(file_path))

        except Exception as e:
            self._load_errors.append(f"Error loading {file_path}: {e}")

    def _load_carrier_policy_file(self, file_path: Path):
        """Load a carrier policy YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data:
                self._process_carrier_data(data, str(file_path))

        except Exception as e:
            self._load_errors.append(f"Error loading {file_path}: {e}")

    def _process_restriction_data(self, data: Dict, source_file: str):
        """Process band restriction data."""
        region = data.get('region', '')
        restriction_type = data.get('restriction_type', 'regional')

        # Process band restrictions
        for item in data.get('band_restrictions', []):
            band = item.get('band')
            if band is None:
                continue

            restriction = BandRestriction(
                band=band,
                restriction_type=item.get('restriction_type', restriction_type),
                regions=[region] if region else item.get('regions', []),
                reason=item.get('reason', ''),
                source_file=source_file,
            )

            if band not in self.context.band_restrictions:
                self.context.band_restrictions[band] = []
            self.context.band_restrictions[band].append(restriction)

        # Process combo restrictions
        for item in data.get('combo_restrictions', []):
            combo_key = item.get('combo', item.get('combo_key', ''))
            if not combo_key:
                continue

            # Normalize combo key
            combo_key = self._normalize_combo_key(combo_key)

            restriction = ComboRestriction(
                combo_key=combo_key,
                restriction_type=item.get('restriction_type', restriction_type),
                reason=item.get('reason', ''),
                source_file=source_file,
            )

            if combo_key not in self.context.combo_restrictions:
                self.context.combo_restrictions[combo_key] = []
            self.context.combo_restrictions[combo_key].append(restriction)

    def _process_carrier_data(self, data: Dict, source_file: str):
        """Process carrier policy data."""
        carrier_name = data.get('carrier', data.get('name', 'Unknown'))

        requirement = CarrierRequirement(
            carrier_name=carrier_name,
            required_combos=set(self._normalize_combo_list(data.get('required_combos', []))),
            optional_combos=set(self._normalize_combo_list(data.get('optional_combos', []))),
            excluded_combos=set(self._normalize_combo_list(data.get('excluded_combos', []))),
            notes=data.get('combo_notes', {}),
        )

        self.context.carrier_requirements[carrier_name.lower()] = requirement

    def _process_generic_data(self, data: Dict, source_file: str):
        """Process generic knowledge base data."""
        # Try to extract any useful information
        if isinstance(data, dict):
            # Check for band-related keys
            for key, value in data.items():
                if 'band' in key.lower() and isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and 'band' in item:
                            self._process_restriction_data(
                                {'band_restrictions': [item]},
                                source_file
                            )

    def _normalize_combo_key(self, combo_str: str) -> str:
        """Normalize a combo key string."""
        # Remove common prefixes and normalize format
        combo_str = combo_str.strip().upper()
        combo_str = combo_str.replace('B', '').replace('_', '-').replace('+', '-')

        # Sort components for consistent key
        parts = combo_str.split('-')
        lte_parts = []
        nr_parts = []

        for part in parts:
            part = part.strip()
            if part.startswith('N') and part[1:2].isdigit():
                nr_parts.append(part.lower())  # n77A format
            else:
                lte_parts.append(part)  # 66A format

        # Sort each group
        lte_parts.sort(key=lambda x: (int(''.join(c for c in x if c.isdigit()) or '0'), x))
        nr_parts.sort(key=lambda x: (int(''.join(c for c in x if c.isdigit()) or '0'), x))

        return '-'.join(lte_parts + nr_parts)

    def _normalize_combo_list(self, combos: List[str]) -> List[str]:
        """Normalize a list of combo strings."""
        return [self._normalize_combo_key(c) for c in combos if c]

    def get_band_restrictions(self, band: int) -> List[BandRestriction]:
        """Get all restrictions for a specific band."""
        return self.context.band_restrictions.get(band, [])

    def get_combo_restrictions(self, combo_key: str) -> List[ComboRestriction]:
        """Get all restrictions for a specific combo."""
        normalized_key = self._normalize_combo_key(combo_key)
        return self.context.combo_restrictions.get(normalized_key, [])

    def get_carrier_requirement(self, carrier: str) -> Optional[CarrierRequirement]:
        """Get requirements for a specific carrier."""
        return self.context.carrier_requirements.get(carrier.lower())

    def is_band_restricted(self, band: int, region: Optional[str] = None) -> bool:
        """Check if a band is restricted."""
        restrictions = self.get_band_restrictions(band)

        if not restrictions:
            return False

        if region is None:
            return True

        # Check if any restriction applies to the region
        for r in restrictions:
            if not r.regions or region.upper() in [reg.upper() for reg in r.regions]:
                return True

        return False

    def is_combo_excluded_by_carrier(self, combo_key: str, carrier: str) -> bool:
        """Check if a combo is excluded by carrier policy."""
        requirement = self.get_carrier_requirement(carrier)
        if not requirement:
            return False

        normalized_key = self._normalize_combo_key(combo_key)
        return normalized_key in requirement.excluded_combos

    def get_load_errors(self) -> List[str]:
        """Get any errors encountered during loading."""
        return self._load_errors

    def is_loaded(self) -> bool:
        """Check if knowledge base has been loaded."""
        return self._loaded

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of loaded knowledge base."""
        return {
            'loaded': self._loaded,
            'band_restrictions_count': len(self.context.band_restrictions),
            'combo_restrictions_count': len(self.context.combo_restrictions),
            'carrier_policies_count': len(self.context.carrier_requirements),
            'active_region': self.context.active_region,
            'active_carrier': self.context.active_carrier,
            'load_errors': self._load_errors,
        }
