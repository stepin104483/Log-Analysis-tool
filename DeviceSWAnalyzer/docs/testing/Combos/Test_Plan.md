# Combos Module Test Plan

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TP-COMBOS-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-16 |
| **Author** | DeviceSWAnalyzer Team |
| **Status** | Draft |

---

## 1. Introduction

### 1.1 Purpose
This document defines the test plan for the Combos Analysis Module, which analyzes Carrier Aggregation (CA) and Dual Connectivity (DC) combinations from multiple data sources (RFC, QXDM, UE Capability) to identify discrepancies and provide knowledge-based reasoning.

### 1.2 Scope

**In Scope:**
- RFC XML parsing for combo extraction
- QXDM 0xB826 log parsing
- UE Capability (ASN.1 XML) parsing
- EFS control file parsing
- Combo normalization and comparison
- Knowledge Base loading (YAML)
- Reasoning Engine discrepancy explanation
- Severity classification
- HTML report generation
- Claude prompt generation
- LTE CA, NRCA, EN-DC, NR-DC combo types

**Out of Scope:**
- GUI testing (covered in GUI Test Plan)
- Claude CLI integration (covered in AI Integration test plan)
- Other modules (Bands, IMS, etc.)

### 1.3 References

| Document | Location |
|----------|----------|
| Combos Requirements | `docs/modules/combos/Requirements.md` |
| Combos Architecture | `docs/modules/combos/Architecture.md` |
| Overall Requirements | `docs/Overall_Requirements.md` |
| Combos Test Cases | `docs/testing/Combos/test_cases/TC_Combos.md` |
| Traceability Matrix | `docs/testing/Combos/Traceability_Matrix.md` |

---

## 2. Test Items

### 2.1 Features to Test

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| COMBOS-F01 | RFC Parsing | Parse RFC XML and extract combos |
| COMBOS-F02 | QXDM Parsing | Parse 0xB826 log output |
| COMBOS-F03 | UE Cap Parsing | Parse ASN.1 XML UE Capability |
| COMBOS-F04 | EFS Parsing | Parse EFS control files |
| COMBOS-F05 | Normalization | Normalize combos for comparison |
| COMBOS-F06 | Comparison | Three-source comparison |
| COMBOS-F07 | Knowledge Base | Load YAML restrictions/policies |
| COMBOS-F08 | Reasoning Engine | Explain discrepancies |
| COMBOS-F09 | Severity Classification | Assign severity levels |
| COMBOS-F10 | HTML Report | Generate analysis report |
| COMBOS-F11 | Claude Prompt | Generate AI prompt |
| COMBOS-F12 | LTE CA Analysis | Analyze LTE CA combos |
| COMBOS-F13 | EN-DC Analysis | Analyze EN-DC combos |
| COMBOS-F14 | NRCA Analysis | Analyze NR CA combos |
| COMBOS-F15 | NR-DC Analysis | Analyze NR-DC combos |

### 2.2 Features NOT to Test

| Feature | Reason |
|---------|--------|
| Web UI | Covered in GUI Test Plan |
| Claude CLI execution | Covered in AI Integration Test Plan |
| File upload handling | Covered in GUI Test Plan |

---

## 3. Test Approach

### 3.1 Test Types

| Test Type | Description | Priority |
|-----------|-------------|----------|
| **Unit** | Individual parser functions, models | High |
| **Integration** | End-to-end analysis flow | High |
| **Functional** | Feature verification | High |
| **Negative** | Error handling, malformed input | High |
| **Boundary** | Edge cases, large files, empty sets | Medium |

### 3.2 Test Levels

| Level | Description | Test Location |
|-------|-------------|---------------|
| **Unit** | Individual parsers, normalizer, comparator | `src/modules/combos/tests/` |
| **Component** | Analyzer module as a whole | `tests/unit/combos/` |
| **Integration** | Module + Web UI + Output | `tests/integration/` |
| **E2E** | Browser-based workflow testing | `tests/e2e/Combos/` |

### 3.3 Test Execution Approach

- **Automated Testing**: pytest for unit/integration tests
- **E2E Testing**: Playwright for browser-based tests
- **Manual Testing**: Verification of output content and reasoning accuracy

---

## 4. Entry Criteria

Testing can begin when:

- [ ] Combos module code is complete (P0/P1/P2)
- [ ] Sample RFC XML files are available
- [ ] Sample QXDM 0xB826 logs are available
- [ ] Sample UE Capability files are available
- [ ] Knowledge base YAML files created
- [ ] pytest environment configured
- [ ] Test cases reviewed and approved

---

## 5. Exit Criteria

Testing is complete when:

- [ ] All High priority test cases executed
- [ ] All High priority test cases passed (or defects documented)
- [ ] All Medium priority test cases executed
- [ ] Code coverage >= 80% for core parsing/comparison logic
- [ ] No Critical/Blocker defects remain open
- [ ] Test report generated and reviewed

---

## 6. Test Environment

### 6.1 Software Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 |
| **Python** | 3.8+ |
| **pytest** | 7.x+ |
| **Flask** | Running at localhost:5000 |
| **PyYAML** | 6.x+ (for Knowledge Base tests) |

### 6.2 Test Data

| Data Type | Location | Description |
|-----------|----------|-------------|
| Valid RFC XML | `test_data/combos/valid/` | Valid RFC files with various combo configs |
| Invalid XML | `test_data/combos/invalid/` | Malformed XML files |
| QXDM Logs | `test_data/combos/qxdm/` | 0xB826 log output samples |
| UE Capability | `test_data/combos/uecap/` | ASN.1 XML exports |
| EFS Files | `test_data/combos/efs/` | prune_ca_combos, ca_disable |
| Knowledge Base | `knowledge_library/combos/` | YAML restriction/policy files |
| Large Files | `test_data/combos/boundary/` | Files near size limits |

---

## 7. Test Data Requirements

### 7.1 RFC XML Test Files

| File | Description | Purpose |
|------|-------------|---------|
| `rfc_lte_ca.xml` | RFC with LTE CA combos only | LTE CA parsing |
| `rfc_endc.xml` | RFC with EN-DC combos | EN-DC parsing |
| `rfc_nrca.xml` | RFC with NR CA combos | NRCA parsing |
| `rfc_full.xml` | RFC with all combo types | Full analysis |
| `rfc_empty.xml` | RFC with empty combo lists | Edge case |
| `rfc_malformed.xml` | Invalid XML structure | Error handling |

### 7.2 QXDM Test Files

| File | Description |
|------|-------------|
| `0xb826_structured.txt` | Structured table format |
| `0xb826_raw.txt` | Raw combo strings |
| `0xb826_labeled.txt` | Labeled combo entries |
| `0xb826_empty.txt` | No combos found |

### 7.3 UE Capability Test Files

| File | Description |
|------|-------------|
| `uecap_eutra.xml` | EUTRA-Capability (LTE CA) |
| `uecap_mrdc.xml` | UE-MRDC-Capability (EN-DC) |
| `uecap_nr.xml` | UE-NR-Capability (NR CA) |
| `uecap_full.xml` | All capability types |

### 7.4 EFS Test Files

| File | Description |
|------|-------------|
| `prune_ca_combos` | Pruned combo list |
| `ca_disable` | CA disable flag |
| `cap_control_nrca_enabled` | NRCA enable flag |
| `cap_control_nrdc_enabled` | NR-DC enable flag |

---

## 8. Requirements Traceability

### 8.1 RFC Parsing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-001.1 | Parse RFC XML to extract combos | TC-COMBOS-001 |
| FR-COMBOS-001.2 | Extract LTE CA combos from ca_combos_list | TC-COMBOS-002 |
| FR-COMBOS-001.3 | Extract EN-DC combos from ca_4g_5g_combos | TC-COMBOS-003 |
| FR-COMBOS-001.4 | Extract NRCA combos from nr_ca_combos_list | TC-COMBOS-004 |
| FR-COMBOS-001.5 | Extract NR-DC combos from nr_dc_combos_list | TC-COMBOS-005 |
| FR-COMBOS-001.6 | Handle missing RFC file gracefully | TC-COMBOS-006 |
| FR-COMBOS-001.7 | Handle malformed RFC XML without crashing | TC-COMBOS-007 |

### 8.2 QXDM Parsing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-002.1 | Parse QXDM 0xB826 log output | TC-COMBOS-010 |
| FR-COMBOS-002.2 | Support structured table format parsing | TC-COMBOS-011 |
| FR-COMBOS-002.3 | Support raw combo string parsing | TC-COMBOS-012 |
| FR-COMBOS-002.4 | Extract BCS values | TC-COMBOS-013 |
| FR-COMBOS-002.5 | Identify combo type | TC-COMBOS-014 |
| FR-COMBOS-002.6 | Handle empty or missing QXDM file | TC-COMBOS-015 |

### 8.3 UE Capability Parsing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-003.1 | Parse ASN.1 XML exports | TC-COMBOS-020 |
| FR-COMBOS-003.2 | Extract LTE CA from EUTRA-Capability | TC-COMBOS-021 |
| FR-COMBOS-003.3 | Extract EN-DC from UE-MRDC-Capability | TC-COMBOS-022 |
| FR-COMBOS-003.4 | Extract NRCA from UE-NR-Capability | TC-COMBOS-023 |
| FR-COMBOS-003.5 | Support supportedBandCombination-r10 format | TC-COMBOS-024 |
| FR-COMBOS-003.6 | Support supportedBandCombinationList format | TC-COMBOS-025 |
| FR-COMBOS-003.7 | Extract supported bands list | TC-COMBOS-026 |

### 8.4 EFS Parsing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-004.1 | Parse prune_ca_combos EFS file | TC-COMBOS-030 |
| FR-COMBOS-004.2 | Parse ca_disable binary flag | TC-COMBOS-031 |
| FR-COMBOS-004.3 | Parse cap_control_nrca_enabled flag | TC-COMBOS-032 |
| FR-COMBOS-004.4 | Parse cap_control_nrdc_enabled flag | TC-COMBOS-033 |
| FR-COMBOS-004.5 | Support BCS-specific pruning | TC-COMBOS-034 |
| FR-COMBOS-004.6 | Handle missing EFS files gracefully | TC-COMBOS-035 |

### 8.5 Normalization Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-005.1 | Normalize combo keys for comparison | TC-COMBOS-040 |
| FR-COMBOS-005.2 | Sort band components consistently | TC-COMBOS-041 |
| FR-COMBOS-005.3 | Uppercase band class letters | TC-COMBOS-042 |
| FR-COMBOS-005.4 | Distinguish LTE and NR bands in EN-DC | TC-COMBOS-043 |
| FR-COMBOS-005.5 | Handle BCS value normalization | TC-COMBOS-044 |

### 8.6 Comparison Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-006.1 | Compare RFC combos vs QXDM | TC-COMBOS-050 |
| FR-COMBOS-006.2 | Compare QXDM vs UE Capability | TC-COMBOS-051 |
| FR-COMBOS-006.3 | Identify combos missing in target source | TC-COMBOS-052 |
| FR-COMBOS-006.4 | Identify extra combos in target source | TC-COMBOS-053 |
| FR-COMBOS-006.5 | Calculate match percentage | TC-COMBOS-054 |
| FR-COMBOS-006.6 | Compare by combo type | TC-COMBOS-055 |

### 8.7 Knowledge Base Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-007.1 | Load band restrictions from YAML | TC-COMBOS-060 |
| FR-COMBOS-007.2 | Load carrier policies from YAML | TC-COMBOS-061 |
| FR-COMBOS-007.3 | Support regional band restrictions | TC-COMBOS-062 |
| FR-COMBOS-007.4 | Support regulatory band restrictions | TC-COMBOS-063 |
| FR-COMBOS-007.5 | Support hardware variant restrictions | TC-COMBOS-064 |
| FR-COMBOS-007.6 | Support carrier-specific exclusions | TC-COMBOS-065 |
| FR-COMBOS-007.7 | Support carrier-required combos | TC-COMBOS-066 |

### 8.8 Reasoning Engine Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-008.1 | Explain discrepancies using knowledge base | TC-COMBOS-070 |
| FR-COMBOS-008.2 | Detect EFS pruning as explanation | TC-COMBOS-071 |
| FR-COMBOS-008.3 | Detect band restrictions as explanation | TC-COMBOS-072 |
| FR-COMBOS-008.4 | Detect carrier exclusions as explanation | TC-COMBOS-073 |
| FR-COMBOS-008.5 | Apply heuristics for mmWave bands | TC-COMBOS-074 |
| FR-COMBOS-008.6 | Apply heuristics for Band 14 (FirstNet) | TC-COMBOS-075 |
| FR-COMBOS-008.7 | Assign severity levels to discrepancies | TC-COMBOS-076 |
| FR-COMBOS-008.8 | Categorize discrepancies by severity | TC-COMBOS-077 |

### 8.9 Output Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-COMBOS-010.1 | Generate HTML analysis report | TC-COMBOS-080 |
| FR-COMBOS-010.2 | Report includes summary dashboard | TC-COMBOS-081 |
| FR-COMBOS-010.3 | Report includes combo count statistics | TC-COMBOS-082 |
| FR-COMBOS-010.4 | Report includes match percentage bars | TC-COMBOS-083 |
| FR-COMBOS-010.5 | Report includes discrepancy tables | TC-COMBOS-084 |
| FR-COMBOS-010.6 | Report includes reasoning column | TC-COMBOS-085 |
| FR-COMBOS-010.7 | Report includes severity distribution | TC-COMBOS-086 |
| FR-COMBOS-010.8 | Report supports collapsible sections | TC-COMBOS-087 |
| FR-COMBOS-011.1 | Generate Claude AI prompt | TC-COMBOS-090 |
| FR-COMBOS-011.2 | Prompt includes all comparison data | TC-COMBOS-091 |
| FR-COMBOS-011.3 | Prompt requests expert analysis | TC-COMBOS-092 |

### 8.10 Non-Functional Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| NFR-COMBOS-001 | Analysis completes within 60 seconds | TC-COMBOS-100 |
| NFR-COMBOS-002 | Handle RFC files up to 20MB | TC-COMBOS-101 |
| NFR-COMBOS-003 | Handle QXDM logs up to 10MB | TC-COMBOS-102 |
| NFR-COMBOS-004 | Handle >1000 combos per source | TC-COMBOS-103 |
| NFR-COMBOS-010 | No crash on malformed input | TC-COMBOS-110 |
| NFR-COMBOS-011 | Handle partial input gracefully | TC-COMBOS-111 |
| NFR-COMBOS-012 | Report parsing errors clearly | TC-COMBOS-112 |
| NFR-COMBOS-020 | Output readable by non-experts | TC-COMBOS-115 |
| NFR-COMBOS-021 | Error messages indicate problematic file | TC-COMBOS-116 |
| NFR-COMBOS-023 | HTML report viewable standalone | TC-COMBOS-117 |

---

## 9. Test Cases Summary

| Category | TC ID Range | Count | Priority |
|----------|-------------|-------|----------|
| RFC Parsing | TC-COMBOS-001 to TC-COMBOS-009 | 9 | High |
| QXDM Parsing | TC-COMBOS-010 to TC-COMBOS-019 | 10 | High |
| UE Cap Parsing | TC-COMBOS-020 to TC-COMBOS-029 | 10 | High |
| EFS Parsing | TC-COMBOS-030 to TC-COMBOS-039 | 10 | High |
| Normalization | TC-COMBOS-040 to TC-COMBOS-049 | 10 | High |
| Comparison | TC-COMBOS-050 to TC-COMBOS-059 | 10 | High |
| Knowledge Base | TC-COMBOS-060 to TC-COMBOS-069 | 10 | High |
| Reasoning Engine | TC-COMBOS-070 to TC-COMBOS-079 | 10 | High |
| HTML Report | TC-COMBOS-080 to TC-COMBOS-089 | 10 | High |
| Claude Prompt | TC-COMBOS-090 to TC-COMBOS-094 | 5 | High |
| Performance | TC-COMBOS-100 to TC-COMBOS-104 | 5 | Medium |
| Reliability | TC-COMBOS-110 to TC-COMBOS-114 | 5 | High |
| Usability | TC-COMBOS-115 to TC-COMBOS-119 | 5 | Medium |
| Integration | TC-COMBOS-120 to TC-COMBOS-129 | 10 | High |
| E2E | TC-COMBOS-130 to TC-COMBOS-139 | 10 | High |
| **Total** | | **119** | |

Detailed test cases: `docs/testing/Combos/test_cases/TC_Combos.md`

---

## 10. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Incomplete test data | Medium | High | Create comprehensive test files for all formats |
| RFC format variations | High | Medium | Test with multiple RFC versions/formats |
| QXDM log format variations | High | Medium | Test structured, raw, and labeled formats |
| UE Cap XML format variations | Medium | Medium | Test EUTRA, MRDC, and NR formats |
| Knowledge base YAML parsing | Low | Medium | Ensure PyYAML installed, skip tests if not |
| Parser edge cases | Medium | Medium | Add boundary tests for empty/large files |
| Large file handling | Low | High | Test with 20MB RFC, 10MB QXDM files |

---

## 11. Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Test Plan | `docs/testing/Combos/Test_Plan.md` | This document |
| Test Cases | `docs/testing/Combos/test_cases/TC_Combos.md` | Detailed test cases |
| Traceability Matrix | `docs/testing/Combos/Traceability_Matrix.md` | Requirements mapping |
| Unit Tests | `src/modules/combos/tests/` | pytest unit tests |
| Integration Tests | `tests/integration/combos/` | Integration tests |
| E2E Tests | `tests/e2e/Combos/` | Playwright E2E tests |
| Test Data | `test_data/combos/` | Test input files |
| Test Report | `docs/testing/test_reports/` | Execution results |

---

## 12. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | | | |
| Developer | | | |
| Product Owner | | | |

---

## 13. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-16 | DeviceSWAnalyzer Team | Initial version |
