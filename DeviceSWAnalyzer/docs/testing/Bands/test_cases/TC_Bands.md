# Bands Module Test Cases

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TC-BANDS |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Related Test Plan** | TP-BANDS-001 |

---

## 1. RFC Parsing Test Cases

### TC-BANDS-001: Parse Valid RFC XML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-001.1 |
| **Preconditions** | Valid RFC XML file available |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide valid RFC XML file to analyzer | File is accepted |
| 2 | Run analysis | Parsing completes without errors |
| 3 | Verify bands extracted | Band lists populated correctly |

---

### TC-BANDS-002: Extract LTE Bands from eutra_band_list

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-001.2 |
| **Preconditions** | RFC with eutra_band_list section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with LTE bands 1, 3, 7, 20 | Parsing completes |
| 2 | Verify extracted LTE bands | [1, 3, 7, 20] extracted |
| 3 | Verify band count | Count matches XML content |

---

### TC-BANDS-003: Extract NR SA Bands from nr_sa_band_list

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-001.3 |
| **Preconditions** | RFC with nr_sa_band_list section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with NR SA bands n78, n79 | Parsing completes |
| 2 | Verify extracted NR SA bands | [n78, n79] extracted |
| 3 | Verify band format | "n" prefix preserved |

---

### TC-BANDS-004: Extract NR NSA Bands from ca_4g_5g_combos

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-001.4 |
| **Preconditions** | RFC with EN-DC combo section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with EN-DC combos | Parsing completes |
| 2 | Verify NR bands extracted from combos | NR bands identified |
| 3 | Verify anchor LTE bands identified | LTE anchors listed |

---

### TC-BANDS-005: Handle Missing RFC File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-001.5 |
| **Preconditions** | No RFC file provided |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis without RFC file | Error message displayed |
| 2 | Verify error message | "RFC file required" or similar |
| 3 | Verify no crash | Application remains stable |

---

### TC-BANDS-006: Parse RFC with Empty Band Lists

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-BANDS-001.1 |
| **Preconditions** | RFC with empty eutra_band_list |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with empty band lists | Parsing completes |
| 2 | Verify output | Empty band set reported |
| 3 | Verify no crash | Analysis continues |

---

### TC-BANDS-007: Parse Malformed RFC XML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-BANDS-020 |
| **Preconditions** | Malformed XML file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide malformed XML | Error detected |
| 2 | Verify error message | Clear parsing error message |
| 3 | Verify no crash | Application stable |

---

### TC-BANDS-008: Parse RFC with Special Characters

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | NFR-BANDS-020 |
| **Preconditions** | RFC with UTF-8 special characters |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with special characters | Parsing handles encoding |
| 2 | Verify output | No garbled text |

---

### TC-BANDS-009: Parse Large RFC File (10MB)

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-BANDS-002 |
| **Preconditions** | RFC file ~10MB |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide 10MB RFC file | File accepted |
| 2 | Run analysis | Completes within timeout |
| 3 | Verify results | Bands extracted correctly |

---

## 2. HW Band Filter Parsing Test Cases

### TC-BANDS-010: Parse Valid HW Band Filter

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-002.1 |
| **Preconditions** | Valid HW band filter XML |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide HW band filter file | File accepted |
| 2 | Run analysis | HW filter parsed |
| 3 | Verify bands extracted | HW-enabled bands listed |

---

### TC-BANDS-011: Extract HW-Enabled Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-002.2 |
| **Preconditions** | HW filter with enabled bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse HW filter | Parsing completes |
| 2 | Verify enabled bands extracted | Correct band list |
| 3 | Compare with RFC bands | Intersection calculated |

---

### TC-BANDS-012: Identify HW-Disabled Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-002.3 |
| **Preconditions** | RFC + HW filter with differences |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC has bands 1,3,7; HW enables 1,3 | Analysis runs |
| 2 | Verify band 7 identified as HW-disabled | Correctly flagged |
| 3 | Verify in output | Mismatch reported |

---

### TC-BANDS-013: Handle Missing HW Filter (Optional)

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-BANDS-021 |
| **Preconditions** | Only RFC provided |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis without HW filter | Analysis proceeds |
| 2 | Verify output | "HW filter not provided" noted |
| 3 | Verify RFC bands shown | RFC bands displayed |

---

### TC-BANDS-014: Parse Malformed HW Filter

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-BANDS-020 |
| **Preconditions** | Malformed HW filter XML |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide malformed HW filter | Error detected |
| 2 | Verify error message | Clear message shown |
| 3 | Verify RFC analysis continues | Partial analysis possible |

---

## 3. Carrier Policy Parsing Test Cases

### TC-BANDS-015: Parse Valid Carrier Policy

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-003.1 |
| **Preconditions** | Valid carrier policy XML |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide carrier policy file | File accepted |
| 2 | Run analysis | Policy parsed |
| 3 | Verify carrier bands extracted | Bands listed |

---

### TC-BANDS-016: Extract Carrier-Enabled Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-003.2 |
| **Preconditions** | Carrier policy with enabled bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse carrier policy | Parsing completes |
| 2 | Verify enabled bands | Correct list extracted |

---

### TC-BANDS-017: Handle Multiple Carrier Profiles

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-BANDS-003.3 |
| **Preconditions** | Policy with multiple profiles |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide multi-profile policy | File parsed |
| 2 | Verify all profiles processed | Each profile analyzed |
| 3 | Verify output shows profile info | Profiles listed |

---

## 4. Band Flow Tracing Test Cases

### TC-BANDS-040: Trace Bands Through All Layers

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-010.1 |
| **Preconditions** | RFC + HW + Carrier + UE Cap files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide all input files | Files accepted |
| 2 | Run analysis | Full trace executed |
| 3 | Verify each layer shown | RFC → HW → Carrier → UE Cap |

---

### TC-BANDS-041: Identify Bands Added at Each Stage

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-010.2 |
| **Preconditions** | Config with band additions |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | UE Cap has band not in RFC | Anomaly detected |
| 2 | Verify addition flagged | "Band X added" message |
| 3 | Verify in output | Highlighted as anomaly |

---

### TC-BANDS-042: Identify Bands Removed at Each Stage

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-010.3 |
| **Preconditions** | RFC band filtered by HW |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC has band 7, HW disables it | Trace shows removal |
| 2 | Verify removal point identified | "Removed at HW layer" |
| 3 | Verify in output | Clear indication |

---

### TC-BANDS-043: Calculate Final Band Set

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-010.4 |
| **Preconditions** | Multi-layer configuration |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run full analysis | Analysis completes |
| 2 | Verify final band set | Correct intersection |
| 3 | Compare with UE Cap | Match or mismatch noted |

---

## 5. Mismatch Detection Test Cases

### TC-BANDS-045: Detect RFC vs HW Filter Mismatch

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-011.1 |
| **Preconditions** | RFC and HW with different bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC: [1,3,7], HW: [1,3] | Mismatch detected |
| 2 | Verify band 7 flagged | "Band 7 in RFC but disabled by HW" |
| 3 | Verify severity | Appropriate indicator |

---

### TC-BANDS-046: Detect Carrier Policy Mismatch

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-011.2 |
| **Preconditions** | HW passes band, carrier blocks |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | HW enables band 3, carrier disables | Mismatch detected |
| 2 | Verify carrier policy flagged | Clear message |

---

### TC-BANDS-047: Detect Generic Restriction Mismatch

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-BANDS-011.3 |
| **Preconditions** | Generic restriction applied |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Band restricted by generic policy | Restriction noted |
| 2 | Verify in output | Restriction shown |

---

### TC-BANDS-048: Detect UE Capability vs Expected Mismatch

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-011.4 |
| **Preconditions** | Expected final set differs from UE Cap |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Expected: [1,3], UE Cap: [1,3,7] | Mismatch detected |
| 2 | Verify unexpected band flagged | Band 7 anomaly |
| 3 | Verify in verdict | Issue highlighted |

---

## 6. Anomaly Detection Test Cases

### TC-BANDS-050: Flag Unexpected Band Addition

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-012.1 |
| **Preconditions** | Band in UE Cap not in RFC |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | UE Cap has band not traced from RFC | Anomaly flagged |
| 2 | Verify message | "Unexpected band addition" |
| 3 | Verify severity | Warning or error |

---

### TC-BANDS-051: Flag Unexpected Band Removal

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-012.2 |
| **Preconditions** | Band expected but missing from UE Cap |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC band passes all filters but missing in UE Cap | Anomaly flagged |
| 2 | Verify message | "Unexpected band removal" |

---

### TC-BANDS-052: Identify Configuration Issues

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-012.3 |
| **Preconditions** | Conflicting configurations |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Multiple issues in config | Issues listed |
| 2 | Verify each issue described | Clear descriptions |
| 3 | Verify recommendations | Suggestions provided |

---

## 7. HTML Report Test Cases

### TC-BANDS-065: Generate HTML Report

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-021.1 |
| **Preconditions** | Analysis completed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis | HTML file generated |
| 2 | Verify file exists | band_analysis_*.html created |
| 3 | Verify file size | Non-empty file |

---

### TC-BANDS-066: Report Includes All Sections

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-021.2 |
| **Preconditions** | HTML report generated |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open HTML report | Report loads |
| 2 | Verify Summary section | Present |
| 3 | Verify LTE section | Present |
| 4 | Verify NR SA section | Present |
| 5 | Verify NR NSA section | Present |
| 6 | Verify Mismatches section | Present |

---

### TC-BANDS-067: Report Viewable Standalone

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-021.3 |
| **Preconditions** | HTML report downloaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open HTML in browser (file://) | Report renders |
| 2 | Verify CSS applied | Styled correctly |
| 3 | Verify no external dependencies | Works offline |

---

### TC-BANDS-068: Visual Indicators for Issues

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-021.4 |
| **Preconditions** | Report with mismatches |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View report with issues | Visual indicators present |
| 2 | Verify PASS styling | Green/success color |
| 3 | Verify FAIL styling | Red/error color |
| 4 | Verify WARNING styling | Yellow/warning color |

---

## 8. Claude Prompt Test Cases

### TC-BANDS-070: Generate Structured Prompt

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-022.1 |
| **Preconditions** | Analysis completed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis | Prompt file generated |
| 2 | Verify file exists | prompt_*.txt created |
| 3 | Verify structure | Proper sections |

---

### TC-BANDS-071: Prompt Includes All Data

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-022.2 |
| **Preconditions** | Prompt file generated |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open prompt file | File readable |
| 2 | Verify RFC bands included | RFC data present |
| 3 | Verify tracing data | Flow data present |
| 4 | Verify mismatches | Issues listed |

---

### TC-BANDS-072: Prompt Requests Verdict

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-022.3 |
| **Preconditions** | Prompt file generated |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open prompt file | File readable |
| 2 | Verify verdict request | "Please provide verdict" or similar |
| 3 | Verify format instructions | Response format specified |

---

## 9. LTE Band Analysis Test Cases

### TC-BANDS-080: Analyze LTE FDD Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-030.1 |
| **Preconditions** | RFC with LTE FDD bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with bands 1, 3, 7 (FDD) | Analysis runs |
| 2 | Verify FDD identification | Bands marked as FDD |
| 3 | Verify in output | FDD section populated |

---

### TC-BANDS-081: Analyze LTE TDD Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-030.2 |
| **Preconditions** | RFC with LTE TDD bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with bands 38, 40, 41 (TDD) | Analysis runs |
| 2 | Verify TDD identification | Bands marked as TDD |
| 3 | Verify in output | TDD section populated |

---

### TC-BANDS-082: Categorize Bands by Region

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-BANDS-030.3 |
| **Preconditions** | RFC with various regional bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with global and regional bands | Analysis runs |
| 2 | Verify region categorization | NA, EU, APAC, Global |
| 3 | Verify in output | Regions shown |

---

## 10. NR SA Band Analysis Test Cases

### TC-BANDS-085: Analyze NR SA Sub-6 Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-031.1 |
| **Preconditions** | RFC with NR SA Sub-6 bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with n78, n79 | Analysis runs |
| 2 | Verify Sub-6 identification | Marked as Sub-6 |
| 3 | Verify in output | NR SA section shows bands |

---

### TC-BANDS-086: Analyze NR SA mmWave Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-031.2 |
| **Preconditions** | RFC with mmWave bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with n260, n261 | Analysis runs |
| 2 | Verify mmWave identification | Marked as mmWave |
| 3 | Verify in output | mmWave section shows bands |

---

### TC-BANDS-087: Identify TDD vs FDD NR Bands

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-BANDS-031.3 |
| **Preconditions** | RFC with TDD and FDD NR bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with n78 (TDD), n71 (FDD) | Analysis runs |
| 2 | Verify duplex identification | Correctly categorized |

---

## 11. NR NSA Band Analysis Test Cases

### TC-BANDS-090: Analyze NR NSA (EN-DC) Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-032.1 |
| **Preconditions** | RFC with EN-DC combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | RFC with EN-DC combinations | Analysis runs |
| 2 | Verify combos parsed | Combinations listed |
| 3 | Verify in output | EN-DC section populated |

---

### TC-BANDS-091: Extract NR Bands from EN-DC Combos

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-032.2 |
| **Preconditions** | RFC with EN-DC combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Combo: LTE B3 + NR n78 | NR band extracted |
| 2 | Verify n78 in NR NSA list | Band listed |
| 3 | Verify unique bands | No duplicates |

---

### TC-BANDS-092: Identify Anchor LTE Bands

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-BANDS-032.3 |
| **Preconditions** | RFC with EN-DC combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Combo: LTE B3 + NR n78 | LTE anchor identified |
| 2 | Verify B3 listed as anchor | Anchor list correct |
| 3 | Verify anchor-NR mapping | Relationships shown |

---

## 12. Performance Test Cases

### TC-BANDS-100: Analysis Completes Within 30 Seconds

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-BANDS-001 |
| **Preconditions** | Standard test files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start timer | Timer running |
| 2 | Run full analysis | Analysis completes |
| 3 | Check elapsed time | < 30 seconds |

---

### TC-BANDS-101: Handle 10MB RFC File

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-BANDS-002 |
| **Preconditions** | 10MB RFC file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide 10MB RFC | File accepted |
| 2 | Run analysis | Completes without memory error |
| 3 | Verify results | Correct output |

---

## 13. Reliability Test Cases

### TC-BANDS-110: No Crash on Malformed Input

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-BANDS-020 |
| **Preconditions** | Malformed test files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide malformed RFC | Error shown |
| 2 | Provide malformed HW filter | Error shown |
| 3 | Verify no crash | Application stable |

---

### TC-BANDS-111: Handle Partial Input Gracefully

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-BANDS-021 |
| **Preconditions** | Only RFC provided |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide only RFC (no optional files) | Analysis runs |
| 2 | Verify output | RFC analysis shown |
| 3 | Verify missing files noted | Clear indication |

---

### TC-BANDS-112: Report Parsing Errors Clearly

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-BANDS-022 |
| **Preconditions** | File with parsing errors |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide file with XML errors | Error detected |
| 2 | Verify error message | Line number, error type shown |
| 3 | Verify file identified | Filename in error |

---

## 14. Test Execution Summary

| Category | Total TCs | Passed | Failed | Blocked | Not Run |
|----------|-----------|--------|--------|---------|---------|
| RFC Parsing | 9 | | | | |
| HW Filter | 5 | | | | |
| Carrier Policy | 3 | | | | |
| Band Flow Tracing | 4 | | | | |
| Mismatch Detection | 4 | | | | |
| Anomaly Detection | 3 | | | | |
| HTML Report | 4 | | | | |
| Claude Prompt | 3 | | | | |
| LTE Bands | 3 | | | | |
| NR SA Bands | 3 | | | | |
| NR NSA Bands | 3 | | | | |
| Performance | 2 | | | | |
| Reliability | 3 | | | | |
| **Total** | **49** | | | | |

---

## 15. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
