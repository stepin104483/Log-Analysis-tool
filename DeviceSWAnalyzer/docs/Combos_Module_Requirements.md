# Combos Module Requirements Document

**Document Version:** 1.2
**Date:** January 2026
**Status:** Draft (Updated with RFPD Report Integration)
**Related Research:** [CA_ENDC_NRDC_NRCA_research_document.md](./CA_ENDC_NRDC_NRCA_research_document.md)

---

## 1. Executive Summary

### 1.1 Purpose
The Combos Module enables analysis of Carrier Aggregation (CA) and Dual Connectivity (DC) combo support across different sources, identifying which combos are supported and **where exactly they are filtered** - similar to the Bands module's band filtering analysis.

### 1.2 Scope
- Parse and analyze combos from RFC, UE Capability, and related logs
- Classify combos by type: LTE CA, NR CA (NRCA), EN-DC, NR-DC
- Compare combos across sources to identify gaps
- Generate HTML reports showing combo support status and filtering points

### 1.3 Key Goals
| Goal | Description |
|------|-------------|
| **Identify Supported Combos** | Parse all combo sources and consolidate support status |
| **Identify Filtering Points** | Determine WHERE a combo is filtered (RFC, Carrier Policy, UE Cap, Network) |
| **Classify Combos** | Categorize by type: LTE CA, NRCA, EN-DC, NR-DC |
| **Generate Reports** | Visual HTML reports similar to Band Analysis output |

---

## 2. Input Sources

### 2.1 Primary Sources

| Source | File Type | Combo Types | Purpose |
|--------|-----------|-------------|---------|
| **RFC XML** | `.xml` | LTE CA, NRCA, EN-DC | RF Hardware supported combos |
| **UE Capability Log** | `.txt` (QXDM) | LTE CA, NRCA, EN-DC, NR-DC | Combos UE advertises to network |
| **Carrier Policy** | `.xml` | Band-level | Indirect combo filtering via bands |
| **QXDM 0xB826** | `.txt` | All types | RRC Table (RF-supported after envelope check) |
| **QXDM 0xB0C0** | `.txt` | All types | UECapabilityEnquiry/Information messages |
| **RFPD Report** | `.html` | All types | Envelope check ground truth (pre/post filtering counts) |

### 2.2 RFC XML Combo Structure

```xml
<ca_combo_list>
  <combo_group target="CAMANO" sku="camano-0">
    <cards_supported>
      <card_name>rfc_hwid966_Q6515_v2_APT_ag</card_name>
    </cards_supported>
    <sub_capability>HIGH</sub_capability>

    <!-- LTE CA Combos -->
    <ca_4g_combos>
      <ca_combo>B1A[4];A[1]</ca_combo>
      <ca_combo>B1A[4];A[1]+B3A[4];A[1]</ca_combo>
      <ca_combo>B1A[4]+B1A[4]+B3C[4,4];C[1,1]</ca_combo>
    </ca_4g_combos>

    <!-- NR CA (5G SA) Combos -->
    <ca_5g_combos>
      <ca_combo pc="2">N77A[100x4];A[100x1]</ca_combo>
      <ca_combo pc="2">N78C[100x4,100x4];A[100x1]</ca_combo>
    </ca_5g_combos>

    <!-- EN-DC (4G+5G NSA) Combos -->
    <ca_4g_5g_combos>
      <ca_combo>B1A[4];A[1]+N77A[100x4];A[100x1]</ca_combo>
      <ca_combo pc="2">B66A[4];A[1]+N77A[100x4];A[100x1]</ca_combo>
    </ca_4g_5g_combos>
  </combo_group>
</ca_combo_list>
```

### 2.3 UE Capability Combo Structure (from QXDM)

```
supportedBandCombinationList
{
  {
    bandList
    {
      nr :
        {
          bandNR 77,
          ca-BandwidthClassDL-NR c,
          ca-BandwidthClassUL-NR a
        }
    },
    featureSetCombination 1,
    powerClass-v1530 pc2
  },
  {
    bandList
    {
      nr :
        {
          bandNR 77,
          ca-BandwidthClassDL-NR a,
          ca-BandwidthClassUL-NR a
        },
      nr :
        {
          bandNR 77,
          ca-BandwidthClassDL-NR a
        }
    },
    featureSetCombination 0
  }
}
```

### 2.4 QXDM 0xB826 Log Structure (RRC Supported CA Combos)

The **0xB826 (NR5G RRC Supported CA Combos)** log packet contains combos in the RRC Table after envelope check. This is the **intermediate filtering stage** between RFC and UE Capability.

**Log Header:**
```
0xB826  NR5G RRC Supported CA Combos
Subscription ID = 1
Misc ID         = 0
Version = 14
Total Num Combos = 817
starting_index = 0
```

**Record Structure (tabular format):**
```
| Idx | Valid | Bands | RAT | DL Class    | DL Antenna   | UL Class    | UL Antenna   | SRS Switching | SCS    | DL BW      | UL BW      |
|-----|-------|-------|-----|-------------|--------------|-------------|--------------|---------------|--------|------------|------------|
|   0 |  true |    2  |  NR | CLASS_A     | ANTENNA_4    | CLASS_A     | ANTENNA_1    | SRS_T1_R4     | SCS_30 | BW_100     | BW_100     |
|   1 |  true |    2  | LTE | CLASS_A     | ANTENNA_4    | CLASS_A     | ANTENNA_1    | SRS_UNSUPPORTED| SCS_15 | BW_20      | BW_20      |
|   2 |  true |    2  |  NR | CLASS_C     | ANTENNA_2_2  | CLASS_A     | ANTENNA_1    | SRS_T1_R4     | SCS_30 | BW_20_20   | BW_100     |
```

**Key Fields:**
| Field | Description | Values |
|-------|-------------|--------|
| **Idx** | Combo index | 0 to Total Num Combos - 1 |
| **Bands** | Number of bands in combo | 1, 2, 3, etc. |
| **RAT** | Radio Access Technology | NR, LTE |
| **DL Class** | Downlink bandwidth class | CLASS_A, CLASS_B, CLASS_C, etc. |
| **DL Antenna** | DL MIMO configuration | ANTENNA_2, ANTENNA_4, ANTENNA_2_2 |
| **UL Class** | Uplink bandwidth class | CLASS_A, CLASS_NONE |
| **UL Antenna** | UL MIMO configuration | ANTENNA_1, ANTENNA_2, INVALID |
| **SRS Switching** | SRS antenna switching | SRS_T1_R4, SRS_T2_R4, SRS_UNSUPPORTED |
| **SCS** | Subcarrier spacing | SCS_15 (LTE), SCS_30 (NR) |
| **DL BW** | Downlink bandwidth | BW_20, BW_100, BW_20_20 (contiguous) |
| **UL BW** | Uplink bandwidth | BW_20, BW_100, BW_DEFAULT |

**Multi-band Combo Example (EN-DC):**
```
| Idx | Bands | Entry | RAT | Band | DL Class | DL Antenna | UL Class | UL Antenna | SRS        | BW     |
|-----|-------|-------|-----|------|----------|------------|----------|------------|------------|--------|
|  99 |     2 |     0 | LTE |    1 | CLASS_A  | ANTENNA_4  | CLASS_A  | ANTENNA_1  | UNSUPPORTED| BW_20  |
|     |       |     1 |  NR |   78 | CLASS_A  | ANTENNA_4  | CLASS_A  | ANTENNA_1  | SRS_T1_R4  | BW_100 |
```

**Why 0xB826 is Critical:**
- Shows **817 combos** in RRC table (after envelope check)
- Intermediate stage: RFC → **0xB826** → UE Capability
- Helps identify if combo is filtered at envelope check vs later stages

---


### 2.5 RFPD Report Structure (Optional - Enhanced Analysis)

The **RFPD (RF Path Director) Report** provides ground truth for envelope check filtering. When available, it enables precise identification of combos filtered at the envelope check stage.

**Key RFPD Report Files:**

| File Pattern | Content | Purpose |
|--------------|---------|---------|
| `rfpd_report_index.html` | Main report index | Navigation to all sub-reports |
| `RFC_*_env_combos.html` | Envelope combos | Pre-envelope check combo list with limits |
| `RFC_*_rrc_combos.html` | RRC Table combos | Post-envelope check combos (matches 0xB826) |
| `warning_combos_*.html` | Warning combos | Combos that failed resource allocation |
| `*_superset_ag.xml` | Superset XML | Post-envelope combos in XML format |

**Sample RFPD Statistics (from actual report):**

| Combo Type | Combos Processed | Combos Advertised | Failed | Notes |
|------------|------------------|-------------------|--------|-------|
| **LTE CA** | 3,866 | ~3,800 | 0 | Pure LTE combos |
| **NR5G (NRCA)** | 1,077 → 640 unique | 616 | 0 | After duplicate/subset rollup |
| **LTE_NR5G (EN-DC)** | 1,667 → 983 unique | 817 | 1 | **Matches 0xB826 count!** |

**Envelope Rules Information:**
- Envelope Used: e.g., "DenaliA CS3.1 camano-0"
- Max limits per config: CC count, BW, Layers, MCS for Sub6/mmW/LTE

**RFPD RRC Table Data Fields:**
```
| Combo | 3GPP Combo | Power Class | Band Num | tech | band | dl_bw_class | dl_bw_per_cc | dl_max_antennas_index | ul_bw_class | ul_bw_per_cc | ul_max_antennas_index | ul_qam_cap_index | srs_tx_switch_type | tx_switch_impact_to_rx | max_scs | BCS Num | Tx Switching | simrxtx ENDC,CA,BMAP |
```

**Integration Value:**
1. **Validation**: Verify 0xB826 count matches RFPD advertised count (817 = 817 ✓)
2. **Root Cause**: If combo missing from 0xB826, check RFPD warning/failed combos
3. **Envelope Limits**: Understand max CC, BW, Layers per configuration
4. **Superset Mapping**: Know which combos use superset resources

---

## 3. Combo Types and Classification

### 3.1 Combo Type Definitions

| Type | Description | RFC Section | Example |
|------|-------------|-------------|---------|
| **LTE CA** | Pure 4G carrier aggregation | `<ca_4g_combos>` | `B1A[4];A[1]+B3A[4];A[1]` |
| **NRCA** | Pure 5G NR carrier aggregation | `<ca_5g_combos>` | `N77C[100x4,100x4];A[100x1]` |
| **EN-DC** | LTE + NR dual connectivity (5G NSA) | `<ca_4g_5g_combos>` | `B1A[4];A[1]+N77A[100x4];A[100x1]` |
| **NR-DC** | NR + NR dual connectivity (FR1+FR2) | `<nr_dc_combos>` | `N77A[100x4];A[100x1]+N257A[400x4];A[400x1]` |

### 3.2 Classification Logic

```
IF combo contains only "B" prefixed bands:
    Type = LTE_CA
ELSE IF combo contains only "N" prefixed bands:
    IF combo has FR1 + FR2 bands (different frequency ranges):
        Type = NR_DC
    ELSE:
        Type = NRCA
ELSE IF combo contains both "B" and "N" prefixed bands:
    Type = EN_DC
```

### 3.3 Detection Rules

| Pattern | Classification |
|---------|----------------|
| `B\d+` only | LTE CA |
| `N\d+` only (same FR) | NRCA |
| `N\d+` (FR1) + `N\d+` (FR2) | NR-DC |
| `B\d+` + `N\d+` | EN-DC |

---

## 4. Combo Parsing Requirements

### 4.1 Qualcomm RFC Format Parser

**Input Format:** `B1A[4];A[1]+B3A[4];A[1]+N77A[100x4];A[100x1]`

**Parsed Output:**
```python
{
    "raw_string": "B1A[4];A[1]+B3A[4];A[1]+N77A[100x4];A[100x1]",
    "combo_type": "EN_DC",
    "bands": [
        {
            "rat": "LTE",
            "band": 1,
            "dl_class": "A",
            "dl_mimo": 4,
            "ul_class": "A",
            "ul_mimo": 1
        },
        {
            "rat": "LTE",
            "band": 3,
            "dl_class": "A",
            "dl_mimo": 4,
            "ul_class": "A",
            "ul_mimo": 1
        },
        {
            "rat": "NR",
            "band": 77,
            "dl_class": "A",
            "dl_bw": 100,
            "dl_mimo": 4,
            "ul_class": "A",
            "ul_bw": 100,
            "ul_mimo": 1
        }
    ],
    "attributes": {
        "power_class": None,
        "srs_ant_switch": None
    }
}
```

### 4.2 Qualcomm RFC Notation Patterns

| Component | Pattern | Example | Meaning |
|-----------|---------|---------|---------|
| LTE Band | `B\d+` | `B1`, `B66` | LTE Band number |
| NR Band | `N\d+` | `N77`, `N78` | NR Band number |
| BW Class (LTE) | `[A-F]` | `A`, `C` | Bandwidth class |
| BW Class (NR) | `[A-Q]` | `A`, `C`, `G` | Bandwidth class |
| MIMO DL | `\[\d+\]` or `\[\d+x\d+\]` | `[4]`, `[100x4]` | MIMO layers or BW×MIMO |
| MIMO UL | `;\w+\[\d+\]` | `;A[1]`, `;A[100x1]` | UL class and MIMO |
| Contiguous | `C\[\d+,\d+\]` | `C[4,4]`, `C[100x4,100x4]` | Contiguous 2CC |
| Band Separator | `+` | `+` | Between bands |
| DL/UL Separator | `;` | `;` | DL;UL within band |

### 4.3 UE Capability Format Parser

**Input:** ASN.1 decoded text from QXDM

**Extract:**
- `bandNR` / `bandEUTRA` - Band number
- `ca-BandwidthClassDL-NR` / `ca-BandwidthClassDL-EUTRA` - DL BW class
- `ca-BandwidthClassUL-NR` / `ca-BandwidthClassUL-EUTRA` - UL BW class
- `powerClass-v1530` - Power class
- `featureSetCombination` - Feature set index

### 4.4 Contiguous Combo Notation

| RFC Format | Meaning | 3GPP Equivalent |
|------------|---------|-----------------|
| `B3C[4,4];C[1,1]` | LTE B3, Class C, 2×4 DL MIMO, 2×1 UL | CA_3C |
| `N77C[100x4,100x4]` | NR n77, Class C, 2×100MHz×4 MIMO | CA_n77C |
| `B7C[2,2];C[1,1]` | LTE B7, Class C, 2×2 DL MIMO, 2×1 UL | CA_7C |

---

## 5. Combo Filtering Analysis

### 5.1 Filtering Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COMBO FILTERING PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ SOURCE 1: RFC XML                                                    │    │
│  │ ├── All RF hardware supported combos                                 │    │
│  │ └── Sections: ca_4g_combos, ca_5g_combos, ca_4g_5g_combos           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                    │                                                        │
│                    ▼                                                        │
│  FILTER 1: Envelope Check (RFPD Processing)                                 │
│  ├── Compares combo requirements vs RF platform capabilities                │
│  ├── Checks: CC count, BW, MIMO layers, MCS                                │
│  └── Result: Combos that pass envelope check                                │
│                    │                                                        │
│                    ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ SOURCE 2: 0xB826 (RRC Table - After Envelope Check)    [KEY SOURCE] │    │
│  │ ├── Contains 817 combos (in sample)                                  │    │
│  │ ├── Intermediate stage between RFC and UE Capability                 │    │
│  │ └── Shows: Band, Class, MIMO, SRS, BW per combo                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                    │                                                        │
│                    ▼                                                        │
│  FILTER 2: Carrier Policy (Indirect)                                        │
│  ├── Bands enabled/disabled affect available combos                         │
│  ├── Example: If B1 disabled, all combos with B1 unavailable               │
│  └── Check: nr5g_sa_bands, nr5g_nsa_bands, lte_bands                       │
│                    │                                                        │
│                    ▼                                                        │
│  FILTER 3: RRC EFS Controls                                                 │
│  ├── cap_control_nrca_*, cap_control_mrdc_*                                 │
│  ├── Combo type enable/disable                                              │
│  └── cap_prune for bandwidth class pruning                                  │
│                    │                                                        │
│                    ▼                                                        │
│  FILTER 4: Band Preference NVs                                              │
│  ├── NV74213 (NR NSA), NV74087 (NR SA), NV74485 (NRDC)                      │
│  └── Band-level preference affecting combo availability                     │
│                    │                                                        │
│                    ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ SOURCE 3: UE Capability (What UE Advertises)                         │    │
│  │ ├── supportedBandCombinationList                                     │    │
│  │ └── Filtered combos after all device-side filtering                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                    │                                                        │
│                    ▼                                                        │
│  FILTER 5: Network UECapabilityEnquiry                                      │
│  ├── frequencyBandListFilter                                                │
│  └── Network requests specific bands, UE filters response                   │
│                    │                                                        │
│                    ▼                                                        │
│  OUTPUT: UECapabilityInformation (Final Advertised Combos)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Three-Source Comparison Model:**
```
RFC XML ──────────► 0xB826 (RRC Table) ──────────► UE Capability
  │                       │                              │
  │                       │                              │
  ▼                       ▼                              ▼
All HW combos      Post-envelope combos         Advertised combos
                   (817 in sample)
```

### 5.2 Filtering Points to Analyze

| Filter Point | Source | What to Check | Status Values |
|--------------|--------|---------------|---------------|
| **RFC Support** | RFC XML | Combo exists in ca_*_combos | Supported / Not Present |
| **RRC Table (0xB826)** | QXDM Log | Combo exists in 0xB826 log | In RRC Table / Filtered by Envelope |
| **Carrier Policy** | carrier_policy.xml | Bands in combo are enabled | Enabled / Disabled |
| **RRC EFS** | EFS files (if available) | Combo type not disabled | Enabled / Disabled |
| **Band Preference** | NV items (if available) | Bands not set to 0x00 | Preferred / Deprioritized |
| **UE Capability** | QXDM log | Combo in supportedBandCombinationList | Advertised / Not Advertised |
| **Network Filter** | UECapabilityEnquiry | Bands in frequencyBandListFilter | Requested / Not Requested |

### 5.3 Combo Status Classification

```python
class ComboStatus:
    RFC_SUPPORTED = "Supported in RFC"
    RFC_NOT_PRESENT = "Not in RFC"
    CARRIER_FILTERED = "Filtered by Carrier Policy"
    EFS_DISABLED = "Disabled by EFS Control"
    UE_CAP_PRESENT = "In UE Capability"
    UE_CAP_MISSING = "Missing from UE Capability"
    NETWORK_FILTERED = "Filtered by Network"
```

---

## 6. Functional Requirements

### 6.1 Core Functions

| ID | Function | Description | Priority |
|----|----------|-------------|----------|
| **FR-001** | Parse RFC Combos | Extract combos from RFC XML (all types) | High |
| **FR-002** | Parse UE Capability Combos | Extract combos from QXDM UE capability | High |
| **FR-003** | Parse 0xB826 Combos | Extract combos from RRC Table (QXDM 0xB826 log) | High |
| **FR-004** | Classify Combo Type | Determine LTE CA/NRCA/EN-DC/NR-DC | High |
| **FR-005** | Compare Sources (RFC vs 0xB826 vs UE Cap) | Identify combos filtered at each stage | High |
| **FR-006** | Identify Filtering Point | Determine where combo was filtered | High |
| **FR-007** | Generate HTML Report | Visual report with combo support matrix | High |
| **FR-008** | Parse Carrier Policy | Check if bands in combo are enabled | Medium |
| **FR-009** | Normalize Combo Format | Convert between RFC and 3GPP notation | Medium |
| **FR-010** | Parse RFPD Report | Extract envelope check results from RFPD HTML | Medium |

### 6.2 Parser Requirements

#### FR-001: RFC Combo Parser

**Input:** RFC XML file path
**Output:** List of parsed combo objects

```python
def parse_rfc_combos(rfc_path: str) -> Dict[str, List[Combo]]:
    """
    Parse all combos from RFC XML.

    Returns:
        {
            "lte_ca": [Combo, ...],
            "nrca": [Combo, ...],
            "endc": [Combo, ...],
            "nrdc": [Combo, ...]
        }
    """
```

#### FR-002: UE Capability Combo Parser

**Input:** QXDM log file with UECapabilityInformation
**Output:** List of parsed combo objects

```python
def parse_ue_capability_combos(log_path: str) -> Dict[str, List[Combo]]:
    """
    Parse combos from UE Capability in QXDM log.

    Sections to parse:
    - supportedBandCombination-r10 (LTE CA)
    - supportedBandCombinationList (NR/MR-DC)
    - supportedBandCombinationList-v1540
    - supportedBandCombinationList-v1610
    """
```

#### FR-003: 0xB826 RRC Table Combo Parser

**Input:** QXDM log file containing 0xB826 packets
**Output:** List of parsed combo objects with metadata

```python
@dataclass
class B826ComboRecord:
    """Single combo record from 0xB826 log."""
    index: int
    num_bands: int
    bands: List[B826BandEntry]

@dataclass
class B826BandEntry:
    """Single band entry within a 0xB826 combo."""
    rat: str                    # "NR" or "LTE"
    band: int                   # Band number
    dl_class: str               # "CLASS_A", "CLASS_C", etc.
    ul_class: str               # "CLASS_A", "CLASS_NONE"
    dl_antenna: str             # "ANTENNA_4", "ANTENNA_2_2"
    ul_antenna: str             # "ANTENNA_1", "INVALID"
    srs_switching: str          # "SRS_T1_R4", "SRS_UNSUPPORTED"
    scs: str                    # "SCS_15", "SCS_30"
    dl_bw: str                  # "BW_20", "BW_100", "BW_20_20"
    ul_bw: str                  # "BW_20", "BW_100", "BW_DEFAULT"

@dataclass
class B826LogMetadata:
    """Metadata from 0xB826 log header."""
    subscription_id: int
    misc_id: int
    version: int                # Log packet version (e.g., 14)
    total_num_combos: int       # Total combos in RRC table (e.g., 817)
    starting_index: int         # Starting index for this packet segment

def parse_b826_combos(log_path: str) -> Tuple[B826LogMetadata, List[B826ComboRecord]]:
    """
    Parse 0xB826 (NR5G RRC Supported CA Combos) from QXDM log.

    Returns:
        - Metadata (version, total_num_combos)
        - List of combo records

    Note: 0xB826 is paginated (starting_index increments by 100).
    Must combine all segments to get complete combo list.
    """
```

**Key Parsing Considerations:**
1. **Version Handling:** Log version (e.g., Version = 14) may affect field layout
2. **Pagination:** Log is split into segments (starting_index: 0, 100, 200...)
3. **Multi-band combos:** Each combo has multiple band entries
4. **Contiguous notation:** "BW_20_20" indicates contiguous 2CC

### 6.2.1 QXDM Log Parsing Logic

#### Log File Structure

QXDM exports logs as text files with this pattern:

```
[Timestamp]  [Code]  0x[LogCode]  [Log Name]  --  [SubType]
[Metadata fields]
[Content - varies by log type]
```

**Example:**
```
2025 Sep 28  07:18:37.808  [B5]  0xB0C0  LTE RRC OTA Packet  --  UL_DCCH / UECapabilityInformation
Subscription ID = 1
Pkt Version = 27
RRC Release Number.Major.minor = 16.1.0
...
value UL-DCCH-Message ::=
{
  message c1 : ueCapabilityInformation : ...
}
```

#### Parsing Steps by Log Type

**Step 1: Split log file into packets**
```python
def split_into_packets(content: str) -> List[str]:
    """
    Split QXDM log by timestamp pattern.
    Pattern: YYYY Mon DD  HH:MM:SS.mmm
    Example: 2025 Sep 28  07:18:37.808
    """
    pattern = r'(\d{4} \w{3} \d{2}  \d{2}:\d{2}:\d{2}\.\d{3})'
    # Split and keep delimiter
```

**Step 2: Identify packet type by log code**
```python
def identify_packet_type(packet: str) -> str:
    if '0xB826' in packet:
        return 'RRC_SUPPORTED_CA_COMBOS'
    elif '0xB0C0' in packet:
        if 'UECapabilityInformation' in packet:
            return 'UE_CAPABILITY_INFO'
        elif 'UECapabilityEnquiry' in packet:
            return 'UE_CAPABILITY_ENQUIRY'
    return 'OTHER'
```

**Step 3: Parse based on packet type**

#### 0xB826 Parsing (Tabular Format)

```python
def parse_b826_packet(packet: str) -> Tuple[B826LogMetadata, List[B826ComboRecord]]:
    """
    Parse 0xB826 NR5G RRC Supported CA Combos.

    Log format:
    - Header with metadata (Version, Total Num Combos, starting_index)
    - Pipe-delimited table with combo records
    """
    # Extract metadata
    version = extract_field(packet, r'Version = (\d+)')
    total_combos = extract_field(packet, r'Total Num Combos = (\d+)')
    starting_index = extract_field(packet, r'starting_index = (\d+)')

    # Parse table rows
    # Format: | Idx | Valid | Bands | RAT | Band | DL Class | DL Antenna | UL Class | ...
    table_pattern = r'\|\s*(\d+)\s*\|\s*(true|false)\s*\|\s*(\d+)\s*\|(.+)'

    combos = []
    current_combo = None

    for match in re.finditer(table_pattern, packet):
        idx, valid, num_bands, rest = match.groups()
        # Parse band entries from rest of row
        # Handle multi-band combos (subsequent rows without Idx)
```

#### 0xB0C0 UE Capability Parsing (ASN.1 Text Format)

**3GPP Reference:** The UE Capability structure follows 3GPP ASN.1 definitions:

| 3GPP Spec | IE Name | Section |
|-----------|---------|---------|
| **TS 36.331** | UE-EUTRA-Capability | 6.3.6 |
| **TS 36.331** | supportedBandCombination-r10 | 6.3.6 |
| **TS 38.331** | UE-NR-Capability | 6.3.3 |
| **TS 38.331** | supportedBandCombinationList | 6.3.3 |
| **TS 38.331** | BandCombination | 6.3.3 |
| **TS 38.331** | BandParameters | 6.3.3 |

```python
def parse_ue_capability_packet(packet: str) -> List[Combo]:
    """
    Parse UE Capability Information from 0xB0C0 log.

    The content is ASN.1 decoded text following 3GPP TS 38.331 structure:

    supportedBandCombinationList {
      {
        bandList {
          nr : {
            bandNR 77,
            ca-BandwidthClassDL-NR c,
            ca-BandwidthClassUL-NR a
          }
        },
        featureSetCombination 1,
        powerClass-v1530 pc2
      },
      ...
    }
    """
    combos = []

    # Find supportedBandCombinationList blocks
    # Pattern matches nested ASN.1 structure

    # For each combo in list:
    #   1. Extract bandList entries (nr: or eutra:)
    #   2. Extract bandwidth classes (ca-BandwidthClassDL-NR, etc.)
    #   3. Extract optional fields (powerClass, featureSetCombination)

    return combos
```

**ASN.1 Structure Parsing:**
```python
def parse_asn1_band_combination(text: str) -> Dict:
    """
    Parse single BandCombination from ASN.1 text.

    3GPP TS 38.331 BandCombination structure:
    - bandList: List of BandParameters
    - featureSetCombination: Index to featureSetCombinations
    - ca-ParametersNR: Optional CA parameters
    - powerClass-v1530: Optional power class (pc2, pc3)
    """
    result = {
        'bands': [],
        'feature_set_combination': None,
        'power_class': None
    }

    # Parse bandList
    band_pattern = r'(nr|eutra)\s*:\s*\{([^}]+)\}'
    for match in re.finditer(band_pattern, text):
        rat_type, band_content = match.groups()
        band_entry = parse_band_parameters(rat_type, band_content)
        result['bands'].append(band_entry)

    # Parse featureSetCombination
    fsc_match = re.search(r'featureSetCombination\s+(\d+)', text)
    if fsc_match:
        result['feature_set_combination'] = int(fsc_match.group(1))

    # Parse powerClass
    pc_match = re.search(r'powerClass-v1530\s+(pc\d+)', text)
    if pc_match:
        result['power_class'] = pc_match.group(1)

    return result

def parse_band_parameters(rat_type: str, content: str) -> Dict:
    """
    Parse BandParameters from ASN.1 text.

    3GPP TS 38.331 BandParameters:
    - bandNR / bandEUTRA: Band number
    - ca-BandwidthClassDL-NR / ca-BandwidthClassDL-EUTRA: DL class
    - ca-BandwidthClassUL-NR / ca-BandwidthClassUL-EUTRA: UL class
    """
    if rat_type == 'nr':
        band = extract_field(content, r'bandNR\s+(\d+)')
        dl_class = extract_field(content, r'ca-BandwidthClassDL-NR\s+(\w+)')
        ul_class = extract_field(content, r'ca-BandwidthClassUL-NR\s+(\w+)')
    else:  # eutra
        band = extract_field(content, r'bandEUTRA\s+(\d+)')
        dl_class = extract_field(content, r'ca-BandwidthClassDL-EUTRA\s+(\w+)')
        ul_class = extract_field(content, r'ca-BandwidthClassUL-EUTRA\s+(\w+)')

    return {
        'rat': 'NR' if rat_type == 'nr' else 'LTE',
        'band': int(band) if band else None,
        'dl_class': dl_class.upper() if dl_class else None,
        'ul_class': ul_class.upper() if ul_class else None
    }
```

#### UE Capability Enquiry Parsing

```python
def parse_ue_cap_enquiry(packet: str) -> Dict:
    """
    Parse UECapabilityEnquiry from 0xB0C0 log.

    3GPP TS 38.331: Network sends frequencyBandListFilter to request
    specific bands. UE filters its capability response accordingly.

    Structure:
    ue-CapabilityRAT-RequestList {
      {
        rat-Type eutra-nr,
        capabilityRequestFilter mrdc-Request : {
          frequencyBandListFilter {
            bandInformationEUTRA : { bandEUTRA 2 },
            bandInformationNR : { bandNR 77 }
          }
        }
      }
    }
    """
    result = {
        'rat_types_requested': [],
        'band_filter': {
            'lte_bands': [],
            'nr_bands': []
        }
    }

    # Extract requested RAT types
    # Extract frequencyBandListFilter bands

    return result
```

#### Complete QXDM Log Parser

```python
def parse_qxdm_log(log_path: str) -> QXDMLogResult:
    """
    Parse complete QXDM log file for combo analysis.

    Returns:
        QXDMLogResult with:
        - b826_metadata: Version, total combos
        - b826_combos: List of RRC table combos
        - ue_cap_combos: List of UE Capability combos
        - ue_cap_enquiry: Network's band filter (if present)
    """
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = QXDMLogResult()

    # Split into packets
    packets = split_into_packets(content)

    # Parse each packet
    b826_segments = []

    for packet in packets:
        pkt_type = identify_packet_type(packet)

        if pkt_type == 'RRC_SUPPORTED_CA_COMBOS':
            metadata, combos = parse_b826_packet(packet)
            result.b826_metadata = metadata
            b826_segments.append((metadata.starting_index, combos))

        elif pkt_type == 'UE_CAPABILITY_INFO':
            combos = parse_ue_capability_packet(packet)
            result.ue_cap_combos.extend(combos)

        elif pkt_type == 'UE_CAPABILITY_ENQUIRY':
            result.ue_cap_enquiry = parse_ue_cap_enquiry(packet)

    # Combine paginated 0xB826 segments
    b826_segments.sort(key=lambda x: x[0])  # Sort by starting_index
    for _, combos in b826_segments:
        result.b826_combos.extend(combos)

    return result
```

#### Parsing Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| **0xB826 Pagination** | Collect all segments, sort by `starting_index`, combine |
| **ASN.1 Nested Structures** | Recursive regex or state machine for brace matching |
| **Multi-band Combos in 0xB826** | Track combo index; rows without index belong to previous combo |
| **Optional Fields** | Use regex with optional groups, default to None |
| **Log Version Differences** | Check `Version` field, maintain version-specific parsers if needed |
| **Large Log Files** | Stream parsing or chunked reading for memory efficiency |

### 6.3 Analysis Requirements

#### FR-005: Three-Source Comparison (RFC vs 0xB826 vs UE Cap)

**Logic:**
```
FOR each combo in RFC:
    1. Check if combo exists in 0xB826 (RRC Table)
       IF not found:
           Mark as "Filtered at Envelope Check"
           Status = RFC_ONLY

    2. IF found in 0xB826, check if exists in UE Capability
       IF not found:
           Mark as "Filtered after RRC Table"
           Status = RFC_AND_B826

    3. IF found in all sources:
       Mark as "Fully Supported"
       Status = SUPPORTED
```

**Comparison Result Categories:**
| Status | In RFC | In 0xB826 | In UE Cap | Meaning |
|--------|--------|-----------|-----------|---------|
| SUPPORTED | Yes | Yes | Yes | Combo fully supported and advertised |
| RFC_AND_B826 | Yes | Yes | No | Filtered after RRC table (Carrier/EFS/NV) |
| RFC_ONLY | Yes | No | No | Filtered at envelope check |
| B826_ONLY | No | Yes | No | In RRC table but not in RFC (unusual) |
| UE_CAP_ONLY | No | No | Yes | In UE Cap but not in RFC (unusual) |

#### FR-006: Filtering Point Identification

**Logic:**
```
FOR each combo missing from UE Capability:
    1. Check if combo is in 0xB826 (RRC Table)
       IF not in 0xB826:
           Filtering Point = "Envelope Check (RFC → RRC Table)"

    2. IF in 0xB826 but not in UE Cap:
       a. Check Carrier Policy - are all bands in combo enabled?
          IF any band disabled:
              Filtering Point = "Carrier Policy"

       b. Check Band Preference (if NV data available)
          IF any band preference = 0x00:
              Filtering Point = "Band Preference NV"

       c. Check EFS Controls (if available)
          IF combo type disabled:
              Filtering Point = "RRC EFS Control"

       d. Default:
       Filtering Point = "Unknown (UE Capability)"
```

### 6.4 Report Requirements

#### FR-006: HTML Report Generation

**Report Sections:**
1. **Summary Statistics**
   - Total combos by type
   - Supported vs filtered counts
   - Filtering breakdown

2. **Combo Support Matrix**
   - Table with all combos
   - Columns: Combo String, Type, RFC Status, UE Cap Status, Filtering Point

3. **Detailed Analysis**
   - Per-type breakdown (LTE CA, NRCA, EN-DC, NR-DC)
   - Filtering analysis with reasons

4. **Recommendations**
   - Combos missing from RFC
   - Combos filtered by policy

---

## 7. Data Structures

### 7.1 Core Data Classes

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class RAT(Enum):
    LTE = "LTE"
    NR = "NR"

class ComboType(Enum):
    LTE_CA = "LTE_CA"
    NRCA = "NRCA"
    ENDC = "EN-DC"
    NRDC = "NR-DC"

class FilteringPoint(Enum):
    RFC_SUPPORTED = "RFC Supported"
    RFC_NOT_PRESENT = "Not in RFC"
    CARRIER_POLICY = "Carrier Policy Filter"
    BAND_PREFERENCE = "Band Preference NV"
    EFS_CONTROL = "RRC EFS Control"
    UE_CAP_MISSING = "Missing from UE Capability"
    NETWORK_FILTER = "Network UECapabilityEnquiry Filter"
    UNKNOWN = "Unknown"

@dataclass
class BandComponent:
    """Single band in a combo."""
    rat: RAT
    band: int
    dl_class: str
    ul_class: Optional[str] = None
    dl_mimo: Optional[int] = None
    ul_mimo: Optional[int] = None
    dl_bw: Optional[int] = None  # NR only (MHz)
    ul_bw: Optional[int] = None  # NR only (MHz)

@dataclass
class Combo:
    """Complete combo definition."""
    raw_string: str
    combo_type: ComboType
    bands: List[BandComponent]
    power_class: Optional[str] = None
    srs_ant_switch: Optional[str] = None
    source: str = ""  # "RFC", "UE_CAP", etc.

@dataclass
class ComboAnalysisResult:
    """Result of analyzing a single combo."""
    combo: Combo
    rfc_supported: bool
    ue_cap_supported: bool
    carrier_policy_enabled: bool
    filtering_point: FilteringPoint
    notes: str = ""

@dataclass
class ComboAnalysisSummary:
    """Summary of combo analysis."""
    total_rfc_combos: Dict[ComboType, int]
    total_ue_cap_combos: Dict[ComboType, int]
    supported_combos: List[ComboAnalysisResult]
    filtered_combos: List[ComboAnalysisResult]
    filtering_breakdown: Dict[FilteringPoint, int]
```

---

## 8. Integration with Existing System

### 8.1 Module Structure

```
src/
├── parsers/
│   ├── rfc_parser.py          # Existing - enhance for combos
│   ├── ue_capability_parser.py # Existing - enhance for combos
│   └── combo_parser.py         # NEW - dedicated combo parsing
├── analyzers/
│   └── combo_analyzer.py       # NEW - combo analysis logic
├── reporters/
│   └── combo_reporter.py       # NEW - HTML report generation
└── web/
    └── routes/
        └── combos.py           # NEW - Flask routes for Combos module
```

### 8.2 Reuse from Bands Module

| Component | Reuse | Notes |
|-----------|-------|-------|
| HTML Report Template | Partial | Adapt styling, new tables |
| Carrier Policy Parser | Yes | Reuse band extraction |
| RFC Parser | Enhance | Add combo extraction |
| UE Capability Parser | Enhance | Add combo extraction |
| Flask Route Structure | Yes | Same pattern as bands.py |

### 8.3 Web UI Integration

**New Routes:**
- `/combos/` - Upload page for combo analysis
- `/combos/analyze` - Analysis endpoint
- `/combos/results` - Results page with HTML report
- `/combos/download/<filename>` - Download generated report

---

## 9. Test Requirements

### 9.1 Unit Tests

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| TC-COMBO-001 | Parse single-band LTE combo | Correct band, class, MIMO |
| TC-COMBO-002 | Parse multi-band LTE CA combo | All bands parsed correctly |
| TC-COMBO-003 | Parse contiguous combo (Class C) | Contiguous flag set |
| TC-COMBO-004 | Parse NR CA combo with BW×MIMO | BW and MIMO extracted |
| TC-COMBO-005 | Parse EN-DC combo | Both LTE and NR bands parsed |
| TC-COMBO-006 | Classify combo type correctly | Type matches expected |
| TC-COMBO-007 | Compare RFC vs UE Cap combos | Differences identified |
| TC-COMBO-008 | Identify filtering point | Correct filter identified |

### 9.2 Integration Tests

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| TC-INT-001 | Full RFC combo parsing | All combos extracted |
| TC-INT-002 | Full UE Cap combo parsing | All combos extracted |
| TC-INT-003 | End-to-end analysis | Report generated with correct data |
| TC-INT-004 | HTML report generation | Valid HTML, correct content |

---

## 10. Acceptance Criteria

### 10.1 Must Have (P0)

- [ ] Parse LTE CA combos from RFC XML
- [ ] Parse NRCA combos from RFC XML
- [ ] Parse EN-DC combos from RFC XML
- [ ] **Parse 0xB826 (RRC Table) combos from QXDM log**
- [ ] Parse combos from UE Capability (QXDM log)
- [ ] Classify combo types correctly
- [ ] **Three-source comparison: RFC vs 0xB826 vs UE Capability**
- [ ] Identify combos filtered at each stage (Envelope Check, Carrier Policy, etc.)
- [ ] Generate HTML report with combo support matrix
- [ ] Web UI for file upload and analysis

### 10.2 Should Have (P1)

- [ ] Parse NR-DC combos
- [ ] Support multiple RFC/log files
- [ ] Export analysis as JSON
- [ ] Carrier Policy integration for indirect filtering
- [ ] Detailed filtering point identification (EFS, NV, etc.)
- [ ] RFPD Report parsing for enhanced envelope check analysis

### 10.3 Nice to Have (P2)

- [ ] 3GPP notation conversion
- [ ] Band preference NV analysis
- [ ] EFS control file analysis
- [ ] Combo recommendation engine

---

## 11. Open Questions

| # | Question | Impact | Status |
|---|----------|--------|--------|
| 1 | ~~Should we parse 0xB826 log packet for RRC table combos?~~ | Additional filtering point | **Resolved - Yes, P0** |
| 2 | How to handle combo variations (same bands, different MIMO)? | Matching logic | Open |
| 3 | Should carrier policy analysis be mandatory or optional? | User workflow | Open |
| 4 | How to handle QXDM logs without UE Capability data? | Error handling | Open |
| 5 | ~~How to integrate RFPD Report for enhanced envelope check analysis?~~ | Enhanced filtering analysis | **Resolved - Optional input, parse env_combos.html** |

---

## 12. References

- [CA_ENDC_NRDC_NRCA_research_document.md](./CA_ENDC_NRDC_NRCA_research_document.md) - Technical research
- 3GPP TS 36.101 - LTE CA specifications
- 3GPP TS 38.101-1/2/3 - NR CA and MR-DC specifications
- Qualcomm 80-35348-127 - NR Band Combo Advertising and NRCA Control

---

**Document End**
