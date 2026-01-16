"""
EFS Parser for Combo Control Files

Parses EFS files that control combo pruning and disabling:
- prune_ca_combos: Text file listing pruned LTE CA combos
- ca_disable: Binary file to disable all CA
- disable_4l_per_band: Disable 4-layer MIMO per band
- cap_control_nrca_enabled: Binary control for NRCA
- cap_control_nrdc_enabled: Binary control for NRDC

EFS File Locations:
- /nv/item_files/modem/lte/rrc/cap/prune_ca_combos
- /nv/item_files/modem/lte/rrc/cap/ca_disable
- /nv/item_files/modem/lte/rrc/cap/disable_4l_per_band
- /nv/item_files/modem/nr5g/rrc/cap_control_nrca_enabled
- /nv/item_files/modem/nr5g/rrc/cap_control_nrdc_enabled
"""

import re
import os
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PrunedCombo:
    """A single pruned combo entry."""
    combo_key: str          # Normalized combo key "1A-3A"
    bcs: Optional[int] = None       # BCS value if specified
    raw_string: str = ""    # Original string from file


@dataclass
class EFSControlState:
    """State of EFS control files."""
    ca_disabled: bool = False
    nrca_enabled: bool = True
    nrdc_enabled: bool = True
    pruned_combos: List[PrunedCombo] = field(default_factory=list)
    disabled_4l_bands: Set[int] = field(default_factory=set)
    source_files: Dict[str, str] = field(default_factory=dict)  # type -> path


class EFSParser:
    """Parse EFS files for combo control settings."""

    def __init__(self):
        self._parse_errors: List[str] = []
        self._state = EFSControlState()

    def parse_directory(self, efs_path: str) -> EFSControlState:
        """
        Parse all EFS control files from a directory.

        Expected structure:
        efs_path/
        ├── lte/rrc/cap/
        │   ├── prune_ca_combos
        │   ├── ca_disable
        │   └── disable_4l_per_band
        └── nr5g/rrc/
            ├── cap_control_nrca_enabled
            └── cap_control_nrdc_enabled

        Args:
            efs_path: Path to EFS root directory

        Returns:
            EFSControlState with parsed data
        """
        self._parse_errors = []
        self._state = EFSControlState()

        efs_root = Path(efs_path)

        # LTE CA control files
        lte_cap_path = efs_root / 'lte' / 'rrc' / 'cap'
        if lte_cap_path.exists():
            self._parse_lte_cap_files(lte_cap_path)
        else:
            # Try alternative paths
            alt_paths = [
                efs_root / 'modem' / 'lte' / 'rrc' / 'cap',
                efs_root / 'nv' / 'item_files' / 'modem' / 'lte' / 'rrc' / 'cap',
                efs_root,  # Files might be directly in root
            ]
            for alt in alt_paths:
                if alt.exists():
                    self._parse_lte_cap_files(alt)
                    break

        # NR control files
        nr_rrc_path = efs_root / 'nr5g' / 'rrc'
        if nr_rrc_path.exists():
            self._parse_nr_control_files(nr_rrc_path)
        else:
            alt_paths = [
                efs_root / 'modem' / 'nr5g' / 'rrc',
                efs_root / 'nv' / 'item_files' / 'modem' / 'nr5g' / 'rrc',
                efs_root,
            ]
            for alt in alt_paths:
                if alt.exists():
                    self._parse_nr_control_files(alt)
                    break

        return self._state

    def parse_files(self, file_paths: Dict[str, str]) -> EFSControlState:
        """
        Parse specific EFS files.

        Args:
            file_paths: Dict mapping file type to path, e.g.,
                       {'prune_ca_combos': '/path/to/file', ...}

        Returns:
            EFSControlState with parsed data
        """
        self._parse_errors = []
        self._state = EFSControlState()

        for file_type, path in file_paths.items():
            if not os.path.exists(path):
                self._parse_errors.append(f"File not found: {path}")
                continue

            self._state.source_files[file_type] = path

            if file_type == 'prune_ca_combos':
                self._parse_prune_ca_combos(path)
            elif file_type == 'ca_disable':
                self._state.ca_disabled = self._parse_binary_flag(path)
            elif file_type == 'disable_4l_per_band':
                self._parse_disable_4l_per_band(path)
            elif file_type == 'cap_control_nrca_enabled':
                self._state.nrca_enabled = self._parse_binary_flag(path)
            elif file_type == 'cap_control_nrdc_enabled':
                self._state.nrdc_enabled = self._parse_binary_flag(path)

        return self._state

    def _parse_lte_cap_files(self, cap_path: Path):
        """Parse LTE capability control files."""
        # prune_ca_combos
        prune_file = cap_path / 'prune_ca_combos'
        if prune_file.exists():
            self._state.source_files['prune_ca_combos'] = str(prune_file)
            self._parse_prune_ca_combos(str(prune_file))

        # ca_disable
        disable_file = cap_path / 'ca_disable'
        if disable_file.exists():
            self._state.source_files['ca_disable'] = str(disable_file)
            self._state.ca_disabled = self._parse_binary_flag(str(disable_file))

        # disable_4l_per_band
        mimo_file = cap_path / 'disable_4l_per_band'
        if mimo_file.exists():
            self._state.source_files['disable_4l_per_band'] = str(mimo_file)
            self._parse_disable_4l_per_band(str(mimo_file))

    def _parse_nr_control_files(self, nr_path: Path):
        """Parse NR capability control files."""
        # cap_control_nrca_enabled
        nrca_file = nr_path / 'cap_control_nrca_enabled'
        if nrca_file.exists():
            self._state.source_files['cap_control_nrca_enabled'] = str(nrca_file)
            self._state.nrca_enabled = self._parse_binary_flag(str(nrca_file))

        # cap_control_nrdc_enabled
        nrdc_file = nr_path / 'cap_control_nrdc_enabled'
        if nrdc_file.exists():
            self._state.source_files['cap_control_nrdc_enabled'] = str(nrdc_file)
            self._state.nrdc_enabled = self._parse_binary_flag(str(nrdc_file))

    def parse_prune_ca_combos(self, file_path: str) -> Set[str]:
        """
        Parse prune_ca_combos text file.

        Format: [Band][Class]-[Band][Class]-[BCS];
        Example: 1A-3A-0;1A-3A-1;7A-20A-0;

        Args:
            file_path: Path to prune_ca_combos file

        Returns:
            Set of pruned combo keys (normalized)
        """
        self._parse_prune_ca_combos(file_path)
        return {p.combo_key for p in self._state.pruned_combos}

    def _parse_prune_ca_combos(self, file_path: str):
        """Internal method to parse prune_ca_combos file."""
        try:
            # Try text mode first
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            # Try binary mode
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
            except Exception as e:
                self._parse_errors.append(f"Error reading prune_ca_combos: {e}")
                return

        # Parse entries separated by semicolons
        # Format: [Band][Class]-[Band][Class]-[BCS];
        # Or: [Band][Class]-[Band][Class];

        # Pattern to match combo entries
        # Examples: 1A-3A-0; 1A-3A; 66A-71A-2;
        pattern = re.compile(
            r'(\d+[A-Z](?:-\d+[A-Z])*(?:-\d+)?)\s*;',
            re.IGNORECASE
        )

        for match in pattern.finditer(content):
            entry = match.group(1).strip()
            pruned = self._parse_prune_entry(entry)
            if pruned:
                self._state.pruned_combos.append(pruned)

        # Also try alternative format: newline-separated
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check if line matches combo pattern
            if re.match(r'^\d+[A-Z]', line, re.IGNORECASE):
                pruned = self._parse_prune_entry(line.rstrip(';'))
                if pruned and pruned.combo_key not in [p.combo_key for p in self._state.pruned_combos]:
                    self._state.pruned_combos.append(pruned)

    def _parse_prune_entry(self, entry: str) -> Optional[PrunedCombo]:
        """Parse a single prune entry."""
        entry = entry.strip().upper()
        if not entry:
            return None

        parts = entry.split('-')
        if not parts:
            return None

        bands = []
        bcs = None

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if this is a BCS value (just a number)
            if part.isdigit():
                bcs = int(part)
            # Check if this is a band entry (e.g., 1A, 66B)
            elif re.match(r'^\d+[A-Z]$', part, re.IGNORECASE):
                bands.append(part)

        if not bands:
            return None

        # Sort bands and create normalized key
        bands.sort(key=lambda x: (int(re.match(r'(\d+)', x).group(1)), x[-1]))
        combo_key = '-'.join(bands)

        return PrunedCombo(
            combo_key=combo_key,
            bcs=bcs,
            raw_string=entry,
        )

    def parse_ca_disable(self, file_path: str) -> bool:
        """
        Parse ca_disable binary file.

        Format: Single byte - 0x00 (enabled) or 0x01 (disabled)

        Args:
            file_path: Path to ca_disable file

        Returns:
            True if CA is disabled
        """
        return self._parse_binary_flag(file_path)

    def _parse_binary_flag(self, file_path: str) -> bool:
        """Parse a binary flag file (0x00 = False/enabled, 0x01 = True/disabled)."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1)

            if data:
                return data[0] != 0x00
            return False

        except Exception as e:
            self._parse_errors.append(f"Error reading binary flag {file_path}: {e}")
            return False

    def _parse_disable_4l_per_band(self, file_path: str):
        """Parse disable_4l_per_band file."""
        try:
            # This could be a text file with band numbers or binary bitmap
            with open(file_path, 'rb') as f:
                data = f.read()

            # Try to interpret as text first
            try:
                text = data.decode('utf-8', errors='ignore')
                for line in text.split('\n'):
                    line = line.strip()
                    if line.isdigit():
                        self._state.disabled_4l_bands.add(int(line))
                    elif re.match(r'^\d+$', line):
                        self._state.disabled_4l_bands.add(int(line))
            except:
                pass

            # If text parsing didn't find bands, try as bitmap
            if not self._state.disabled_4l_bands and len(data) >= 1:
                # Interpret as bitmap where each bit represents a band
                for byte_idx, byte in enumerate(data):
                    for bit_idx in range(8):
                        if byte & (1 << bit_idx):
                            band = byte_idx * 8 + bit_idx + 1
                            if 1 <= band <= 256:  # Valid LTE band range
                                self._state.disabled_4l_bands.add(band)

        except Exception as e:
            self._parse_errors.append(f"Error reading disable_4l_per_band: {e}")

    def parse_cap_control(self, file_path: str, control_type: str) -> bool:
        """
        Parse cap_control_* binary files for NRCA/NRDC.

        Format: Binary 0x00 (disabled) / 0x01 (enabled)

        Args:
            file_path: Path to cap_control file
            control_type: 'nrca' or 'nrdc'

        Returns:
            True if capability is enabled
        """
        return self._parse_binary_flag(file_path)

    def get_pruned_combo_keys(self) -> Set[str]:
        """Get all pruned combo keys."""
        return {p.combo_key for p in self._state.pruned_combos}

    def is_combo_pruned(self, combo_key: str, bcs: Optional[int] = None) -> bool:
        """
        Check if a combo is pruned.

        Args:
            combo_key: Normalized combo key
            bcs: Optional BCS value to check

        Returns:
            True if combo is pruned
        """
        # Normalize the input key
        normalized = self._normalize_combo_key(combo_key)

        for pruned in self._state.pruned_combos:
            if pruned.combo_key == normalized:
                # If BCS specified, check it matches
                if bcs is not None and pruned.bcs is not None:
                    if pruned.bcs == bcs:
                        return True
                else:
                    return True

        return False

    def _normalize_combo_key(self, combo_key: str) -> str:
        """Normalize a combo key for comparison."""
        # Remove common variations
        key = combo_key.upper().replace(' ', '').replace('_', '-')

        # Extract bands and sort
        parts = key.split('-')
        bands = [p for p in parts if re.match(r'^\d+[A-Z]$', p)]
        bands.sort(key=lambda x: (int(re.match(r'(\d+)', x).group(1)), x[-1]))

        return '-'.join(bands)

    def get_parse_errors(self) -> List[str]:
        """Get list of parse errors encountered."""
        return self._parse_errors

    def get_state(self) -> EFSControlState:
        """Get the current EFS control state."""
        return self._state

    def get_summary(self) -> Dict:
        """Get summary of EFS control state."""
        return {
            'ca_disabled': self._state.ca_disabled,
            'nrca_enabled': self._state.nrca_enabled,
            'nrdc_enabled': self._state.nrdc_enabled,
            'pruned_combos_count': len(self._state.pruned_combos),
            'disabled_4l_bands': sorted(self._state.disabled_4l_bands),
            'source_files': self._state.source_files,
            'parse_errors': self._parse_errors,
        }


def parse_efs_combos(efs_path: str) -> EFSControlState:
    """
    Convenience function to parse EFS control files.

    Args:
        efs_path: Path to EFS directory or file

    Returns:
        EFSControlState with parsed data
    """
    parser = EFSParser()

    if os.path.isdir(efs_path):
        return parser.parse_directory(efs_path)
    elif os.path.isfile(efs_path):
        # Assume it's prune_ca_combos if single file
        return parser.parse_files({'prune_ca_combos': efs_path})

    return EFSControlState()
