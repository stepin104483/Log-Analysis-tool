# Carrier Aggregation, Dual Connectivity & 5G Combo Research Document

**Document Version:** 1.2
**Date:** January 2026
**Purpose:** Deep analysis reference for Combos Module implementation
**Last Updated:** With Qualcomm implementation details from knowledge library

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Carrier Aggregation (CA) Fundamentals](#2-carrier-aggregation-ca-fundamentals)
3. [LTE Carrier Aggregation](#3-lte-carrier-aggregation)
4. [NR Carrier Aggregation (NRCA)](#4-nr-carrier-aggregation-nrca)
5. [Dual Connectivity Overview](#5-dual-connectivity-overview)
6. [EN-DC (E-UTRA NR Dual Connectivity)](#6-en-dc-e-utra-nr-dual-connectivity)
7. [NR-DC (NR-NR Dual Connectivity)](#7-nr-dc-nr-nr-dual-connectivity)
8. [Other MR-DC Options (NGEN-DC, NE-DC)](#8-other-mr-dc-options-ngen-dc-ne-dc)
9. [3GPP Specifications Reference](#9-3gpp-specifications-reference)
10. [Bandwidth Classes](#10-bandwidth-classes)
11. [Combo Notation Formats](#11-combo-notation-formats)
12. [Qualcomm RFC Implementation](#12-qualcomm-rfc-implementation)
13. [UE Capability Structure](#13-ue-capability-structure)
14. [Implementation Considerations](#14-implementation-considerations)
15. [Glossary](#15-glossary)

---

## 1. Executive Summary

This document provides a comprehensive technical reference for understanding Carrier Aggregation (CA) and Dual Connectivity (DC) technologies in LTE and 5G NR networks. It covers:

- **CA (Carrier Aggregation)**: Combining multiple component carriers to increase bandwidth
- **ENDC (E-UTRA NR Dual Connectivity)**: LTE + NR for 5G NSA deployment
- **NRCA (NR Carrier Aggregation)**: Pure NR carrier aggregation for 5G SA
- **NRDC (NR-NR Dual Connectivity)**: Dual NR nodes for advanced 5G scenarios

### Key Differences at a Glance

| Technology | RATs Involved | Core Network | Scheduling | Use Case |
|------------|---------------|--------------|------------|----------|
| **LTE CA** | LTE only | EPC | Single MAC | LTE-A throughput |
| **NR CA** | NR only | 5GC | Single MAC | 5G SA throughput |
| **EN-DC** | LTE + NR | EPC | Dual MAC | 5G NSA (Option 3) |
| **NR-DC** | NR + NR | 5GC | Dual MAC | FR1+FR2 aggregation |
| **NE-DC** | NR + LTE | 5GC | Dual MAC | 5GC with LTE fallback |
| **NGEN-DC** | LTE + NR | 5GC | Dual MAC | Evolved LTE with 5GC |

---

## 2. Carrier Aggregation (CA) Fundamentals

### 2.1 Definition

Carrier Aggregation (CA) is a technology that allows combining multiple component carriers (CCs) to increase the effective bandwidth available to a UE. Introduced in:
- **LTE**: 3GPP Release 10 (LTE-Advanced)
- **NR**: 3GPP Release 15

### 2.2 Key Concepts

#### Component Carrier (CC)
- Individual carrier with independent scheduling
- LTE: Maximum 20 MHz per CC
- NR FR1: Maximum 100 MHz per CC
- NR FR2: Maximum 400 MHz per CC

#### Primary Cell (PCell)
- Main serving cell
- Handles RRC connection
- Always active

#### Secondary Cell (SCell)
- Additional capacity cells
- Can be activated/deactivated dynamically
- Maximum 7 SCells (8 total cells in LTE, up to 16 in NR)

#### Primary Secondary Cell (PSCell)
- Special cell in Dual Connectivity scenarios
- Master cell in Secondary Cell Group (SCG)

### 2.3 CA Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    CARRIER AGGREGATION TYPES                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INTRA-BAND CONTIGUOUS                                       │
│     ┌──────┬──────┐                                             │
│     │  CC1 │  CC2 │  ← Same band, adjacent frequencies          │
│     └──────┴──────┘                                             │
│     Example: CA_n77C (Band n77, Class C)                        │
│                                                                 │
│  2. INTRA-BAND NON-CONTIGUOUS                                   │
│     ┌──────┐      ┌──────┐                                      │
│     │  CC1 │ .... │  CC2 │  ← Same band, frequency gap          │
│     └──────┘      └──────┘                                      │
│     Example: CA_n77(2A) (Band n77, 2 separate Class A)          │
│                                                                 │
│  3. INTER-BAND                                                  │
│     Band X        Band Y                                        │
│     ┌──────┐      ┌──────┐                                      │
│     │  CC1 │      │  CC2 │  ← Different bands                   │
│     └──────┘      └──────┘                                      │
│     Example: CA_n77A-n78A (Band n77 + Band n78)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 CA vs DC Comparison

| Aspect | Carrier Aggregation | Dual Connectivity |
|--------|---------------------|-------------------|
| **Backhaul** | Ideal (same node) | Non-ideal (different nodes) |
| **Scheduling** | Joint (single scheduler) | Loose (independent schedulers) |
| **MAC Entity** | Single | Dual |
| **TX Requirements** | Single TX chain | Dual TX chains |
| **RAT Support** | Single RAT | Multi-RAT possible |
| **PDCP Split** | No | Yes (split bearer) |

---

## 3. LTE Carrier Aggregation

### 3.1 Overview

LTE CA was introduced in 3GPP Release 10 and enhanced in subsequent releases:
- **Rel-10**: Basic CA (2 CCs)
- **Rel-11**: Enhanced CA (3 CCs)
- **Rel-12**: Extended CA (4-5 CCs)
- **Rel-13**: LAA (License Assisted Access)
- **Rel-14**: eLAA, Enhanced CA

### 3.2 LTE Bandwidth Classes (3GPP TS 36.101)

| Class | Aggregated BW | Max CCs | Description |
|-------|---------------|---------|-------------|
| **A** | ≤25 MHz | 1 | Single carrier (baseline) |
| **B** | 25-50 MHz | 2 | Non-contiguous in band |
| **C** | 50-100 MHz | 2 | Contiguous in band |
| **D** | 100-125 MHz | 3 | Higher aggregation |
| **E** | 125-150 MHz | 4 | Extended |
| **F** | 150+ MHz | 5 | Maximum aggregation |

### 3.3 LTE CA Notation

```
CA_[Band1][Class1]-[Band2][Class2]-...

Examples:
- CA_1C        → Intra-band contiguous, Band 1, Class C (2x20 MHz)
- CA_1A-3A     → Inter-band, Band 1 + Band 3, both Class A
- CA_3A-3A     → Intra-band non-contiguous, Band 3 + Band 3
- CA_1A-3A-7A  → Three-band CA: Band 1 + Band 3 + Band 7
```

### 3.4 UE Capability for LTE CA

Per 3GPP TS 36.331, LTE CA capabilities are reported in:

```
UE-EUTRA-Capability
├── rf-Parameters
│   └── supportedBandListEUTRA        # Individual bands (1-64)
├── rf-Parameters-v9e0
│   └── supportedBandListEUTRA-v9e0   # Bands 65+ extension
├── rf-Parameters-v1020
│   └── supportedBandCombination-r10  # CA combos (Rel-10)
├── rf-Parameters-v1090
│   └── supportedBandCombination-v1090 # Extended combos
└── rf-Parameters-v1250
    └── supportedBandCombination-r12  # Enhanced CA (Rel-12)
```

**Note on Band 64+ (v9e0 Extension):**
- `supportedBandListEUTRA` covers bands 1-64
- `supportedBandListEUTRA-v9e0` covers bands 65+ (B66, B68, B71, etc.)
- Entry "64" in base list can be placeholder for v9e0 bands
- Formula: `actual_B64_count = count("64" in base) - count(v9e0 bands)`

---

## 4. NR Carrier Aggregation (NRCA)

### 4.1 Overview

NR CA operates in two frequency ranges:
- **FR1 (Sub-6 GHz)**: 410 MHz - 7125 MHz
- **FR2 (mmWave)**: 24.25 GHz - 52.6 GHz

Key capabilities:
- Up to 16 component carriers
- Mixed numerologies across CCs
- Maximum aggregated bandwidth:
  - FR1: 400 MHz (8 CCs)
  - FR2: 800 MHz (16 CCs)

### 4.2 FR1 Bandwidth Classes (3GPP TS 38.101-1)

#### Fallback Group 1 (Primary)

| Class | Aggregated BW | Max CCs | Notes |
|-------|---------------|---------|-------|
| **A** | Single CC | 1 | No aggregation (baseline) |
| **B** | 20-100 MHz | 2 | Two carriers |
| **C** | 100-200 MHz | 2 | Contiguous two carriers |
| **D** | 200-300 MHz | 3 | Three carriers |
| **E** | 300-400 MHz | 4 | Four carriers (max FR1) |

#### Fallback Group 2

| Class | Aggregated BW | Max CCs | Notes |
|-------|---------------|---------|-------|
| **G** | 100 MHz | 3 | Three carriers |
| **H** | 100-200 MHz | 4 | Four carriers |
| **I** | 200-300 MHz | 5 | Five carriers |
| **J** | 300-400 MHz | 6 | Six carriers |
| **K** | 400-500 MHz | 7 | Seven carriers |
| **L** | 500-600 MHz | 8 | Eight carriers |

#### Fallback Group 3 & 4

| Class | Aggregated BW | Max CCs | Group |
|-------|---------------|---------|-------|
| **M** | 100 MHz | 3 | 3 |
| **N** | 100-200 MHz | 4 | 3 |
| **O** | 200-300 MHz | 5 | 3 |

**Fallback Requirement:** UE MUST support fallback to lower-order bandwidth classes within the same fallback group.

### 4.3 FR2 Bandwidth Classes (3GPP TS 38.101-2)

| Class | Aggregated BW | Max CCs | Fallback Group |
|-------|---------------|---------|----------------|
| **A** | Single CC | 1 | 1 |
| **C** | 200 MHz | 2 | 1 |
| **D** | 200-400 MHz | 2 | 1 |
| **E** | 400-600 MHz | 3 | 1 |
| **F** | 600-800 MHz | 4 | 1 |
| **G** | 100-200 MHz | 2 | 2 |
| **H** | 200-400 MHz | 3 | 2 |
| **I** | 400-600 MHz | 4 | 2 |
| **J** | 600-800 MHz | 5-6 | 2 |
| **K-Q** | Various | 3-8 | 3-4 |

### 4.4 NR CA Configuration Counts (Release 16+)

| Configuration Type | FR1 | FR2 |
|--------------------|-----|-----|
| **Intra-band Contiguous** | 48 configs | 5 configs |
| **Intra-band Non-contiguous** | 40 configs | Multiple with spacing classes I-IX |
| **Inter-band (2 bands)** | 911 configs | N/A (only intra-band in FR2) |
| **Inter-band (3 bands)** | 1,017 configs | N/A |
| **Inter-band (4 bands)** | 381 configs | N/A |
| **Inter-band (5 bands)** | 46 configs | N/A |
| **Inter-band (6 bands)** | 1 config | N/A |

### 4.5 NR CA Notation

```
CA_n[Band][Class][-n[Band][Class]]...

Examples:
- CA_n77C         → Intra-band contiguous, Band n77, Class C
- CA_n77(2A)      → Intra-band non-contiguous, Band n77, 2x Class A
- CA_n77A-n78A    → Inter-band, n77 + n78
- CA_n1A-n3A-n78A → Three-band inter-band CA
```

### 4.6 SUL (Supplementary Uplink) Combinations

SUL provides enhanced uplink coverage using lower frequency bands:

```
CA_nX_nYSUL

Example:
- CA_n78_n80SUL → n78 for DL/UL + n80 as supplementary UL
```

SUL Statistics:
- 39 primary SUL combinations
- Additional configs with intra-band CA and inter-band aggregation

---

## 5. Dual Connectivity Overview

### 5.1 Definition

Dual Connectivity (DC) enables a UE to connect simultaneously to two different network nodes (base stations) with independent schedulers. The nodes connect via non-ideal backhaul.

### 5.2 Evolution

| Release | Technology | Description |
|---------|------------|-------------|
| **Rel-12** | Intra-E-UTRA DC | LTE eNB + LTE SeNB |
| **Rel-15** | MR-DC (EN-DC) | LTE eNB + NR en-gNB |
| **Rel-15** | NR-DC | gNB + gNB |
| **Rel-15** | NGEN-DC | ng-eNB + gNB |
| **Rel-15** | NE-DC | gNB + ng-eNB |
| **Rel-16** | NR-DC Async | Asynchronous NR-DC |

### 5.3 Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL CONNECTIVITY ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────────┐                          │
│                    │   Core Network  │                          │
│                    │   (EPC / 5GC)   │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│              ┌──────────────┼──────────────┐                    │
│              │              │              │                    │
│              ▼              ▼              ▼                    │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│       │ Master   │   │  Xn/X2   │   │Secondary │                │
│       │  Node    │◄──┤Interface ├──►│  Node    │                │
│       │  (MN)    │   │          │   │  (SN)    │                │
│       └────┬─────┘   └──────────┘   └────┬─────┘                │
│            │                              │                     │
│            │         ┌────────┐          │                      │
│            └────────►│   UE   │◄─────────┘                      │
│                      └────────┘                                 │
│                                                                 │
│    MN = Master Node (RRC anchor)                                │
│    SN = Secondary Node (capacity boost)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Cell Groups

| Group | Description | Primary Cell |
|-------|-------------|--------------|
| **MCG** | Master Cell Group (MN's cells) | PCell |
| **SCG** | Secondary Cell Group (SN's cells) | PSCell |

### 5.5 Bearer Types

```
┌─────────────────────────────────────────────────────────────────┐
│                      BEARER TYPES IN DC                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. MCG BEARER                                                  │
│     ┌────────────────────────────────────────┐                  │
│     │              Master Node               │                  │
│     │  ┌──────┐  ┌──────┐  ┌──────┐          │                  │
│     │  │ PDCP │→ │ RLC  │→ │ MAC  │→ → UE    │                  │
│     │  └──────┘  └──────┘  └──────┘          │                  │
│     └────────────────────────────────────────┘                  │
│     Use: MN resources only                                      │
│                                                                 │
│  2. SCG BEARER                                                  │
│     ┌────────────────────────────────────────┐                  │
│     │            Secondary Node              │                  │
│     │  ┌──────┐  ┌──────┐  ┌──────┐          │                  │
│     │  │ PDCP │→ │ RLC  │→ │ MAC  │→ → UE    │                  │
│     │  └──────┘  └──────┘  └──────┘          │                  │
│     └────────────────────────────────────────┘                  │
│     Use: SN resources only                                      │
│                                                                 │
│  3. SPLIT BEARER                                                │
│     ┌────────────────────────────────────────────────────────┐  │
│     │  ┌──────┐    MN: ┌──────┐  ┌──────┐                    │  │
│     │  │ PDCP │──────→ │ RLC  │→ │ MAC  │→ → ┐               │  │
│     │  │      │        └──────┘  └──────┘    │               │  │
│     │  │      │    SN: ┌──────┐  ┌──────┐    ├─→ UE          │  │
│     │  │      │──────→ │ RLC  │→ │ MAC  │→ → ┘               │  │
│     │  └──────┘        └──────┘  └──────┘                    │  │
│     └────────────────────────────────────────────────────────┘  │
│     Use: Both MN and SN resources (PDCP in MN or SN)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. EN-DC (E-UTRA NR Dual Connectivity)

### 6.1 Overview

EN-DC is the primary 5G NSA (Non-Standalone) deployment option, defined as 3GPP Option 3/3a/3x.

**Key Characteristics:**
- LTE eNB acts as Master Node
- NR en-gNB acts as Secondary Node
- Connected to EPC (not 5GC)
- LTE provides control plane anchor
- NR provides capacity boost

### 6.2 Architecture Variants

```
┌─────────────────────────────────────────────────────────────────┐
│                    EN-DC ARCHITECTURE OPTIONS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION 3: User plane via eNB                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                        EPC                                │  │
│  │                    ┌─────────┐                            │  │
│  │                    │  S-GW   │                            │  │
│  │                    └────┬────┘                            │  │
│  │                         │ S1-U                            │  │
│  │                         ▼                                 │  │
│  │  ┌──────────┐    ┌──────────┐                             │  │
│  │  │  en-gNB  │◄───┤   eNB    │← S1-C (Control)             │  │
│  │  │   (SN)   │ X2 │   (MN)   │                             │  │
│  │  └────┬─────┘    └────┬─────┘                             │  │
│  │       └───────┬───────┘                                   │  │
│  │               ▼                                           │  │
│  │            ┌──────┐                                       │  │
│  │            │  UE  │                                       │  │
│  │            └──────┘                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  OPTION 3a: Separate S1-U to gNB                                │
│  - Both eNB and gNB have S1-U to S-GW                           │
│  - Traffic split in core network                                │
│                                                                 │
│  OPTION 3x: User plane via gNB (RECOMMENDED)                    │
│  - S1-U terminates at gNB                                       │
│  - Traffic converges at gNB PDCP                                │
│  - NR carries primary load, LTE provides coverage               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 EN-DC Band Notation

```
DC_[LTE_Band][Class][-LTE_Band][Class]_n[NR_Band][Class][-n[NR_Band][Class]]

Format:
- DC_ prefix indicates Dual Connectivity
- LTE bands use number (1, 3, 7, 66, etc.)
- NR bands use 'n' prefix (n78, n77, n41, etc.)
- Multiple bands separated by '-'
- Underscore '_' separates LTE and NR portions

Examples:
- DC_1A_n78A           → LTE B1 + NR n78 (basic EN-DC)
- DC_3A-7A_n78A        → LTE CA (B3+B7) + NR n78
- DC_66A_n77A-n78A     → LTE B66 + NR CA (n77+n78)
- DC_1A-3A-7A_n78A     → LTE 3CA + NR single band
```

### 6.4 EN-DC Band Combination Counts (TS 38.101-3)

| Configuration | Count | Description |
|---------------|-------|-------------|
| **1 LTE + 1 NR** | 600+ | Basic EN-DC |
| **2 LTE + 1 NR** | 900+ | LTE CA + NR |
| **1 LTE + 2 NR** | 400+ | LTE + NR CA |
| **3+ bands total** | 1000+ | Complex configs |

### 6.5 Power Control in EN-DC

For EN-DC with overlapping TDD slots:
- UE has aggregate power limit
- When combined power exceeds limit, NR power reduces first
- LTE power maintained for coverage stability

```
P_total = P_LTE + P_NR ≤ P_max

If P_LTE + P_NR > P_max:
    P_NR_adjusted = P_max - P_LTE
```

---

## 7. NR-DC (NR-NR Dual Connectivity)

### 7.1 Overview

NR-DC enables a UE to connect to two NR nodes simultaneously, typically combining FR1 (Sub-6 GHz) and FR2 (mmWave) for maximum throughput.

**Key Characteristics:**
- Both nodes are gNBs
- Connected to 5GC (Option 2 derivative)
- Master gNB connected via NG interface
- Secondary gNB connected via Xn interface
- Supports FR1+FR2 aggregation

### 7.2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      NR-DC ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         5G Core (5GC)                           │
│                    ┌─────────────────────┐                      │
│                    │  AMF    │    UPF    │                      │
│                    └────┬────┴─────┬─────┘                      │
│                         │ N2       │ N3                         │
│                         │          │                            │
│                         ▼          ▼                            │
│                    ┌─────────────────────┐                      │
│                    │   Master gNB (MgNB) │                      │
│                    │      (FR1/FR2)      │                      │
│                    └──────────┬──────────┘                      │
│                               │ Xn                              │
│                               ▼                                 │
│                    ┌─────────────────────┐                      │
│                    │ Secondary gNB (SgNB)│                      │
│                    │      (FR1/FR2)      │                      │
│                    └──────────┬──────────┘                      │
│                               │                                 │
│                    ┌──────────┴──────────┐                      │
│                    │         UE          │                      │
│                    │    (FR1 + FR2)      │                      │
│                    └─────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 NR-DC Use Cases

1. **FR1 + FR2 Aggregation**
   - Sub-6 GHz provides coverage and baseline throughput
   - mmWave provides capacity boost when available
   - Seamless fallback to FR1 when FR2 is unavailable

2. **Same FR Different Bands**
   - Two FR1 bands from different nodes
   - Used for load balancing and capacity

3. **CU-DU Split Architecture**
   - Same gNB-CU controlling multiple gNB-DUs
   - One DU for MCG, another for SCG

### 7.4 NR-DC Band Notation

```
DC_n[Band1][Class]-n[Band2][Class]

Examples:
- DC_n78A-n257A      → FR1 n78 + FR2 n257
- DC_n77A-n258G      → FR1 n77 + FR2 n258 (Class G)
- DC_n1A-n78A-n257A  → FR1 n1 + FR1 n78 + FR2 n257
```

### 7.5 NR-DC Band Combination Statistics (TS 38.101-3 Rel-18)

| Configuration | Count | Description |
|---------------|-------|-------------|
| **2-band (FR1+FR2)** | 900+ | One FR1 + one FR2 |
| **3-band** | 1,066 | Two FR1 + one FR2 or one FR1 + two FR2 |
| **4-band** | 227 | Mixed FR1/FR2 |
| **5-band** | 8 | Maximum complexity |

### 7.6 Power Control in NR-DC

When MCG and SCG use different frequency ranges (FR1 and FR2):
- Power control is done **independently** for each group
- No power sharing required between FR1 and FR2

When MCG and SCG use same frequency range:
- Inter-cell-group power sharing may apply
- Dynamic power allocation based on traffic needs

---

## 8. Other MR-DC Options (NGEN-DC, NE-DC)

### 8.1 NGEN-DC (NG-RAN E-UTRA-NR Dual Connectivity)

**Definition:** Evolved LTE (ng-eNB) as Master + NR (gNB) as Secondary, connected to 5GC.

```
┌───────────────────────────────────────────────┐
│                     5GC                       │
│              ┌──────┬──────┐                  │
│              │ AMF  │ UPF  │                  │
│              └──┬───┴──┬───┘                  │
│                 │      │                      │
│              N2 │      │ N3                   │
│                 ▼      ▼                      │
│           ┌─────────────────┐                 │
│           │    ng-eNB (MN)  │◄── LTE anchor   │
│           └────────┬────────┘                 │
│                    │ Xn                       │
│                    ▼                          │
│           ┌─────────────────┐                 │
│           │     gNB (SN)    │◄── NR capacity  │
│           └────────┬────────┘                 │
│                    │                          │
│                    ▼                          │
│                 ┌──────┐                      │
│                 │  UE  │                      │
│                 └──────┘                      │
└───────────────────────────────────────────────┘

3GPP Option: 4
Control Plane: LTE (ng-eNB) anchored
Core Network: 5GC
```

**Use Case:** Migration path from EN-DC to 5GC while maintaining LTE control plane.

### 8.2 NE-DC (NR-E-UTRA Dual Connectivity)

**Definition:** NR (gNB) as Master + Evolved LTE (ng-eNB) as Secondary, connected to 5GC.

```
┌───────────────────────────────────────────────┐
│                     5GC                       │
│              ┌──────┬──────┐                  │
│              │ AMF  │ UPF  │                  │
│              └──┬───┴──┬───┘                  │
│                 │      │                      │
│              N2 │      │ N3                   │
│                 ▼      ▼                      │
│           ┌─────────────────┐                 │
│           │    gNB (MN)     │◄── NR anchor    │
│           └────────┬────────┘                 │
│                    │ Xn                       │
│                    ▼                          │
│           ┌─────────────────┐                 │
│           │   ng-eNB (SN)   │◄── LTE capacity │
│           └────────┬────────┘                 │
│                    │                          │
│                    ▼                          │
│                 ┌──────┐                      │
│                 │  UE  │                      │
│                 └──────┘                      │
└───────────────────────────────────────────────┘

3GPP Option: 7
Control Plane: NR (gNB) anchored
Core Network: 5GC
```

**Use Case:** NR-centric deployment with LTE providing coverage fallback.

### 8.3 MR-DC Summary Comparison

| Aspect | EN-DC | NGEN-DC | NE-DC | NR-DC |
|--------|-------|---------|-------|-------|
| **3GPP Option** | 3/3a/3x | 4 | 7 | 2 derivative |
| **Master Node** | LTE eNB | LTE ng-eNB | NR gNB | NR gNB |
| **Secondary Node** | NR en-gNB | NR gNB | LTE ng-eNB | NR gNB |
| **Core Network** | EPC | 5GC | 5GC | 5GC |
| **Control Plane** | LTE | LTE | NR | NR |
| **Interface** | X2 | Xn | Xn | Xn |
| **Primary Use** | 5G NSA | 5GC migration | NR anchor + LTE | FR1+FR2 |

---

## 9. 3GPP Specifications Reference

### 9.1 LTE Specifications

| Spec | Title | Content |
|------|-------|---------|
| **TS 36.101** | E-UTRA UE Radio Transmission/Reception | LTE bands, CA combinations, RF requirements |
| **TS 36.104** | E-UTRA BS Radio Transmission/Reception | Base station RF requirements |
| **TS 36.300** | E-UTRA Overall Description | Architecture including DC |
| **TS 36.306** | E-UTRA UE Radio Access Capabilities | UE capability IEs, CA capability |
| **TS 36.331** | E-UTRA RRC Protocol | RRC signaling, UE capability procedures |

### 9.2 NR Specifications

| Spec | Title | Content |
|------|-------|---------|
| **TS 38.101-1** | NR UE Radio (FR1 Standalone) | FR1 bands, NR CA combinations |
| **TS 38.101-2** | NR UE Radio (FR2 Standalone) | FR2 bands, mmWave configurations |
| **TS 38.101-3** | NR UE Radio (Interworking) | EN-DC, NR-DC, NGEN-DC, NE-DC combinations |
| **TS 38.104** | NR BS Radio Transmission/Reception | Base station RF requirements |
| **TS 38.300** | NR Overall Description | NR architecture |
| **TS 38.306** | NR UE Radio Access Capabilities | NR capability IEs |
| **TS 38.331** | NR RRC Protocol | NR RRC signaling |

### 9.3 Multi-RAT Specifications

| Spec | Title | Content |
|------|-------|---------|
| **TS 37.340** | E-UTRA and NR Multi-Connectivity | MR-DC architecture, procedures |
| **TS 38.716** | NR-DC Band Combinations (FR1) | Valid NR-DC FR1 band combos |
| **TS 38.717** | NR-DC Band Combinations (FR1+FR2) | FR1+FR2 NR-DC combos |
| **TS 38.718** | NR-DC Band Combinations (FR2) | Valid NR-DC FR2 band combos |

### 9.4 Key Tables Reference

| Spec | Table | Content |
|------|-------|---------|
| **TS 36.101** | 5.5-1 | E-UTRA CA bandwidth classes |
| **TS 36.101** | 5.5A.1.1-1 | Intra-band contiguous CA configs |
| **TS 36.101** | 5.5A.2-1 | Inter-band CA combinations |
| **TS 38.101-1** | 5.3A.5-1 | NR FR1 CA bandwidth classes |
| **TS 38.101-1** | 5.2A.1-1 | NR FR1 intra-band contiguous CA |
| **TS 38.101-1** | 5.2A.2.1-1 | NR FR1 2-band inter-band CA |
| **TS 38.101-2** | 5.3A.4-1 | NR FR2 CA bandwidth classes |
| **TS 38.101-3** | 5.3B.1.1-1 | EN-DC intra-band contiguous configs |
| **TS 38.101-3** | 5.3B.2.1-1 | EN-DC inter-band configs |
| **TS 38.101-3** | 5.5B.7-1 | NR-DC band combinations |

---

## 10. Bandwidth Classes

### 10.1 LTE Bandwidth Classes (Complete)

| Class | Aggregated Transmission BW Configuration | Maximum Number of CCs |
|-------|------------------------------------------|----------------------|
| A | BWGB ≤ 25 RB | 1 |
| B | 25 RB < BWGB ≤ 50 RB | 2 |
| C | 50 RB < BWGB ≤ 100 RB | 2 |
| D | 100 RB < BWGB ≤ 125 RB | 3 |
| E | 125 RB < BWGB ≤ 150 RB | 4 |
| F | 150 RB < BWGB | 5 |

*Note: 1 RB = 180 kHz, 100 RB ≈ 18 MHz*

### 10.2 NR FR1 Bandwidth Classes (Complete)

| Class | Max Aggregated BW (NRB) | Max CCs | Fallback Group |
|-------|------------------------|---------|----------------|
| A | BW of single CC | 1, 2, or 3 | 1 |
| B | 100 MHz | 2, 3 | 2 |
| C | 200 MHz | 2, 3 | 1 |
| D | 300 MHz | 3 | 2 |
| E | 400 MHz | 4 | 1 |
| G | 100 MHz | 3 | 2 |
| H | 200 MHz | 4 | 2 |
| I | 300 MHz | 5 | 2 |
| J | 400 MHz | 6 | 2 |
| K | 500 MHz | 7 | 2 |
| L | 600 MHz | 8 | 2 |
| M | 100 MHz | 3 | 3 |
| N | 200 MHz | 4 | 3 |
| O | 300 MHz | 5 | 3 |

### 10.3 NR FR2 Bandwidth Classes (Complete)

| Class | Max Aggregated BW | Max CCs | Fallback Group |
|-------|-------------------|---------|----------------|
| A | Single CC (400 MHz max) | 1 | 1 |
| C | 200 MHz | 2 | 1 |
| D | 400 MHz | 2 | 1 |
| E | 600 MHz | 3 | 1 |
| F | 800 MHz | 4 | 1 |
| G | 200 MHz | 2 | 2 |
| H | 400 MHz | 3 | 2 |
| I | 600 MHz | 4 | 2 |
| J | 800 MHz | 5-6 | 2 |
| K | 200 MHz | 3 | 3 |
| L | 400 MHz | 4 | 3 |
| M | 600 MHz | 5-6 | 3 |
| N | 800 MHz | 7-8 | 3 |
| O | 200 MHz | 4 | 4 |
| P | 400 MHz | 5-6 | 4 |
| Q | 600-800 MHz | 7-8 | 4 |

### 10.4 Fallback Requirements

**Mandatory Fallback:**
- UE MUST support fallback to lower-order CA configurations within same fallback group
- Example: If UE supports CA_n77C (Class C), it MUST support CA_n77A (Class A)

**Cross-Group Fallback:**
- Optional (not mandated by 3GPP)
- Operator may require for deployment flexibility

---

## 11. Combo Notation Formats

### 11.1 3GPP Standard Notation

#### LTE CA
```
CA_[Band][Class][-[Band][Class]]...

Components:
- CA_ prefix for Carrier Aggregation
- Band: Arabic numeral (1-255)
- Class: Letter (A-F)
- Dash (-) separates multiple bands

Examples:
- CA_1C           → Band 1, Class C (intra-band contiguous)
- CA_7A-7A        → Band 7 + Band 7 (intra-band non-contiguous)
- CA_1A-3A        → Band 1 + Band 3 (inter-band)
- CA_1A-3A-7A-20A → Four-band inter-band CA
```

#### NR CA
```
CA_n[Band][Class][-n[Band][Class]]...

Components:
- CA_ prefix
- n prefix for NR bands
- Band: Arabic numeral (1-261+)
- Class: Letter (A-Q)

Examples:
- CA_n77C         → NR Band n77, Class C
- CA_n77(2A)      → NR Band n77, 2x Class A (non-contiguous)
- CA_n77A-n78A    → NR n77 + NR n78 (inter-band)
```

#### EN-DC
```
DC_[LTE Bands]_n[NR Bands]

Components:
- DC_ prefix for Dual Connectivity
- LTE bands: number with class
- Underscore (_) separates LTE from NR
- NR bands: n prefix with class

Examples:
- DC_1A_n78A              → LTE B1 + NR n78
- DC_3A-7A_n78A           → LTE CA (B3+B7) + NR n78
- DC_66A_n77A-n78A        → LTE B66 + NR CA (n77+n78)
- DC_1A-3A-7A_n78A-n79A   → LTE 3CA + NR 2CA
```

#### NR-DC
```
DC_n[Band][Class]-n[Band][Class]...

Examples:
- DC_n78A-n257A           → FR1 n78 + FR2 n257
- DC_n77A-n78A-n257G      → FR1 n77 + FR1 n78 + FR2 n257
```

### 11.2 Qualcomm RFC Notation

Qualcomm uses a more detailed format in RFC XML files:

```
[RAT][Band][Class][MIMO_DL];[Class][MIMO_UL]+[RAT][Band][Class][BW×MIMO_DL];[Class][BW×MIMO_UL]

Components:
- RAT: B (LTE/E-UTRA) or N (NR)
- Band: Number
- Class: Bandwidth class letter
- MIMO_DL: DL MIMO layers (in brackets)
- MIMO_UL: UL MIMO layers (in brackets)
- BW: Bandwidth in MHz (for NR)
- ; separates DL and UL config
- + separates bands
```

#### Qualcomm RFC Examples

```
B1A[4];A[1]
├─ B1 = LTE Band 1
├─ A = Class A
├─ [4] = 4x4 MIMO downlink
├─ ; = DL/UL separator
├─ A = Class A uplink
└─ [1] = 1x1 MIMO uplink

B1A[4];A[1]+B3A[4];A[1]
├─ LTE Band 1: Class A, 4x4 DL, 1x1 UL
├─ + = band separator
└─ LTE Band 3: Class A, 4x4 DL, 1x1 UL

B1A[4];A[1]+N78A[100x4];A[100x1]
├─ LTE Band 1: Class A, 4x4 DL, 1x1 UL
├─ + = band separator
├─ N78 = NR Band 78
├─ A = Class A
├─ [100x4] = 100 MHz, 4x4 MIMO DL
├─ ; = DL/UL separator
├─ A = Class A UL
└─ [100x1] = 100 MHz, 1x1 MIMO UL

B1C[4];A[1]
├─ B1 = LTE Band 1
├─ C = Class C (contiguous 2CC intra-band)
├─ [4] = 4x4 MIMO DL
└─ A[1] = Class A, 1x1 UL

B66A[4];A[1]+B66A[4]+N77A[100x4];A[100x1]
├─ LTE B66: Class A, 4x4/1x1
├─ LTE B66: Class A, 4x4 DL (no UL on this CC)
└─ NR n77: Class A, 100MHz, 4x4/1x1
```

### 11.3 Notation Comparison Table

| Aspect | 3GPP Standard | Qualcomm RFC |
|--------|---------------|--------------|
| **LTE Band** | Number (1, 3, 66) | B prefix (B1, B3, B66) |
| **NR Band** | n prefix (n77, n78) | N prefix (N77, N78) |
| **MIMO Info** | Not in notation | [layers] or [BWxLayers] |
| **UL Separate** | No | Yes (after ;) |
| **Examples** | CA_1A-3A, DC_1A_n78A | B1A[4];A[1]+B3A[4];A[1] |

---

## 12. Qualcomm RFC Implementation

### 12.1 RFC XML Structure for Combos

Based on analysis of `src/parsers/rfc_parser.py`:

```xml
<rfc_data>
    <card_properties>
        <hwid>0x12345678</hwid>
        <name>RFC_Card_Name</name>
    </card_properties>

    <!-- Individual bands -->
    <band_name>B1</band_name>
    <band_name>B3</band_name>
    <band_name>N78</band_name>

    <!-- 4G+5G (EN-DC) Combos -->
    <ca_4g_5g_combos>
        <ca_combo>B1A[4];A[1]+N78A[100x4];A[100x1]</ca_combo>
        <ca_combo>B1A[4];A[1]+B3A[4];A[1]+N78A[100x4];A[100x1]</ca_combo>
        <ca_combo>B66A[4];A[1]+B66A[4]+N77A[100x4];A[100x1]</ca_combo>
    </ca_4g_5g_combos>

    <!-- Pure LTE CA Combos -->
    <ca_lte_combos>
        <ca_combo>B1A[4];A[1]+B3A[4];A[1]</ca_combo>
        <ca_combo>B1C[4];A[1]</ca_combo>
    </ca_lte_combos>

    <!-- Pure NR CA Combos (5G SA) -->
    <ca_nr_combos>
        <ca_combo>N77A[100x4];A[100x1]+N78A[100x4];A[100x1]</ca_combo>
        <ca_combo>N78C[100x4];A[100x1]</ca_combo>
    </ca_nr_combos>

    <!-- NR-DC Combos -->
    <nr_dc_combos>
        <ca_combo>N78A[100x4];A[100x1]+N257A[400x4];A[400x1]</ca_combo>
    </nr_dc_combos>
</rfc_data>
```

### 12.2 Combo Parsing Logic

```python
# Pseudo-code for parsing Qualcomm RFC combo format
def parse_qualcomm_combo(combo_string):
    """
    Parse Qualcomm RFC combo string into structured data.

    Input: "B1A[4];A[1]+N78A[100x4];A[100x1]"
    Output: {
        'type': 'EN-DC',
        'bands': [
            {'rat': 'LTE', 'band': 1, 'dl_class': 'A', 'dl_mimo': 4,
             'ul_class': 'A', 'ul_mimo': 1},
            {'rat': 'NR', 'band': 78, 'dl_class': 'A', 'dl_bw': 100,
             'dl_mimo': 4, 'ul_class': 'A', 'ul_bw': 100, 'ul_mimo': 1}
        ]
    }
    """
    bands = combo_string.split('+')
    parsed_bands = []

    for band_str in bands:
        # Parse each band component
        # B1A[4];A[1] or N78A[100x4];A[100x1]
        parsed_bands.append(parse_band_component(band_str))

    # Determine combo type
    has_lte = any(b['rat'] == 'LTE' for b in parsed_bands)
    has_nr = any(b['rat'] == 'NR' for b in parsed_bands)

    if has_lte and has_nr:
        combo_type = 'EN-DC'
    elif has_lte:
        combo_type = 'LTE-CA'
    elif has_nr:
        # Check if FR1+FR2 for NR-DC
        combo_type = 'NR-CA' or 'NR-DC'

    return {'type': combo_type, 'bands': parsed_bands}
```

### 12.3 Current RFC Parser Capabilities

From `src/parsers/rfc_parser.py`:

```python
# Current implementation extracts:
# 1. Individual bands from <band_name> elements
# 2. NR bands from EN-DC combos using regex

def extract_nr_bands_from_endc_combos(root):
    """Extract NR bands from <ca_4g_5g_combos> section."""
    nr_nsa_bands = set()

    for combos_elem in root.iter('ca_4g_5g_combos'):
        for combo_elem in combos_elem.iter('ca_combo'):
            if combo_elem.text:
                combo_text = combo_elem.text.strip()
                # Pattern: N followed by digits
                nr_matches = re.findall(r'N(\d+)', combo_text, re.IGNORECASE)
                for match in nr_matches:
                    band_num = int(match)
                    if 0 < band_num < 512:
                        nr_nsa_bands.add(band_num)

    return nr_nsa_bands
```

### 12.4 Enhancement Needed for Combos Module

The current parser only extracts band numbers. For full combo analysis, we need to parse:

1. **Complete combo structure**
2. **Bandwidth classes**
3. **MIMO configurations**
4. **Bandwidth allocations**
5. **Combo type classification**

### 12.5 NR Band Combo Advertising Flow (Qualcomm)

Based on Qualcomm document 80-35348-127, the NR band combo advertising follows this flow:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NR BAND COMBO ADVERTISING OVERALL FLOW                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐    ┌─────────┐    ┌───────────┐    ┌───────────────────────┐   │
│  │   RFC   │───►│  RFPD   │───►│ RRC Table │───►│ NR RRC Processing     │   │
│  │  (XML)  │    │ (Binary)│    │ (0xB826)  │    │ (UECapabilityInfo)    │   │
│  └─────────┘    └─────────┘    └───────────┘    └───────────────────────┘   │
│       │              │              │                      │                │
│       │              │              │                      ▼                │
│       │              ▼              │            ┌───────────────────┐      │
│       │     RF-supported combos     │            │ UECapabilityInfo  │      │
│       │     processed into RFPD     │            │ sent to Network   │      │
│       │                             │            └───────────────────┘      │
│       │                             │                                       │
│       ▼                             ▼                                       │
│  Source: XML config            Log: 0xB826                                  │
│  Contains all RF combos        Contains filtered combos                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **RFC (XML)**: Source XML configuration with all RF-supported combos
- **RFPD (Binary)**: RF Platform Data - compiled binary from RFC
- **RRC Table (0xB826)**: RF-supported combos after envelope check
- **NR RRC Processing**: Final filtering before UECapabilityInformation

### 12.6 Envelope Check Process

The envelope check compares target combos against platform capabilities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENVELOPE CHECK REPORT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    NR TDD Envelope (Example)                          │ │
│  ├────────┬────────────┬────────────┬────────────┬────────────┬─────────┤ │
│  │        │    DL CC   │    DL BW   │  DL Layers │  UL Layers │ UL MCS  │ │
│  ├────────┼────────────┼────────────┼────────────┼────────────┼─────────┤ │
│  │ NR TDD │     2      │  100 MHz   │     4      │     1      │ 256QAM  │ │
│  │ NR FDD │     0      │    N/A     │     0      │     0      │   N/A   │ │
│  │ LTE    │     2      │   20 MHz   │     4      │     1      │  64QAM  │ │
│  └────────┴────────────┴────────────┴────────────┴────────────┴─────────┘ │
│                                                                             │
│  Target Combo: B1A[4];A[1]+N78A[100x4];A[100x1]                             │
│                                                                             │
│  Check: Does target fit within envelope capabilities?                        │
│  - NR n78: 1 CC × 100MHz × 4 layers ≤ 2 CC × 100MHz × 4 layers ✓            │
│  - LTE B1: 1 CC × 20MHz × 4 layers ≤ 2 CC × 20MHz × 4 layers ✓              │
│  Result: PASS - Combo supported by RF platform                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.7 RRC Table Structure (Log Packet 0xB826)

The **0xB826 (NR5G RRC Supported CA Combos)** log packet contains RF-supported combos:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               0xB826 - NR5G RRC Supported CA Combos Structure                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Header Fields:                                                              │
│  ├── Version                                                                 │
│  ├── Subscription ID                                                         │
│  ├── Number of Records                                                       │
│  └── Record List                                                             │
│                                                                             │
│  Per-Record Fields:                                                          │
│  ├── Combo Index                                                             │
│  ├── Number of Bands                                                         │
│  ├── RAT Type (LTE/NR)                                                       │
│  ├── Band Number                                                             │
│  ├── Bandwidth Class (DL)                                                    │
│  ├── Bandwidth Class (UL)                                                    │
│  ├── Power Class                                                             │
│  ├── MIMO Configuration (DL Layers)                                          │
│  ├── MIMO Configuration (UL Layers)                                          │
│  ├── SRS Switching Capability                                                │
│  ├── Uplink TX Switching                                                     │
│  └── Additional Feature Flags                                                │
│                                                                             │
│  Example Record:                                                             │
│  ┌────────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐         │
│  │ Index  │ RAT   │ Band  │ DL BW │ UL BW │ PWR   │ DL    │ UL    │         │
│  │        │       │       │ Class │ Class │ Class │ MIMO  │ MIMO  │         │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤         │
│  │   0    │  LTE  │   1   │   A   │   A   │  PC3  │  4x4  │  1x1  │         │
│  │   1    │  NR   │  78   │   A   │   A   │  PC2  │  4x4  │  1x1  │         │
│  └────────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.8 Combo Filtering Stages

Multiple filtering stages control which combos are advertised to the network:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMBO FILTERING PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Stage 1: ENVELOPE MODE CHECK                                                │
│  ├── Compares combo requirements vs RF platform capabilities                 │
│  ├── Checks: CC count, BW, MIMO layers, MCS                                 │
│  └── Source: RFPD envelope data                                              │
│                                                                             │
│  Stage 2: PM/PRUNE_BC STRING (EFS)                                          │
│  ├── EFS File: /nv/item_files/modem/mmode/cap_prune                         │
│  ├── Purpose: Prune bandwidth classes for specific bands                     │
│  └── Format: Band-specific prune rules                                       │
│                                                                             │
│  Stage 3: BAND PREFERENCE                                                    │
│  ├── NV74213 - NR NSA Band Preference                                        │
│  ├── NV74087 - NR SA Band Preference                                         │
│  ├── NV74485 - NRDC Band Preference                                          │
│  └── NV65633 - LTE Band Preference                                           │
│                                                                             │
│  Stage 4: UECapabilityEnquiry FILTER                                         │
│  ├── Network requests specific bands via frequencyBandListFilter             │
│  ├── UE filters combos based on requested bands                              │
│  └── Log: 0xB0C0 shows the enquiry content                                   │
│                                                                             │
│  Stage 5: RRC EFS FILES                                                      │
│  ├── Control files in /nv/item_files/modem/nr5g/rrc/cap_control_*           │
│  ├── Feature-specific enable/disable controls                                │
│  └── Per-RAT and per-combo-type controls                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.9 NRCA Capability Control Methods

Qualcomm provides multiple methods to control NRCA capability advertisement:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NRCA CAPABILITY CONTROL METHODS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METHOD 1: MDB Files (Carrier-Specific)                                      │
│  ├── plmn2cacombos_nr.mdb                                                    │
│  │   └── Controls which NRCA combos are allowed per PLMN                     │
│  └── plmn2feature.mdb                                                        │
│      └── Feature enable/disable per PLMN                                     │
│                                                                             │
│  METHOD 2: RRC EFS Files (Device-Wide)                                       │
│  ├── cap_control_mrdc_b_c_band_combos                                        │
│  │   └── Controls MR-DC (EN-DC/NE-DC/NGEN-DC) B/C class combos              │
│  ├── cap_control_mrdc_d_band_combos                                          │
│  │   └── Controls MR-DC D class combos                                       │
│  ├── cap_control_nrca_f_plus_t_band_combos                                   │
│  │   └── Controls NRCA FR1+TDD band combos                                   │
│  ├── cap_control_nrca_b_c_band_combos                                        │
│  │   └── Controls NRCA B/C class band combos                                 │
│  ├── cap_control_nrca_d_band_combos                                          │
│  │   └── Controls NRCA D class band combos                                   │
│  ├── cap_control_nrca_e_band_combos                                          │
│  │   └── Controls NRCA E class (4CC) band combos                             │
│  ├── cap_control_inter_nr_dc_b_c_band_combos                                 │
│  │   └── Controls inter-frequency NR-DC B/C class combos                     │
│  └── cap_control_inter_nr_dc_d_band_combos                                   │
│      └── Controls inter-frequency NR-DC D class combos                       │
│                                                                             │
│  METHOD 3: QMI API (Runtime Control)                                         │
│  ├── Dynamic enable/disable via QMI commands                                 │
│  └── Takes effect immediately without reboot                                 │
│                                                                             │
│  METHOD 4: NR Downgrade Control                                              │
│  ├── cap_nrca_downgrade_1cc                                                  │
│  │   └── Downgrades all NRCA to single CC (effectively disables CA)         │
│  └── cap_nrdc_downgrade_1cc                                                  │
│      └── Downgrades all NRDC to single CC                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.10 Band Preference NV Items

Band preference NVs control which bands are preferred/deprioritized:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BAND PREFERENCE NV ITEMS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┬───────────────────────────────────────────────────────────┐│
│  │ NV Item     │ Purpose                                                   ││
│  ├─────────────┼───────────────────────────────────────────────────────────┤│
│  │ NV74213     │ NR NSA (EN-DC) Band Preference                            ││
│  │             │ Controls which NR bands preferred in NSA mode             ││
│  ├─────────────┼───────────────────────────────────────────────────────────┤│
│  │ NV74087     │ NR SA Band Preference                                     ││
│  │             │ Controls which NR bands preferred in SA mode              ││
│  ├─────────────┼───────────────────────────────────────────────────────────┤│
│  │ NV74485     │ NRDC Band Preference                                      ││
│  │             │ Controls which NR bands preferred for NR-DC               ││
│  ├─────────────┼───────────────────────────────────────────────────────────┤│
│  │ NV65633     │ LTE Band Preference                                       ││
│  │             │ Controls which LTE bands preferred                        ││
│  └─────────────┴───────────────────────────────────────────────────────────┘│
│                                                                             │
│  Band Preference Values:                                                     │
│  ├── 0x00: Not Supported / Disabled                                          │
│  ├── 0x01: Supported / Low Priority                                          │
│  ├── 0x02: Supported / Medium Priority                                       │
│  └── 0x03: Supported / High Priority                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```


### 12.11 EFS Control Files (Complete List)

#### 12.11.1 LTE CA EFS Controls

**Reference:** Qualcomm 80-NU834-1 "EFS to Control CA-Supported Band Combinations"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LTE CA EFS CONTROL FILES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Base Path: /nv/item_files/modem/lte/rrc/cap                               │
│                                                                             │
│  prune_ca_combos                                                            │
│  ├── Purpose: Control which LTE CA combos are advertised                    │
│  ├── Format: Text file, semicolon-separated                                 │
│  ├── Syntax: [Band][Class]-[Band][Class]-[BCS];                            │
│  ├── Max entries: 128 combinations                                          │
│  └── Note: Blank file does NOT disable CA                                   │
│                                                                             │
│  ca_disable                                                                 │
│  ├── Purpose: Completely disable LTE CA                                     │
│  └── Format: Binary (0x01 = CA disabled)                                    │
│                                                                             │
│  disable_4l_per_band                                                        │
│  ├── Purpose: Disable 4-layer MIMO per band                                 │
│  └── Effect: Affects CA performance by limiting MIMO                        │
│                                                                             │
│  prune_ca_combos Format Examples:                                           │
│  ├── Enable [1,3,8] BCS 0,1: 1A-3A-8A-0;1A-3A-8A-1;3A-1A-8A-0;             │
│  ├── Enable 41C + [4,13]:    41C-0;41C-1;4A-13A-0;13A-4A-0;                │
│  ├── Enable 41D (3CC):       41D-0;                                         │
│  └── Note: Band order matters (4A-13A ≠ 13A-4A for PCell/SCell)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 12.11.2 NRCA/NR-DC EFS Controls

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NRCA / NR-DC EFS CONTROL FILES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Base Path: /nv/item_files/modem/nr5g/rrc/                                  │
│                                                                             │
│  NRCA (NR Carrier Aggregation) Controls:                                    │
│  ├── cap_control_nrca_b_c_band_combos     (2CC NRCA)                       │
│  ├── cap_control_nrca_d_band_combos       (3CC NRCA)                       │
│  ├── cap_control_nrca_e_band_combos       (4CC NRCA)                       │
│  ├── cap_control_nrca_f_plus_t_band_combos (FR1+TDD)                       │
│  └── cap_control_nrca_inter_band_combos   (inter-band NRCA)                │
│                                                                             │
│  NR-DC (Inter-Frequency DC) Controls:                                       │
│  ├── cap_control_inter_nr_dc_b_c_band_combos                               │
│  ├── cap_control_inter_nr_dc_d_band_combos                                 │
│  └── cap_control_inter_nr_dc_e_band_combos                                 │
│                                                                             │
│  Downgrade Controls:                                                        │
│  ├── cap_nrca_downgrade_1cc   (Downgrade NRCA to 1CC)                      │
│  ├── cap_nrdc_downgrade_1cc   (Downgrade NRDC to 1CC)                      │
│  └── cap_mrdc_downgrade_1cc   (Downgrade MRDC to 1CC)                      │
│                                                                             │
│  File Format: Binary, single byte (0x00=disabled, 0x01=enabled)             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 12.11.3 EN-DC Control (NOT via EFS)

**IMPORTANT:** EN-DC combos are NOT controlled by EFS pruning files. EN-DC is controlled by:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EN-DC CONTROL MECHANISMS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. POLICYMAN XML (Primary)                                                 │
│     ├── device_config.xml                                                   │
│     ├── carrier_policy.xml                                                  │
│     └── Rules define ENDC enable/disable per carrier/PLMN                   │
│                                                                             │
│  2. RF (RFC XML)                                                            │
│     ├── ca_4g_5g_combos section                                             │
│     └── Hardware-defined supported combos                                   │
│                                                                             │
│  3. MCFG (Modem Configuration)                                              │
│     ├── MBN files per carrier                                               │
│     ├── plmn2cacombos_nr.mdb                                                │
│     └── plmn2feature.mdb                                                    │
│                                                                             │
│  Why not EFS for EN-DC?                                                     │
│  ├── EN-DC is carrier-specific (5G NSA deployment varies)                   │
│  ├── Policyman/MCFG allow per-carrier control without SW changes            │
│  └── RFC defines HW support; Policyman/MCFG define allowed combos           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 12.11.4 General Pruning EFS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GENERAL PRUNING EFS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  /nv/item_files/modem/mmode/cap_prune                                       │
│  ├── Purpose: General bandwidth class pruning                               │
│  └── Format: Band-specific prune rules                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.12 Debug Steps for Combo Issues

When combos are not advertised correctly, follow this debug sequence:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEBUG STEPS FOR COMBO ISSUES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: Check RFC/RFPD (Source)                                            │
│  ├── Verify combo exists in RFC XML                                          │
│  ├── Check RFPD binary was generated correctly                               │
│  └── Command: Parse RFC XML for target combo                                 │
│                                                                             │
│  STEP 2: Check RRC Table (Log 0xB826)                                        │
│  ├── Collect log 0xB826 (NR5G RRC Supported CA Combos)                       │
│  ├── Verify target combo present in RRC table                                │
│  └── If missing: Issue is in envelope check or RFPD                          │
│                                                                             │
│  STEP 3: Check Band Preference NVs                                           │
│  ├── Read NV74213 (NSA), NV74087 (SA), NV74485 (NRDC)                        │
│  ├── Verify bands not disabled (value ≠ 0x00)                                │
│  └── If disabled: Modify NV to enable band                                   │
│                                                                             │
│  STEP 4: Check UECapabilityEnquiry (Log 0xB0C0)                              │
│  ├── Collect log 0xB0C0 (NR5G RRC OTA Packet)                                │
│  ├── Check frequencyBandListFilter in enquiry                                │
│  ├── Verify network requested the target bands                               │
│  └── If filtered: Issue is network-side configuration                        │
│                                                                             │
│  STEP 5: Check RRC EFS Control Files                                         │
│  ├── Read cap_control_* EFS files                                            │
│  ├── Verify combo type not disabled                                          │
│  └── If disabled: Modify EFS file to 0x01 (enabled)                          │
│                                                                             │
│  STEP 6: Check UECapabilityInformation (Output)                              │
│  ├── Collect log 0xB0C0 for UECapabilityInformation message                  │
│  ├── Decode and verify combo present in response                             │
│  └── If missing: Check pruning (cap_prune) or MDB files                      │
│                                                                             │
│  STEP 7: Check Carrier Policy                                                │
│  ├── Review plmn2cacombos_nr.mdb for PLMN-specific blocks                   │
│  ├── Review plmn2feature.mdb for feature blocks                             │
│  └── If blocked: Modify MDB or use different carrier config                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.13 QXDM Log Packets Reference

Key log packets for combo debugging:

| Log Code | Name | Purpose |
|----------|------|---------|
| **0xB826** | NR5G RRC Supported CA Combos | RF-supported combos after envelope check |
| **0xB0C0** | NR5G RRC OTA Packet | UECapabilityEnquiry and UECapabilityInformation |
| **0xB0EC** | NR5G RRC Configuration | Active RRC configuration |
| **0xB827** | NR5G RRC Supported Bands | Individual NR band support |
| **0xB825** | NR5G RRC Feature Support | Feature capability flags |
| **0x1CCA** | PM RF Bands (Legacy) | LTE RF band information |

---

## 13. UE Capability Structure

### 13.1 LTE UE Capability (TS 36.331)

```
UE-EUTRA-Capability
├── accessStratumRelease              # Release version
├── ue-Category                       # UE category (1-20)
├── pdcp-Parameters                   # PDCP capabilities
├── phyLayerParameters                # Physical layer
├── rf-Parameters
│   └── supportedBandListEUTRA        # Supported bands (1-64)
├── rf-Parameters-v9e0
│   └── supportedBandListEUTRA-v9e0   # Extended bands (65+)
├── rf-Parameters-v1020
│   └── supportedBandCombination-r10  # CA combinations
│       └── BandCombinationParameters-r10
│           ├── bandEUTRA-r10         # Band number
│           ├── bandParametersUL-r10  # UL parameters
│           └── bandParametersDL-r10  # DL parameters
├── measParameters                    # Measurement capabilities
├── featureGroupIndicators            # Feature Group Indicators
└── irat-ParametersNR-r15            # NR interworking
    ├── supportedBandListEN-DC-r15   # EN-DC bands
    └── supportedBandListNR-SA-r15   # SA bands (in v1540)
```

### 13.2 NR UE Capability (TS 38.331)

```
UE-NR-Capability
├── accessStratumRelease              # NR release
├── pdcp-Parameters                   # NR PDCP
├── rlc-Parameters                    # NR RLC
├── mac-Parameters                    # NR MAC
├── phyParameters                     # Physical layer
│   ├── phyParametersCommon
│   ├── phyParametersXDD-Diff
│   └── phyParametersFRX-Diff         # FR1/FR2 differences
├── rf-Parameters
│   └── supportedBandListNR           # Individual NR bands
│       └── BandNR
│           ├── bandNR                # Band number
│           ├── maxBandwidthRequestedDL
│           ├── maxBandwidthRequestedUL
│           └── mimo-ParametersPerBand
├── measAndMobParameters              # Measurement & mobility
├── featureSets                       # Feature sets
│   ├── featureSetsDownlink
│   ├── featureSetsUplink
│   └── featureSetsDownlinkPerCC
└── featureSetCombinations            # Supported combinations
```

### 13.3 MR-DC UE Capability (TS 37.340)

```
UE-MRDC-Capability
├── measParametersMRDC                # MR-DC measurement params
├── rf-ParametersMRDC
│   ├── supportedBandCombinationList  # EN-DC/NE-DC/NGEN-DC combos
│   └── appliedFreqBandListFilter     # Filter applied
├── generalParametersMRDC             # General MR-DC params
└── featureSetCombinations            # Feature set combinations
    └── FeatureSetCombination
        └── FeatureSetsPerBand        # Per-band feature sets
```

### 13.4 UE Capability Information Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  UE CAPABILITY ENQUIRY FLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Network                                         UE             │
│     │                                             │             │
│     │── UECapabilityEnquiry ─────────────────────►│             │
│     │   (RAT-Type: eutra, nr, eutra-nr)           │             │
│     │   (frequencyBandListFilter)                 │             │
│     │                                             │             │
│     │◄── UECapabilityInformation ────────────────│             │
│     │    ├── UE-CapabilityRAT-Container          │             │
│     │    │   ├── rat-Type: eutra                 │             │
│     │    │   └── ue-CapabilityRAT-Container      │             │
│     │    │       (UE-EUTRA-Capability)           │             │
│     │    ├── rat-Type: nr                        │             │
│     │    │   └── ue-CapabilityRAT-Container      │             │
│     │    │       (UE-NR-Capability)              │             │
│     │    └── rat-Type: eutra-nr                  │             │
│     │        └── ue-CapabilityRAT-Container      │             │
│     │            (UE-MRDC-Capability)            │             │
│     │                                             │             │
└─────────────────────────────────────────────────────────────────┘
```

### 13.5 Current UE Capability Parser Coverage

From `src/parsers/ue_capability_parser.py`:

| Capability | Supported | Notes |
|------------|-----------|-------|
| LTE bands (1-64) | Yes | `bandEUTRA` pattern |
| LTE bands (65+) | Yes | v9e0 extension handling |
| NR bands | Yes | `supportedBandListNR` |
| NR SA bands | Yes | `supportedBandListNR-SA-r15` |
| NR NSA bands | Yes | `supportedBandListEN-DC-r15` |
| CA combinations | **No** | Needs implementation |
| EN-DC combinations | **No** | Needs implementation |
| MIMO capabilities | **No** | Needs implementation |
| Bandwidth classes | **No** | Needs implementation |

---

## 14. Implementation Considerations

### 14.1 Combos Module Scope

Based on this research, the Combos Module should handle:

1. **Parsing**
   - RFC XML combo strings (Qualcomm format)
   - UE Capability combo IEs (3GPP format)
   - Carrier Policy constraints

2. **Classification**
   - LTE CA (pure 4G)
   - NR CA (pure 5G SA)
   - EN-DC (4G + 5G NSA)
   - NR-DC (FR1 + FR2)

3. **Analysis**
   - Compare RFC vs UE Capability combos
   - Identify supported/unsupported combos
   - Bandwidth class validation
   - MIMO capability matching

4. **Reporting**
   - Combo support matrix
   - Missing combos identification
   - Configuration recommendations

### 14.2 Data Structures Needed

```python
@dataclass
class BandComponent:
    """Single band in a combo."""
    rat: str              # 'LTE' or 'NR'
    band: int             # Band number
    dl_class: str         # Bandwidth class (DL)
    ul_class: str         # Bandwidth class (UL)
    dl_mimo: int          # MIMO layers (DL)
    ul_mimo: int          # MIMO layers (UL)
    dl_bw: Optional[int]  # Bandwidth MHz (NR only)
    ul_bw: Optional[int]  # Bandwidth MHz (NR only)

@dataclass
class Combo:
    """Complete combo definition."""
    combo_type: str           # 'LTE-CA', 'NR-CA', 'EN-DC', 'NR-DC'
    components: List[BandComponent]
    raw_string: str           # Original notation
    source: str               # 'RFC', 'UE_CAP', 'CARRIER_POLICY'

@dataclass
class ComboAnalysisResult:
    """Results of combo analysis."""
    rfc_combos: List[Combo]
    ue_cap_combos: List[Combo]
    supported: List[Combo]
    unsupported: List[Combo]
    missing_in_rfc: List[Combo]
    missing_in_ue_cap: List[Combo]
```

### 14.3 Parsing Priorities

1. **Phase 1: RFC Combo Parsing**
   - Parse `<ca_4g_5g_combos>` (EN-DC)
   - Parse `<ca_lte_combos>` (LTE CA)
   - Parse `<ca_nr_combos>` (NR CA)
   - Parse `<nr_dc_combos>` (NR-DC)

2. **Phase 2: UE Capability Combo Parsing**
   - Parse `supportedBandCombination-r10` (LTE CA)
   - Parse `supportedBandCombinationList` (NR/MR-DC)
   - Extract MIMO and bandwidth capabilities

3. **Phase 3: Cross-Source Analysis**
   - Compare RFC vs UE Capability
   - Generate support matrix
   - Identify gaps and issues

### 14.4 Validation Rules

| Check | Description |
|-------|-------------|
| **Band Validity** | Band number exists in 3GPP specs |
| **Class Validity** | Bandwidth class valid for band |
| **MIMO Validity** | MIMO config supported by UE |
| **Combo Structure** | Valid band combination per 3GPP tables |
| **Simultaneous Rx/Tx** | Valid simultaneous operation |

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **CA** | Carrier Aggregation - Combining multiple carriers |
| **CC** | Component Carrier - Individual carrier in CA |
| **DC** | Dual Connectivity - Connection to two nodes |
| **DL** | Downlink - Network to UE direction |
| **EN-DC** | E-UTRA NR Dual Connectivity (5G NSA) |
| **EPC** | Evolved Packet Core (4G core) |
| **FR1** | Frequency Range 1 (410 MHz - 7125 MHz) |
| **FR2** | Frequency Range 2 (24.25 GHz - 52.6 GHz) |
| **gNB** | NR base station (g Node B) |
| **MCG** | Master Cell Group |
| **MIMO** | Multiple Input Multiple Output |
| **MN** | Master Node |
| **MR-DC** | Multi-Radio Dual Connectivity |
| **NE-DC** | NR E-UTRA Dual Connectivity |
| **NGEN-DC** | NG-RAN E-UTRA NR Dual Connectivity |
| **NR** | New Radio (5G) |
| **NR-CA** | NR Carrier Aggregation |
| **NR-DC** | NR-NR Dual Connectivity |
| **NSA** | Non-Standalone (5G with LTE anchor) |
| **PCell** | Primary Cell |
| **PDCP** | Packet Data Convergence Protocol |
| **PSCell** | Primary Secondary Cell |
| **RFC** | RF Card (Qualcomm) |
| **RRC** | Radio Resource Control |
| **SA** | Standalone (5G with 5GC) |
| **SCell** | Secondary Cell |
| **SCG** | Secondary Cell Group |
| **SN** | Secondary Node |
| **SUL** | Supplementary Uplink |
| **UE** | User Equipment |
| **UL** | Uplink - UE to Network direction |
| **5GC** | 5G Core Network |

---

## References

### 3GPP Specifications
- [3GPP TS 36.101](https://www.3gpp.org/dynareport/36101.htm) - E-UTRA UE Radio Transmission and Reception
- [3GPP TS 38.101-1](https://www.3gpp.org/dynareport/38101-1.htm) - NR UE Radio (FR1)
- [3GPP TS 38.101-2](https://www.3gpp.org/dynareport/38101-2.htm) - NR UE Radio (FR2)
- [3GPP TS 38.101-3](https://www.3gpp.org/dynareport/38101-3.htm) - NR Interworking
- [3GPP TS 37.340](https://www.3gpp.org/dynareport/37340.htm) - MR-DC Architecture

### Technical Resources
- [3GPP Carrier Aggregation Explained](https://www.3gpp.org/technologies/101-carrier-aggregation-explained)
- [5G NR Carrier Aggregation - PAKTECHPOINT](https://paktechpoint.com/5g-nr-carrier-aggregation/)
- [NR CA Bandwidth Classes - nrexplained.com](https://www.nrexplained.com/bandwidthca)
- [NR-DC Band Combinations - sqimway.com](https://www.sqimway.com/nr_nrdc.php)
- [Dual Connectivity - Devopedia](https://devopedia.org/dual-connectivity)
- [Multi-RAT Dual Connectivity - 5G HUB](https://5ghub.us/multi-rat-dual-connectivity-in-5g/)

### Qualcomm Documents
- **80-35348-127_AA** - NR Band Combo Advertising and NRCA Capability Control
  - Covers NR band combo advertising flow
  - Envelope check process
  - NRCA capability control methods (EFS, MDB, QMI)
  - Debug steps for combo issues
  - Key log packets (0xB826, 0xB0C0)
- **80-NU834-1_A** - EFS to Control CA-Supported Band Combinations
  - prune_ca_combos EFS file format and usage
  - LTE CA combo control via EFS
  - ca_disable for disabling CA entirely
  - Located in: /nv/item_files/modem/lte/rrc/cap

---


---

## 16. Future Enhancements

### 16.1 DUT Automation Module (Separate Module - Phase 2)

A separate **DUT Automation Module** is planned for direct device communication:

| Capability | Description |
|------------|-------------|
| **EFS Reader** | Read EFS files directly from device via QPST |
| **NV Reader** | Read NV items (NV74213, NV74087, etc.) |
| **PCAT Integration** | Automated test execution |

**Benefits:**
- Reusable across Bands, Combos, and future modules
- No manual EFS file extraction needed
- Real-time device analysis

**Prerequisites:** QPST/PCAT installed, device connected via diagnostic port

---

**Document End**

---


**Document End**
