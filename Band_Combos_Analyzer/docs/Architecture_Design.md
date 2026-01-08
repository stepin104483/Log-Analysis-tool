# Bands & Combos Analyzer Tool - Architecture Design

## 1. Overview

A tool to analyze band filtering from RF Card (RFC) through various configuration layers to final UE Capability, with **two-stage analysis**:
1. **Automated Code Logic** - Parses documents, compares bands, detects mismatches
2. **Claude AI Review** - Validates findings, explains anomalies, adds expert insights

---

## 2. User Interface Design

Based on reference design: `requirements/Basic_design_Image.jfif`

```
+-------------------------------------------------------------------------+
|                      BANDS & COMBOS ANALYZER TOOL                       |
+-------------------------------------------------------------------------+
|                                                                         |
|  INPUT DOCUMENTS                                OUTPUT                  |
|  +--------------------------------+            +--------------------+   |
|  | 1. RFC XML             [Browse]|            |                    |   |
|  +--------------------------------+            |  ANALYSIS REPORT   |   |
|  | 2. HW Band Filter      [Browse]|            |  (Console Display) |   |
|  +--------------------------------+            |                    |   |
|  | 3. Carrier Policy      [Browse]|  [ANALYZE] |  +- Code Analysis  |   |
|  +--------------------------------+     ||     |  +- Claude Review  |   |
|  | 4. Generic Restriction [Browse]|     \/     |  +- Final Verdict  |   |
|  +--------------------------------+            |                    |   |
|  | 5. MDB Config          [Browse]|            +--------------------+   |
|  +--------------------------------+                                     |
|  | 6. QXDM Log Prints     [Browse]|            [Download HTML Report]   |
|  +--------------------------------+                                     |
|  | 7. UE Capability Info  [Browse]|                                     |
|  +--------------------------------+                                     |
+-------------------------------------------------------------------------+
```

---

## 3. Three-Stage Analysis Architecture

### 3.1 High-Level Flow

```
+-----------------------------------------------------------------------------+
|                         BAND ANALYZER TOOL                                  |
+-----------------------------------------------------------------------------+
|                                                                             |
|   STAGE 1: Python          STAGE 2: Claude CLI       STAGE 3: Report Gen   |
|   +------------------+     +------------------+     +--------------------+  |
|   |                  |     |                  |     |                    |  |
|   | Input Documents  |     | claude -p \      |     | Merge Stage 1 +    |  |
|   |       |          |     |   --dangerously- |     | Stage 2 outputs    |  |
|   |       v          |     |   skip-perms     |     |       |            |  |
|   | Parsers + Tracer | --> |   < prompt.txt   | --> | Generate final     |  |
|   |       |          |     |       |          |     | HTML report        |  |
|   |       v          |     |       v          |     |                    |  |
|   | prompt.txt       |     | claude_review    |     | report.html        |  |
|   | (analysis)       |     | .txt             |     | (integrated)       |  |
|   +------------------+     +------------------+     +--------------------+  |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### 3.2 Detailed Architecture

```
+-----------------------------------------------------------------------------+
|                              STAGE 1: PYTHON CODE                           |
+-----------------------------------------------------------------------------+
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                      INPUT DOCUMENTS                                 |   |
|   |  RFC | HW Filter | Carrier Policy | Generic | MDB | QXDM | UE Cap   |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                    |
|                                        v                                    |
|   +---------------------------------------------------------------------+   |
|   |                           PARSERS                                    |   |
|   |  RFC | HW Filter | Carrier Policy | Generic | MDB | QXDM | UE Cap   |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                    |
|                                        v                                    |
|   +---------------------------------------------------------------------+   |
|   |                      BAND TRACER ENGINE                              |   |
|   |  - Compare band sets at each stage                                   |   |
|   |  - Identify PASS / FAIL / ANOMALY                                    |   |
|   |  - Generate raw analysis data                                        |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                    |
|                                        v                                    |
|   +---------------------------------------------------------------------+   |
|   |                    PROMPT GENERATOR                                  |   |
|   |  - Format raw analysis as structured prompt                          |   |
|   |  - Include document context                                          |   |
|   |  - Add instructions for Claude review                                |   |
|   |  - Output: prompt.txt                                                |   |
|   +---------------------------------------------------------------------+   |
|                                        |                                    |
+----------------------------------------|------------------------------------+
                                         |
                                         v
                                  [ prompt.txt ]
                                         |
                                         v
+-----------------------------------------------------------------------------+
|                           STAGE 2: CLAUDE CLI                               |
+-----------------------------------------------------------------------------+
|                                                                             |
|   Command: claude -p --dangerously-skip-permissions < prompt.txt            |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                    CLAUDE'S REVIEW                                   |   |
|   |  - Validate automated findings                                       |   |
|   |  - Explain WHY bands are filtered (domain knowledge)                 |   |
|   |  - Identify root causes of anomalies                                 |   |
|   |  - Catch edge cases code might miss                                  |   |
|   |  - Provide actionable recommendations                                |   |
|   +---------------------------------------------------------------------+   |
|                                        |                                    |
|                                        v                                    |
|   +---------------------------------------------------------------------+   |
|   |                      FINAL OUTPUT                                    |   |
|   |       +-------------------+       +-------------------+              |   |
|   |       |  CONSOLE OUTPUT   |       |   HTML REPORT     |              |   |
|   |       |  (Display)        |       |   (Download)      |              |   |
|   |       +-------------------+       +-------------------+              |   |
|   +---------------------------------------------------------------------+   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### 3.3 Execution Flow

```bash
# Stage 1: Run Python tool to generate prompt and initial analysis
python -m src.main --rfc rfc.xml --hw-filter hw_filter.xml ...
# Output: output/prompt.txt

# Stage 2: Pipe prompt to Claude CLI for expert review
claude -p --dangerously-skip-permissions < output/prompt.txt > output/claude_review.txt
# Output: output/claude_review.txt

# Stage 3: Generate integrated HTML report with Claude's review embedded
python -m src.merge_report
# Output: output/band_analysis_report.html (contains both Stage 1 + Stage 2)
```

### 3.4 Integrated Report Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        run_analysis.bat                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [STAGE 1] Python Analysis                                              │
│      │                                                                  │
│      ├──► output/prompt.txt (analysis data for Claude)                  │
│      │                                                                  │
│  [STAGE 2] Claude CLI Review                                            │
│      │                                                                  │
│      ├──► output/claude_review.txt (expert insights)                    │
│      │                                                                  │
│  [STAGE 3] Report Generator                                             │
│      │                                                                  │
│      └──► output/band_analysis_report.html                              │
│           ┌─────────────────────────────────────────┐                   │
│           │  INTEGRATED HTML REPORT                 │                   │
│           │  ├── Document Status                    │                   │
│           │  ├── Summary Statistics                 │                   │
│           │  ├── Band Tracing Tables                │                   │
│           │  ├── Anomalies Detected                 │                   │
│           │  └── Claude's Expert Review  ◄──────────│── Embedded!       │
│           └─────────────────────────────────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Input Files (All Optional - Independent Layers)

**Key Design Principle:** All document inputs are **OPTIONAL**. The tool analyzes whatever documents are provided and clearly indicates what's missing and its impact.

| # | Document | File Type | Purpose | If Missing - Impact |
|---|----------|-----------|---------|---------------------|
| 1 | **RFC** | XML | RF Card supported bands (source of truth) | Cannot verify hardware capability |
| 2 | **HW Band Filtering** | XML | Hardware-level band restrictions | HW filter stage skipped |
| 3 | **Carrier Policy** | XML | Operator-specific band rules | Carrier filter stage skipped |
| 4 | **Generic Restrictions** | XML | Regulatory restrictions (FCC, etc.) | Regulatory filter stage skipped |
| 5 | **MCFG NV Config** | XML | NV band preference bitmasks (SW filtering) | NV band pref stage skipped |
| 6 | **MDB Config** | XML/MDB | MCC-based info (**Context for Claude only - NOT used in filtering**) | Claude lacks location context |
| 7 | **QXDM Log Prints** | TXT/Log | 0x1CCA PM RF Band logs | Cannot verify actual device state |
| 8 | **UE Capability Info** | TXT/Log | Final bands reported to network | Cannot verify network-reported bands |

### 4.1 Independent Layer Design

```
+------------------------------------------------------------------+
|                    INDEPENDENT LAYERS                             |
+------------------------------------------------------------------+
|                                                                   |
|  Each layer operates INDEPENDENTLY:                               |
|                                                                   |
|  [RFC]     --> If missing: "RFC not provided - using other       |
|                sources as reference"                              |
|                                                                   |
|  [HW Filter] --> If missing: "HW Filter skipped - cannot verify  |
|                  hardware restrictions"                           |
|                                                                   |
|  [Carrier]  --> If missing: "Carrier Policy skipped - cannot     |
|                 verify operator restrictions"                     |
|                                                                   |
|  [Generic]  --> If missing: "Generic Restrictions skipped"       |
|                                                                   |
|  [MCFG NV]  --> If missing: "NV Band Pref skipped - cannot       |
|                 verify SW band preferences"                       |
|                                                                   |
|  [MDB]      --> If missing: "MDB not provided - Claude lacks     |
|                 location context" (NOT used in filtering)         |
|                                                                   |
|  [QXDM]     --> If missing: "QXDM logs not provided - cannot     |
|                 verify actual device bands"                       |
|                                                                   |
|  [UE Cap]   --> If missing: "UE Capability not provided -        |
|                 cannot verify network-reported bands"             |
|                                                                   |
+------------------------------------------------------------------+
```

### 4.2 Missing Document Report

When documents are missing, the tool displays:

```
================================================================================
                    DOCUMENT STATUS
================================================================================
[OK]      RFC XML                    - Loaded (31 LTE, 26 NR bands)
[OK]      HW Band Filtering          - Loaded
[MISSING] Carrier Policy             - Not provided
[OK]      Generic Restrictions       - Loaded
[MISSING] MDB Config                 - Not provided
[OK]      QXDM Log (0x1CCA)          - Loaded (25 LTE, 20 NR SA bands)
[OK]      UE Capability              - Loaded

*** IMPACT OF MISSING DOCUMENTS ***
- Carrier Policy: Cannot verify operator-specific band exclusions
                  Bands like B7, B17-19 may appear as "ENABLED" but could
                  be filtered by carrier in actual deployment
- MDB Config:     Cannot verify MCC-based filtering
                  Location-specific band restrictions not analyzed

>>> Analysis will proceed with available documents <<<
================================================================================
```

### 4.3 Minimum Viable Analysis

The tool can work with **ANY subset** of documents:

| Scenario | Documents Provided | Analysis Capability |
|----------|-------------------|---------------------|
| Full Analysis | All 7 documents | Complete end-to-end tracing |
| Config Only | RFC + HW + Carrier + Generic | Expected bands (no device verification) |
| Device Only | QXDM + UE Cap | Actual bands (no config verification) |
| Comparison | RFC + UE Cap | Source vs Final comparison |
| Single Doc | Any one document | List bands from that source |

---

## 5. Filtering Pipeline

```
                         BAND FILTERING PIPELINE

    +-------+     +----------+     +---------+     +---------+     +---------+
    |  RFC  | --> | HW Filter| --> | Carrier | --> | Generic | --> | NV Band |
    +-------+     +----------+     | Policy  |     | Restr.  |     | Pref    |
                                   +---------+     +---------+     +---------+
                                                                        |
         +--------------------------------------------------------------+
         |
         v
    +----------+     +---------+
    | QXDM Log | --> | UE Cap  |
    | Prints   |     | Info    |
    +----------+     +---------+

    Stage 1       Stage 2          Stage 3         Stage 4         Stage 5
    (Source)      (Hardware)       (Operator)      (Regulatory)    (SW/NV)

                  Stage 6          Stage 7
                  (Device Log)     (Final/Network)


    +------------------------------------------------------------------+
    |  NOTE: MDB (mcc2bands) is NOT part of filtering pipeline.        |
    |  MDB data is passed to Claude as CONTEXT for expert insights.    |
    |  Claude uses MDB to explain location-based band restrictions.    |
    +------------------------------------------------------------------+
```

---

## 6. Stage 1: Automated Code Logic

### 6.1 Purpose
- Parse all input documents
- Extract band information from each source
- Compare bands at each filtering stage
- Generate raw analysis data

### 6.2 Components

| Component | Function |
|-----------|----------|
| **RFC Parser** | Extract LTE/NR bands from RFC XML |
| **HW Filter Parser** | Parse allowed band ranges (0-indexed) |
| **Carrier Policy Parser** | Extract excluded bands per carrier |
| **Generic Restriction Parser** | Parse FCC/regulatory restrictions |
| **MCFG NV Parser** | Parse NV band preference bitmasks from MCFG XML |
| **MDB Parser** | Parse mcc2bands for Claude context (**NOT used in filtering**) |
| **QXDM Log Parser** | Decode 0x1CCA hex bitmasks to bands |
| **UE Capability Parser** | Extract bandEUTRA, bandNR values |
| **Band Tracer Engine** | Compare bands across filtering stages (RFC→HW→Carrier→Generic→NV→QXDM→UE Cap) |

### 6.3 Output: Raw Analysis Data

```python
{
    "band": "n38",
    "type": "NR_SA",
    "stages": {
        "RFC": True,
        "HW_Filter": True,
        "Carrier_Policy": True,
        "Generic": True,
        "NV_Band_Pref": True,
        "QXDM": True,
        "UE_Cap": True
    },
    "status": "ENABLED",
    "filtered_at": None,
    "anomaly": None
}
# Note: MDB is NOT included in stages - it's passed separately as Claude context
```

### 6.4 Band Selection Logic (OR Condition)

**Key Design Principle:** Bands shown in the report are the **OR union** of all meaningful sources. This ensures that if a band appears in ANY source, it will be analyzed and shown in the report.

#### 6.4.1 Why OR Condition?

**Problem Scenario:** A band is implemented in carrier_policy.xml (as exclusion) but missed in RFC. If we only trace RFC bands, this mismatch would go undetected.

**Solution:** Include bands from ALL meaningful sources so any configuration mismatch is detected.

#### 6.4.2 Meaningful Sources (Included in OR Union)

| Source | Why Included | What It Indicates |
|--------|--------------|-------------------|
| **RFC Bands** | Hardware supported bands | Bands the RF card can physically support |
| **Carrier Policy Exclusions** | Bands mentioned exist somewhere | If excluded, band must exist in system |
| **Generic Restriction Exclusions** | Bands mentioned exist somewhere | If restricted, band must exist in system |
| **QXDM Bands** | Actual device bands | What device is currently broadcasting |
| **UE Capability Bands** | Network-reported bands | What network sees from device |

#### 6.4.3 Sources Excluded from OR Union

| Source | Why Excluded |
|--------|--------------|
| **HW Filter Ranges** | Contains broad whitelist ranges (0-255 for LTE, 0-511 for NR) which would pollute output with hundreds of irrelevant bands |
| **MDB Bands** | MDB is location-dependent runtime data, not a filtering stage. Passed to Claude as context only. |

#### 6.4.4 Example

**Scenario:**
- RFC contains: B1, B2, B3, B7, B20
- Carrier Policy excludes: B4, B12, B13
- QXDM shows: B1, B2, B3

**Bands Analyzed (OR union):**
```
B1, B2, B3, B4, B7, B12, B13, B20
```

**Result:**
- B1, B2, B3: ENABLED (in RFC, in QXDM)
- B4, B12, B13: NOT_SUPPORTED (not in RFC, but detected in carrier exclusions - configuration review needed)
- B7, B20: MISSING_IN_QXDM (in RFC but not in device logs - investigation needed)

This approach catches:
1. **Bands in config but not in RFC** - Configuration references unsupported band
2. **Bands in RFC but not in device** - Expected band not appearing
3. **Bands in device but not in RFC** - Anomaly detection

### 6.5 MDB as Claude Context (NOT Filtering)

**Key Design Decision:** MDB (mcc2bands) is **NOT** part of the filtering pipeline. It is passed to Claude as **context information** for expert insights.

#### 6.5.1 Why MDB is Excluded from Filtering

| Reason | Explanation |
|--------|-------------|
| **Location-dependent** | MDB filtering changes based on where device is located (MCC) |
| **Runtime behavior** | MDB is applied at runtime, not a static configuration |
| **QXDM already reflects it** | QXDM logs show actual bands AFTER MDB is applied |
| **Analysis focus** | We analyze device configuration, not location-specific behavior |

#### 6.5.2 How MDB is Used

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMPT.TXT STRUCTURE                      │
├─────────────────────────────────────────────────────────────┤
│  1. Analysis Results (RFC→HW→Carrier→Generic→QXDM→UE Cap)   │
│  2. Anomalies Detected                                       │
│  3. MDB Context (if provided)  <── For Claude's reference    │
│     - MCC being analyzed                                     │
│     - Allowed LTE bands for this MCC                         │
│     - Allowed NR SA/NSA bands for this MCC                   │
│  4. Instructions for Claude                                  │
└─────────────────────────────────────────────────────────────┘
```

#### 6.5.3 Claude Uses MDB For

- **Explaining location-based restrictions**: "B7 is not in MDB for US (MCC 310) - expected behavior"
- **Identifying MDB mismatches**: "Band is in QXDM but not allowed by MDB - possible auto-learning"
- **Regional insights**: "B38 is TDD band primarily used in China/Europe per MDB"
- **Debugging location issues**: "Device tested in India where B71 is not allowed by MDB"

### 6.6 QXDM 0x1CCA Parsing Logic

**Note:** This section documents the current parsing approach. Subject to review and refinement based on future findings.

#### 6.6.1 What is 0x1CCA?

**0x1CCA** is a QXDM log packet called **"PM RF Band Info"** (Protocol Manager RF Band Information). It shows the **actual bands currently enabled** on the device modem.

#### 6.6.2 Log Format

```
[0x1CCA]  PM RF Band Info
Version = 2
Sub Id = 2
Lte Bands
   Lte Bands 1_64 = 0x000087C0BB08389F
   Lte Bands 65_128 = 0x000000000000004A
   Lte Bands 129_192 = 0x0000000000000000
   Lte Bands 193_256 = 0x0000000000000000
Nr5g Sa Bands
   Nr5g Sa Bands 1_64 = 0x000081A00B0800D7
   Nr5g Sa Bands 65_128 = 0x0000000000003462
   ...
Nr5g Nsa Bands
   Nr5g Nsa Bands 1_64 = 0x000001A00A0800D7
   ...
```

#### 6.6.3 Parsing Algorithm

Each hex value is a **64-bit bitmask** where each bit represents a band:

```
┌─────────────────────────────────────────────────────────────────┐
│  Lte Bands 1_64 = 0x000087C0BB08389F                            │
│                   ↓                                              │
│  Convert to 64-bit binary                                        │
│                   ↓                                              │
│  For each bit position (0-63):                                   │
│    if bit == 1:                                                  │
│      band_number = start_band + bit_position                     │
│      (start_band = 1 for "1_64", 65 for "65_128", etc.)         │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.6.4 Decoding Example

```
Hex: 0x9F (last byte of 0x000087C0BB08389F)
Binary: 1001 1111

Bit 0 = 1 → Band 1  ✓
Bit 1 = 1 → Band 2  ✓
Bit 2 = 1 → Band 3  ✓
Bit 3 = 1 → Band 4  ✓
Bit 4 = 1 → Band 5  ✓
Bit 5 = 0 → Band 6  ✗
Bit 6 = 0 → Band 7  ✗
Bit 7 = 1 → Band 8  ✓
```

#### 6.6.5 Band Ranges

| Field Pattern | Band Range | Bits |
|---------------|------------|------|
| `Lte Bands 1_64` | B1 - B64 | 64 |
| `Lte Bands 65_128` | B65 - B128 | 64 |
| `Lte Bands 129_192` | B129 - B192 | 64 |
| `Lte Bands 193_256` | B193 - B256 | 64 |
| `Nr5g Sa Bands 1_64` | n1 - n64 | 64 |
| `Nr5g Sa Bands 65_128` | n65 - n128 | 64 |
| ... | ... | ... |

#### 6.6.6 Future Enhancements

- Support for additional log formats (if discovered)
- QCAT tool integration for automatic log extraction
- Support for other PM logs (future scope)

### 6.7 Band Indexing Rules (CRITICAL)

**CRITICAL**: Different Qualcomm configuration files use different band indexing conventions. Parsers MUST apply the correct conversion to ensure accurate band identification.

#### 6.7.1 Indexing Summary Table

| Document | Indexing | Conversion Required | Example |
|----------|----------|---------------------|---------|
| **RFC XML** | 1-indexed | None | `<band>7</band>` = Band 7 |
| **HW Band Filtering** | 0-indexed | Add +1 | Value `6` = Band 7 |
| **Carrier Policy** | 0-indexed | Add +1 | Value `6` = Band 7 |
| **Generic Restrictions** | 0-indexed | Add +1 | Value `6` = Band 7 |
| **MDB (mcc2bands)** | 0-indexed | Add +1 | Value `6` = Band 7 |
| **QXDM (0x1CCA)** | 1-indexed | None | Bit 0 = Band 1, Bit 6 = Band 7 |
| **UE Capability** | 1-indexed | None | `bandEUTRA: 7` = Band 7 |

#### 6.7.2 0-Indexed Files (Qualcomm Internal Format)

The following files use **0-indexed** band numbering where value `N` represents Band `N+1`:

```
┌─────────────────────────────────────────────────────────────────┐
│  0-INDEXED FILES (Value N = Band N+1)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. hardware_band_filtering.xml                                 │
│     <NR_SA_BAND val="6"/>  →  n7 (not n6!)                      │
│     <LTE_BAND val="37"/>   →  B38 (not B37!)                    │
│                                                                 │
│  2. carrier_policy.xml                                          │
│     <Band>6</Band>         →  B7 (excluded band is B7)          │
│                                                                 │
│  3. generic_band_restrictions.xml                               │
│     <band val="6"/>        →  B7                                │
│                                                                 │
│  4. MDB mcc2bands.xml                                           │
│     <band>6</band>         →  B7                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.7.3 1-Indexed Files (Standard/3GPP Format)

The following files use **1-indexed** band numbering where value `N` represents Band `N`:

```
┌─────────────────────────────────────────────────────────────────┐
│  1-INDEXED FILES (Value N = Band N)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RFC XML (RF Card)                                           │
│     <band>7</band>         →  B7                                │
│     <nr_band>38</nr_band>  →  n38                               │
│                                                                 │
│  2. QXDM 0x1CCA (PM RF Band Info)                               │
│     Bit position 0 in "Lte Bands 1_64" = Band 1                 │
│     Bit position 6 in "Lte Bands 1_64" = Band 7                 │
│                                                                 │
│  3. UE Capability Information                                   │
│     bandEUTRA: 7           →  B7                                │
│     bandNR: 78             →  n78                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.7.4 Parser Implementation Notes

```python
# Example: HW Filter Parser (0-indexed → 1-indexed conversion)
def parse_hw_filter(xml_file):
    bands = []
    for band_elem in root.findall('.//LTE_BAND'):
        raw_value = int(band_elem.get('val'))
        actual_band = raw_value + 1  # Convert 0-indexed to 1-indexed
        bands.append(actual_band)
    return bands

# Example: RFC Parser (already 1-indexed, no conversion)
def parse_rfc(xml_file):
    bands = []
    for band_elem in root.findall('.//band'):
        actual_band = int(band_elem.text)  # Already 1-indexed
        bands.append(actual_band)
    return bands
```

#### 6.7.5 Common Indexing Errors to Avoid

| Error | Symptom | Solution |
|-------|---------|----------|
| Not converting 0-indexed files | B6, B37 flagged as anomalies when B7, B38 work correctly | Apply +1 conversion to HW Filter, Carrier, Generic, MDB parsers |
| Double-converting RFC bands | B8 reported when B7 is expected | RFC is already 1-indexed, do not add +1 |
| Misaligned QXDM bits | All bands off by 1 | QXDM bit 0 = Band 1 (1-indexed), not Band 0 |

### 6.8 UE Capability Extended Band Parsing (Bands 64+)

**Reference**: 3GPP TS 36.331 (RRC Protocol specification for E-UTRA), Section 6.3.6

#### 6.8.1 Problem Statement

The UE Capability Information uses two separate Information Elements (IEs) for LTE bands:
- `supportedBandListEUTRA`: Covers bands 1-64
- `supportedBandListEUTRA-v9e0`: Extension for bands 65 and above (B65, B66, B68, B71, etc.)

**Challenge**: When bands 65+ are supported, `supportedBandListEUTRA` contains "64" as a **placeholder** value, and the actual band number is in the v9e0 extension.

#### 6.8.2 UE Capability Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  UE-EUTRA-Capability                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  supportedBandListEUTRA:     [1, 2, 3, 7, 64, 64, 64, 64]      │
│                               ↑↑↑↑↑↑↑↑↑     ↑↑↑↑↑↑↑↑↑↑↑↑       │
│                               Actual        Placeholders        │
│                               bands 1-64    for v9e0 bands      │
│                                                                 │
│  supportedBandListEUTRA-v9e0: [66, 68, 71]                      │
│                                ↑↑↑↑↑↑↑↑↑↑↑                      │
│                                Actual band numbers              │
│                                for bands 65+                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.8.3 Band 64 Mapping Logic

**Formula for determining actual Band 64 support:**

```
Actual B64 count = (count of "64" in supportedBandListEUTRA) - (count in supportedBandListEUTRA-v9e0)
```

**Example Scenarios:**

| supportedBandListEUTRA | supportedBandListEUTRA-v9e0 | Calculation | Supported Bands |
|------------------------|----------------------------|-------------|-----------------|
| [1, 2, 3, 7, 64, 64, 64, 64] | [66, 68, 71] | 4 - 3 = 1 | B1, B2, B3, B7, **B64**, B66, B68, B71 |
| [1, 2, 3, 7, 64, 64, 64] | [66, 68, 71] | 3 - 3 = 0 | B1, B2, B3, B7, B66, B68, B71 (NO B64) |
| [1, 2, 3, 7, 64] | [] | 1 - 0 = 1 | B1, B2, B3, B7, **B64** |
| [1, 2, 3, 7] | [] | 0 - 0 = 0 | B1, B2, B3, B7 (no bands ≥64) |

#### 6.8.4 Parsing Algorithm

```python
def parse_ue_capability_lte_bands(ue_cap_content):
    """
    Parse LTE bands from UE Capability Information.
    Handles both supportedBandListEUTRA and v9e0 extension.
    """
    lte_bands = set()

    # Step 1: Extract bands from supportedBandListEUTRA
    base_bands = extract_supported_band_list_eutra(ue_cap_content)
    count_64_in_base = base_bands.count(64)

    # Add all bands except "64" placeholders
    for band in base_bands:
        if band != 64:
            lte_bands.add(band)

    # Step 2: Extract bands from supportedBandListEUTRA-v9e0 (if present)
    v9e0_bands = extract_supported_band_list_eutra_v9e0(ue_cap_content)

    # Add v9e0 bands (these are bands 65+)
    for band in v9e0_bands:
        lte_bands.add(band)

    # Step 3: Determine actual B64 support
    actual_b64_count = count_64_in_base - len(v9e0_bands)
    if actual_b64_count > 0:
        lte_bands.add(64)

    return sorted(lte_bands)
```

#### 6.8.5 Example UE Capability Parsing

**Input (UE Capability Information):**
```
supportedBandListEUTRA
  bandEUTRA: 1
  bandEUTRA: 2
  bandEUTRA: 3
  bandEUTRA: 7
  bandEUTRA: 64
  bandEUTRA: 64
  bandEUTRA: 64
  bandEUTRA: 64

supportedBandListEUTRA-v9e0
  bandEUTRA-v9e0: 66
  bandEUTRA-v9e0: 68
  bandEUTRA-v9e0: 71
```

**Parsing Steps:**
1. Base bands: [1, 2, 3, 7, 64, 64, 64, 64] → Count of "64" = 4
2. v9e0 bands: [66, 68, 71] → Count = 3
3. Actual B64 support: 4 - 3 = 1 (YES, B64 is supported)
4. **Final LTE bands: [1, 2, 3, 7, 64, 66, 68, 71]**

#### 6.8.6 NR Bands Extended Parsing

Similar logic applies to NR bands for bands beyond the base range:
- `supportedBandListNR`: Base NR bands
- `supportedBandListNR-v15xy`: Extensions for additional NR bands

**Note**: NR band extensions follow a similar pattern but the specific IE names may vary based on 3GPP release. Refer to 3GPP TS 38.331 for NR-specific extensions.

#### 6.8.7 Implementation Requirements

| Requirement | Description |
|-------------|-------------|
| **Parse v9e0 IE** | UE Capability parser MUST extract supportedBandListEUTRA-v9e0 when present |
| **Count B64 entries** | Count occurrences of "64" in base IE separately |
| **Apply formula** | Use (base B64 count) - (v9e0 count) to determine actual B64 support |
| **Handle missing v9e0** | If v9e0 IE is absent, treat all "64" entries as actual Band 64 |
| **Validate consistency** | v9e0 count should not exceed B64 placeholder count |

### 6.9 MCFG NV Band Preference Parsing

**Purpose:** Parse NV band preference items from MCFG XML to identify software-level band filtering applied before QXDM.

#### 6.9.1 Overview

MCFG (Modem Configuration) XML files contain NV (Non-Volatile) items that control band preferences at the software/firmware level. These NV items use **bitmask encoding** where each bit represents a specific band's enable/disable status.

```
┌─────────────────────────────────────────────────────────────────┐
│  NV Band Preference Flow                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MCFG XML → NV Items (bitmask) → SW Band Filtering → QXDM      │
│                                                                 │
│  If bit = 1: Band ENABLED                                       │
│  If bit = 0: Band DISABLED (filtered at SW level)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.9.2 NV Item Reference Table

| NV ID | Name | RAT | Band Coverage | Bits | Notes |
|-------|------|-----|---------------|------|-------|
| **65633** | lte_bandpref | LTE | B1 - B64 | 64 bits (8 bytes) | Bit 0 = Band 1 |
| **73680** | lte_bandpref_ext | LTE | B65 - B256 | 192 bits (24 bytes) | Bit 0 = Band 65 |
| **74087** | nr5g_sa_bandpref | NR SA | All NR SA bands | Variable | Bitmask for NR SA |
| **74213** | nr5g_nsa_bandpref | NR NSA | All NR NSA bands | Variable | Bitmask for NR NSA |
| **441** | band_pref | 2G/3G (CGW) | GSM/WCDMA bands | Variable | Legacy RATs |
| **946** | band_pref_16_31 | 2G/3G (CGW) | Extended GSM/WCDMA | Variable | Legacy RATs |
| **2954** | band_pref_32_63 | 2G/3G (CGW) | Further extension | Variable | Legacy RATs |

#### 6.9.3 MCFG XML Format

NV items in MCFG XML follow this structure:

```xml
<NvItemData id="65633" subs_id="0" encoding="dec">
  <Member name="lte_bandpref" encoding="dec">
    223 56 14 187 224 135 0 0
  </Member>
</NvItemData>
```

**Key Attributes:**
- `id`: NV item ID number
- `subs_id`: Subscription ID (typically 0 for primary SIM)
- `encoding`: Value encoding format ("dec" = decimal bytes)
- `<Member>`: Contains the actual byte values (space-separated)

#### 6.9.4 Bit-to-Band Mapping (NV 65633 - LTE B1-B64)

**Critical: Bit 0 = Band 1 (1-indexed mapping)**

```
┌─────────────────────────────────────────────────────────────────┐
│  NV 65633: lte_bandpref (8 bytes = 64 bits)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Byte layout (little-endian bit order within each byte):        │
│                                                                 │
│  Byte 0 (bits 0-7):   Bands 1-8                                 │
│  Byte 1 (bits 8-15):  Bands 9-16                                │
│  Byte 2 (bits 16-23): Bands 17-24                               │
│  Byte 3 (bits 24-31): Bands 25-32                               │
│  Byte 4 (bits 32-39): Bands 33-40                               │
│  Byte 5 (bits 40-47): Bands 41-48                               │
│  Byte 6 (bits 48-55): Bands 49-56                               │
│  Byte 7 (bits 56-63): Bands 57-64                               │
│                                                                 │
│  Formula: Band N is enabled if bit (N-1) is set to 1            │
│           Byte index = (N-1) // 8                               │
│           Bit position within byte = (N-1) % 8                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.9.5 Decoding Example (NV 65633)

**Input:** `223 56 14 187 224 135 0 0`

**Step-by-step decoding:**

```
Byte 0: 223 = 0b11011111
  Bit 0 (B1):  1 → ENABLED
  Bit 1 (B2):  1 → ENABLED
  Bit 2 (B3):  1 → ENABLED
  Bit 3 (B4):  1 → ENABLED
  Bit 4 (B5):  1 → ENABLED
  Bit 5 (B6):  0 → DISABLED  ←── B6 filtered!
  Bit 6 (B7):  1 → ENABLED
  Bit 7 (B8):  1 → ENABLED

Byte 1: 56 = 0b00111000
  Bit 0 (B9):  0 → DISABLED
  Bit 1 (B10): 0 → DISABLED
  Bit 2 (B11): 0 → DISABLED
  Bit 3 (B12): 1 → ENABLED
  Bit 4 (B13): 1 → ENABLED
  Bit 5 (B14): 1 → ENABLED
  Bit 6 (B15): 0 → DISABLED
  Bit 7 (B16): 0 → DISABLED

... (continue for all 8 bytes)

Byte 5: 135 = 0b10000111
  Bit 0 (B41): 1 → ENABLED
  Bit 1 (B42): 1 → ENABLED
  Bit 2 (B43): 1 → ENABLED
  Bit 3 (B44): 0 → DISABLED
  Bit 4 (B45): 0 → DISABLED
  Bit 5 (B46): 0 → DISABLED  ←── B46 (LAA) filtered!
  Bit 6 (B47): 0 → DISABLED
  Bit 7 (B48): 1 → ENABLED
```

**Result:** Bands like B6, B46 are disabled at SW level even if HW supports them.

#### 6.9.6 Parsing Algorithm

```python
def parse_nv_band_pref(nv_bytes: List[int], start_band: int = 1) -> Set[int]:
    """
    Parse NV band preference bitmask to extract enabled bands.

    Args:
        nv_bytes: List of byte values from MCFG XML
        start_band: Starting band number (1 for NV65633, 65 for NV73680)

    Returns:
        Set of enabled band numbers (1-indexed)
    """
    enabled_bands = set()

    for byte_idx, byte_val in enumerate(nv_bytes):
        for bit_pos in range(8):
            if byte_val & (1 << bit_pos):  # Check if bit is set
                band_num = start_band + (byte_idx * 8) + bit_pos
                enabled_bands.add(band_num)

    return enabled_bands


def parse_mcfg_xml(mcfg_file: str) -> Dict[str, Set[int]]:
    """
    Parse MCFG XML to extract band preferences from NV items.

    Returns:
        Dict with keys: 'lte_bands', 'lte_ext_bands', 'nr_sa_bands', 'nr_nsa_bands'
    """
    result = {
        'lte_bands': set(),      # From NV 65633
        'lte_ext_bands': set(),  # From NV 73680
        'nr_sa_bands': set(),    # From NV 74087
        'nr_nsa_bands': set()    # From NV 74213
    }

    tree = ET.parse(mcfg_file)

    for nv_item in tree.findall('.//NvItemData'):
        nv_id = int(nv_item.get('id', 0))
        member = nv_item.find('Member')

        if member is not None and member.text:
            bytes_str = member.text.strip()
            nv_bytes = [int(b) for b in bytes_str.split()]

            if nv_id == 65633:
                result['lte_bands'] = parse_nv_band_pref(nv_bytes, start_band=1)
            elif nv_id == 73680:
                result['lte_ext_bands'] = parse_nv_band_pref(nv_bytes, start_band=65)
            elif nv_id == 74087:
                result['nr_sa_bands'] = parse_nv_band_pref(nv_bytes, start_band=1)
            elif nv_id == 74213:
                result['nr_nsa_bands'] = parse_nv_band_pref(nv_bytes, start_band=1)

    return result
```

#### 6.9.7 Integration with Band Tracer

The NV Band Pref stage fits between Generic Restrictions and QXDM in the filtering pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│  Band Tracing with NV Band Pref Stage                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  For each band:                                                 │
│                                                                 │
│  1. RFC           → Is band in RF Card capability?              │
│  2. HW Filter     → Is band allowed by hardware filtering?      │
│  3. Carrier Policy→ Is band NOT excluded by carrier?            │
│  4. Generic Restr → Is band NOT restricted by regulations?      │
│  5. NV Band Pref  → Is band enabled in MCFG NV bitmask?  [NEW]  │
│  6. QXDM          → Does band appear in 0x1CCA log?             │
│  7. UE Capability → Does band appear in UE Cap?                 │
│                                                                 │
│  If NV Band Pref FAIL: Status = "FILTERED", Filtered_At = "NV"  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.9.8 Output Format Updates

**Band Tracing Table with NV Stage:**

```
LTE BAND TRACING:
---------------------------------------------------------------------------------
Band   RFC    HW     Carrier  Generic  NV_Pref  QXDM   UE_Cap  Status    Filtered At
---------------------------------------------------------------------------------
B1     PASS   PASS   PASS     PASS     PASS     PASS   PASS    ENABLED   -
B6     PASS   PASS   PASS     PASS     FAIL     FAIL   FAIL    FILTERED  NV_Pref
B46    PASS   PASS   PASS     PASS     FAIL     FAIL   FAIL    FILTERED  NV_Pref
---------------------------------------------------------------------------------
```

#### 6.9.9 Handling Missing NV Items

| Scenario | Behavior |
|----------|----------|
| **MCFG XML not provided** | NV_Pref stage skipped, all bands PASS |
| **NV 65633 missing** | LTE B1-B64 NV filtering skipped |
| **NV 73680 missing** | LTE B65+ NV filtering skipped |
| **NV 74087 missing** | NR SA NV filtering skipped |
| **NV 74213 missing** | NR NSA NV filtering skipped |

**Important:** Missing NV items are common and expected. The tool should gracefully skip NV filtering for RATs where the corresponding NV item is not present in the MCFG XML.

#### 6.9.10 Implementation Requirements

| Requirement | Description |
|-------------|-------------|
| **Parse MCFG XML** | Extract NvItemData elements with specific IDs |
| **Handle encoding** | Support "dec" (decimal) encoding; add "hex" if needed |
| **Bit mapping** | Bit 0 = Band 1 (1-indexed, NOT 0-indexed) |
| **Little-endian bytes** | Byte 0 contains lowest bands (B1-B8) |
| **Graceful missing** | If NV item absent, skip that RAT's NV filtering |
| **Combine LTE** | Merge NV65633 (B1-64) and NV73680 (B65+) for full LTE coverage |

---

## 7. Stage 2: Claude CLI Review

### 7.1 Purpose
- Validate automated findings with domain expertise
- Provide intelligent explanations for filtering decisions
- Identify root causes of anomalies
- Offer actionable recommendations

### 7.2 Execution Command

```bash
claude -p --dangerously-skip-permissions < prompt.txt > claude_review.txt
```

### 7.3 prompt.txt Structure

The prompt.txt generated by Stage 1 contains:

```
================================================================================
                    BAND ANALYSIS - CLAUDE REVIEW REQUEST
================================================================================

You are an expert in Qualcomm modem band configuration and RF analysis.
Review the following automated band analysis and provide your expert insights.

--------------------------------------------------------------------------------
SECTION 1: DOCUMENT STATUS
--------------------------------------------------------------------------------
[OK]      RFC XML                    - Loaded (31 LTE, 26 NR bands)
[OK]      HW Band Filtering          - Loaded
[MISSING] Carrier Policy             - Not provided
[OK]      Generic Restrictions       - Loaded
[OK]      MDB Config                 - Loaded (MCC: 310)
[OK]      QXDM Log (0x1CCA)          - Loaded (25 LTE, 20 NR SA bands)
[OK]      UE Capability              - Loaded

--------------------------------------------------------------------------------
SECTION 2: AUTOMATED ANALYSIS RESULTS
--------------------------------------------------------------------------------

LTE BAND TRACING:
Band   RFC    HW     Carrier  Generic  QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
B1     PASS   PASS   N/A      PASS     PASS   PASS     ENABLED
B7     PASS   PASS   N/A      PASS     FAIL   FAIL     MISSING_IN_QXDM
B38    PASS   PASS   N/A      PASS     PASS   PASS     ENABLED
...

NR SA BAND TRACING:
Band   RFC    HW     Carrier  Generic  QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
n1     PASS   PASS   N/A      PASS     PASS   PASS     ENABLED
n75    FAIL   PASS   N/A      PASS     PASS   PASS     ANOMALY
...

--------------------------------------------------------------------------------
SECTION 3: DETECTED ANOMALIES
--------------------------------------------------------------------------------
1. NR n75: Present in QXDM and UE Cap but NOT in RFC
2. LTE B7: Present in RFC but MISSING in QXDM and UE Cap
3. LTE B68: Present in QXDM but NOT in RFC

--------------------------------------------------------------------------------
SECTION 4: REVIEW INSTRUCTIONS
--------------------------------------------------------------------------------
Please provide:
1. Validation of the automated findings
2. Explanation for each anomaly (possible root causes)
3. Impact assessment for each issue
4. Recommended actions to resolve anomalies
5. Overall verdict: Is this configuration safe for deployment?

Format your response with clear sections for each anomaly.
================================================================================
```

### 7.4 Claude's Review Areas

| Area | What Claude Analyzes |
|------|---------------------|
| **Validation** | Verify code's PASS/FAIL determinations are correct |
| **Explanations** | Explain WHY a band is filtered (e.g., "B7 excluded - not licensed for ATT in US") |
| **Anomaly Analysis** | Deep-dive into anomalies (e.g., "n75 present without RFC support - likely MBN override") |
| **Edge Cases** | Catch issues code might miss (e.g., 0-indexed vs 1-indexed band numbering) |
| **Recommendations** | Suggest fixes (e.g., "Check EFS persisted items", "Verify active MBN") |

### 7.5 Claude's Output (claude_review.txt)

```
================================================================================
                         CLAUDE'S EXPERT REVIEW
================================================================================

ANOMALY 1: NR n75 - CRITICAL
----------------------------
Finding: Present in QXDM (0x1CCA) and UE Capability, but NOT in RFC.

Analysis:
This is a critical anomaly. Band n75 (1500 MHz SDL) should not appear
in device capabilities if the RF card doesn't support it.

Possible Root Causes:
1. Wrong RFC file provided for analysis (different HW variant)
2. MBN dynamically adding bands not in base RFC
3. EFS override persisting incorrect band configuration
4. hardware_band_filtering.xml on device differs from analyzed file

Impact: HIGH - Device advertising capability it may not physically support

Recommendation:
- Pull active RFC from device: adb shell cat /vendor/rfc/...
- Clear EFS persisted items: adb shell rm -rf /efs/policyman/persisted_items/
- Verify MBN version matches expected configuration

--------------------------------------------------------------------------------

ANOMALY 2: LTE B7 - MEDIUM
--------------------------
Finding: Present in RFC but missing in QXDM and UE Capability.

Analysis:
Band B7 (2600 MHz) is supported by hardware but not appearing in device
logs or network capabilities.

Possible Root Causes:
1. Carrier Policy filtering B7 (check carrier_policy.xml)
2. MDB filtering based on MCC (B7 not allowed for current country)
3. Generic restriction (FCC or regional block)

Impact: MEDIUM - Band capability not being utilized

Recommendation:
- Provide Carrier Policy XML for complete analysis
- Check MDB mcc2bands for MCC 310 B7 status

--------------------------------------------------------------------------------

OVERALL VERDICT: NEEDS INVESTIGATION
------------------------------------
2 anomalies detected that require resolution before deployment:
- n75 anomaly is CRITICAL - hardware mismatch suspected
- B7 missing is MEDIUM - likely configuration issue

Do NOT deploy until n75 anomaly is resolved.
================================================================================
```

---

## 8. Output Format

### 8.1 Console Output (Combined Report)

```
================================================================================
                         BAND ANALYSIS REPORT
================================================================================

[STAGE 1: AUTOMATED ANALYSIS]
--------------------------------------------------------------------------------
BAND TRACING - NR SA
--------------------------------------------------------------------------------
Band   RFC    HW     Carrier  Generic  QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
n1     PASS   PASS   PASS     PASS     PASS   PASS     ENABLED
n38    PASS   PASS   PASS     PASS     PASS   PASS     ENABLED
n75    FAIL   PASS   PASS     PASS     PASS   PASS     ANOMALY!
--------------------------------------------------------------------------------

[STAGE 2: CLAUDE'S REVIEW]
--------------------------------------------------------------------------------

>> n1 (2100 MHz FDD)
   Status: ENABLED - Correctly configured
   Comment: Standard band, properly supported across all stages.

>> n38 (2600 MHz TDD)
   Status: ENABLED - Correctly configured
   Comment: TDD band commonly used globally. HW filter range 34-37 (0-indexed)
   includes band 38. No issues detected.

>> n75 (1500 MHz SDL) - CRITICAL ANOMALY
   Status: ANOMALY - Requires Investigation

   Finding: Band appears in device logs but NOT in RFC hardware capability.

   Root Cause Analysis:
   - RF card (HWID 966) does not list n75 support
   - Yet band appears in 0x1CCA and UE Capability
   - This indicates configuration override or wrong RFC reference

   Recommended Actions:
   1. Verify RFC file matches device hardware
   2. Check for EFS band overrides
   3. Review MBN band additions

================================================================================
                              SUMMARY
================================================================================
Total Bands Analyzed: 27 NR SA
  - ENABLED: 19
  - FILTERED: 6
  - ANOMALY: 2

Claude's Verdict: 2 anomalies require investigation before deployment.
================================================================================
```

### 8.2 HTML Output (Integrated Report)

The final HTML report combines **Stage 1 analysis** and **Stage 2 Claude review** into a single document:

```
┌─────────────────────────────────────────────────────────────────┐
│              BAND ANALYSIS REPORT (HTML)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  HEADER                                                  │   │
│  │  - Report title                                          │   │
│  │  - Generation timestamp                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  DOCUMENT STATUS                                         │   │
│  │  - Which files were loaded                               │   │
│  │  - Band counts per source                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SUMMARY CARDS                                           │   │
│  │  - LTE: X enabled / Y total                              │   │
│  │  - NR SA: X enabled / Y total                            │   │
│  │  - NR NSA: X enabled / Y total                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  BAND TRACING TABLES (Stage 1)                           │   │
│  │  - LTE bands with PASS/FAIL per stage                    │   │
│  │  - NR SA bands with PASS/FAIL per stage                  │   │
│  │  - Color-coded status (green/yellow/red)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ANOMALIES DETECTED (Stage 1)                            │   │
│  │  - List of anomalies with descriptions                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  CLAUDE'S EXPERT REVIEW (Stage 2)  ◄── INTEGRATED       │   │
│  │  - Validation of findings                                │   │
│  │  - Root cause analysis per anomaly                       │   │
│  │  - Impact assessment matrix                              │   │
│  │  - Recommended actions                                   │   │
│  │  - Overall verdict                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FOOTER                                                  │   │
│  │  - Generated by Band Combos Analyzer Tool                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Single self-contained HTML file
- Color-coded band status (Green=ENABLED, Yellow=FILTERED, Red=ANOMALY)
- Claude's expert review embedded directly in report
- Downloadable for offline review and sharing
- No external dependencies (all CSS inline)

---

## 9. Single Band Trace Feature

User can trace a specific band with both automated + Claude analysis:

```
Input: NR 75

================================================================================
TRACING NR BAND 75
================================================================================

[AUTOMATED TRACE]
-----------------
Stage 1 - RFC (RF Card):        FAIL  <-- Not in RFC!
Stage 2 - HW Band Filtering:    PASS  (Bit 74 allowed)
Stage 3 - Carrier Policy:       PASS  (Not excluded)
Stage 4 - Generic Restriction:  PASS  (No restriction)
Stage 5 - QXDM Log (0x1CCA):    PASS  <-- Present in log!
Stage 6 - UE Capability:        PASS  <-- Reported to network!

[MDB CONTEXT - For Claude's reference]
MDB (mcc2bands) for MCC 310: n75 is ALLOWED

Automated Result: ANOMALY - Present in logs but not in RFC

[CLAUDE'S ANALYSIS]
-------------------
This is a significant anomaly that warrants investigation.

Technical Analysis:
- Band n75 (1500 MHz) is an SDL (Supplemental Downlink) band
- The RF card (Q6515, HWID 966) does not include n75 in its capabilities
- However, the band appears in both QXDM 0x1CCA log and UE Capability

Possible Explanations:
1. RFC Mismatch: The RFC file analyzed may not match the actual device
2. Dynamic Addition: MBN or carrier policy adding band post-RFC
3. EFS Override: Persisted EFS items overriding hardware limitations

Impact:
- Device is advertising capability it may not physically support
- Could lead to network assignment failures or RF issues

Recommendation:
- IMMEDIATE: Verify RFC matches actual device hardware
- Pull device RFC: adb pull /vendor/etc/modem/rfc_*.xml
- Compare with analyzed RFC file
================================================================================
```

---

## 10. Architecture Components

```
Band_Combos_Analyzer/
|
+-- docs/
|   +-- Architecture_Design.md        # This document
|   +-- MDB_Understanding.md          # MDB reference
|
+-- requirements/
|   +-- Basic_design_Image.jfif       # Reference UI design
|
+-- src/
|   +-- parsers/
|   |   +-- __init__.py
|   |   +-- rfc_parser.py             # Parse RFC XML
|   |   +-- hw_filter_parser.py       # Parse hardware_band_filtering.xml
|   |   +-- carrier_policy_parser.py  # Parse carrier_policy.xml
|   |   +-- generic_restriction_parser.py
|   |   +-- mcfg_parser.py            # Parse MCFG NV band preferences
|   |   +-- mdb_parser.py             # Parse mcc2bands.xml
|   |   +-- qxdm_log_parser.py        # Parse 0x1CCA logs
|   |   +-- ue_capability_parser.py   # Parse UE Capability
|   |
|   +-- core/
|   |   +-- __init__.py
|   |   +-- band_tracer.py            # Band tracing engine
|   |   +-- analyzer.py               # Analysis logic
|   |   +-- prompt_generator.py       # Generate prompt.txt for Claude
|   |
|   +-- output/
|   |   +-- __init__.py
|   |   +-- console_report.py         # Console output generator
|   |   +-- html_report.py            # HTML report generator
|   |
|   +-- main.py                       # Main entry point (Stage 1)
|   +-- merge_report.py               # Stage 3: Merge Claude review into HTML report
|
+-- templates/
|   +-- report_template.html          # HTML report template
|
+-- output/
|   +-- prompt.txt                    # Generated prompt for Claude (Stage 1 output)
|   +-- claude_review.txt             # Claude's review (Stage 2 output)
|   +-- (generated HTML reports)
|
+-- run_analysis.sh                   # Script to run full analysis (Stage 1 + 2)
```

### 10.1 Execution Scripts

**run_analysis.bat** (Windows):

```batch
@echo off
REM Full Band Analysis Pipeline - 3 Stages

cd /d "%~dp0"

echo ============================================================
echo           BAND COMBOS ANALYZER TOOL
echo ============================================================

REM Configuration - Edit file paths as needed
set RFC_FILE=Input\rfc.xml
set HW_FILTER_FILE=Input\hardware_band_filtering.xml
set CARRIER_FILE=Input\carrier_policy.xml
set GENERIC_FILE=Input\generic_band_restrictions.xml
set MCFG_FILE=Input\mcfg_sw_gen_VoLTE.xml
set MDB_FILE=Input\MDB\mcc2bands\mcc2bands.xml
set QXDM_FILE=Input\qxdm_log.txt
set UE_CAP_FILE=Input\ue_capability.txt
set TARGET_MCC=310

echo.
echo [STAGE 1] Running Python Analysis...
python -m src.main ^
    --rfc "%RFC_FILE%" ^
    --hw-filter "%HW_FILTER_FILE%" ^
    --carrier "%CARRIER_FILE%" ^
    --generic "%GENERIC_FILE%" ^
    --mcfg "%MCFG_FILE%" ^
    --mdb "%MDB_FILE%" --mcc %TARGET_MCC% ^
    --qxdm "%QXDM_FILE%" ^
    --ue-cap "%UE_CAP_FILE%"

echo.
echo [STAGE 2] Running Claude CLI Review...
claude -p --dangerously-skip-permissions < output\prompt.txt > output\claude_review.txt

echo.
echo [STAGE 3] Generating Integrated HTML Report...
python -m src.merge_report

echo.
echo ============================================================
echo                     ANALYSIS COMPLETE
echo ============================================================
echo.
echo Output files:
echo   - output\prompt.txt              : Stage 1 analysis
echo   - output\claude_review.txt       : Stage 2 Claude review
echo   - output\band_analysis_report.html : INTEGRATED REPORT (Stage 1 + 2)
echo.
pause
```

**run_analysis.sh** (Linux/Mac):

```bash
#!/bin/bash
# Full Band Analysis Pipeline - 3 Stages

cd "$(dirname "$0")"

echo "============================================================"
echo "           BAND COMBOS ANALYZER TOOL"
echo "============================================================"

echo ""
echo "[STAGE 1] Running Python Analysis..."
python -m src.main \
    --rfc "Input/rfc.xml" \
    --hw-filter "Input/hardware_band_filtering.xml" \
    --carrier "Input/carrier_policy.xml" \
    --generic "Input/generic_band_restrictions.xml" \
    --mcfg "Input/mcfg_sw_gen_VoLTE.xml" \
    --mdb "Input/MDB/mcc2bands/mcc2bands.xml" --mcc 310 \
    --qxdm "Input/qxdm_log.txt" \
    --ue-cap "Input/ue_capability.txt"

echo ""
echo "[STAGE 2] Running Claude CLI Review..."
claude -p --dangerously-skip-permissions < output/prompt.txt > output/claude_review.txt

echo ""
echo "[STAGE 3] Generating Integrated HTML Report..."
python -m src.merge_report

echo ""
echo "============================================================"
echo "                     ANALYSIS COMPLETE"
echo "============================================================"
echo ""
echo "Output files:"
echo "  - output/prompt.txt              : Stage 1 analysis"
echo "  - output/claude_review.txt       : Stage 2 Claude review"
echo "  - output/band_analysis_report.html : INTEGRATED REPORT (Stage 1 + 2)"
```

---

## 11. Data Flow (Detailed)

```
+--------------------------------------------------------------------------+
|                            USER INPUT                                     |
|         (Upload 7 Document Files)                                        |
+-------------------------------------+------------------------------------+
                                      |
                                      v
+--------------------------------------------------------------------------+
|                        STAGE 1: CODE LOGIC                                |
|  +--------------------------------------------------------------------+  |
|  |                           PARSERS                                   |  |
|  |  +--------+ +--------+ +--------+ +--------+ +--------+            |  |
|  |  |  RFC   | |   HW   | |Carrier | |Generic | |  MDB   |            |  |
|  |  | Parser | | Filter | | Policy | | Restr. | | Parser |            |  |
|  |  +---+----+ +---+----+ +---+----+ +---+----+ +---+----+            |  |
|  |      |          |          |          |          |                  |  |
|  |  +---+----------+----------+----------+----------+---+              |  |
|  |  |              Extracted Band Sets                  |              |  |
|  |  +---------------------------+-----------------------+              |  |
|  |                              |                                      |  |
|  |  +--------+ +--------+       |                                      |  |
|  |  |  QXDM  | | UE Cap |       |                                      |  |
|  |  | Parser | | Parser |       |                                      |  |
|  |  +---+----+ +---+----+       |                                      |  |
|  |      |          |            |                                      |  |
|  |      +-----+----+            |                                      |  |
|  |            |                 |                                      |  |
|  |            v                 v                                      |  |
|  |  +------------------------------------------------------------+    |  |
|  |  |              BAND TRACER ENGINE                             |    |  |
|  |  |  - For each band: trace through all 7 stages                |    |  |
|  |  |  - Determine PASS/FAIL at each stage                        |    |  |
|  |  |  - Identify filtering point                                 |    |  |
|  |  |  - Flag anomalies                                           |    |  |
|  |  +-----------------------------+------------------------------+    |  |
|  +------------------------------------+-------------------------------+  |
|                                       |                                   |
|                                       v                                   |
|  +--------------------------------------------------------------------+  |
|  |                    RAW ANALYSIS RESULTS                             |  |
|  |  - Band status matrix (band x stage)                                |  |
|  |  - Anomaly list with details                                        |  |
|  |  - Statistics (enabled/filtered/anomaly counts)                     |  |
|  +------------------------------------+-------------------------------+  |
+-------------------------------------------+------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------+
|                       STAGE 2: CLAUDE AI REVIEW                           |
|  +--------------------------------------------------------------------+  |
|  |                         INPUTS TO CLAUDE                            |  |
|  |  - Raw analysis results from Stage 1                                |  |
|  |  - Original documents (for context)                                 |  |
|  |  - Domain knowledge (band specs, regional info, common issues)      |  |
|  +------------------------------------+-------------------------------+  |
|                                       |                                   |
|                                       v                                   |
|  +--------------------------------------------------------------------+  |
|  |                    CLAUDE'S ANALYSIS                                |  |
|  |  - Validate each finding                                            |  |
|  |  - Explain filtering reasons with domain context                    |  |
|  |  - Analyze anomalies (root cause, impact, recommendations)          |  |
|  |  - Provide overall assessment and verdict                           |  |
|  +------------------------------------+-------------------------------+  |
|                                       |                                   |
|                                       v                                   |
|  +--------------------------------------------------------------------+  |
|  |                    CLAUDE'S OUTPUT                                  |  |
|  |  - Per-band commentary                                              |  |
|  |  - Anomaly explanations with root causes                            |  |
|  |  - Recommendations for fixes                                        |  |
|  |  - Overall verdict (safe to deploy / needs investigation)           |  |
|  +--------------------------------------------------------------------+  |
+-------------------------------------------+------------------------------+
                                            |
                                            v
+--------------------------------------------------------------------------+
|                          FINAL OUTPUT                                     |
|                                                                           |
|    +---------------------+              +---------------------+           |
|    |   CONSOLE REPORT    |              |    HTML REPORT      |           |
|    |   (Display)         |              |    (Download)       |           |
|    |                     |              |                     |           |
|    | - Automated Results |              | - Full Analysis     |           |
|    | - Claude's Review   |              | - Interactive       |           |
|    | - Summary & Verdict |              | - Color Coded       |           |
|    +---------------------+              +---------------------+           |
|                                                                           |
+--------------------------------------------------------------------------+
```

---

## 12. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| XML Parsing | xml.etree.ElementTree |
| Log Parsing | Regular Expressions (re) |
| Claude Integration | Claude API / Claude Code |
| HTML Generation | Jinja2 templates |
| CLI Interface | argparse / simple input |
| Console Output | Print to terminal |
| HTML Output | Generated file (downloadable) |

---

## 13. Phase 1 Scope (Current)

| Feature | Status |
|---------|--------|
| RFC XML parsing | In Scope |
| HW Band Filtering parsing | In Scope |
| Carrier Policy parsing | In Scope |
| Generic Restriction parsing | In Scope |
| MDB parsing (mcc2bands) | In Scope |
| QXDM Log parsing (0x1CCA) | In Scope |
| UE Capability parsing | In Scope |
| Stage 1: Automated band tracing | In Scope |
| Stage 2: Claude AI review | In Scope |
| Single band trace | In Scope |
| Console output (display) | In Scope |
| HTML output (download) | In Scope |
| Full band analysis | In Scope |
| Combo analysis | Future Phase |

---

## 14. QXDM Log Input

### 14.1 Current Approach (Phase 1)
- User provides a `.txt` file containing 0x1CCA log content
- Manually copied/exported from QXDM

**Expected .txt file format:**
```
[0x1CCA] PM RF Band Info
  LTE Bands: 0x00000000 0x0007EFFF 0x00000000 0x00000000
  NR SA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000
  NR NSA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000
```

### 14.2 Future Enhancement: QCAT Integration

```
+------------------+      +------------+      +------------------+      +----------+
| Raw QXDM Log     | ---> | QCAT Tool  | ---> | Converted .txt   | ---> | Parser   |
| (.isf / .dlf)    |      | (Qualcomm) |      | (Full log text)  |      | extracts |
+------------------+      +------------+      +------------------+      | 0x1CCA   |
                                                                        +----------+
```

**Future capabilities:**
- Accept raw QXDM log files (.isf, .dlf)
- Automatically invoke QCAT to convert to .txt
- Extract multiple log types (0x1CCA, and others as needed)
- Parse extracted logs

---

## 15. Knowledge Base

### 15.1 Purpose

A centralized repository of Qualcomm documents, KBAs, carrier specifications, and domain knowledge that:
- Improves Stage 1 parsing accuracy
- Enriches Stage 2 Claude review with domain-specific context
- Grows over time as more documents are added

### 15.2 Architecture

```
+-----------------------------------------------------------------------------+
|                            KNOWLEDGE BASE                                   |
+-----------------------------------------------------------------------------+
|                                                                             |
|   docs/knowledge_base/                                                      |
|   |                                                                         |
|   +-- qualcomm_kbas/           # Qualcomm Knowledge Base Articles           |
|   |   +-- KBA-201108184431.md  # How to check LTE and NR band               |
|   |   +-- KBA-220107011510.md  # Disable MDB auto-learning                  |
|   |   +-- KBA-230421012404.md  # MDB per SUB                                |
|   |   +-- ...                                                               |
|   |                                                                         |
|   +-- band_specifications/     # Band technical specs                       |
|   |   +-- lte_bands.md         # LTE band frequencies, regions              |
|   |   +-- nr_bands.md          # NR band frequencies, regions               |
|   |   +-- band_classes.md      # Band class definitions                     |
|   |                                                                         |
|   +-- carrier_info/            # Carrier-specific information               |
|   |   +-- att.md               # ATT band configs, known issues             |
|   |   +-- verizon.md           # Verizon band configs                       |
|   |   +-- tmobile.md           # T-Mobile band configs                      |
|   |                                                                         |
|   +-- known_issues/            # Common issues and solutions                |
|   |   +-- anomaly_patterns.md  # Known anomaly patterns                     |
|   |   +-- troubleshooting.md   # Common troubleshooting steps               |
|   |                                                                         |
|   +-- mdb_docs/                # MDB-related documentation                  |
|       +-- MDB_Understanding.md # MDB structure and usage                    |
|       +-- mcc_country_map.md   # MCC to country mapping                     |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### 15.3 Knowledge Index

A JSON index file that catalogs all knowledge base content for quick lookup:

**knowledge_index.json:**
```json
{
  "version": "1.0",
  "last_updated": "2026-01-07",
  "entries": [
    {
      "id": "kb001",
      "title": "MDB Understanding",
      "file": "mdb_docs/MDB_Understanding.md",
      "topics": ["mdb", "mcc2bands", "band_filtering", "auto_learning"],
      "keywords": ["0-indexed", "mcc", "location", "policyman"],
      "use_for": ["mdb_anomalies", "band_filtering_issues"]
    },
    {
      "id": "kb002",
      "title": "NR Band n75 SDL Issues",
      "file": "known_issues/n75_sdl.md",
      "topics": ["nr_bands", "sdl", "anomaly"],
      "keywords": ["n75", "1500MHz", "supplemental_downlink"],
      "use_for": ["n75_anomaly"]
    },
    {
      "id": "kb003",
      "title": "ATT Carrier Configuration",
      "file": "carrier_info/att.md",
      "topics": ["carrier", "att", "band_exclusions"],
      "keywords": ["firstnet", "b14", "b29", "carrier_policy"],
      "use_for": ["carrier_filtering", "att_issues"]
    }
  ]
}
```

### 15.4 How Knowledge Base is Used

```
+------------------+     +-------------------+     +--------------------+
|  User adds       |     |  Knowledge Base   |     |  Analysis          |
|  Qualcomm docs   | --> |  Indexer scans    | --> |  Tools use KB      |
|  to KB folder    |     |  and updates JSON |     |  for insights      |
+------------------+     +-------------------+     +--------------------+
                                                            |
                         +----------------------------------+
                         |
          +--------------+---------------+
          |                              |
          v                              v
+-------------------+          +-------------------+
| STAGE 1: Code     |          | STAGE 2: Claude   |
|                   |          |                   |
| - Parsing rules   |          | - prompt.txt      |
|   from KB         |          |   includes        |
| - Known patterns  |          |   relevant KB     |
| - Band specs      |          |   excerpts        |
+-------------------+          +-------------------+
```

### 15.5 Integration with prompt.txt

When anomalies are detected, relevant KB content is included in prompt.txt:

```
================================================================================
                    BAND ANALYSIS - CLAUDE REVIEW REQUEST
================================================================================

... [SECTION 1-3 as before] ...

--------------------------------------------------------------------------------
SECTION 5: RELEVANT KNOWLEDGE BASE CONTEXT
--------------------------------------------------------------------------------

[KB: MDB Understanding]
MDB uses 0-indexed bands for LTE: MDB value 0 = B1, value 2 = B3
NR bands appear to be 1-indexed (actual band numbers)
Auto-learning can add bands not originally in mcc2bands.xml

[KB: NR Band n75 SDL Issues]
Band n75 (1500 MHz) is Supplemental Downlink only.
Common issue: n75 appearing without RFC support indicates:
- Wrong RFC file for device variant
- MBN override adding unsupported band
- EFS persisted items corruption

[KB: ATT Carrier Configuration]
ATT typically excludes: B7 (GW), B8, B9 for US market
FirstNet uses B14 exclusively
...

--------------------------------------------------------------------------------
SECTION 6: REVIEW INSTRUCTIONS
--------------------------------------------------------------------------------
Use the above knowledge base context to enhance your analysis.
================================================================================
```

### 15.6 Knowledge Base Management

| Operation | Command/Action |
|-----------|----------------|
| **Add document** | Place file in appropriate KB subfolder |
| **Update index** | Run `python kb_indexer.py` to refresh knowledge_index.json |
| **Search KB** | `python kb_search.py --query "n75 anomaly"` |
| **View KB stats** | `python kb_indexer.py --stats` |

### 15.7 Updated Architecture Components

```
Band_Combos_Analyzer/
|
+-- docs/
|   +-- knowledge_base/              # NEW: Knowledge Base folder
|   |   +-- qualcomm_kbas/
|   |   +-- band_specifications/
|   |   +-- carrier_info/
|   |   +-- known_issues/
|   |   +-- mdb_docs/
|   |   +-- knowledge_index.json     # KB index file
|   |
|   +-- Architecture_Design.md
|   +-- MDB_Understanding.md
|
+-- src/
|   +-- knowledge/                   # NEW: KB management modules
|   |   +-- __init__.py
|   |   +-- kb_indexer.py            # Index KB documents
|   |   +-- kb_search.py             # Search KB for relevant content
|   |   +-- kb_loader.py             # Load KB content for prompt
|   |
|   +-- parsers/
|   +-- core/
|   +-- output/
|   +-- main.py
```

---

## 16. Open Questions

1. **Combo Analysis**: What specific combo information is needed? (Future phase)

---

## 17. Next Steps

1. [x] Review architecture document
2. [x] Document MDB understanding
3. [x] Define Claude integration approach (prompt.txt -> Claude CLI)
4. [x] Design Knowledge Base architecture
5. [ ] Begin implementation when approved

---

*Document Version: 2.8*
*Last Updated: Added MCFG NV Band Preference parsing (Section 6.9) - SW-level band filtering from NV items*
*Status: IMPLEMENTATION IN PROGRESS*
