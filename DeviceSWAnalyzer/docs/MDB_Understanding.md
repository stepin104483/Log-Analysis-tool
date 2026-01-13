# MDB (Mobile Database) - Complete Understanding

## 1. What is MDB?

MDB (Mobile Database) is a Qualcomm mechanism to **limit bands based on geographic location (MCC - Mobile Country Code)**. It ensures UE only uses bands that are valid/licensed in a specific country.

---

## 2. MDB Types

| MDB Type | Purpose | Example |
|----------|---------|---------|
| **mcc2bands** | Maps MCC to allowed LTE/NR bands | US (310-316) allows LTE B1,B3,B4... |
| **mcc2arfcn** | Maps MCC to ARFCN frequency ranges | US n77 allows 630000-665333 |
| **mcc2border** | Maps MCC to neighboring country MCCs | US borders Canada (302), Mexico (334) |
| **polygon2mccs** | Maps geographic regions to MCCs | "us_mainland" -> 310,311,312... |
| **location_polygons** | Defines geographic polygons (lat/long) | US mainland boundary vertices |
| **plmn2freqlist** | Maps PLMN to frequency lists | Per-operator frequency config |
| **plmn2cacombos** | Maps PLMN to CA combinations | Per-operator CA combos |
| **plmn2features** | Maps PLMN to features | Per-operator feature flags |

---

## 3. mcc2bands.xml Structure

```xml
<mdb type="mcc2bands" content_version="41" owner="Qualcomm">

  <!-- US MCCs: 310-316 -->
  <entry mccs="310 311 312 313 314 315 316">
    <c> all </c>                                    <!-- CDMA bands -->
    <l> 1 3 4 6 11 12 13 16 24 25 28 29 37 40 45 47 65 70 </l>  <!-- LTE bands (0-indexed) -->
    <n> 1 4 24 28 40 65 70 76 257 259 260 </n>     <!-- NR NSA bands -->
    <s> 1 4 24 25 28 40 47 65 69 70 76 </s>        <!-- NR SA bands -->
  </entry>

  <!-- Default: all other countries -->
  <entry mccs="*">
    <c> all </c>
    <n> all </n>
    <s> </s>     <!-- SA disabled by default -->
  </entry>

</mdb>
```

### Band Tags:
| Tag | RAT | Description |
|-----|-----|-------------|
| `<c>` | CDMA | CDMA/1x bands |
| `<t>` | TDS | TD-SCDMA bands |
| `<g>` | GSM | GSM bands |
| `<l>` | LTE | LTE bands (0-indexed: 0=B1, 2=B3) |
| `<n>` | NR NSA | NR NSA bands |
| `<s>` | NR SA | NR SA bands |

### Special Values:
- `all` - All bands allowed
- Empty `<s></s>` - No SA bands allowed
- `*` in mccs - Default/fallback entry

---

## 4. Band Indexing (IMPORTANT)

**MDB uses 0-indexed bands for LTE:**
```
MDB Value  ->  Actual Band
    0      ->     B1
    2      ->     B3
    6      ->     B7
   39      ->    B40
```

**NR bands appear to be 1-indexed (actual band numbers)**

---

## 5. MDB in Band Filtering Pipeline

```
RFC (RF Card)
     |
     v
HW Band Filtering
     |
     v
Carrier Policy
     |
     v
Generic Restrictions
     |
     v
+---> MDB (mcc2bands) <--- Based on current MCC
     |
     v
Final Bands -> UE Capability
```

**MDB filters bands based on:**
1. Current registered MCC (from network)
2. GPS location (polygon-based)
3. Border country detection

---

## 6. MDB Levels

### Device Level (DEV MDB)
- Applies to entire device
- Configured in **HW MBN**
- Files: `mcc2arfcn.mdb`, `plmn2freqlist.mdb`, `plmn2cacombos.mdb`, `plmn2features.mdb`
- mcfgVariant = "2"

### Subscription Level (SUB MDB)
- Applies per SIM/subscription
- Configured in **SW MBN**
- Files: `plmn2freqlist_sub.mdb`, `plmn2cacombos_sub.mdb`, `plmn2features_sub.mdb`
- mcfgVariant = "23"

**Lookup Priority:** SUB MDB first, then DEV MDB if not found

---

## 7. MDB Auto-Learning

MDB can **automatically learn new bands** when UE registers on bands not in the database.

### Enable/Disable Auto-Learning:
```bash
# Disable auto-learning (make MDB read-only)
mdbc.py -i <input> -o <output> -ro

# Disable via EFS
EFS: ignore_mcc2bands_mdb
```

### Auto-Learn Timers:
- `auto_learn_time` - Timer after going online (default: 25 hours)
- `net_scan_time` - Retry time for network scan

### Log Indicators:
```
// MDB lookup
policyman_location.c 2136  determined MCC 334 from location source 2
policyman_location.c 2205  rf bands from database for MCC 334

// Auto-learn attempt
policyman_location.c 3433  Band 126 reported for MCC 334

// Read-only failure
mdb_split.c 369  Update to MDB 0x39a529df failed, MDB is read only

// Success
"Learned new Band %d on MCC %d"
```

---

## 8. MDB File Locations

| Location | Type |
|----------|------|
| `/mdb/nr/mcc2bands.mdb` | NR mcc2bands |
| `/mdb/lte/mcc2bands_lte.mdb` | LTE mcc2bands |
| `/mdb/nr/mcc2arfcn.mdb` | NR frequency limits |
| `/mdb/nr/plmn2features.mdb` | NR features per PLMN |
| `/policyman/hardware_band_filtering.xml` | HW band filter |

---

## 9. Disabling MDB

```bash
# Option 1: EFS item
Create EFS: /nv/item_files/modem/mmode/ignore_mcc2bands_mdb

# Option 2: Remove mcc2bands.mdb from MBN

# Option 3: Set all bands to "all" in mcc2bands.xml
<entry mccs="*">
  <l> all </l>
  <n> all </n>
  <s> all </s>
</entry>
```

---

## 10. Sample Country Configurations

### US (MCC 310-316)
```xml
<entry mccs="310 311 312 313 314 315 316">
  <c> all </c>
  <l> 1 3 4 6 11 12 13 16 24 25 28 29 37 40 45 47 65 70 </l>
  <n> 1 4 24 28 40 65 70 76 257 259 260 </n>
  <s> 1 4 24 25 28 40 47 65 69 70 76 </s>
</entry>
```

### China (MCC 460)
```xml
<entry mccs="460">
  <c> all </c>
  <t> all </t>
  <l> 0 2 4 7 33 37 38 39 40 </l>
  <n> 40 77 78 </n>
  <s> 0 4 7 27 40 77 78 </s>
</entry>
```

### India (MCC 404, 405)
```xml
<entry mccs="404 405">
  <l> 0 2 4 7 39 40 </l>
  <n> all </n>
  <s> 27 77 </s>
</entry>
```

---

## 11. Integration with Band Analyzer Tool

For our tool, MDB parsing needs to:

1. **Parse mcc2bands.xml** - Extract allowed bands per MCC
2. **Convert 0-indexed to 1-indexed** for LTE bands
3. **Support "all" keyword** - Means no filtering
4. **Handle default entry** - `mccs="*"` is fallback
5. **Check current MCC** - From QXDM log or user input

### Parser Logic:
```python
def parse_mcc2bands(xml_file, target_mcc):
    # Find entry matching target_mcc
    # If not found, use default "*" entry
    # Extract <l>, <n>, <s> bands
    # Convert LTE bands: actual_band = mdb_value + 1
    # Return allowed bands set
```

---

## 12. References

| Document | Description |
|----------|-------------|
| KBA-201108184431 | How to check LTE and NR band |
| KBA-220107011510 | Disable MDB auto-learning |
| KBA-221026190225 | Manual PLMN search by Policyman |
| KBA-230421012404 | MDB per SUB |
| 80-PN878-44 | MDB User Guide (Qualcomm DCN) |

---

*Document Version: 1.0*
*Based on Qualcomm KBAs and sample MDB files*
