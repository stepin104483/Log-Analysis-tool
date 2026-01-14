# Bands Module Test Plan

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TP-BANDS-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Author** | DeviceSWAnalyzer Team |
| **Status** | Draft |

---

## 1. Introduction

### 1.1 Purpose
This document defines the test plan for the Bands Analysis Module, which analyzes band filtering from RF Card (RFC) through various configuration layers to final UE Capability.

### 1.2 Scope

**In Scope:**
- RFC XML parsing and band extraction
- Hardware band filter parsing
- Carrier policy parsing
- Generic restriction parsing
- MDB configuration parsing
- QXDM log parsing
- UE capability parsing
- Band flow tracing
- Mismatch and anomaly detection
- Output generation (CLI, HTML, Prompt)
- LTE, NR SA, NR NSA band analysis

**Out of Scope:**
- GUI testing (covered in GUI Test Plan)
- Claude CLI integration (covered in AI Integration test plan)
- Other modules (Combos, IMS, etc.)

### 1.3 References

| Document | Location |
|----------|----------|
| Bands Requirements | `docs/modules/bands/Requirements.md` |
| Bands Architecture | `docs/modules/bands/Architecture.md` |
| Overall Requirements | `docs/Overall_Requirements.md` |
| Bands Test Cases | `docs/testing/Bands/test_cases/TC_Bands.md` |

---

## 2. Test Items

### 2.1 Features to Test

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| BANDS-F01 | RFC Parsing | Parse RFC XML and extract bands |
| BANDS-F02 | HW Filter Parsing | Parse hardware band filter |
| BANDS-F03 | Carrier Policy Parsing | Parse carrier policy document |
| BANDS-F04 | Generic Restriction Parsing | Parse generic restrictions |
| BANDS-F05 | MDB Config Parsing | Parse MDB configuration |
| BANDS-F06 | QXDM Log Parsing | Parse QXDM log prints |
| BANDS-F07 | UE Capability Parsing | Parse UE capability info |
| BANDS-F08 | Band Flow Tracing | Trace bands through layers |
| BANDS-F09 | Mismatch Detection | Detect band mismatches |
| BANDS-F10 | Anomaly Detection | Flag unexpected changes |
| BANDS-F11 | LTE Band Analysis | Analyze LTE FDD/TDD bands |
| BANDS-F12 | NR SA Band Analysis | Analyze NR SA bands |
| BANDS-F13 | NR NSA Band Analysis | Analyze NR NSA/EN-DC bands |
| BANDS-F14 | HTML Report Generation | Generate HTML report |
| BANDS-F15 | Claude Prompt Generation | Generate AI prompt |

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
| **Unit** | Individual parser functions | High |
| **Integration** | End-to-end analysis flow | High |
| **Functional** | Feature verification | High |
| **Negative** | Error handling, malformed input | High |
| **Boundary** | Edge cases, large files | Medium |

### 3.2 Test Levels

| Level | Description |
|-------|-------------|
| **Unit** | Individual parsers, extractors |
| **Component** | Analyzer module as a whole |
| **Integration** | Module + Web UI + Output |

### 3.3 Test Execution Approach

- **Automated Testing**: pytest for unit/integration tests
- **E2E Testing**: Playwright for browser-based tests
- **Manual Testing**: Verification of output content

---

## 4. Entry Criteria

Testing can begin when:

- [ ] Bands module code is complete
- [ ] Sample RFC XML files are available
- [ ] Test data files prepared for all input types
- [ ] pytest environment configured
- [ ] Test cases reviewed and approved

---

## 5. Exit Criteria

Testing is complete when:

- [ ] All High priority test cases executed
- [ ] All High priority test cases passed (or defects documented)
- [ ] All Medium priority test cases executed
- [ ] Code coverage >= 80% for core parsing logic
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

### 6.2 Test Data

| Data Type | Location | Description |
|-----------|----------|-------------|
| Valid RFC XML | `test_data/bands/valid/` | Valid RFC files with various band configs |
| Invalid XML | `test_data/bands/invalid/` | Malformed XML files |
| Partial Input | `test_data/bands/partial/` | RFC with missing sections |
| Large Files | `test_data/bands/boundary/` | Files near size limits |
| Multi-layer | `test_data/bands/multi/` | RFC + HW + Carrier + etc. |

---

## 7. Test Data Requirements

### 7.1 RFC XML Test Files

| File | Description | Purpose |
|------|-------------|---------|
| `rfc_lte_only.xml` | RFC with LTE bands only | LTE parsing |
| `rfc_nr_sa_only.xml` | RFC with NR SA bands only | NR SA parsing |
| `rfc_nr_nsa_only.xml` | RFC with NR NSA combos | NR NSA parsing |
| `rfc_full.xml` | RFC with all band types | Full analysis |
| `rfc_empty_bands.xml` | RFC with empty band lists | Edge case |
| `rfc_malformed.xml` | Invalid XML structure | Error handling |

### 7.2 Supporting Files

| File | Description |
|------|-------------|
| `hw_band_filter.xml` | Sample HW band filter |
| `carrier_policy.xml` | Sample carrier policy |
| `generic_restriction.xml` | Sample restrictions |
| `mdb_config.xml` | Sample MDB config |
| `qxdm_log.txt` | Sample QXDM output |
| `ue_capability.xml` | Sample UE cap info |

---

## 8. Requirements Traceability

### 8.1 Input Parsing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-BANDS-001.1 | Parse RFC XML to extract bands | TC-BANDS-001 |
| FR-BANDS-001.2 | Extract LTE bands from eutra_band_list | TC-BANDS-002 |
| FR-BANDS-001.3 | Extract NR SA bands from nr_sa_band_list | TC-BANDS-003 |
| FR-BANDS-001.4 | Extract NR NSA bands from ca_4g_5g_combos | TC-BANDS-004 |
| FR-BANDS-001.5 | Handle missing RFC file gracefully | TC-BANDS-005 |
| FR-BANDS-002.1 | Parse HW band filter document | TC-BANDS-010 |
| FR-BANDS-002.2 | Extract bands enabled by hardware | TC-BANDS-011 |
| FR-BANDS-002.3 | Identify HW-disabled bands | TC-BANDS-012 |
| FR-BANDS-003.1 | Parse carrier policy document | TC-BANDS-015 |
| FR-BANDS-003.2 | Extract carrier-enabled bands | TC-BANDS-016 |
| FR-BANDS-003.3 | Handle multiple carrier profiles | TC-BANDS-017 |
| FR-BANDS-004.1 | Parse generic restriction document | TC-BANDS-020 |
| FR-BANDS-004.2 | Extract restricted bands | TC-BANDS-021 |
| FR-BANDS-005.1 | Parse MDB configuration | TC-BANDS-025 |
| FR-BANDS-005.2 | Extract MDB band settings | TC-BANDS-026 |
| FR-BANDS-006.1 | Parse QXDM log prints | TC-BANDS-030 |
| FR-BANDS-006.2 | Extract runtime band information | TC-BANDS-031 |
| FR-BANDS-007.1 | Parse UE capability information | TC-BANDS-035 |
| FR-BANDS-007.2 | Extract final advertised bands | TC-BANDS-036 |

### 8.2 Band Tracing Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-BANDS-010.1 | Trace bands through all layers | TC-BANDS-040 |
| FR-BANDS-010.2 | Identify bands added at each stage | TC-BANDS-041 |
| FR-BANDS-010.3 | Identify bands removed at each stage | TC-BANDS-042 |
| FR-BANDS-010.4 | Calculate final band set | TC-BANDS-043 |
| FR-BANDS-011.1 | Detect RFC vs HW filter mismatches | TC-BANDS-045 |
| FR-BANDS-011.2 | Detect carrier policy mismatches | TC-BANDS-046 |
| FR-BANDS-011.3 | Detect generic restriction mismatches | TC-BANDS-047 |
| FR-BANDS-011.4 | Detect UE cap vs expected mismatches | TC-BANDS-048 |
| FR-BANDS-012.1 | Flag unexpected band additions | TC-BANDS-050 |
| FR-BANDS-012.2 | Flag unexpected band removals | TC-BANDS-051 |
| FR-BANDS-012.3 | Identify configuration issues | TC-BANDS-052 |

### 8.3 Output Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-BANDS-020.1 | Generate human-readable CLI output | TC-BANDS-060 |
| FR-BANDS-020.2 | Show bands at each stage | TC-BANDS-061 |
| FR-BANDS-020.3 | Highlight mismatches with indicators | TC-BANDS-062 |
| FR-BANDS-020.4 | Use color coding for PASS/FAIL | TC-BANDS-063 |
| FR-BANDS-021.1 | Generate HTML report | TC-BANDS-065 |
| FR-BANDS-021.2 | Report includes all sections | TC-BANDS-066 |
| FR-BANDS-021.3 | Report viewable standalone | TC-BANDS-067 |
| FR-BANDS-021.4 | Visual indicators for issues | TC-BANDS-068 |
| FR-BANDS-022.1 | Generate structured Claude prompt | TC-BANDS-070 |
| FR-BANDS-022.2 | Prompt includes all data | TC-BANDS-071 |
| FR-BANDS-022.3 | Prompt requests verdict | TC-BANDS-072 |

### 8.4 Band Category Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| FR-BANDS-030.1 | Analyze LTE FDD bands | TC-BANDS-080 |
| FR-BANDS-030.2 | Analyze LTE TDD bands | TC-BANDS-081 |
| FR-BANDS-030.3 | Categorize bands by region | TC-BANDS-082 |
| FR-BANDS-031.1 | Analyze NR SA Sub-6 bands | TC-BANDS-085 |
| FR-BANDS-031.2 | Analyze NR SA mmWave bands | TC-BANDS-086 |
| FR-BANDS-031.3 | Identify TDD vs FDD NR bands | TC-BANDS-087 |
| FR-BANDS-032.1 | Analyze NR NSA (EN-DC) bands | TC-BANDS-090 |
| FR-BANDS-032.2 | Extract NR bands from EN-DC combos | TC-BANDS-091 |
| FR-BANDS-032.3 | Identify anchor LTE bands | TC-BANDS-092 |

### 8.5 Non-Functional Requirements

| Requirement ID | Requirement | Test Case ID |
|----------------|-------------|--------------|
| NFR-BANDS-001 | Analysis completes within 30 seconds | TC-BANDS-100 |
| NFR-BANDS-002 | Handle RFC files up to 10MB | TC-BANDS-101 |
| NFR-BANDS-003 | Process multiple files efficiently | TC-BANDS-102 |
| NFR-BANDS-010 | Output readable by non-experts | TC-BANDS-105 |
| NFR-BANDS-011 | Error messages indicate file | TC-BANDS-106 |
| NFR-BANDS-012 | Helpful messages for missing files | TC-BANDS-107 |
| NFR-BANDS-020 | No crash on malformed input | TC-BANDS-110 |
| NFR-BANDS-021 | Handle partial input gracefully | TC-BANDS-111 |
| NFR-BANDS-022 | Report parsing errors clearly | TC-BANDS-112 |

---

## 9. Test Cases Summary

| Category | TC ID Range | Count | Priority |
|----------|-------------|-------|----------|
| RFC Parsing | TC-BANDS-001 to TC-BANDS-009 | 9 | High |
| HW Filter Parsing | TC-BANDS-010 to TC-BANDS-014 | 5 | High |
| Carrier Policy Parsing | TC-BANDS-015 to TC-BANDS-019 | 5 | High |
| Generic Restriction | TC-BANDS-020 to TC-BANDS-024 | 5 | Medium |
| MDB Config | TC-BANDS-025 to TC-BANDS-029 | 5 | Medium |
| QXDM Log | TC-BANDS-030 to TC-BANDS-034 | 5 | Medium |
| UE Capability | TC-BANDS-035 to TC-BANDS-039 | 5 | High |
| Band Flow Tracing | TC-BANDS-040 to TC-BANDS-044 | 5 | High |
| Mismatch Detection | TC-BANDS-045 to TC-BANDS-049 | 5 | High |
| Anomaly Detection | TC-BANDS-050 to TC-BANDS-054 | 5 | High |
| CLI Output | TC-BANDS-060 to TC-BANDS-064 | 5 | Medium |
| HTML Report | TC-BANDS-065 to TC-BANDS-069 | 5 | High |
| Claude Prompt | TC-BANDS-070 to TC-BANDS-074 | 5 | High |
| LTE Bands | TC-BANDS-080 to TC-BANDS-084 | 5 | High |
| NR SA Bands | TC-BANDS-085 to TC-BANDS-089 | 5 | High |
| NR NSA Bands | TC-BANDS-090 to TC-BANDS-094 | 5 | High |
| Performance | TC-BANDS-100 to TC-BANDS-104 | 5 | Medium |
| Usability | TC-BANDS-105 to TC-BANDS-109 | 5 | Medium |
| Reliability | TC-BANDS-110 to TC-BANDS-114 | 5 | High |
| **Total** | | **99** | |

Detailed test cases: `docs/testing/test_cases/TC_Bands.md`

---

## 10. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Incomplete test data | Medium | High | Create comprehensive test files |
| RFC format variations | High | Medium | Test with multiple RFC versions |
| Parser edge cases | Medium | Medium | Add boundary tests |
| Large file handling | Low | High | Test with 10MB files |
| Missing optional inputs | Low | Low | Test all combinations |

---

## 11. Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Test Plan | `docs/testing/Bands/Test_Plan.md` | This document |
| Test Cases | `docs/testing/Bands/test_cases/TC_Bands.md` | Detailed test cases |
| Traceability Matrix | `docs/testing/Bands/Traceability_Matrix.md` | Requirements mapping |
| Unit Tests | `tests/unit/bands/` | pytest unit tests |
| E2E Tests | `tests/e2e/Bands/` | Playwright E2E tests |
| Test Data | `docs/testing/test_data/bands/` | Test input files |
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
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
