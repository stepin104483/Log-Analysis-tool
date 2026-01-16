# Combos Module Test Cases

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TC-COMBOS |
| **Version** | 1.0 |
| **Created** | 2026-01-16 |
| **Related Test Plan** | TP-COMBOS-001 |

---

## 1. RFC Parsing Test Cases

### TC-COMBOS-001: Parse Valid RFC XML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.1 |
| **Preconditions** | Valid RFC XML file available |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide valid RFC XML file to analyzer | File is accepted |
| 2 | Run analysis | Parsing completes without errors |
| 3 | Verify combos extracted | Combo lists populated correctly |

---

### TC-COMBOS-002: Extract LTE CA Combos from ca_combos_list

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.2 |
| **Preconditions** | RFC with ca_combos_list section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with LTE CA combos 1A-3A, 1A-7A | Parsing completes |
| 2 | Verify extracted combos | 1A-3A, 1A-7A extracted |
| 3 | Verify combo type | ComboType.LTE_CA assigned |

---

### TC-COMBOS-003: Extract EN-DC Combos from ca_4g_5g_combos

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.3 |
| **Preconditions** | RFC with EN-DC combo section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with EN-DC combo 66A-n77A | Parsing completes |
| 2 | Verify LTE anchor band extracted | Band 66 identified as LTE |
| 3 | Verify NR band extracted | Band n77 identified as NR |
| 4 | Verify combo type | ComboType.ENDC assigned |

---

### TC-COMBOS-004: Extract NRCA Combos from nr_ca_combos_list

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.4 |
| **Preconditions** | RFC with nr_ca_combos_list section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with NR CA combo n77A-n78A | Parsing completes |
| 2 | Verify NR bands extracted | n77, n78 extracted |
| 3 | Verify combo type | ComboType.NRCA assigned |

---

### TC-COMBOS-005: Extract NR-DC Combos from nr_dc_combos_list

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-001.5 |
| **Preconditions** | RFC with nr_dc_combos_list section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with NR-DC combos | Parsing completes |
| 2 | Verify combos extracted | NR-DC combos listed |
| 3 | Verify combo type | ComboType.NRDC assigned |

---

### TC-COMBOS-006: Handle Missing RFC File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.6 |
| **Preconditions** | No RFC file provided |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis without RFC file | Error message displayed |
| 2 | Verify error message | Clear "file not found" message |
| 3 | Verify no crash | Application remains stable |

---

### TC-COMBOS-007: Handle Malformed RFC XML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-001.7, NFR-COMBOS-010 |
| **Preconditions** | Malformed XML file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide malformed XML file | Error detected |
| 2 | Verify error message | Clear XML parsing error |
| 3 | Verify no crash | Application stable |

---

### TC-COMBOS-008: Parse RFC with Empty Combo Lists

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-001.1, NFR-COMBOS-011 |
| **Preconditions** | RFC with empty combo sections |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with empty combo lists | Parsing completes |
| 2 | Verify output | Empty combo sets reported |
| 3 | Verify no crash | Analysis continues |

---

### TC-COMBOS-009: Parse Large RFC File (20MB)

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-COMBOS-002 |
| **Preconditions** | RFC file ~20MB |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide 20MB RFC file | File accepted |
| 2 | Run analysis | Completes within timeout |
| 3 | Verify results | Combos extracted correctly |

---

## 2. QXDM Parsing Test Cases

### TC-COMBOS-010: Parse QXDM 0xB826 Log Output

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-002.1 |
| **Preconditions** | Valid QXDM 0xB826 log file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide QXDM log file | File accepted |
| 2 | Run parsing | Combos extracted |
| 3 | Verify combo count | Matches log content |

---

### TC-COMBOS-011: Parse Structured Table Format

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-002.2 |
| **Preconditions** | QXDM log with structured table |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse log with table format (columns) | Format detected |
| 2 | Verify bands extracted from columns | Correct band list |
| 3 | Verify BCS extracted | BCS values captured |

---

### TC-COMBOS-012: Parse Raw Combo String Format

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-002.3 |
| **Preconditions** | QXDM log with raw strings like "66A+n77A" |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse log with combo strings | Strings parsed |
| 2 | Verify + separator handled | Bands separated correctly |
| 3 | Verify DC_ prefix handled | DC notation recognized |

---

### TC-COMBOS-013: Extract BCS Values

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-002.4 |
| **Preconditions** | QXDM log with BCS values |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse log with BCS column | BCS values extracted |
| 2 | Verify BCS attached to combos | Combo.bcs populated |
| 3 | Verify multiple BCS per combo | Set of BCS values |

---

### TC-COMBOS-014: Identify Combo Type from QXDM

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-002.5 |
| **Preconditions** | QXDM log with mixed combo types |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse log with LTE CA combos | Type = LTE_CA |
| 2 | Parse log with EN-DC combos | Type = ENDC |
| 3 | Parse log with NR CA combos | Type = NRCA |

---

### TC-COMBOS-015: Handle Empty QXDM File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-002.6 |
| **Preconditions** | Empty or missing QXDM file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide empty QXDM file | No crash |
| 2 | Verify result | Empty combo set |
| 3 | Run without QXDM file | Analysis continues |

---

### TC-COMBOS-016: Parse QXDM with Labeled Combos

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-002.1 |
| **Preconditions** | QXDM log with "LTE CA:" labels |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse log with "LTE CA: 1A-3A" format | Labels recognized |
| 2 | Verify combos extracted | Correct parsing |
| 3 | Verify type from label | Type assigned correctly |

---

## 3. UE Capability Parsing Test Cases

### TC-COMBOS-020: Parse ASN.1 XML Export

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.1 |
| **Preconditions** | Valid UE Capability ASN.1 XML |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide UE Capability XML | File accepted |
| 2 | Run parsing | Combos extracted |
| 3 | Verify no errors | Clean parse |

---

### TC-COMBOS-021: Extract LTE CA from EUTRA-Capability

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.2 |
| **Preconditions** | XML with EUTRA-Capability section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with eutra_capability | LTE CA combos extracted |
| 2 | Verify bands from bandEUTRA elements | Correct bands |
| 3 | Verify combo type | ComboType.LTE_CA |

---

### TC-COMBOS-022: Extract EN-DC from UE-MRDC-Capability

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.3 |
| **Preconditions** | XML with UE-MRDC-Capability section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with mrdc_capability | EN-DC combos extracted |
| 2 | Verify LTE and NR components | Both identified |
| 3 | Verify combo type | ComboType.ENDC |

---

### TC-COMBOS-023: Extract NRCA from UE-NR-Capability

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.4 |
| **Preconditions** | XML with UE-NR-Capability section |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with nr_capability | NR CA combos extracted |
| 2 | Verify bands from bandNR elements | Correct NR bands |
| 3 | Verify combo type | ComboType.NRCA |

---

### TC-COMBOS-024: Parse supportedBandCombination-r10 Format

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.5 |
| **Preconditions** | XML with r10 format |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse r10 format XML | Format recognized |
| 2 | Verify BandCombinationParameters-r10 parsed | Parameters extracted |
| 3 | Verify bands from bandParametersDL-r10 | Correct bands |

---

### TC-COMBOS-025: Parse supportedBandCombinationList Format

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-003.6 |
| **Preconditions** | XML with BandCombinationList |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse list format XML | Format recognized |
| 2 | Verify BandCombination elements | Elements parsed |
| 3 | Verify bands extracted | Correct combos |

---

### TC-COMBOS-026: Extract Supported Bands List

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-003.7 |
| **Preconditions** | UE Capability with band lists |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse UE capability file | File parsed |
| 2 | Call get_supported_bands() | Returns band dict |
| 3 | Verify LTE and NR bands separated | Correct categorization |

---

### TC-COMBOS-027: Handle Invalid UE Capability XML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-COMBOS-010 |
| **Preconditions** | Malformed UE Cap XML |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide invalid XML | Error detected |
| 2 | Verify error recorded | get_parse_errors() returns errors |
| 3 | Verify no crash | Parser stable |

---

## 4. EFS Parsing Test Cases

### TC-COMBOS-030: Parse prune_ca_combos File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-004.1 |
| **Preconditions** | Valid prune_ca_combos file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide prune_ca_combos file | File parsed |
| 2 | Verify pruned combos extracted | Combo list populated |
| 3 | Verify format: 66A-2A; | Semicolon separator handled |

---

### TC-COMBOS-031: Parse ca_disable Binary Flag

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-004.2 |
| **Preconditions** | ca_disable binary file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with 0x01 | CA disabled = True |
| 2 | Parse file with 0x00 | CA disabled = False |

---

### TC-COMBOS-032: Parse cap_control_nrca_enabled

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-004.3 |
| **Preconditions** | cap_control_nrca_enabled file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with 0x01 | NRCA enabled = True |
| 2 | Parse file with 0x00 | NRCA enabled = False |

---

### TC-COMBOS-033: Parse cap_control_nrdc_enabled

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-004.4 |
| **Preconditions** | cap_control_nrdc_enabled file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file | Flag value extracted |
| 2 | Verify NRDC state | Correct enable/disable |

---

### TC-COMBOS-034: Parse prune_ca_combos with BCS

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-004.5 |
| **Preconditions** | prune_ca_combos with BCS values |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with "66A-2A-0;" format | BCS extracted |
| 2 | Verify BCS value | bcs=0 for combo |
| 3 | Test is_combo_pruned with BCS | BCS-specific check works |

---

### TC-COMBOS-035: Handle Missing EFS Files

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-004.6 |
| **Preconditions** | Non-existent EFS directory |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse non-existent directory | No crash |
| 2 | Verify result | Empty pruned set |
| 3 | Verify defaults | CA enabled, NRCA/NRDC enabled |

---

## 5. Normalization Test Cases

### TC-COMBOS-040: Normalize Combo Keys

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-005.1 |
| **Preconditions** | Combos with various formats |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Normalize "1a-3a" | Returns "1A-3A" |
| 2 | Normalize "3A-1A" | Returns "1A-3A" (sorted) |
| 3 | Verify identical keys | Same combos = same key |

---

### TC-COMBOS-041: Sort Band Components Consistently

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-005.2 |
| **Preconditions** | Combos with unordered bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Normalize "7A-3A-1A" | Returns "1A-3A-7A" |
| 2 | Verify LTE before NR in EN-DC | LTE bands first |
| 3 | Verify numeric sorting | Lower band numbers first |

---

### TC-COMBOS-042: Uppercase Band Class Letters

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-005.3 |
| **Preconditions** | Combos with lowercase class |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Normalize "1a-3b" | Returns "1A-3B" |
| 2 | Normalize "n77a" | Returns "N77A" |

---

### TC-COMBOS-043: Distinguish LTE and NR Bands in EN-DC

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-005.4 |
| **Preconditions** | EN-DC combo |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse "66A-n77A" | LTE=66A, NR=n77A |
| 2 | Verify lte_components | [66A] |
| 3 | Verify nr_components | [n77A] |

---

### TC-COMBOS-044: Handle BCS Value Normalization

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-005.5 |
| **Preconditions** | Combos with BCS |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Normalize BCS set {0, 1, 2} | Valid values kept |
| 2 | Normalize BCS with invalid | Invalid filtered |
| 3 | Normalize None BCS | None preserved |

---

## 6. Comparison Test Cases

### TC-COMBOS-050: Compare RFC vs QXDM (RRC Table)

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.1 |
| **Preconditions** | RFC and QXDM files with combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse RFC with combos A, B, C | RFC combos loaded |
| 2 | Parse QXDM with combos A, B | QXDM combos loaded |
| 3 | Run comparison | C identified as missing |

---

### TC-COMBOS-051: Compare QXDM vs UE Capability

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.2 |
| **Preconditions** | QXDM and UE Cap files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse QXDM with combos A, B | QXDM loaded |
| 2 | Parse UE Cap with combos A | UE Cap loaded |
| 3 | Run comparison | B missing in UE Cap |

---

### TC-COMBOS-052: Identify Missing Combos

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.3 |
| **Preconditions** | Sources with differences |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Compare sources | only_in_a populated |
| 2 | Verify discrepancy type | MISSING_IN_RRC or MISSING_IN_UECAP |

---

### TC-COMBOS-053: Identify Extra Combos

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.4 |
| **Preconditions** | Target has extra combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Compare sources | only_in_b populated |
| 2 | Verify discrepancy type | EXTRA_IN_RRC or EXTRA_IN_UECAP |

---

### TC-COMBOS-054: Calculate Match Percentage

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.5 |
| **Preconditions** | Known combo counts |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Source A: 10 combos, B: 8 combos, 6 common | Calculate match |
| 2 | Verify percentage | match_percentage calculated correctly |

---

### TC-COMBOS-055: Compare by Combo Type

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.6 |
| **Preconditions** | Mixed combo types |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Compare with LTE CA and EN-DC | Separate results per type |
| 2 | Verify LTE CA comparison | LTE_CA results |
| 3 | Verify EN-DC comparison | ENDC results |

---

## 7. Knowledge Base Test Cases

### TC-COMBOS-060: Load Band Restrictions from YAML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-007.1 |
| **Preconditions** | YAML file with band_restrictions |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load YAML with band 71 restriction | KB loaded |
| 2 | Query get_band_restrictions(71) | Returns restriction |
| 3 | Verify reason text | Correct reason |

---

### TC-COMBOS-061: Load Carrier Policies from YAML

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-007.2 |
| **Preconditions** | YAML with carrier policy |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load YAML with carrier: Verizon | KB loaded |
| 2 | Query get_carrier_requirement("Verizon") | Returns policy |
| 3 | Verify required_combos | List populated |

---

### TC-COMBOS-062: Regional Band Restrictions

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-007.3 |
| **Preconditions** | YAML with regional restrictions |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load APAC regional restrictions | KB loaded |
| 2 | Check band 71 restricted | is_band_restricted(71) = True |
| 3 | Check band 66 not restricted | is_band_restricted(66) = False |

---

### TC-COMBOS-063: Regulatory Band Restrictions

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-007.4 |
| **Preconditions** | YAML with regulatory type |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load regulatory restriction for band 14 | KB loaded |
| 2 | Query restriction type | restriction_type = "regulatory" |

---

### TC-COMBOS-064: Hardware Variant Restrictions

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-007.5 |
| **Preconditions** | YAML with hw_variant restrictions |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load mmWave band restrictions | KB loaded |
| 2 | Check band 260 restricted | Restriction found |
| 3 | Verify reason | "requires mmWave RF module" |

---

### TC-COMBOS-065: Carrier-Specific Exclusions

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-007.6 |
| **Preconditions** | YAML with excluded_combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load carrier policy with exclusions | KB loaded |
| 2 | Query excluded_combos | Set populated |
| 3 | Verify specific combo excluded | Combo in set |

---

### TC-COMBOS-066: Carrier-Required Combos

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-007.7 |
| **Preconditions** | YAML with required_combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load carrier policy with requirements | KB loaded |
| 2 | Query required_combos | Set populated |
| 3 | Verify specific combo required | Combo in set |

---

## 8. Reasoning Engine Test Cases

### TC-COMBOS-070: Explain Discrepancy Using Knowledge Base

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.1 |
| **Preconditions** | KB loaded, discrepancy with restricted band |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create discrepancy with band 71 | Discrepancy created |
| 2 | Call explain_discrepancy() | ReasoningResult returned |
| 3 | Verify has_explanation | True |
| 4 | Verify explanation text | Contains band 71 reason |

---

### TC-COMBOS-071: Detect EFS Pruning as Explanation

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.2 |
| **Preconditions** | Discrepancy with PRUNED_BY_EFS type |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create PRUNED_BY_EFS discrepancy | Discrepancy created |
| 2 | Call explain_discrepancy() | Result returned |
| 3 | Verify reason_type | "efs" |
| 4 | Verify severity | "expected" |

---

### TC-COMBOS-072: Detect Band Restrictions as Explanation

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.3 |
| **Preconditions** | KB with band restriction loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create discrepancy with restricted band | Discrepancy created |
| 2 | Call explain_discrepancy() | Result returned |
| 3 | Verify reason_type | "regional" or "regulatory" |
| 4 | Verify has_explanation | True |

---

### TC-COMBOS-073: Detect Carrier Exclusions as Explanation

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.4 |
| **Preconditions** | KB with carrier exclusion, active carrier set |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Set active carrier | Context updated |
| 2 | Create discrepancy with excluded combo | Discrepancy created |
| 3 | Call explain_discrepancy() | Exclusion detected |
| 4 | Verify reason_type | "carrier_exclusion" |

---

### TC-COMBOS-074: Apply mmWave Heuristics

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-008.5 |
| **Preconditions** | Discrepancy with band 260 (mmWave) |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create discrepancy with n260 | Discrepancy created |
| 2 | Call explain_discrepancy() | Result returned |
| 3 | Verify explanation | Contains "mmwave" |
| 4 | Verify severity | "low" or "expected" |

---

### TC-COMBOS-075: Apply Band 14 (FirstNet) Heuristics

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-008.6 |
| **Preconditions** | Discrepancy with band 14 |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create discrepancy with band 14 | Discrepancy created |
| 2 | Call explain_discrepancy() | Result returned |
| 3 | Verify explanation | Contains "14" or "firstnet" |

---

### TC-COMBOS-076: Assign Severity Levels

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.7 |
| **Preconditions** | Various discrepancy types |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | EFS pruned discrepancy | severity = "expected" |
| 2 | Band restriction discrepancy | severity = "expected" or "low" |
| 3 | Unknown discrepancy | severity = "high" |

---

### TC-COMBOS-077: Categorize by Severity

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.8 |
| **Preconditions** | Multiple enriched discrepancies |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enrich list of discrepancies | All have severity |
| 2 | Call categorize_by_severity() | Dict returned |
| 3 | Verify keys | "expected", "low", "medium", "high" |

---

## 9. HTML Report Test Cases

### TC-COMBOS-080: Generate HTML Analysis Report

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.1 |
| **Preconditions** | AnalysisResult with data |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Generate HTML report | HTML string returned |
| 2 | Verify HTML structure | Valid HTML5 document |
| 3 | Save to file | File created |

---

### TC-COMBOS-081: Report Includes Summary Dashboard

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.2 |
| **Preconditions** | Generated HTML report |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check report content | Contains "Summary" section |
| 2 | Verify status banner | Status displayed |
| 3 | Verify stat cards | RFC, RRC, UE Cap counts shown |

---

### TC-COMBOS-082: Report Includes Combo Statistics

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.3 |
| **Preconditions** | Generated HTML report |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check statistics | Combo counts displayed |
| 2 | Verify by type | LTE CA, EN-DC counts shown |
| 3 | Verify totals | Total discrepancies count |

---

### TC-COMBOS-083: Report Includes Match Percentage Bars

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.4 |
| **Preconditions** | Generated HTML report |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check for progress bars | Progress elements present |
| 2 | Verify RFC vs RRC match | Percentage shown |
| 3 | Verify RRC vs UE Cap match | Percentage shown |

---

### TC-COMBOS-084: Report Includes Discrepancy Tables

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.5 |
| **Preconditions** | Report with discrepancies |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check discrepancy section | Tables present |
| 2 | Verify columns | Combo, Type, Severity columns |
| 3 | Verify row styling | Severity colors applied |

---

### TC-COMBOS-085: Report Includes Reasoning Column

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.6 |
| **Preconditions** | Report with reasoned discrepancies |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check discrepancy table | Explanation column present |
| 2 | Verify explanations | Text shown for explained items |
| 3 | Verify reason badges | Reason type badges displayed |

---

### TC-COMBOS-086: Report Includes Severity Distribution

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-010.7 |
| **Preconditions** | Report with reasoning |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check reasoning section | Severity cards present |
| 2 | Verify severity counts | expected, low, high counts |
| 3 | Verify explanation rate | Percentage shown |

---

### TC-COMBOS-087: Report Supports Collapsible Sections

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-COMBOS-010.8 |
| **Preconditions** | Generated HTML report |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check for toggle buttons | Buttons present |
| 2 | Click toggle | Section expands/collapses |
| 3 | Verify JavaScript | toggleTable function present |

---

## 10. Claude Prompt Test Cases

### TC-COMBOS-090: Generate Claude AI Prompt

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-011.1 |
| **Preconditions** | AnalysisResult available |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Generate prompt | Text returned |
| 2 | Verify structure | Markdown formatted |

---

### TC-COMBOS-091: Prompt Includes All Comparison Data

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-011.2 |
| **Preconditions** | Generated prompt |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check for combo counts | Counts included |
| 2 | Check for discrepancies | Discrepancy list included |
| 3 | Check for match rates | Percentages included |

---

### TC-COMBOS-092: Prompt Requests Expert Analysis

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-011.3 |
| **Preconditions** | Generated prompt |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Check for analysis request | Request for verdict |
| 2 | Check for output format | JSON format requested |
| 3 | Check for recommendations | Recommendation request |

---

## 11. Performance Test Cases

### TC-COMBOS-100: Analysis Completes Within 60 Seconds

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-COMBOS-001 |
| **Preconditions** | Typical-sized input files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start timer | Time recorded |
| 2 | Run full analysis | Analysis completes |
| 3 | Check elapsed time | < 60 seconds |

---

### TC-COMBOS-101: Handle RFC Files up to 20MB

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-COMBOS-002 |
| **Preconditions** | 20MB RFC XML file |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide 20MB file | File accepted |
| 2 | Run analysis | Parsing completes |
| 3 | Verify results | Correct extraction |

---

### TC-COMBOS-103: Handle >1000 Combos Per Source

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-COMBOS-004 |
| **Preconditions** | Files with 1000+ combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Parse file with 1000+ combos | All combos extracted |
| 2 | Run comparison | Comparison completes |
| 3 | Generate report | Report handles large data |

---

## 12. Reliability Test Cases

### TC-COMBOS-110: No Crash on Malformed Input

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-COMBOS-010 |
| **Preconditions** | Various malformed files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide invalid RFC XML | Error reported, no crash |
| 2 | Provide invalid QXDM | Error reported, no crash |
| 3 | Provide invalid UE Cap | Error reported, no crash |

---

### TC-COMBOS-111: Handle Partial Input Gracefully

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-COMBOS-011 |
| **Preconditions** | Only RFC file provided |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run with RFC only | Analysis proceeds |
| 2 | Verify RFC combos | RFC data available |
| 3 | Verify comparison | Partial comparison (RFC only) |

---

### TC-COMBOS-112: Report Parsing Errors Clearly

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-COMBOS-012 |
| **Preconditions** | File with parsing error |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide file with errors | Parsing attempted |
| 2 | Check error messages | Clear error description |
| 3 | Verify file indicated | Filename in error message |

---

## 13. Integration Test Cases

### TC-COMBOS-120: End-to-End Three-Source Analysis

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-006.1, FR-COMBOS-006.2 |
| **Preconditions** | RFC, QXDM, UE Cap files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Provide all three files | Files accepted |
| 2 | Run CombosOrchestrator.analyze() | Analysis completes |
| 3 | Verify rfc_vs_rrc results | Comparison populated |
| 4 | Verify rrc_vs_uecap results | Comparison populated |
| 5 | Verify HTML report generated | Report file created |

---

### TC-COMBOS-121: Analysis with Knowledge Base Integration

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-008.1 |
| **Preconditions** | Files + KB YAML files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis with KB | KB loaded |
| 2 | Verify discrepancies enriched | Explanations added |
| 3 | Verify severity assigned | Severity levels set |

---

### TC-COMBOS-122: Analysis with EFS Integration

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-COMBOS-004.1, FR-COMBOS-008.2 |
| **Preconditions** | Files + EFS prune_ca_combos |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis with EFS path | EFS parsed |
| 2 | Verify pruned combos detected | PRUNED_BY_EFS type |
| 3 | Verify explanation | EFS explanation applied |

---

## 14. E2E Test Cases

### TC-COMBOS-130: Web UI Full Workflow

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | All |
| **Preconditions** | Flask server running |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to /combos page | Page loads |
| 2 | Upload RFC and QXDM files | Files accepted |
| 3 | Click Analyze | Analysis runs |
| 4 | Verify results page | Results displayed |
| 5 | Download HTML report | Report downloads |

---

### TC-COMBOS-131: E2E LTE CA Analysis

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | COMBOS-F12 |
| **Preconditions** | LTE CA test files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload LTE CA RFC | File accepted |
| 2 | Upload LTE CA QXDM | File accepted |
| 3 | Run analysis | LTE CA combos compared |
| 4 | Verify report | LTE CA section present |

---

### TC-COMBOS-132: E2E EN-DC Analysis

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | COMBOS-F13 |
| **Preconditions** | EN-DC test files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload EN-DC RFC | File accepted |
| 2 | Upload EN-DC QXDM | File accepted |
| 3 | Run analysis | EN-DC combos compared |
| 4 | Verify report | EN-DC section present |

---

## 15. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-16 | DeviceSWAnalyzer Team | Initial version |
