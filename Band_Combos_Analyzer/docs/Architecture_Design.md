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

## 3. Two-Stage Analysis Architecture

### 3.1 High-Level Flow

```
+-----------------------------------------------------------------------------+
|                         BAND ANALYZER TOOL                                  |
+-----------------------------------------------------------------------------+
|                                                                             |
|   STAGE 1: Python Code                    STAGE 2: Claude CLI               |
|   +---------------------------+           +---------------------------+     |
|   |                           |           |                           |     |
|   |  Input Documents          |           |  claude -p \              |     |
|   |        |                  |           |    --dangerously-skip-    |     |
|   |        v                  |           |    permissions            |     |
|   |  Parsers + Band Tracer    |  ------>  |    < prompt.txt           |     |
|   |        |                  | prompt.txt|                           |     |
|   |        v                  |           |        |                  |     |
|   |  Generate prompt.txt      |           |        v                  |     |
|   |                           |           |  Claude's Expert Review   |     |
|   +---------------------------+           +---------------------------+     |
|                                                    |                        |
|                                                    v                        |
|                                           +------------------+              |
|                                           |  FINAL OUTPUT    |              |
|                                           |  (Console + HTML)|              |
|                                           +------------------+              |
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
# Step 1: Run Python tool to generate prompt
python band_analyzer.py --rfc rfc.xml --hw hw_filter.xml ... --output prompt.txt

# Step 2: Pipe prompt to Claude CLI for review
claude -p --dangerously-skip-permissions < prompt.txt > claude_review.txt

# Step 3: (Optional) Generate final HTML report
python generate_report.py --stage1 prompt.txt --stage2 claude_review.txt
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
| 5 | **MDB Config** | XML/MDB | MCC-based band filtering | MDB filter stage skipped |
| 6 | **QXDM Log Prints** | TXT/Log | 0x1CCA PM RF Band logs | Cannot verify actual device state |
| 7 | **UE Capability Info** | TXT/Log | Final bands reported to network | Cannot verify network-reported bands |

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
|  [MDB]      --> If missing: "MDB skipped - cannot verify         |
|                 location-based filtering"                         |
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

    +-------+     +----------+     +---------+     +---------+     +-----+
    |  RFC  | --> | HW Filter| --> | Carrier | --> | Generic | --> | MDB |
    +-------+     +----------+     | Policy  |     | Restr.  |     +-----+
                                   +---------+     +---------+        |
                                                                      |
         +------------------------------------------------------------+
         |
         v
    +----------+     +---------+
    | QXDM Log | --> | UE Cap  |
    | Prints   |     | Info    |
    +----------+     +---------+

    Stage 1       Stage 2          Stage 3         Stage 4        Stage 5
    (Source)      (Hardware)       (Operator)      (Regulatory)   (Location)

                  Stage 6          Stage 7
                  (Device Log)     (Final/Network)
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
| **MDB Parser** | Parse mcc2bands, extract bands per MCC |
| **QXDM Log Parser** | Decode 0x1CCA hex bitmasks to bands |
| **UE Capability Parser** | Extract bandEUTRA, bandNR values |
| **Band Tracer Engine** | Compare bands across all stages |

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
        "MDB": True,
        "QXDM": True,
        "UE_Cap": True
    },
    "status": "ENABLED",
    "filtered_at": None,
    "anomaly": None
}
```

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
Band   RFC    HW     Carrier  Generic  MDB    QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
B1     PASS   PASS   N/A      PASS     PASS   PASS   PASS     ENABLED
B7     PASS   PASS   N/A      PASS     PASS   FAIL   FAIL     MISSING_IN_QXDM
B38    PASS   PASS   N/A      PASS     PASS   PASS   PASS     ENABLED
...

NR SA BAND TRACING:
Band   RFC    HW     Carrier  Generic  MDB    QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
n1     PASS   PASS   N/A      PASS     PASS   PASS   PASS     ENABLED
n75    FAIL   PASS   N/A      PASS     PASS   PASS   PASS     ANOMALY
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
Band   RFC    HW     Carrier  Generic  MDB    QXDM   UE_Cap   Status
--------------------------------------------------------------------------------
n1     PASS   PASS   PASS     PASS     PASS   PASS   PASS     ENABLED
n38    PASS   PASS   PASS     PASS     PASS   PASS   PASS     ENABLED
n75    FAIL   PASS   PASS     PASS     PASS   PASS   PASS     ANOMALY!
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

### 8.2 HTML Output (Downloadable)

HTML report with:
- Color-coded band status (Green/Yellow/Red)
- Expandable Claude review sections per band
- Summary dashboard
- Downloadable for offline review

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
Stage 5 - MDB (mcc2bands):      PASS  (Allowed for MCC 310)
Stage 6 - QXDM Log (0x1CCA):    PASS  <-- Present in log!
Stage 7 - UE Capability:        PASS  <-- Reported to network!

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
|   |   +-- html_report.py            # HTML report generator (combines Stage 1 + 2)
|   |
|   +-- main.py                       # Main entry point (Stage 1)
|   +-- generate_report.py            # Combine Stage 1 + Stage 2 into HTML
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

**run_analysis.sh** (Linux/Mac) or **run_analysis.bat** (Windows):

```bash
#!/bin/bash
# Full Band Analysis Pipeline

echo "=== STAGE 1: Running Python Analysis ==="
python src/main.py \
    --rfc input/rfc.xml \
    --hw-filter input/hw_band_filtering.xml \
    --carrier input/carrier_policy.xml \
    --generic input/generic_restrictions.xml \
    --mdb input/mcc2bands.xml \
    --qxdm input/qxdm_log.txt \
    --ue-cap input/ue_capability.txt \
    --output output/prompt.txt

echo ""
echo "=== STAGE 2: Claude CLI Review ==="
claude -p --dangerously-skip-permissions < output/prompt.txt > output/claude_review.txt

echo ""
echo "=== STAGE 3: Generating HTML Report ==="
python src/generate_report.py \
    --stage1 output/prompt.txt \
    --stage2 output/claude_review.txt \
    --output output/band_analysis_report.html

echo ""
echo "=== COMPLETE ==="
echo "Report: output/band_analysis_report.html"
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

## 15. Open Questions

1. **Combo Analysis**: What specific combo information is needed? (Future phase)

---

## 16. Next Steps

1. [x] Review architecture document
2. [x] Document MDB understanding
3. [x] Define Claude integration approach (prompt.txt -> Claude CLI)
4. [ ] Begin implementation when approved

---

*Document Version: 2.2*
*Last Updated: Added QXDM log input section with QCAT future enhancement*
*Status: PENDING FINAL REVIEW*
