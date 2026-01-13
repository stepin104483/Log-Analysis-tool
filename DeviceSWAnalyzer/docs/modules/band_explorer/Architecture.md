# Band Explorer Module - Architecture

> **Status:** Coming Soon

## 1. Overview

The Band Explorer module will provide a search/lookup interface for band information including bandwidth (BW), subcarrier spacing (SCS), and related CA/EN-DC combos for SA and NSA modes.

---

## 2. Planned Features

- Search bands by band number
- Display supported bandwidths for each band
- Display supported SCS configurations
- Show related CA combos
- Show related EN-DC combos
- Differentiate SA vs NSA support
- Provide band specifications (frequency, duplex mode)

---

## 3. Data Sources

| Source | Description |
|--------|-------------|
| 3GPP TS 38.101-1 | NR FR1 bands |
| 3GPP TS 38.101-2 | NR FR2 bands |
| 3GPP TS 36.101 | LTE bands |
| Internal KB | Combo definitions |

---

## 4. User Interface

### 4.1 Search Interface
- Band number input field
- Technology filter (LTE/NR/Both)
- Mode filter (SA/NSA/Both)

### 4.2 Results Display
- Band basic info (frequency, duplex)
- Supported BWs table
- Supported SCS table
- Related combos list

---

## 5. Architecture Design

*To be defined when module is implemented.*

---

## 6. Related Documents

- [Requirements.md](./Requirements.md) - Module requirements
- [Overall_Architecture.md](../../Overall_Architecture.md) - System architecture
