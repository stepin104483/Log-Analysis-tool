# Bands & Combos Analyzer Tool - Architecture Design

## 1. Overview

A tool to analyze band filtering from RF Card (RFC) through various configuration layers to final UE Capability, identifying where each band passes or gets filtered.

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
|  | 3. Carrier Policy      [Browse]|  [ANALYZE] |  Band | Status     |   |
|  +--------------------------------+     ||     |  -----|--------    |   |
|  | 4. Generic Restriction [Browse]|     \/     |  B1   | PASS       |   |
|  +--------------------------------+            |  B7   | FILTERED   |   |
|  | 5. MDB Config          [Browse]|            |  ...  | ...        |   |
|  +--------------------------------+            |                    |   |
|  | 6. QXDM Log Prints     [Browse]|            +--------------------+   |
|  +--------------------------------+                                     |
|  | 7. UE Capability Info  [Browse]|            [Download HTML Report]   |
|  +--------------------------------+                                     |
+-------------------------------------------------------------------------+
```

---

## 3. Input Files

| # | Document | File Type | Purpose | Required |
|---|----------|-----------|---------|----------|
| 1 | **RFC** | XML | RF Card supported bands (source of truth) | YES |
| 2 | **HW Band Filtering** | XML | Hardware-level band restrictions | YES |
| 3 | **Carrier Policy** | XML | Operator-specific band rules | YES |
| 4 | **Generic Restrictions** | XML | Regulatory restrictions (FCC, etc.) | YES |
| 5 | **MDB Config** | TBD | MDB band configuration | Optional |
| 6 | **QXDM Log Prints** | TXT/Log | 0x1CCA PM RF Band logs, other QXDM prints | Optional |
| 7 | **UE Capability Info** | TXT/Log | Final bands reported to network | YES |

---

## 4. Filtering Pipeline

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
    (Source)      (Hardware)       (Operator)      (Regulatory)   (Config)

                  Stage 6          Stage 7
                  (Device Log)     (Final/Network)
```

### Stage Details

| Stage | Name | Filter Logic | Example |
|-------|------|--------------|---------|
| 1 | RFC | Starting bands from RF Card | 31 LTE, 26 NR bands |
| 2 | HW Filter | Bitwise AND with allowed ranges | Remove mmWave bands |
| 3 | Carrier Policy | Remove excluded bands per carrier | ATT excludes GW 7,8,9 |
| 4 | Generic Restriction | Remove regulatory-blocked bands | FCC excludes B6, B37 |
| 5 | MDB | Additional MDB-based filtering | TBD |
| 6 | QXDM Log Prints | Actual bands on device (0x1CCA, etc.) | Verify device state |
| 7 | UE Capability | Final bands reported to network | Match expected bands |

---

## 5. Output Format

### 5.1 Console Output (Primary - Displayed on Screen)

```
================================================================================
                         BAND ANALYSIS REPORT
================================================================================

BAND TRACING - LTE
-----------------------------------------------------------------------------------
Band   RFC    HW     Carrier  Generic  MDB    QXDM   UE_Cap   Status      Filtered At
-----------------------------------------------------------------------------------
B1     PASS   PASS   PASS     PASS     PASS   PASS   PASS     ENABLED     -
B7     PASS   PASS   FAIL     -        -      -      -        FILTERED    Carrier Policy
B12    PASS   PASS   PASS     PASS     PASS   PASS   PASS     ENABLED     -
B37    PASS   PASS   PASS     FAIL     -      -      -        FILTERED    Generic (FCC)
-----------------------------------------------------------------------------------

BAND TRACING - NR SA
-----------------------------------------------------------------------------------
Band   RFC    HW     Carrier  Generic  MDB    QXDM   UE_Cap   Status      Filtered At
-----------------------------------------------------------------------------------
n1     PASS   PASS   PASS     PASS     PASS   PASS   PASS     ENABLED     -
n12    PASS   FAIL   -        -        -      -      -        FILTERED    HW Filter
n75    FAIL   -      -        -        -      PASS   PASS     ANOMALY     Not in RFC!
-----------------------------------------------------------------------------------

*** ANOMALIES DETECTED ***
- n75: Present in QXDM/UE Cap but NOT in RFC!
================================================================================
```

### 5.2 HTML Output (Downloadable Report)

```html
<table class="band-analysis">
  <tr class="enabled"><td>B1</td><td>PASS</td>...<td>ENABLED</td></tr>
  <tr class="filtered"><td>B7</td><td>PASS</td>...<td>FILTERED</td></tr>
  <tr class="anomaly"><td>n75</td><td>FAIL</td>...<td>ANOMALY</td></tr>
</table>
```

Color coding in HTML:
- **Green**: ENABLED (passes all stages)
- **Yellow**: FILTERED (blocked at some stage)
- **Red**: ANOMALY (unexpected behavior)

---

## 6. Single Band Trace Feature

User can trace a specific band through all stages:

```
Input: LTE 7

================================================================================
TRACING LTE BAND 7
================================================================================

Stage 1 - RFC (RF Card):
  Status: PASS
  Detail: Band B7 found in RFC XML

Stage 2 - HW Band Filtering:
  Status: PASS
  Detail: Band 7 in allowed range (0-255)

Stage 3 - Carrier Policy (ATT):
  Status: FAIL  <-- FILTERED HERE
  Detail: Band 7 in exclusion list for GW bands

Stage 4 - Generic Restriction:
  Status: SKIPPED (already filtered)

Stage 5 - MDB:
  Status: SKIPPED (already filtered)

Stage 6 - QXDM Log Prints:
  Status: NOT PRESENT (as expected - filtered earlier)

Stage 7 - UE Capability:
  Status: NOT PRESENT (as expected - filtered earlier)

================================================================================
RESULT: Band B7 FILTERED at Stage 3 (Carrier Policy)
================================================================================
```

---

## 7. Architecture Components

```
Band_Analyse_tool/
|
+-- requirements/
|   +-- Basic_design_Image.jfif       # Reference UI design
|
+-- docs/
|   +-- Architecture_Design.md        # This document
|
+-- src/
|   +-- parsers/
|   |   +-- rfc_parser.py             # Parse RFC XML
|   |   +-- hw_filter_parser.py       # Parse hardware_band_filtering.xml
|   |   +-- carrier_policy_parser.py  # Parse carrier_policy.xml
|   |   +-- generic_restriction_parser.py
|   |   +-- mdb_parser.py             # Parse MDB (TBD)
|   |   +-- qxdm_log_parser.py        # Parse 0x1CCA and other QXDM logs
|   |   +-- ue_capability_parser.py   # Parse UE Capability logs
|   |
|   +-- core/
|   |   +-- band_tracer.py            # Core tracing engine
|   |   +-- analyzer.py               # Analysis logic
|   |
|   +-- output/
|   |   +-- console_report.py         # Console output generator
|   |   +-- html_report.py            # HTML report generator
|   |
|   +-- main.py                       # Main entry point
|
+-- templates/
|   +-- report_template.html          # HTML report template
|
+-- output/
|   +-- (generated HTML reports)
```

---

## 8. Data Flow

```
+------------------------------------------------------------------+
|                         USER INPUT                                |
|    (Upload 7 Document Files via Browse)                          |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                          PARSERS                                  |
|  +--------+  +--------+  +--------+  +--------+  +--------+      |
|  |  RFC   |  |   HW   |  |Carrier |  |Generic |  |  MDB   |      |
|  | Parser |  | Filter |  | Policy |  | Restr. |  | Parser |      |
|  +--------+  +--------+  +--------+  +--------+  +--------+      |
|                                                                   |
|  +------------------+     +--------------------+                  |
|  |  QXDM Log        |     |  UE Capability     |                  |
|  |  Parser          |     |  Parser            |                  |
|  |  (0x1CCA, etc.)  |     |  (bandEUTRA,       |                  |
|  +------------------+     |   bandNR, etc.)    |                  |
|                           +--------------------+                  |
+------------------------------------------------------------------+
         |
         | Extracted Band Sets from Each Source
         v
+------------------------------------------------------------------+
|                      BAND TRACER ENGINE                           |
|                                                                   |
|   For each band:                                                  |
|   +-----------------------------------------------------------+  |
|   | RFC -> HW Filter -> Carrier -> Generic -> MDB -> QXDM ->  |  |
|   |                                            UE Capability  |  |
|   +-----------------------------------------------------------+  |
|                                                                   |
|   Determine: PASS / FAIL at each stage                           |
|   Identify: Where band got filtered or if ANOMALY exists         |
+------------------------------------------------------------------+
         |
         |
         +-----------------------------+
         |                             |
         v                             v
+------------------+         +--------------------+
|  CONSOLE OUTPUT  |         |    HTML REPORT     |
|  (Display on     |         |    (Downloadable)  |
|   Screen)        |         |                    |
+------------------+         +--------------------+
         |                             |
         v                             v
   [User Views                  [User Downloads
    Analysis in                  HTML File for
    Terminal]                    Offline Review]
```

### Data Sources Explained

| Source | Parser Output | Usage |
|--------|---------------|-------|
| **RFC XML** | Set of supported LTE & NR bands | Starting point (ground truth) |
| **HW Filter XML** | Allowed band ranges | Filter against RFC bands |
| **Carrier Policy XML** | Excluded bands per carrier | Filter based on operator rules |
| **Generic Restriction XML** | Regulatory blocked bands | Filter based on FCC/region |
| **MDB Config** | MDB band configuration | Additional filtering (TBD) |
| **QXDM Log Prints** | 0x1CCA hex bitmasks, other logs | Actual device state verification |
| **UE Capability Info** | bandEUTRA, bandNR values | Final network-reported bands |

### Verification Points

```
CONFIG FILES (Expected)              DEVICE LOGS (Actual)
+-----------------------+            +-----------------------+
| RFC                   |            |                       |
| HW Filter             |  Compare   | QXDM Logs (0x1CCA)    |
| Carrier Policy        | ========> | UE Capability Info    |
| Generic Restriction   |            |                       |
| MDB                   |            |                       |
+-----------------------+            +-----------------------+
         |                                      |
         v                                      v
    Expected Bands                        Actual Bands
         |                                      |
         +----------------+---------------------+
                          |
                          v
                   ANOMALY DETECTION
                   (Mismatch = Issue)
```

---

## 9. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| XML Parsing | xml.etree.ElementTree |
| Log Parsing | Regular Expressions (re) |
| HTML Generation | Jinja2 templates |
| CLI Interface | argparse / simple input |
| Console Output | Print to terminal |
| HTML Output | Generated file (downloadable) |

---

## 10. Phase 1 Scope (Current)

| Feature | Status |
|---------|--------|
| RFC XML parsing | In Scope |
| HW Band Filtering parsing | In Scope |
| Carrier Policy parsing | In Scope |
| Generic Restriction parsing | In Scope |
| MDB parsing | Pending (need Qualcomm doc) |
| QXDM Log parsing (0x1CCA, etc.) | In Scope |
| UE Capability parsing | In Scope |
| Single band trace | In Scope |
| Console output (display) | In Scope |
| HTML output (download) | In Scope |
| Full band analysis | In Scope |
| Combo analysis | Future Phase |

---

## 11. Open Questions

1. **MDB Format**: What is the structure of MDB files? (Awaiting Qualcomm document)
2. **QXDM Logs**: Which specific QXDM log packets besides 0x1CCA are needed?
3. **Combo Analysis**: What specific combo information is needed? (Future phase)
4. **Additional Filters**: Any other filtering stages beyond the 7 mentioned?

---

## 12. Next Steps

1. [ ] Review this architecture document
2. [ ] Share MDB Qualcomm document for parser development
3. [ ] Confirm list of QXDM log packets to parse
4. [ ] Approve architecture and proceed with implementation

---

*Document Version: 1.1*
*Last Updated: Based on review feedback*
*Status: PENDING REVIEW*
