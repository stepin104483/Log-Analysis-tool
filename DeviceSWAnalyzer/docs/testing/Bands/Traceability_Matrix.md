# Bands Module Requirements Traceability Matrix

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TM-BANDS-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Related Documents** | TP-BANDS-001, TC-BANDS |

---

## 1. Input Parsing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-BANDS-001.1 | Parse RFC XML to extract bands | TC-BANDS-001 | Full |
| FR-BANDS-001.2 | Extract LTE bands from eutra_band_list | TC-BANDS-002 | Full |
| FR-BANDS-001.3 | Extract NR SA bands from nr_sa_band_list | TC-BANDS-003 | Full |
| FR-BANDS-001.4 | Extract NR NSA bands from ca_4g_5g_combos | TC-BANDS-004 | Full |
| FR-BANDS-001.5 | Handle missing RFC file gracefully | TC-BANDS-005 | Full |
| FR-BANDS-002.1 | Parse HW band filter document | TC-BANDS-010 | Full |
| FR-BANDS-002.2 | Extract bands enabled by hardware | TC-BANDS-011 | Full |
| FR-BANDS-002.3 | Identify HW-disabled bands | TC-BANDS-012 | Full |
| FR-BANDS-003.1 | Parse carrier policy document | TC-BANDS-015 | Full |
| FR-BANDS-003.2 | Extract carrier-enabled bands | TC-BANDS-016 | Full |
| FR-BANDS-003.3 | Handle multiple carrier profiles | TC-BANDS-017 | Full |
| FR-BANDS-004.1 | Parse generic restriction document | TC-BANDS-020 | Full |
| FR-BANDS-004.2 | Extract restricted bands | TC-BANDS-021 | Full |
| FR-BANDS-005.1 | Parse MDB configuration | TC-BANDS-025 | Full |
| FR-BANDS-005.2 | Extract MDB band settings | TC-BANDS-026 | Full |
| FR-BANDS-006.1 | Parse QXDM log prints | TC-BANDS-030 | Full |
| FR-BANDS-006.2 | Extract runtime band information | TC-BANDS-031 | Full |
| FR-BANDS-007.1 | Parse UE capability information | TC-BANDS-035 | Full |
| FR-BANDS-007.2 | Extract final advertised bands | TC-BANDS-036 | Full |

---

## 2. Band Tracing Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-BANDS-010.1 | Trace bands through all layers | TC-BANDS-040 | Full |
| FR-BANDS-010.2 | Identify bands added at each stage | TC-BANDS-041 | Full |
| FR-BANDS-010.3 | Identify bands removed at each stage | TC-BANDS-042 | Full |
| FR-BANDS-010.4 | Calculate final band set | TC-BANDS-043 | Full |
| FR-BANDS-011.1 | Detect RFC vs HW filter mismatches | TC-BANDS-045 | Full |
| FR-BANDS-011.2 | Detect carrier policy mismatches | TC-BANDS-046 | Full |
| FR-BANDS-011.3 | Detect generic restriction mismatches | TC-BANDS-047 | Full |
| FR-BANDS-011.4 | Detect UE cap vs expected mismatches | TC-BANDS-048 | Full |
| FR-BANDS-012.1 | Flag unexpected band additions | TC-BANDS-050 | Full |
| FR-BANDS-012.2 | Flag unexpected band removals | TC-BANDS-051 | Full |
| FR-BANDS-012.3 | Identify configuration issues | TC-BANDS-052 | Full |

---

## 3. Output Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-BANDS-020.1 | Generate human-readable CLI output | TC-BANDS-060 | Full |
| FR-BANDS-020.2 | Show bands at each stage | TC-BANDS-061 | Full |
| FR-BANDS-020.3 | Highlight mismatches with indicators | TC-BANDS-062 | Full |
| FR-BANDS-020.4 | Use color coding for PASS/FAIL | TC-BANDS-063 | Full |
| FR-BANDS-021.1 | Generate HTML report | TC-BANDS-065 | Full |
| FR-BANDS-021.2 | Report includes all sections | TC-BANDS-066 | Full |
| FR-BANDS-021.3 | Report viewable standalone | TC-BANDS-067 | Full |
| FR-BANDS-021.4 | Visual indicators for issues | TC-BANDS-068 | Full |
| FR-BANDS-022.1 | Generate structured Claude prompt | TC-BANDS-070 | Full |
| FR-BANDS-022.2 | Prompt includes all data | TC-BANDS-071 | Full |
| FR-BANDS-022.3 | Prompt requests verdict | TC-BANDS-072 | Full |

---

## 4. Band Category Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-BANDS-030.1 | Analyze LTE FDD bands | TC-BANDS-080 | Full |
| FR-BANDS-030.2 | Analyze LTE TDD bands | TC-BANDS-081 | Full |
| FR-BANDS-030.3 | Categorize bands by region | TC-BANDS-082 | Full |
| FR-BANDS-031.1 | Analyze NR SA Sub-6 bands | TC-BANDS-085 | Full |
| FR-BANDS-031.2 | Analyze NR SA mmWave bands | TC-BANDS-086 | Full |
| FR-BANDS-031.3 | Identify TDD vs FDD NR bands | TC-BANDS-087 | Full |
| FR-BANDS-032.1 | Analyze NR NSA (EN-DC) bands | TC-BANDS-090 | Full |
| FR-BANDS-032.2 | Extract NR bands from EN-DC combos | TC-BANDS-091 | Full |
| FR-BANDS-032.3 | Identify anchor LTE bands | TC-BANDS-092 | Full |

---

## 5. Non-Functional Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| NFR-BANDS-001 | Analysis completes within 30 seconds | TC-BANDS-100 | Full |
| NFR-BANDS-002 | Handle RFC files up to 10MB | TC-BANDS-101 | Full |
| NFR-BANDS-003 | Process multiple files efficiently | TC-BANDS-102 | Full |
| NFR-BANDS-010 | Output readable by non-experts | TC-BANDS-105 | Full |
| NFR-BANDS-011 | Error messages indicate file | TC-BANDS-106 | Full |
| NFR-BANDS-012 | Helpful messages for missing files | TC-BANDS-107 | Full |
| NFR-BANDS-020 | No crash on malformed input | TC-BANDS-110 | Full |
| NFR-BANDS-021 | Handle partial input gracefully | TC-BANDS-111 | Full |
| NFR-BANDS-022 | Report parsing errors clearly | TC-BANDS-112 | Full |

---

## 6. Test Case to Requirements Mapping

| Test Case ID | Test Case Name | Requirements Covered |
|--------------|----------------|---------------------|
| TC-BANDS-001 | Parse Valid RFC XML | FR-BANDS-001.1 |
| TC-BANDS-002 | Extract LTE Bands | FR-BANDS-001.2 |
| TC-BANDS-003 | Extract NR SA Bands | FR-BANDS-001.3 |
| TC-BANDS-004 | Extract NR NSA Bands | FR-BANDS-001.4 |
| TC-BANDS-005 | Handle Missing RFC | FR-BANDS-001.5 |
| TC-BANDS-006 | Parse Empty Band Lists | FR-BANDS-001.1 |
| TC-BANDS-007 | Parse Malformed RFC | NFR-BANDS-020 |
| TC-BANDS-008 | Parse Special Characters | NFR-BANDS-020 |
| TC-BANDS-009 | Parse Large RFC | NFR-BANDS-002 |
| TC-BANDS-010 | Parse HW Band Filter | FR-BANDS-002.1 |
| TC-BANDS-011 | Extract HW-Enabled Bands | FR-BANDS-002.2 |
| TC-BANDS-012 | Identify HW-Disabled Bands | FR-BANDS-002.3 |
| TC-BANDS-013 | Handle Missing HW Filter | NFR-BANDS-021 |
| TC-BANDS-014 | Parse Malformed HW Filter | NFR-BANDS-020 |
| TC-BANDS-015 | Parse Carrier Policy | FR-BANDS-003.1 |
| TC-BANDS-016 | Extract Carrier Bands | FR-BANDS-003.2 |
| TC-BANDS-017 | Handle Multiple Profiles | FR-BANDS-003.3 |
| TC-BANDS-040 | Trace Through All Layers | FR-BANDS-010.1 |
| TC-BANDS-041 | Identify Bands Added | FR-BANDS-010.2 |
| TC-BANDS-042 | Identify Bands Removed | FR-BANDS-010.3 |
| TC-BANDS-043 | Calculate Final Set | FR-BANDS-010.4 |
| TC-BANDS-045 | RFC vs HW Mismatch | FR-BANDS-011.1 |
| TC-BANDS-046 | Carrier Policy Mismatch | FR-BANDS-011.2 |
| TC-BANDS-047 | Generic Restriction Mismatch | FR-BANDS-011.3 |
| TC-BANDS-048 | UE Cap vs Expected Mismatch | FR-BANDS-011.4 |
| TC-BANDS-050 | Unexpected Band Addition | FR-BANDS-012.1 |
| TC-BANDS-051 | Unexpected Band Removal | FR-BANDS-012.2 |
| TC-BANDS-052 | Configuration Issues | FR-BANDS-012.3 |
| TC-BANDS-065 | Generate HTML Report | FR-BANDS-021.1 |
| TC-BANDS-066 | Report Includes Sections | FR-BANDS-021.2 |
| TC-BANDS-067 | Report Viewable Standalone | FR-BANDS-021.3 |
| TC-BANDS-068 | Visual Indicators | FR-BANDS-021.4 |
| TC-BANDS-070 | Generate Claude Prompt | FR-BANDS-022.1 |
| TC-BANDS-071 | Prompt Includes Data | FR-BANDS-022.2 |
| TC-BANDS-072 | Prompt Requests Verdict | FR-BANDS-022.3 |
| TC-BANDS-080 | LTE FDD Analysis | FR-BANDS-030.1 |
| TC-BANDS-081 | LTE TDD Analysis | FR-BANDS-030.2 |
| TC-BANDS-082 | Region Categorization | FR-BANDS-030.3 |
| TC-BANDS-085 | NR SA Sub-6 Analysis | FR-BANDS-031.1 |
| TC-BANDS-086 | NR SA mmWave Analysis | FR-BANDS-031.2 |
| TC-BANDS-087 | TDD vs FDD NR Bands | FR-BANDS-031.3 |
| TC-BANDS-090 | EN-DC Analysis | FR-BANDS-032.1 |
| TC-BANDS-091 | Extract NR from Combos | FR-BANDS-032.2 |
| TC-BANDS-092 | Identify Anchor Bands | FR-BANDS-032.3 |
| TC-BANDS-100 | Performance 30s | NFR-BANDS-001 |
| TC-BANDS-101 | Handle 10MB File | NFR-BANDS-002 |
| TC-BANDS-110 | No Crash Malformed | NFR-BANDS-020 |
| TC-BANDS-111 | Handle Partial Input | NFR-BANDS-021 |
| TC-BANDS-112 | Report Errors Clearly | NFR-BANDS-022 |

---

## 7. Coverage Summary

### 7.1 Requirements Coverage Statistics

| Category | Total Requirements | Covered | Coverage % |
|----------|-------------------|---------|------------|
| Input Parsing (FR-BANDS-001 to 007) | 19 | 19 | 100% |
| Band Tracing (FR-BANDS-010 to 012) | 11 | 11 | 100% |
| Output (FR-BANDS-020 to 022) | 11 | 11 | 100% |
| Band Categories (FR-BANDS-030 to 032) | 9 | 9 | 100% |
| Non-Functional (NFR-BANDS) | 9 | 9 | 100% |
| **Total** | **59** | **59** | **100%** |

### 7.2 Test Case Distribution

| Category | Test Cases | % of Total |
|----------|------------|------------|
| RFC Parsing | 9 | 18% |
| HW Filter | 5 | 10% |
| Carrier Policy | 3 | 6% |
| Band Tracing | 4 | 8% |
| Mismatch Detection | 4 | 8% |
| Anomaly Detection | 3 | 6% |
| HTML Report | 4 | 8% |
| Claude Prompt | 3 | 6% |
| LTE Bands | 3 | 6% |
| NR Bands | 6 | 12% |
| Non-Functional | 6 | 12% |
| **Total** | **49** | **100%** |

### 7.3 Priority Distribution

| Priority | Count | % |
|----------|-------|---|
| High | 35 | 71% |
| Medium | 11 | 23% |
| Low | 3 | 6% |
| **Total** | **49** | **100%** |

---

## 8. E2E Test Coverage

| E2E Test File | Test Cases Covered |
|---------------|-------------------|
| test_bands_module.py | TC-BANDS-001, TC-BANDS-002, TC-BANDS-003, TC-BANDS-006, TC-BANDS-065, TC-BANDS-066, TC-BANDS-068, TC-BANDS-080, TC-BANDS-085, TC-BANDS-090 |

---

## 9. Gaps and Notes

### 9.1 Requirements Fully Covered

All 59 requirements from the Bands Module Requirements document have corresponding test cases.

### 9.2 Areas Requiring Test Data

| Area | Test Data Needed |
|------|-----------------|
| HW Filter Parsing | Sample HW filter XML files |
| Carrier Policy | Sample carrier policy files |
| MDB Config | Sample MDB configuration |
| QXDM Logs | Sample QXDM log output |
| UE Capability | Sample UE capability XML |
| Large Files | 10MB test file for boundary testing |

### 9.3 Integration with GUI Tests

| GUI Test | Related Bands Test |
|----------|-------------------|
| TC-GUI-020 (Results Display) | TC-BANDS-065 (HTML Report) |
| TC-GUI-022 (AI Review Button) | TC-BANDS-070 (Claude Prompt) |
| TC-GUI-031 (Download Report) | TC-BANDS-067 (Standalone Report) |

---

## 10. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
