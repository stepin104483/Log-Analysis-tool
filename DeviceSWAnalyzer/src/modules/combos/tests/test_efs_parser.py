"""
Unit tests for EFS Parser
"""

import pytest
import tempfile
import os

from ..parsers import EFSParser


class TestEFSParser:
    """Tests for EFSParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EFSParser()

    def _create_temp_file(self, content: str, filename: str) -> str:
        """Create a temporary file with given content."""
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
        return temp_dir, path

    def test_parse_prune_ca_combos_basic(self):
        """Test parsing basic prune_ca_combos file."""
        content = """# Pruned combos
66A-2A
66A-n77A
1A-3A-7A
"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            pruned = self.parser.parse_prune_ca_combos(path)

            assert "66A-2A" in pruned or "2A-66A" in pruned
            assert len(pruned) >= 3
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

    def test_parse_prune_ca_combos_with_bcs(self):
        """Test parsing prune_ca_combos with BCS values."""
        # EFS format uses hyphen-separated entries, BCS is the last number
        content = """# Pruned combos with BCS
66A-2A-0;
66A-71A-1;
1A-3A-2;
"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            pruned = self.parser.parse_prune_ca_combos(path)

            # Should parse combos even with BCS values
            assert len(pruned) >= 3
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

    def test_parse_prune_ca_combos_comments(self):
        """Test that comments are ignored."""
        content = """# This is a comment
66A-2A
# Another comment
66A-n77A
"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            pruned = self.parser.parse_prune_ca_combos(path)

            # Should only have 2 combos, not comments
            assert len(pruned) == 2
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

    def test_parse_prune_ca_combos_empty_lines(self):
        """Test that empty lines are ignored."""
        content = """66A-2A

66A-n77A

"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            pruned = self.parser.parse_prune_ca_combos(path)

            assert len(pruned) == 2
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

    def test_parse_directory(self):
        """Test parsing entire EFS directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create prune_ca_combos file
            prune_path = os.path.join(temp_dir, "prune_ca_combos")
            with open(prune_path, 'w') as f:
                f.write("66A-2A\n66A-n77A\n")

            state = self.parser.parse_directory(temp_dir)

            assert len(state.pruned_combos) >= 2
        finally:
            os.unlink(prune_path)
            os.rmdir(temp_dir)

    def test_is_combo_pruned(self):
        """Test checking if combo is pruned."""
        content = """66A-2A
66A-N77A
"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            self.parser.parse_prune_ca_combos(path)

            # Should find pruned combo (case insensitive)
            assert self.parser.is_combo_pruned("66A-2A")
            assert self.parser.is_combo_pruned("66a-2a")

            # Should not find non-pruned combo
            assert not self.parser.is_combo_pruned("1A-3A")
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns empty set."""
        pruned = self.parser.parse_prune_ca_combos("/nonexistent/file")

        assert len(pruned) == 0

    def test_parse_nonexistent_directory(self):
        """Test parsing non-existent directory."""
        state = self.parser.parse_directory("/nonexistent/dir")

        assert len(state.pruned_combos) == 0
        assert not state.ca_disabled

    def test_get_summary(self):
        """Test getting parser summary."""
        content = """66A-2A
66A-n77A
1A-3A
"""
        temp_dir, path = self._create_temp_file(content, "prune_ca_combos")
        try:
            self.parser.parse_prune_ca_combos(path)
            summary = self.parser.get_summary()

            assert summary['pruned_combos_count'] >= 3
        finally:
            os.unlink(path)
            os.rmdir(temp_dir)

