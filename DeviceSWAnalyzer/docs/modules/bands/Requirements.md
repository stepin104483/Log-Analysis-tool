# Bands Module - Requirements

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for the Bands Analysis Module, which analyzes band filtering from RF Card (RFC) through various configuration layers to final UE Capability.

### 1.2 Scope
The Bands module traces how bands are filtered at each stage of the configuration pipeline and identifies mismatches, anomalies, and potential issues.

### 1.3 Related Documents
- [Architecture.md](./Architecture.md) - Bands module architecture
- [Overall_Requirements.md](../../Overall_Requirements.md) - System requirements

---

## 2. Functional Requirements

### 2.1 Input Document Processing

#### FR-BANDS-001: RFC XML Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-001.1 | Module SHALL parse RFC XML to extract supported bands |
| FR-BANDS-001.2 | Module SHALL extract LTE bands from `eutra_band_list` |
| FR-BANDS-001.3 | Module SHALL extract NR SA bands from `nr_sa_band_list` |
| FR-BANDS-001.4 | Module SHALL extract NR NSA bands from `ca_4g_5g_combos` |
| FR-BANDS-001.5 | Module SHALL handle missing RFC file gracefully |

#### FR-BANDS-002: Hardware Band Filter Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-002.1 | Module SHALL parse HW band filter document |
| FR-BANDS-002.2 | Module SHALL extract bands enabled by hardware |
| FR-BANDS-002.3 | Module SHALL identify HW-disabled bands |

#### FR-BANDS-003: Carrier Policy Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-003.1 | Module SHALL parse carrier policy document |
| FR-BANDS-003.2 | Module SHALL extract carrier-enabled bands |
| FR-BANDS-003.3 | Module SHALL handle multiple carrier profiles |

#### FR-BANDS-004: Generic Restriction Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-004.1 | Module SHALL parse generic restriction document |
| FR-BANDS-004.2 | Module SHALL extract restricted bands |

#### FR-BANDS-005: MDB Configuration Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-005.1 | Module SHALL parse MDB configuration |
| FR-BANDS-005.2 | Module SHALL extract MDB band settings |

#### FR-BANDS-006: QXDM Log Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-006.1 | Module SHALL parse QXDM log prints |
| FR-BANDS-006.2 | Module SHALL extract runtime band information |

#### FR-BANDS-007: UE Capability Parsing
| ID | Requirement |
|----|-------------|
| FR-BANDS-007.1 | Module SHALL parse UE capability information |
| FR-BANDS-007.2 | Module SHALL extract final advertised bands |

---

### 2.2 Band Tracing

#### FR-BANDS-010: Band Flow Tracing
| ID | Requirement |
|----|-------------|
| FR-BANDS-010.1 | Module SHALL trace bands through all configuration layers |
| FR-BANDS-010.2 | Module SHALL identify bands added at each stage |
| FR-BANDS-010.3 | Module SHALL identify bands removed at each stage |
| FR-BANDS-010.4 | Module SHALL calculate final band set |

#### FR-BANDS-011: Mismatch Detection
| ID | Requirement |
|----|-------------|
| FR-BANDS-011.1 | Module SHALL detect RFC vs HW filter mismatches |
| FR-BANDS-011.2 | Module SHALL detect carrier policy mismatches |
| FR-BANDS-011.3 | Module SHALL detect generic restriction mismatches |
| FR-BANDS-011.4 | Module SHALL detect UE capability vs expected mismatches |

#### FR-BANDS-012: Anomaly Detection
| ID | Requirement |
|----|-------------|
| FR-BANDS-012.1 | Module SHALL flag unexpected band additions |
| FR-BANDS-012.2 | Module SHALL flag unexpected band removals |
| FR-BANDS-012.3 | Module SHALL identify potential configuration issues |

---

### 2.3 Analysis Output

#### FR-BANDS-020: CLI Output
| ID | Requirement |
|----|-------------|
| FR-BANDS-020.1 | Module SHALL generate human-readable CLI output |
| FR-BANDS-020.2 | Output SHALL show bands at each stage |
| FR-BANDS-020.3 | Output SHALL highlight mismatches with indicators |
| FR-BANDS-020.4 | Output SHALL use color coding for PASS/FAIL/ANOMALY |

#### FR-BANDS-021: HTML Report
| ID | Requirement |
|----|-------------|
| FR-BANDS-021.1 | Module SHALL generate HTML report |
| FR-BANDS-021.2 | Report SHALL include all analysis sections |
| FR-BANDS-021.3 | Report SHALL be viewable standalone in browser |
| FR-BANDS-021.4 | Report SHALL include visual indicators for issues |

#### FR-BANDS-022: Claude Prompt
| ID | Requirement |
|----|-------------|
| FR-BANDS-022.1 | Module SHALL generate structured prompt for Claude |
| FR-BANDS-022.2 | Prompt SHALL include all analysis data |
| FR-BANDS-022.3 | Prompt SHALL request expert review and verdict |

---

### 2.4 Band Categories

#### FR-BANDS-030: LTE Band Analysis
| ID | Requirement |
|----|-------------|
| FR-BANDS-030.1 | Module SHALL analyze LTE FDD bands |
| FR-BANDS-030.2 | Module SHALL analyze LTE TDD bands |
| FR-BANDS-030.3 | Module SHALL categorize bands by region (global, NA, EU, APAC) |

#### FR-BANDS-031: NR SA Band Analysis
| ID | Requirement |
|----|-------------|
| FR-BANDS-031.1 | Module SHALL analyze NR SA Sub-6 bands |
| FR-BANDS-031.2 | Module SHALL analyze NR SA mmWave bands |
| FR-BANDS-031.3 | Module SHALL identify TDD vs FDD NR bands |

#### FR-BANDS-032: NR NSA Band Analysis
| ID | Requirement |
|----|-------------|
| FR-BANDS-032.1 | Module SHALL analyze NR NSA (EN-DC) bands |
| FR-BANDS-032.2 | Module SHALL extract NR bands from EN-DC combos |
| FR-BANDS-032.3 | Module SHALL identify anchor LTE bands |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement |
|----|-------------|
| NFR-BANDS-001 | Analysis SHALL complete within 30 seconds |
| NFR-BANDS-002 | Module SHALL handle RFC files up to 10MB |
| NFR-BANDS-003 | Module SHALL process multiple input files efficiently |

### 3.2 Usability

| ID | Requirement |
|----|-------------|
| NFR-BANDS-010 | Output SHALL be readable by non-experts |
| NFR-BANDS-011 | Error messages SHALL indicate which file has issues |
| NFR-BANDS-012 | Module SHALL provide helpful messages for missing files |

### 3.3 Reliability

| ID | Requirement |
|----|-------------|
| NFR-BANDS-020 | Module SHALL not crash on malformed input |
| NFR-BANDS-021 | Module SHALL handle partial input gracefully |
| NFR-BANDS-022 | Module SHALL report parsing errors clearly |

---

## 4. Input Requirements

### 4.1 Required Inputs

| Input | File Pattern | Required | Description |
|-------|--------------|----------|-------------|
| RFC XML | `*rfc*.xml`, `*RFC*.xml` | Yes | RF Card configuration |

### 4.2 Optional Inputs

| Input | File Pattern | Description |
|-------|--------------|-------------|
| HW Band Filter | `*hw*.xml`, `*band*filter*.xml` | Hardware band settings |
| Carrier Policy | `*carrier*.xml`, `*policy*.xml` | Carrier-specific bands |
| Generic Restriction | `*generic*.xml`, `*restriction*.xml` | Generic restrictions |
| MDB Config | `*mdb*.xml` | MDB configuration |
| QXDM Logs | `*.txt` | QXDM log output |
| UE Capability | `*uecap*.xml`, `*capability*.xml` | UE capability info |

### 4.3 Knowledge Base Files

| File | Description |
|------|-------------|
| Band reference | Standard band definitions |
| Region mappings | Band-to-region mappings |

---

## 5. Output Requirements

### 5.1 Output Files

| File | Format | Description |
|------|--------|-------------|
| `band_analysis_<timestamp>.html` | HTML | Stage 1 analysis report |
| `prompt_<timestamp>.txt` | Text | Claude prompt file |
| `band_analysis_final_<timestamp>.html` | HTML | Final report with AI review |

### 5.2 Output Sections

| Section | Description |
|---------|-------------|
| Summary | Overview of analysis results |
| LTE Band Analysis | LTE band tracing results |
| NR SA Band Analysis | NR SA band tracing results |
| NR NSA Band Analysis | NR NSA band tracing results |
| Mismatches | Detected mismatches list |
| Claude Expert Review | AI analysis (Stage 2) |
| Verdict | Final assessment |

---

## 6. Test Requirements

| ID | Requirement |
|----|-------------|
| TEST-001 | Module SHALL be tested with sample RFC files |
| TEST-002 | Module SHALL be tested with partial inputs |
| TEST-003 | Module SHALL be tested with malformed inputs |
| TEST-004 | Output SHALL be validated against expected results |

---

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-13 | Migrated to modular architecture |
| 1.0 | 2026-01-07 | Initial requirements |
