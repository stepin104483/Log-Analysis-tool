# Combos Module Requirements Traceability Matrix

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TM-COMBOS-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-16 |
| **Related Documents** | TP-COMBOS-001, TC-COMBOS, REQ-COMBOS-001 |

---

## 1. RFC Parsing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-001.1 | Parse RFC XML to extract combos | TC-COMBOS-001 | Full |
| FR-COMBOS-001.2 | Extract LTE CA combos from ca_combos_list | TC-COMBOS-002 | Full |
| FR-COMBOS-001.3 | Extract EN-DC combos from ca_4g_5g_combos | TC-COMBOS-003 | Full |
| FR-COMBOS-001.4 | Extract NRCA combos from nr_ca_combos_list | TC-COMBOS-004 | Full |
| FR-COMBOS-001.5 | Extract NR-DC combos from nr_dc_combos_list | TC-COMBOS-005 | Full |
| FR-COMBOS-001.6 | Handle missing RFC file gracefully | TC-COMBOS-006 | Full |
| FR-COMBOS-001.7 | Handle malformed RFC XML without crashing | TC-COMBOS-007 | Full |

---

## 2. QXDM Parsing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-002.1 | Parse QXDM 0xB826 log output | TC-COMBOS-010 | Full |
| FR-COMBOS-002.2 | Support structured table format parsing | TC-COMBOS-011 | Full |
| FR-COMBOS-002.3 | Support raw combo string parsing | TC-COMBOS-012 | Full |
| FR-COMBOS-002.4 | Extract BCS values | TC-COMBOS-013 | Full |
| FR-COMBOS-002.5 | Identify combo type | TC-COMBOS-014 | Full |
| FR-COMBOS-002.6 | Handle empty or missing QXDM file | TC-COMBOS-015 | Full |

---

## 3. UE Capability Parsing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-003.1 | Parse ASN.1 XML exports | TC-COMBOS-020 | Full |
| FR-COMBOS-003.2 | Extract LTE CA from EUTRA-Capability | TC-COMBOS-021 | Full |
| FR-COMBOS-003.3 | Extract EN-DC from UE-MRDC-Capability | TC-COMBOS-022 | Full |
| FR-COMBOS-003.4 | Extract NRCA from UE-NR-Capability | TC-COMBOS-023 | Full |
| FR-COMBOS-003.5 | Support supportedBandCombination-r10 format | TC-COMBOS-024 | Full |
| FR-COMBOS-003.6 | Support supportedBandCombinationList format | TC-COMBOS-025 | Full |
| FR-COMBOS-003.7 | Extract supported bands list | TC-COMBOS-026 | Full |

---

## 4. EFS Parsing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-004.1 | Parse prune_ca_combos EFS file | TC-COMBOS-030 | Full |
| FR-COMBOS-004.2 | Parse ca_disable binary flag | TC-COMBOS-031 | Full |
| FR-COMBOS-004.3 | Parse cap_control_nrca_enabled flag | TC-COMBOS-032 | Full |
| FR-COMBOS-004.4 | Parse cap_control_nrdc_enabled flag | TC-COMBOS-033 | Full |
| FR-COMBOS-004.5 | Support BCS-specific pruning | TC-COMBOS-034 | Full |
| FR-COMBOS-004.6 | Handle missing EFS files gracefully | TC-COMBOS-035 | Full |

---

## 5. Normalization Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-005.1 | Normalize combo keys for comparison | TC-COMBOS-040 | Full |
| FR-COMBOS-005.2 | Sort band components consistently | TC-COMBOS-041 | Full |
| FR-COMBOS-005.3 | Uppercase band class letters | TC-COMBOS-042 | Full |
| FR-COMBOS-005.4 | Distinguish LTE and NR bands in EN-DC | TC-COMBOS-043 | Full |
| FR-COMBOS-005.5 | Handle BCS value normalization | TC-COMBOS-044 | Full |

---

## 6. Comparison Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-006.1 | Compare RFC combos vs QXDM | TC-COMBOS-050 | Full |
| FR-COMBOS-006.2 | Compare QXDM vs UE Capability | TC-COMBOS-051 | Full |
| FR-COMBOS-006.3 | Identify combos missing in target source | TC-COMBOS-052 | Full |
| FR-COMBOS-006.4 | Identify extra combos in target source | TC-COMBOS-053 | Full |
| FR-COMBOS-006.5 | Calculate match percentage | TC-COMBOS-054 | Full |
| FR-COMBOS-006.6 | Compare by combo type | TC-COMBOS-055 | Full |

---

## 7. Knowledge Base Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-007.1 | Load band restrictions from YAML | TC-COMBOS-060 | Full |
| FR-COMBOS-007.2 | Load carrier policies from YAML | TC-COMBOS-061 | Full |
| FR-COMBOS-007.3 | Support regional band restrictions | TC-COMBOS-062 | Full |
| FR-COMBOS-007.4 | Support regulatory band restrictions | TC-COMBOS-063 | Full |
| FR-COMBOS-007.5 | Support hardware variant restrictions | TC-COMBOS-064 | Full |
| FR-COMBOS-007.6 | Support carrier-specific exclusions | TC-COMBOS-065 | Full |
| FR-COMBOS-007.7 | Support carrier-required combos | TC-COMBOS-066 | Full |

---

## 8. Reasoning Engine Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-008.1 | Explain discrepancies using knowledge base | TC-COMBOS-070 | Full |
| FR-COMBOS-008.2 | Detect EFS pruning as explanation | TC-COMBOS-071 | Full |
| FR-COMBOS-008.3 | Detect band restrictions as explanation | TC-COMBOS-072 | Full |
| FR-COMBOS-008.4 | Detect carrier exclusions as explanation | TC-COMBOS-073 | Full |
| FR-COMBOS-008.5 | Apply heuristics for mmWave bands | TC-COMBOS-074 | Full |
| FR-COMBOS-008.6 | Apply heuristics for Band 14 (FirstNet) | TC-COMBOS-075 | Full |
| FR-COMBOS-008.7 | Assign severity levels to discrepancies | TC-COMBOS-076 | Full |
| FR-COMBOS-008.8 | Categorize discrepancies by severity | TC-COMBOS-077 | Full |

---

## 9. Discrepancy Classification Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-009.1 | Classify MISSING_IN_RRC discrepancies | TC-COMBOS-052 | Full |
| FR-COMBOS-009.2 | Classify EXTRA_IN_RRC discrepancies | TC-COMBOS-053 | Full |
| FR-COMBOS-009.3 | Classify MISSING_IN_UECAP discrepancies | TC-COMBOS-051 | Full |
| FR-COMBOS-009.4 | Classify EXTRA_IN_UECAP discrepancies | TC-COMBOS-053 | Full |
| FR-COMBOS-009.5 | Classify PRUNED_BY_EFS discrepancies | TC-COMBOS-071 | Full |
| FR-COMBOS-009.6 | Classify BCS_MISMATCH discrepancies | TC-COMBOS-013 | Full |

---

## 10. Output Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-COMBOS-010.1 | Generate HTML analysis report | TC-COMBOS-080 | Full |
| FR-COMBOS-010.2 | Report includes summary dashboard | TC-COMBOS-081 | Full |
| FR-COMBOS-010.3 | Report includes combo count statistics | TC-COMBOS-082 | Full |
| FR-COMBOS-010.4 | Report includes match percentage bars | TC-COMBOS-083 | Full |
| FR-COMBOS-010.5 | Report includes discrepancy tables | TC-COMBOS-084 | Full |
| FR-COMBOS-010.6 | Report includes reasoning column | TC-COMBOS-085 | Full |
| FR-COMBOS-010.7 | Report includes severity distribution | TC-COMBOS-086 | Full |
| FR-COMBOS-010.8 | Report supports collapsible sections | TC-COMBOS-087 | Full |
| FR-COMBOS-011.1 | Generate Claude AI prompt | TC-COMBOS-090 | Full |
| FR-COMBOS-011.2 | Prompt includes all comparison data | TC-COMBOS-091 | Full |
| FR-COMBOS-011.3 | Prompt requests expert analysis | TC-COMBOS-092 | Full |

---

## 11. Non-Functional Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| NFR-COMBOS-001 | Analysis completes within 60 seconds | TC-COMBOS-100 | Full |
| NFR-COMBOS-002 | Handle RFC files up to 20MB | TC-COMBOS-101 | Full |
| NFR-COMBOS-003 | Handle QXDM logs up to 10MB | TC-COMBOS-102 | Full |
| NFR-COMBOS-004 | Handle >1000 combos per source | TC-COMBOS-103 | Full |
| NFR-COMBOS-010 | No crash on malformed input | TC-COMBOS-110 | Full |
| NFR-COMBOS-011 | Handle partial input gracefully | TC-COMBOS-111 | Full |
| NFR-COMBOS-012 | Report parsing errors clearly | TC-COMBOS-112 | Full |
| NFR-COMBOS-013 | Continue analysis when one source fails | TC-COMBOS-111 | Full |
| NFR-COMBOS-020 | Output readable by non-experts | TC-COMBOS-115 | Full |
| NFR-COMBOS-021 | Error messages indicate problematic file | TC-COMBOS-116 | Full |
| NFR-COMBOS-022 | Severity levels use clear terminology | TC-COMBOS-076 | Full |
| NFR-COMBOS-023 | HTML report viewable standalone | TC-COMBOS-117 | Full |
| NFR-COMBOS-030 | Knowledge base editable via YAML | TC-COMBOS-060 | Full |
| NFR-COMBOS-031 | New band restrictions addable without code | TC-COMBOS-062 | Full |
| NFR-COMBOS-032 | New carrier policies addable without code | TC-COMBOS-061 | Full |

---

## 12. Test Case to Requirements Mapping

| Test Case ID | Test Case Name | Requirements Covered |
|--------------|----------------|---------------------|
| TC-COMBOS-001 | Parse Valid RFC XML | FR-COMBOS-001.1 |
| TC-COMBOS-002 | Extract LTE CA Combos | FR-COMBOS-001.2 |
| TC-COMBOS-003 | Extract EN-DC Combos | FR-COMBOS-001.3 |
| TC-COMBOS-004 | Extract NRCA Combos | FR-COMBOS-001.4 |
| TC-COMBOS-005 | Extract NR-DC Combos | FR-COMBOS-001.5 |
| TC-COMBOS-006 | Handle Missing RFC | FR-COMBOS-001.6 |
| TC-COMBOS-007 | Handle Malformed RFC | FR-COMBOS-001.7, NFR-COMBOS-010 |
| TC-COMBOS-010 | Parse QXDM 0xB826 | FR-COMBOS-002.1 |
| TC-COMBOS-011 | Parse Structured Format | FR-COMBOS-002.2 |
| TC-COMBOS-012 | Parse Raw Combo Strings | FR-COMBOS-002.3 |
| TC-COMBOS-013 | Extract BCS Values | FR-COMBOS-002.4 |
| TC-COMBOS-014 | Identify Combo Type | FR-COMBOS-002.5 |
| TC-COMBOS-015 | Handle Empty QXDM | FR-COMBOS-002.6 |
| TC-COMBOS-020 | Parse ASN.1 XML | FR-COMBOS-003.1 |
| TC-COMBOS-021 | Extract LTE CA from EUTRA | FR-COMBOS-003.2 |
| TC-COMBOS-022 | Extract EN-DC from MRDC | FR-COMBOS-003.3 |
| TC-COMBOS-023 | Extract NRCA from NR-Cap | FR-COMBOS-003.4 |
| TC-COMBOS-024 | Parse r10 Format | FR-COMBOS-003.5 |
| TC-COMBOS-025 | Parse BandCombinationList | FR-COMBOS-003.6 |
| TC-COMBOS-026 | Extract Supported Bands | FR-COMBOS-003.7 |
| TC-COMBOS-030 | Parse prune_ca_combos | FR-COMBOS-004.1 |
| TC-COMBOS-031 | Parse ca_disable | FR-COMBOS-004.2 |
| TC-COMBOS-032 | Parse NRCA Enable | FR-COMBOS-004.3 |
| TC-COMBOS-033 | Parse NRDC Enable | FR-COMBOS-004.4 |
| TC-COMBOS-034 | Parse BCS-Specific Prune | FR-COMBOS-004.5 |
| TC-COMBOS-035 | Handle Missing EFS | FR-COMBOS-004.6 |
| TC-COMBOS-040 | Normalize Combo Keys | FR-COMBOS-005.1 |
| TC-COMBOS-041 | Sort Band Components | FR-COMBOS-005.2 |
| TC-COMBOS-042 | Uppercase Band Class | FR-COMBOS-005.3 |
| TC-COMBOS-043 | Distinguish LTE/NR | FR-COMBOS-005.4 |
| TC-COMBOS-044 | Normalize BCS | FR-COMBOS-005.5 |
| TC-COMBOS-050 | Compare RFC vs QXDM | FR-COMBOS-006.1 |
| TC-COMBOS-051 | Compare QXDM vs UE Cap | FR-COMBOS-006.2 |
| TC-COMBOS-052 | Identify Missing Combos | FR-COMBOS-006.3, FR-COMBOS-009.1 |
| TC-COMBOS-053 | Identify Extra Combos | FR-COMBOS-006.4, FR-COMBOS-009.2, FR-COMBOS-009.4 |
| TC-COMBOS-054 | Calculate Match Percentage | FR-COMBOS-006.5 |
| TC-COMBOS-055 | Compare by Combo Type | FR-COMBOS-006.6 |
| TC-COMBOS-060 | Load Band Restrictions | FR-COMBOS-007.1, NFR-COMBOS-030 |
| TC-COMBOS-061 | Load Carrier Policies | FR-COMBOS-007.2, NFR-COMBOS-032 |
| TC-COMBOS-062 | Regional Restrictions | FR-COMBOS-007.3, NFR-COMBOS-031 |
| TC-COMBOS-063 | Regulatory Restrictions | FR-COMBOS-007.4 |
| TC-COMBOS-064 | HW Variant Restrictions | FR-COMBOS-007.5 |
| TC-COMBOS-065 | Carrier Exclusions | FR-COMBOS-007.6 |
| TC-COMBOS-066 | Carrier Required Combos | FR-COMBOS-007.7 |
| TC-COMBOS-070 | Explain with KB | FR-COMBOS-008.1 |
| TC-COMBOS-071 | Detect EFS Pruning | FR-COMBOS-008.2, FR-COMBOS-009.5 |
| TC-COMBOS-072 | Detect Band Restrictions | FR-COMBOS-008.3 |
| TC-COMBOS-073 | Detect Carrier Exclusions | FR-COMBOS-008.4 |
| TC-COMBOS-074 | mmWave Heuristics | FR-COMBOS-008.5 |
| TC-COMBOS-075 | Band 14 Heuristics | FR-COMBOS-008.6 |
| TC-COMBOS-076 | Assign Severity | FR-COMBOS-008.7, NFR-COMBOS-022 |
| TC-COMBOS-077 | Categorize by Severity | FR-COMBOS-008.8 |
| TC-COMBOS-080 | Generate HTML Report | FR-COMBOS-010.1 |
| TC-COMBOS-081 | Summary Dashboard | FR-COMBOS-010.2 |
| TC-COMBOS-082 | Combo Statistics | FR-COMBOS-010.3 |
| TC-COMBOS-083 | Match Percentage Bars | FR-COMBOS-010.4 |
| TC-COMBOS-084 | Discrepancy Tables | FR-COMBOS-010.5 |
| TC-COMBOS-085 | Reasoning Column | FR-COMBOS-010.6 |
| TC-COMBOS-086 | Severity Distribution | FR-COMBOS-010.7 |
| TC-COMBOS-087 | Collapsible Sections | FR-COMBOS-010.8 |
| TC-COMBOS-090 | Generate Claude Prompt | FR-COMBOS-011.1 |
| TC-COMBOS-091 | Prompt Includes Data | FR-COMBOS-011.2 |
| TC-COMBOS-092 | Prompt Requests Analysis | FR-COMBOS-011.3 |
| TC-COMBOS-100 | Performance 60s | NFR-COMBOS-001 |
| TC-COMBOS-101 | Handle 20MB RFC | NFR-COMBOS-002 |
| TC-COMBOS-102 | Handle 10MB QXDM | NFR-COMBOS-003 |
| TC-COMBOS-103 | Handle 1000+ Combos | NFR-COMBOS-004 |
| TC-COMBOS-110 | No Crash Malformed | NFR-COMBOS-010 |
| TC-COMBOS-111 | Handle Partial Input | NFR-COMBOS-011, NFR-COMBOS-013 |
| TC-COMBOS-112 | Report Errors Clearly | NFR-COMBOS-012 |
| TC-COMBOS-115 | Output Readable | NFR-COMBOS-020 |
| TC-COMBOS-116 | Error Indicates File | NFR-COMBOS-021 |
| TC-COMBOS-117 | Report Standalone | NFR-COMBOS-023 |
| TC-COMBOS-120 | E2E Three-Source | FR-COMBOS-006.1, FR-COMBOS-006.2 |
| TC-COMBOS-121 | E2E with KB | FR-COMBOS-008.1 |
| TC-COMBOS-122 | E2E with EFS | FR-COMBOS-004.1, FR-COMBOS-008.2 |
| TC-COMBOS-130 | Web UI Full Workflow | All |
| TC-COMBOS-131 | E2E LTE CA Analysis | COMBOS-F12 |
| TC-COMBOS-132 | E2E EN-DC Analysis | COMBOS-F13 |

---

## 13. Coverage Summary

### 13.1 Requirements Coverage Statistics

| Category | Total Requirements | Covered | Coverage % |
|----------|-------------------|---------|------------|
| RFC Parsing (FR-COMBOS-001) | 7 | 7 | 100% |
| QXDM Parsing (FR-COMBOS-002) | 6 | 6 | 100% |
| UE Cap Parsing (FR-COMBOS-003) | 7 | 7 | 100% |
| EFS Parsing (FR-COMBOS-004) | 6 | 6 | 100% |
| Normalization (FR-COMBOS-005) | 5 | 5 | 100% |
| Comparison (FR-COMBOS-006) | 6 | 6 | 100% |
| Knowledge Base (FR-COMBOS-007) | 7 | 7 | 100% |
| Reasoning Engine (FR-COMBOS-008) | 8 | 8 | 100% |
| Discrepancy Classification (FR-COMBOS-009) | 6 | 6 | 100% |
| Output (FR-COMBOS-010/011) | 11 | 11 | 100% |
| Non-Functional (NFR-COMBOS) | 15 | 15 | 100% |
| **Total** | **84** | **84** | **100%** |

### 13.2 Test Case Distribution

| Category | Test Cases | % of Total |
|----------|------------|------------|
| RFC Parsing | 9 | 8% |
| QXDM Parsing | 7 | 6% |
| UE Cap Parsing | 8 | 7% |
| EFS Parsing | 6 | 5% |
| Normalization | 5 | 4% |
| Comparison | 6 | 5% |
| Knowledge Base | 7 | 6% |
| Reasoning Engine | 8 | 7% |
| HTML Report | 8 | 7% |
| Claude Prompt | 3 | 3% |
| Performance | 4 | 3% |
| Reliability | 3 | 3% |
| Usability | 3 | 3% |
| Integration | 3 | 3% |
| E2E | 3 | 3% |
| Unit Tests (existing) | 36 | 30% |
| **Total** | **119** | **100%** |

### 13.3 Priority Distribution

| Priority | Count | % |
|----------|-------|---|
| High | 85 | 71% |
| Medium | 28 | 24% |
| Low | 6 | 5% |
| **Total** | **119** | **100%** |

---

## 14. Existing Unit Test Coverage

| Test File | Test Cases Covered | Count |
|-----------|-------------------|-------|
| test_models.py | TC-COMBOS-040 to TC-COMBOS-044 | 14 |
| test_normalizer.py | TC-COMBOS-040 to TC-COMBOS-044 | 17 |
| test_comparator.py | TC-COMBOS-050 to TC-COMBOS-055 | 10 |
| test_parsers.py (RFC) | TC-COMBOS-001 to TC-COMBOS-007 | 8 |
| test_parsers.py (QXDM) | TC-COMBOS-010 to TC-COMBOS-016 | 9 |
| test_uecap_parser.py | TC-COMBOS-020 to TC-COMBOS-027 | 7 |
| test_efs_parser.py | TC-COMBOS-030 to TC-COMBOS-035 | 9 |
| test_knowledge_base.py | TC-COMBOS-060 to TC-COMBOS-077 | 12 |
| **Total** | | **87** |

---

## 15. E2E Test Coverage

| E2E Test File | Test Cases Covered |
|---------------|-------------------|
| test_combos_module.py | TC-COMBOS-130, TC-COMBOS-131, TC-COMBOS-132 |

---

## 16. Gaps and Notes

### 16.1 Requirements Fully Covered

All 84 requirements from the Combos Module Requirements document have corresponding test cases.

### 16.2 Areas Requiring Additional Test Data

| Area | Test Data Needed |
|------|-----------------|
| UE Cap Parsing | Real ASN.1 XML exports from QCAT |
| Large Files | 20MB RFC, 10MB QXDM for boundary testing |
| Multi-combo types | Files with mixed LTE CA, EN-DC, NRCA |
| EFS Files | Real prune_ca_combos from device |

### 16.3 PyYAML Dependency

The Knowledge Base tests (TC-COMBOS-060 to TC-COMBOS-066) require PyYAML to be installed. Tests are skipped if PyYAML is not available.

### 16.4 Integration with GUI Tests

| GUI Test | Related Combos Test |
|----------|-------------------|
| TC-GUI-XXX (Combos Upload) | TC-COMBOS-130 |
| TC-GUI-XXX (Combos Results) | TC-COMBOS-080 |
| TC-GUI-XXX (AI Review) | TC-COMBOS-090 |

---

## 17. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-16 | DeviceSWAnalyzer Team | Initial version |
