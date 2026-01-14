# GUI Test Cases

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TC-GUI |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Related Test Plan** | TP-GUI-001 |

---

## 1. Dashboard Test Cases

### TC-GUI-001: Verify Dashboard Displays All Modules

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.1, UI-001 |
| **Preconditions** | Flask server running at localhost:5000 |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open browser and navigate to http://localhost:5000 | Dashboard page loads |
| 2 | Count module tiles on dashboard | 7 module tiles displayed |
| 3 | Verify module names | Bands, Combos, IMS, Supp Services, PICS, Band Explorer, Future Purpose |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-002: Verify Module Tile Content

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-005 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Inspect each module tile | Each tile shows: Name, Description, Icon |
| 2 | Verify Bands tile | Name: "Band Analysis", Description visible |
| 3 | Verify Combos tile | Name: "Combos (CA, ENDC)", Description visible |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-003: Verify Active Module Visual Style

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.2, UI-002 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Observe Bands module tile | Tile is clickable, no "Coming Soon" badge |
| 2 | Hover over Bands tile | Cursor changes to pointer, hover effect visible |
| 3 | Verify tile is not grayed out | Full color, active appearance |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-004: Verify Coming Soon Module Visual Style

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.2, UI-002 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Observe Combos module tile | "Coming Soon" badge visible |
| 2 | Observe IMS module tile | "Coming Soon" badge visible |
| 3 | Verify tiles appear disabled/grayed | Visual distinction from active modules |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-005: Verify Active Module Navigation

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-003 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click on Bands module tile | Navigate to /bands upload page |
| 2 | Verify URL | URL is http://localhost:5000/bands |
| 3 | Verify page content | Upload page for Bands module displayed |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-006: Verify Coming Soon Module Navigation

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-004 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click on Combos module tile | Navigate to placeholder page |
| 2 | Verify page content | "Coming Soon" message displayed |
| 3 | Verify "Back to Dashboard" link | Link present and functional |
| 4 | Click "Back to Dashboard" | Returns to main dashboard |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-007: Verify All Coming Soon Modules Show Placeholder

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | UI-004 |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click Combos tile | Coming Soon page displayed |
| 2 | Return to dashboard, click IMS tile | Coming Soon page displayed |
| 3 | Repeat for Supp Services, PICS, Band Explorer, Future | All show Coming Soon page |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-008: Verify Dashboard Header

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | UI Design |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Observe page header | "Analysis Tool" title visible |
| 2 | Verify breadcrumb | Shows "Home" |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-009: Verify Dashboard Responsive Layout

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | Usability |
| **Preconditions** | Dashboard loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Resize browser window to 1920x1080 | Tiles arranged properly |
| 2 | Resize browser window to 1366x768 | Tiles rearrange, still accessible |
| 3 | Resize browser window to 1024x768 | Tiles stack vertically if needed |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 2. Upload Page Test Cases

### TC-GUI-010: Verify Upload Page Content

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-010 |
| **Preconditions** | Navigate to /bands |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify page title | "Band Analysis" displayed |
| 2 | Verify module description | Description text visible |
| 3 | Verify breadcrumb | Shows "Home > Band Analysis" |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-011: Verify File Input Field

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.3, UI-011 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate file input field | File input area visible |
| 2 | Verify input label | Clear label indicating file type expected |
| 3 | Click "Browse" or input area | File browser opens |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-012: Verify Single File Upload

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.3 |
| **Preconditions** | Upload page loaded, valid RFC XML available |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click file input | File browser opens |
| 2 | Select valid RFC XML file | File name displayed in input |
| 3 | Verify file is staged | File name visible, ready for upload |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-013: Verify Multiple File Upload

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.4 |
| **Preconditions** | Upload page loaded, multiple test files available |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select multiple files (RFC, HW filter, Carrier Policy) | All file names displayed |
| 2 | Verify all files are staged | Multiple files listed |
| 3 | Click Analyze | Analysis runs with all files |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-014: Verify Drag and Drop Upload

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | UI-012 |
| **Preconditions** | Upload page loaded, file explorer open |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Drag file over upload area | Drop zone highlights |
| 2 | Drop file onto upload area | File is accepted and displayed |
| 3 | Verify file name shows | File ready for upload |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-015: Verify Analyze Button

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-014 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate Analyze button | Button visible and labeled "Analyze" |
| 2 | Verify button state without files | Button may be disabled or show warning |
| 3 | Select file, then verify button | Button enabled/clickable |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-016: Verify Loading Indicator During Analysis

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-001.3 |
| **Preconditions** | File selected |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click Analyze button | Loading indicator appears |
| 2 | Observe during processing | Spinner/progress visible |
| 3 | Wait for completion | Loading indicator disappears, results shown |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-017: Verify Upload Without File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | Error Handling |
| **Preconditions** | Upload page loaded, no files selected |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click Analyze without selecting files | Error message displayed |
| 2 | Verify error message content | Clear message: "Please upload at least one file" |
| 3 | Verify page state | Stays on upload page, no crash |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-018: Verify Back to Dashboard Link

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Navigation |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Home" in breadcrumb | Returns to dashboard |
| 2 | Verify URL | http://localhost:5000 |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-019: Verify Invalid File Type Handling

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Error Handling |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Try to upload unsupported file type (.exe, .zip) | File rejected or warning shown |
| 2 | Verify behavior | Clear feedback to user |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 3. Results Page Test Cases

### TC-GUI-020: Verify Results Page Display

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.5, UI-020 |
| **Preconditions** | Analysis completed successfully |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify page loads after analysis | Results page displayed |
| 2 | Verify Stage 1 output visible | CLI output/analysis results shown |
| 3 | Verify content is readable | Proper formatting, no garbled text |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-021: Verify Stage 1 Output Content

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-020 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify analysis sections visible | LTE, NR SA, NR NSA sections |
| 2 | Verify band lists displayed | Band numbers visible |
| 3 | Verify PASS/FAIL indicators | Status indicators visible |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-022: Verify AI Expert Review Button

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-021 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate "AI Expert Review" button | Button visible and clickable |
| 2 | Verify button label | Clearly labeled "AI Expert Review" |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-023: Verify Loading During AI Review

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-001.2, NFR-001.3, UI-023 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "AI Expert Review" button | Loading overlay appears |
| 2 | Verify loading message | Message indicates AI review in progress |
| 3 | Wait for completion (may take 1-2 mins) | AI results page loads |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-024: Verify New Analysis Link

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Navigation |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate "New Analysis" link/button | Link visible |
| 2 | Click link | Returns to upload page |
| 3 | Verify page state | Clean upload page, no previous data |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-025: Verify AI Results Page Display

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-030 |
| **Preconditions** | AI review completed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify AI results page loads | Page displayed without errors |
| 2 | Verify Claude's review visible | Review text displayed |
| 3 | Verify Markdown rendered as HTML | Proper formatting (headers, lists, etc.) |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-026: Verify Verdict Section Highlighted

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | UI-031 |
| **Preconditions** | AI results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate verdict section | Verdict visible near top of report |
| 2 | Verify visual distinction | Different color/style from rest |
| 3 | Verify color coding | Green (pass), Yellow (warning), Red (fail) |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-027: Verify Unicode Characters Display

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Encoding |
| **Preconditions** | AI results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Look for checkmarks in report | Proper checkmarks (✓) displayed |
| 2 | Verify no mojibake | No "â" or garbled characters |
| 3 | Verify special characters | All symbols render correctly |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-028: Verify Results Page Scrolling

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | Usability |
| **Preconditions** | Results page with long content |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Scroll through results | Smooth scrolling |
| 2 | Verify all content accessible | Can reach bottom of report |
| 3 | Scroll back to top | Can return to top |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-029: Verify Results Page with No Issues

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Functional |
| **Preconditions** | Analysis with all bands matching |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run analysis with clean config | Results show |
| 2 | Verify PASS indicators | All sections show PASS |
| 3 | Verify no error styling | No red/warning colors |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 4. Download Test Cases

### TC-GUI-030: Verify Download Button Presence

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.6, UI-022 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate download button/link | Button visible |
| 2 | Verify label | "Download Report" or similar |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-031: Verify HTML Report Download

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-002.6, FR-006.4, UI-032 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click download button | File download starts |
| 2 | Verify file type | .html file downloaded |
| 3 | Verify filename | Contains timestamp |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-032: Verify Downloaded Report Opens Standalone

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-006.4 |
| **Preconditions** | HTML report downloaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open downloaded HTML in browser | Report displays correctly |
| 2 | Verify all sections visible | Stage 1 + Stage 2 content visible |
| 3 | Verify styling | CSS applied, report looks formatted |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-033: Verify Final Report Contains Both Stages

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-003.4, FR-006.2, FR-006.3 |
| **Preconditions** | Final report downloaded after AI review |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open final report | Report opens |
| 2 | Verify Stage 1 section | Automated analysis present |
| 3 | Verify Stage 2 section | AI Expert Review present |
| 4 | Verify Verdict section | Verdict at top of report |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-034: Verify Download from AI Results Page

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | UI-032 |
| **Preconditions** | AI results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate "Download Final Report" button | Button visible |
| 2 | Click download | File downloads |
| 3 | Verify file is final version | Contains both stages |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 5. Knowledge Base Test Cases

### TC-GUI-040: Verify Knowledge Base Section

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-005.1, UI-013 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate Knowledge Base section | Section visible on upload page |
| 2 | Verify KB files listed | Existing KB files shown |
| 3 | Verify file selection | Can select/deselect KB files |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-041: Verify Upload to Knowledge Base

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | FR-005.2 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate KB upload option | Upload button/area visible |
| 2 | Upload file to KB | File accepted |
| 3 | Verify file appears in KB list | New file listed |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-042: Verify Delete from Knowledge Base

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | File Management |
| **Preconditions** | KB has files |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate delete option for KB file | Delete button/icon visible |
| 2 | Click delete | Confirmation prompt or file removed |
| 3 | Verify file removed from list | File no longer listed |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 6. Accessibility Test Cases

### TC-GUI-050: Verify Server Accessibility

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-001.1 |
| **Preconditions** | Flask server started |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open browser | Browser launches |
| 2 | Navigate to http://localhost:5000 | Page loads |
| 3 | Verify no connection errors | Dashboard displayed |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-051: Verify Page Load Speed

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | Performance |
| **Preconditions** | Server running |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to dashboard | Page loads within 2 seconds |
| 2 | Navigate to upload page | Page loads within 2 seconds |
| 3 | Navigate to coming soon page | Page loads within 2 seconds |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 7. Error Handling Test Cases

### TC-GUI-060: Verify Error on No Files Selected

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-001.4 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click Analyze without files | Error message shown |
| 2 | Verify message is user-friendly | Clear, actionable message |
| 3 | Verify page doesn't crash | Page remains functional |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-061: Verify Error on Invalid File

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-001.4 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload malformed XML file | Error message shown |
| 2 | Verify error describes issue | Message indicates file problem |
| 3 | Verify can try again | Page allows new upload |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-062: Verify Error on Empty File

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-001.4 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload empty file (0 bytes) | Error message shown |
| 2 | Verify appropriate message | "File is empty" or similar |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-063: Verify Error on Claude CLI Timeout

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | FR-004.2, NFR-001.4 |
| **Preconditions** | Results page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click AI Expert Review | Processing starts |
| 2 | If Claude times out | Error message displayed |
| 3 | Verify message is helpful | Suggests retry or alternative |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-064: Verify Error on Claude CLI Not Installed

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-001.4 |
| **Preconditions** | Claude CLI not in PATH |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Try AI Expert Review | Error message shown |
| 2 | Verify message content | Indicates Claude CLI not found |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-065: Verify 404 Page

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | Error Handling |
| **Preconditions** | Server running |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to invalid URL (e.g., /invalid) | Error page shown |
| 2 | Verify error message | 404 or "Page not found" |
| 3 | Verify link to home | Can navigate back to dashboard |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 8. Boundary Test Cases

### TC-GUI-070: Verify Maximum File Size Upload

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-002.3 |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload file slightly under 50MB | File accepted |
| 2 | Upload file exactly 50MB | File accepted |
| 3 | Upload file over 50MB | Error message, file rejected |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-071: Verify Long Filename Handling

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | Usability |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload file with very long filename | File accepted |
| 2 | Verify filename display | Truncated or scrollable |
| 3 | Verify download works | Download preserves name |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-072: Verify Special Characters in Filename

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Requirement** | Security |
| **Preconditions** | Upload page loaded |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Upload file with spaces in name | File handled correctly |
| 2 | Upload file with special chars | File sanitized or rejected safely |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 9. Browser Compatibility Test Cases

### TC-GUI-080: Verify Chrome Compatibility

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Requirement** | NFR-005.3 |
| **Preconditions** | Chrome browser installed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open application in Chrome | Dashboard loads correctly |
| 2 | Test file upload | Works correctly |
| 3 | Test results display | Displays correctly |
| 4 | Test download | Downloads correctly |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-081: Verify Firefox Compatibility

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-005.3 |
| **Preconditions** | Firefox browser installed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open application in Firefox | Dashboard loads correctly |
| 2 | Test file upload | Works correctly |
| 3 | Test results display | Displays correctly |
| 4 | Test download | Downloads correctly |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

### TC-GUI-082: Verify Edge Compatibility

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Requirement** | NFR-005.3 |
| **Preconditions** | Edge browser installed |

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open application in Edge | Dashboard loads correctly |
| 2 | Test file upload | Works correctly |
| 3 | Test results display | Displays correctly |
| 4 | Test download | Downloads correctly |

| **Status** | |
| **Actual Result** | |
| **Comments** | |

---

## 10. Test Execution Summary

| Category | Total TCs | Passed | Failed | Blocked | Not Run |
|----------|-----------|--------|--------|---------|---------|
| Dashboard | 9 | | | | |
| Upload Page | 10 | | | | |
| Results Page | 10 | | | | |
| Download | 5 | | | | |
| Knowledge Base | 3 | | | | |
| Accessibility | 2 | | | | |
| Error Handling | 6 | | | | |
| Boundary | 3 | | | | |
| Compatibility | 3 | | | | |
| **Total** | **51** | | | | |

---

## 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
