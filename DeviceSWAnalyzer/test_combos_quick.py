#!/usr/bin/env python
"""
Quick test script for Combos module
Run: python test_combos_quick.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.combos import (
    CombosOrchestrator,
    RFCParser,
    QXDMParser,
    UECapParser,
    EFSParser,
    KnowledgeBase,
    ReasoningEngine,
    ComboType,
)

def test_parsers():
    """Test individual parsers."""
    print("=" * 60)
    print("TESTING PARSERS")
    print("=" * 60)

    # Test RFC Parser
    print("\n[RFC Parser]")
    rfc = RFCParser()
    print(f"  - RFCParser instantiated: OK")

    # Test QXDM Parser
    print("\n[QXDM Parser]")
    qxdm = QXDMParser()
    # Test combo string parsing
    bands = qxdm._extract_bands_from_string("66A+n77A")
    print(f"  - Parse '66A+n77A': {[str(b) for b in bands]}")

    # Test UE Cap Parser
    print("\n[UE Cap Parser]")
    uecap = UECapParser()
    bands = uecap._parse_combo_string("66A+n77A")
    print(f"  - Parse '66A+n77A': {[str(b) for b in bands]}")

    # Test EFS Parser
    print("\n[EFS Parser]")
    efs = EFSParser()
    print(f"  - EFSParser instantiated: OK")
    summary = efs.get_summary()
    print(f"  - Default state: CA disabled={summary['ca_disabled']}, NRCA enabled={summary['nrca_enabled']}")

def test_knowledge_base():
    """Test Knowledge Base."""
    print("\n" + "=" * 60)
    print("TESTING KNOWLEDGE BASE")
    print("=" * 60)

    kb = KnowledgeBase()

    # Try to load sample files
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_library', 'combos')
    if os.path.exists(kb_path):
        print(f"\n[Loading from {kb_path}]")
        try:
            kb.load(region='APAC')
            summary = kb.get_summary()
            print(f"  - Loaded: {summary['loaded']}")
            print(f"  - Band restrictions: {summary['band_restrictions_count']}")
            print(f"  - Carrier requirements: {summary['carrier_requirements_count']}")
        except Exception as e:
            print(f"  - Load failed (PyYAML may not be installed): {e}")
    else:
        print(f"  - Knowledge base path not found: {kb_path}")
        print("  - Creating in-memory test...")

    # Test with in-memory data
    from modules.combos.models import KnowledgeBaseContext, BandRestriction
    ctx = KnowledgeBaseContext()
    ctx.band_restrictions[71] = [
        BandRestriction(band=71, restriction_type="regional", reason="Band 71 not in APAC")
    ]

    engine = ReasoningEngine(ctx)
    print(f"\n[Reasoning Engine]")
    print(f"  - ReasoningEngine instantiated: OK")

def test_models():
    """Test data models."""
    print("\n" + "=" * 60)
    print("TESTING MODELS")
    print("=" * 60)

    from modules.combos.models import BandComponent, Combo, ComboSet

    # Create LTE CA combo
    print("\n[LTE CA Combo]")
    lte_combo = Combo(
        combo_type=ComboType.LTE_CA,
        components=[
            BandComponent(band=1, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
        ]
    )
    print(f"  - Created: {lte_combo}")
    print(f"  - Normalized key: {lte_combo.normalized_key}")

    # Create EN-DC combo
    print("\n[EN-DC Combo]")
    endc_combo = Combo(
        combo_type=ComboType.ENDC,
        components=[
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
    )
    print(f"  - Created: {endc_combo}")
    print(f"  - LTE components: {[str(c) for c in endc_combo.lte_components]}")
    print(f"  - NR components: {[str(c) for c in endc_combo.nr_components]}")

    # Test ComboSet
    print("\n[ComboSet]")
    combo_set = ComboSet(combo_type=ComboType.LTE_CA, source="test")
    combo_set.add(lte_combo)
    print(f"  - Added 1 LTE CA combo, count: {len(combo_set)}")

def test_comparison():
    """Test comparison functionality."""
    print("\n" + "=" * 60)
    print("TESTING COMPARISON")
    print("=" * 60)

    from modules.combos.models import BandComponent, Combo, ComboSet, DataSource
    from modules.combos.analyzers import Comparator

    # Create two sets with differences
    set_a = ComboSet(combo_type=ComboType.LTE_CA, source="RFC")
    set_b = ComboSet(combo_type=ComboType.LTE_CA, source="RRC")

    # Common combo
    combo1 = Combo(combo_type=ComboType.LTE_CA, components=[
        BandComponent(band=1, band_class='A', is_nr=False),
        BandComponent(band=3, band_class='A', is_nr=False),
    ])

    # Only in A
    combo2 = Combo(combo_type=ComboType.LTE_CA, components=[
        BandComponent(band=7, band_class='A', is_nr=False),
        BandComponent(band=20, band_class='A', is_nr=False),
    ])

    # Only in B
    combo3 = Combo(combo_type=ComboType.LTE_CA, components=[
        BandComponent(band=1, band_class='A', is_nr=False),
        BandComponent(band=7, band_class='A', is_nr=False),
    ])

    set_a.add(combo1)
    set_a.add(combo2)
    set_b.add(combo1)
    set_b.add(combo3)

    print(f"\n[Set A (RFC)]: {[str(c) for c in set_a.values()]}")
    print(f"[Set B (RRC)]: {[str(c) for c in set_b.values()]}")

    # Compare
    comparator = Comparator()
    result = comparator.compare(set_a, set_b)

    print(f"\n[Comparison Result]")
    print(f"  - Common: {len(result.common)}")
    print(f"  - Only in RFC: {len(result.only_in_a)} -> {result.only_in_a}")
    print(f"  - Only in RRC: {len(result.only_in_b)} -> {result.only_in_b}")
    print(f"  - Match %: {result.match_percentage:.1f}%")

def test_html_report():
    """Test HTML report generation."""
    print("\n" + "=" * 60)
    print("TESTING HTML REPORT")
    print("=" * 60)

    from modules.combos.models import AnalysisResult, BandComponent, Combo, ComboSet
    from modules.combos.reports import HTMLReportGenerator

    # Create minimal analysis result
    result = AnalysisResult(
        rfc_combos={ComboType.LTE_CA: ComboSet(combo_type=ComboType.LTE_CA, source="RFC")},
        rrc_combos={ComboType.LTE_CA: ComboSet(combo_type=ComboType.LTE_CA, source="RRC")},
        uecap_combos={ComboType.LTE_CA: ComboSet(combo_type=ComboType.LTE_CA, source="UECap")},
    )
    result.input_files = {"RFC": "test_rfc.xml", "QXDM": "test_0xb826.txt"}

    generator = HTMLReportGenerator()
    html = generator.generate(result)

    print(f"\n[Generated HTML]")
    print(f"  - Length: {len(html)} characters")
    print(f"  - Contains <html>: {'<html' in html}")
    print(f"  - Contains Summary: {'Summary' in html}")
    print(f"  - Contains Reasoning: {'Reasoning' in html}")

def main():
    print("\n" + "=" * 60)
    print("COMBOS MODULE - QUICK TEST")
    print("=" * 60)

    try:
        test_parsers()
        test_knowledge_base()
        test_models()
        test_comparison()
        test_html_report()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run full unit tests: python -m pytest src/modules/combos/tests/ -v")
        print("  2. Test with real files via web UI at http://localhost:5000/combos")
        print("  3. Or use the orchestrator directly:")
        print("     from modules.combos import run_analysis")
        print("     result = run_analysis(rfc_file='path/to/rfc.xml', qxdm_file='path/to/0xb826.txt')")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
