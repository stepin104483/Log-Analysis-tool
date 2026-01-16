# Combos Module - Requirements

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | REQ-COMBOS-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-16 |
| **Author** | DeviceSWAnalyzer Team |
| **Status** | Final |

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for the Combos Analysis Module, which analyzes Carrier Aggregation (CA) and Dual Connectivity (DC) combinations from multiple data sources to identify discrepancies and provide knowledge-based reasoning.

### 1.2 Scope
The module supports analysis of:
- LTE Carrier Aggregation (LTE CA)
- NR Carrier Aggregation (NRCA)
- E-UTRA NR Dual Connectivity (EN-DC/NSA)
- NR Dual Connectivity (NR-DC)

### 1.3 Related Documents

| Document | Location |
|----------|----------|
| Architecture | `docs/modules/combos/Architecture.md` |
| Overall Requirements | `docs/Overall_Requirements.md` |
| Test Plan | `docs/testing/Combos/Test_Plan.md` |

---

## 2. Functional Requirements

### 2.1 RFC Parsing Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-001.1 | Module SHALL parse RFC XML files to extract combo definitions | High |
| FR-COMBOS-001.2 | Module SHALL extract LTE CA combos from `ca_combos_list` section | High |
| FR-COMBOS-001.3 | Module SHALL extract EN-DC combos from `ca_4g_5g_combos` section | High |
| FR-COMBOS-001.4 | Module SHALL extract NRCA combos from `nr_ca_combos_list` section | High |
| FR-COMBOS-001.5 | Module SHALL extract NR-DC combos from `nr_dc_combos_list` section | Medium |
| FR-COMBOS-001.6 | Module SHALL handle missing RFC file gracefully | High |
| FR-COMBOS-001.7 | Module SHALL handle malformed RFC XML without crashing | High |

### 2.2 QXDM Parsing Requirements (0xB826)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-002.1 | Module SHALL parse QXDM 0xB826 log output | High |
| FR-COMBOS-002.2 | Module SHALL support structured table format parsing | High |
| FR-COMBOS-002.3 | Module SHALL support raw combo string parsing | High |
| FR-COMBOS-002.4 | Module SHALL extract BCS (Band Combination Set) values | Medium |
| FR-COMBOS-002.5 | Module SHALL identify combo type (LTE CA, EN-DC, NRCA) | High |
| FR-COMBOS-002.6 | Module SHALL handle empty or missing QXDM file | High |

### 2.3 UE Capability Parsing Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-003.1 | Module SHALL parse ASN.1 XML exports of UE Capability | High |
| FR-COMBOS-003.2 | Module SHALL extract LTE CA from EUTRA-Capability | High |
| FR-COMBOS-003.3 | Module SHALL extract EN-DC from UE-MRDC-Capability | High |
| FR-COMBOS-003.4 | Module SHALL extract NRCA from UE-NR-Capability | High |
| FR-COMBOS-003.5 | Module SHALL support `supportedBandCombination-r10` format | High |
| FR-COMBOS-003.6 | Module SHALL support `supportedBandCombinationList` format | High |
| FR-COMBOS-003.7 | Module SHALL extract supported bands list | Medium |

### 2.4 EFS Control Parsing Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-004.1 | Module SHALL parse `prune_ca_combos` EFS file | High |
| FR-COMBOS-004.2 | Module SHALL parse `ca_disable` binary flag | Medium |
| FR-COMBOS-004.3 | Module SHALL parse `cap_control_nrca_enabled` flag | Medium |
| FR-COMBOS-004.4 | Module SHALL parse `cap_control_nrdc_enabled` flag | Medium |
| FR-COMBOS-004.5 | Module SHALL support BCS-specific pruning | Medium |
| FR-COMBOS-004.6 | Module SHALL handle missing EFS files gracefully | High |

### 2.5 Normalization Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-005.1 | Module SHALL normalize combo keys for comparison | High |
| FR-COMBOS-005.2 | Module SHALL sort band components consistently | High |
| FR-COMBOS-005.3 | Module SHALL uppercase band class letters | High |
| FR-COMBOS-005.4 | Module SHALL distinguish LTE and NR bands in EN-DC | High |
| FR-COMBOS-005.5 | Module SHALL handle BCS value normalization | Medium |

### 2.6 Comparison Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-006.1 | Module SHALL compare RFC combos vs QXDM (RRC Table) | High |
| FR-COMBOS-006.2 | Module SHALL compare QXDM vs UE Capability | High |
| FR-COMBOS-006.3 | Module SHALL identify combos missing in target source | High |
| FR-COMBOS-006.4 | Module SHALL identify extra combos in target source | High |
| FR-COMBOS-006.5 | Module SHALL calculate match percentage | High |
| FR-COMBOS-006.6 | Module SHALL compare by combo type (LTE CA, EN-DC, etc.) | High |

### 2.7 Knowledge Base Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-007.1 | Module SHALL load band restrictions from YAML files | High |
| FR-COMBOS-007.2 | Module SHALL load carrier policies from YAML files | High |
| FR-COMBOS-007.3 | Module SHALL support regional band restrictions | High |
| FR-COMBOS-007.4 | Module SHALL support regulatory band restrictions | High |
| FR-COMBOS-007.5 | Module SHALL support hardware variant restrictions | Medium |
| FR-COMBOS-007.6 | Module SHALL support carrier-specific exclusions | High |
| FR-COMBOS-007.7 | Module SHALL support carrier-required combos | Medium |

### 2.8 Reasoning Engine Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-008.1 | Module SHALL explain discrepancies using knowledge base | High |
| FR-COMBOS-008.2 | Module SHALL detect EFS pruning as explanation | High |
| FR-COMBOS-008.3 | Module SHALL detect band restrictions as explanation | High |
| FR-COMBOS-008.4 | Module SHALL detect carrier exclusions as explanation | High |
| FR-COMBOS-008.5 | Module SHALL apply heuristics for mmWave bands | Medium |
| FR-COMBOS-008.6 | Module SHALL apply heuristics for Band 14 (FirstNet) | Medium |
| FR-COMBOS-008.7 | Module SHALL assign severity levels to discrepancies | High |
| FR-COMBOS-008.8 | Module SHALL categorize discrepancies by severity | High |

### 2.9 Discrepancy Classification Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-009.1 | Module SHALL classify MISSING_IN_RRC discrepancies | High |
| FR-COMBOS-009.2 | Module SHALL classify EXTRA_IN_RRC discrepancies | High |
| FR-COMBOS-009.3 | Module SHALL classify MISSING_IN_UECAP discrepancies | High |
| FR-COMBOS-009.4 | Module SHALL classify EXTRA_IN_UECAP discrepancies | High |
| FR-COMBOS-009.5 | Module SHALL classify PRUNED_BY_EFS discrepancies | High |
| FR-COMBOS-009.6 | Module SHALL classify BCS_MISMATCH discrepancies | Medium |

### 2.10 Output Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COMBOS-010.1 | Module SHALL generate HTML analysis report | High |
| FR-COMBOS-010.2 | Report SHALL include summary dashboard | High |
| FR-COMBOS-010.3 | Report SHALL include combo count statistics | High |
| FR-COMBOS-010.4 | Report SHALL include match percentage bars | High |
| FR-COMBOS-010.5 | Report SHALL include discrepancy tables | High |
| FR-COMBOS-010.6 | Report SHALL include reasoning/explanation column | High |
| FR-COMBOS-010.7 | Report SHALL include severity distribution | High |
| FR-COMBOS-010.8 | Report SHALL support collapsible sections | Medium |
| FR-COMBOS-011.1 | Module SHALL generate Claude AI prompt | High |
| FR-COMBOS-011.2 | Prompt SHALL include all comparison data | High |
| FR-COMBOS-011.3 | Prompt SHALL request expert analysis | High |

---

## 3. Non-Functional Requirements

### 3.1 Performance Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-COMBOS-001 | Analysis SHALL complete within 60 seconds for typical files | High |
| NFR-COMBOS-002 | Module SHALL handle RFC files up to 20MB | Medium |
| NFR-COMBOS-003 | Module SHALL handle QXDM logs up to 10MB | Medium |
| NFR-COMBOS-004 | Module SHALL handle >1000 combos per source | High |

### 3.2 Reliability Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-COMBOS-010 | Module SHALL NOT crash on malformed input | High |
| NFR-COMBOS-011 | Module SHALL handle partial input gracefully | High |
| NFR-COMBOS-012 | Module SHALL report parsing errors clearly | High |
| NFR-COMBOS-013 | Module SHALL continue analysis when one source fails | Medium |

### 3.3 Usability Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-COMBOS-020 | Output SHALL be readable by non-experts | High |
| NFR-COMBOS-021 | Error messages SHALL indicate problematic file | High |
| NFR-COMBOS-022 | Severity levels SHALL use clear terminology | High |
| NFR-COMBOS-023 | HTML report SHALL be viewable standalone | High |

### 3.4 Maintainability Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-COMBOS-030 | Knowledge base SHALL be editable via YAML | High |
| NFR-COMBOS-031 | New band restrictions SHALL be addable without code changes | High |
| NFR-COMBOS-032 | New carrier policies SHALL be addable without code changes | High |

---

## 4. Combo Type Definitions

### 4.1 Supported Combo Types

| Type | Description | Example |
|------|-------------|---------|
| LTE_CA | LTE Carrier Aggregation | 1A-3A-7A |
| NRCA | NR Carrier Aggregation | n77A-n78A |
| ENDC | E-UTRA NR Dual Connectivity (NSA) | 66A-n77A |
| NRDC | NR Dual Connectivity | n77A-n260A |

### 4.2 Discrepancy Types

| Type | Description |
|------|-------------|
| MISSING_IN_RRC | Combo in RFC but not in RRC Table |
| EXTRA_IN_RRC | Combo in RRC Table but not in RFC |
| MISSING_IN_UECAP | Combo in RRC Table but not in UE Capability |
| EXTRA_IN_UECAP | Combo in UE Capability but not in RRC Table |
| PRUNED_BY_EFS | Combo pruned by EFS control file |
| BCS_MISMATCH | BCS values differ between sources |

### 4.3 Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| expected | Known/intentional discrepancy | No action |
| low | Minor issue, likely configuration | Optional review |
| medium | Potential issue, needs investigation | Review recommended |
| high | Significant issue | Investigation required |
| critical | Major issue, may impact functionality | Immediate action |

---

## 5. Data Sources

### 5.1 Three-Source Comparison

```
RFC (XML)           QXDM (0xB826)        UE Capability (ASN.1 XML)
What should         What's actually      What device
be built            built (RRC Table)    advertises
    │                     │                    │
    └─────────────────────┼────────────────────┘
                          │
                    Comparison
                          │
                   Discrepancies
                          │
                   Reasoning
                          │
                     Report
```

### 5.2 Knowledge Base Files

| File Type | Location | Purpose |
|-----------|----------|---------|
| Band Restrictions | `knowledge_library/combos/band_restrictions/*.yaml` | Regional/regulatory restrictions |
| Carrier Policies | `knowledge_library/combos/carrier_policies/*.yaml` | Carrier-specific requirements |

---

## 6. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-13 | DeviceSWAnalyzer Team | Initial placeholder |
| 1.0 | 2026-01-16 | DeviceSWAnalyzer Team | Full requirements for P0/P1/P2 |
