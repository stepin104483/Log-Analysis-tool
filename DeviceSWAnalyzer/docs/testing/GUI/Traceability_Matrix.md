# GUI Requirements Traceability Matrix

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TM-GUI-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Related Documents** | TP-GUI-001, TC-GUI |

---

## 1. Functional Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| FR-002.1 | Web-based dashboard showing all modules | TC-GUI-001, TC-GUI-002 | Full |
| FR-002.2 | Dashboard displays module status (active/coming soon) | TC-GUI-003, TC-GUI-004 | Full |
| FR-002.3 | File upload interface for active modules | TC-GUI-010, TC-GUI-011, TC-GUI-012 | Full |
| FR-002.4 | Support multiple file uploads | TC-GUI-013 | Full |
| FR-002.5 | Display analysis results in browser | TC-GUI-020, TC-GUI-021 | Full |
| FR-002.6 | Download option for HTML reports | TC-GUI-030, TC-GUI-031, TC-GUI-032 | Full |
| FR-003.4 | Final report combines Stage 1 and Stage 2 | TC-GUI-033 | Full |
| FR-004.2 | Handle Claude CLI timeout gracefully | TC-GUI-063 | Full |
| FR-005.1 | Knowledge base file library | TC-GUI-040 | Full |
| FR-005.2 | Upload files to knowledge base | TC-GUI-041 | Full |
| FR-006.2 | Stage 1 output in final report | TC-GUI-033 | Full |
| FR-006.3 | Stage 2 output in final report | TC-GUI-033 | Full |
| FR-006.4 | Standalone viewable HTML report | TC-GUI-032 | Full |

---

## 2. UI Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| UI-001 | Dashboard displays all registered modules as tiles | TC-GUI-001 | Full |
| UI-002 | Active modules visually distinct from coming soon | TC-GUI-003, TC-GUI-004 | Full |
| UI-003 | Clicking active module navigates to upload page | TC-GUI-005 | Full |
| UI-004 | Clicking coming soon module shows placeholder | TC-GUI-006, TC-GUI-007 | Full |
| UI-005 | Module tiles display name, description, icon | TC-GUI-002 | Full |
| UI-010 | Upload page shows module name and description | TC-GUI-010 | Full |
| UI-011 | File input for each required field | TC-GUI-011 | Full |
| UI-012 | Support drag-and-drop file upload | TC-GUI-014 | Full |
| UI-013 | Knowledge base file selector | TC-GUI-040 | Full |
| UI-014 | Analyze button to start analysis | TC-GUI-015 | Full |
| UI-020 | Results page displays Stage 1 output | TC-GUI-020, TC-GUI-021 | Full |
| UI-021 | AI Expert Review button | TC-GUI-022 | Full |
| UI-022 | Download Report option | TC-GUI-030 | Full |
| UI-023 | Loading indicator during AI review | TC-GUI-023 | Full |
| UI-030 | AI results display Claude's review | TC-GUI-025 | Full |
| UI-031 | Verdict section highlighted | TC-GUI-026 | Full |
| UI-032 | Final report download | TC-GUI-031, TC-GUI-034 | Full |

---

## 3. Non-Functional Requirements Coverage

| Req ID | Requirement Description | Test Case(s) | Coverage |
|--------|-------------------------|--------------|----------|
| NFR-001.1 | UI accessible at localhost:5000 | TC-GUI-050 | Full |
| NFR-001.2 | Clear feedback during long operations | TC-GUI-023 | Full |
| NFR-001.3 | Loading indicators during analysis | TC-GUI-016, TC-GUI-023 | Full |
| NFR-001.4 | User-friendly error messages | TC-GUI-060, TC-GUI-061, TC-GUI-062, TC-GUI-063, TC-GUI-064, TC-GUI-065 | Full |
| NFR-002.3 | Maximum upload file size 50MB | TC-GUI-070 | Full |
| NFR-005.3 | Support Chrome, Firefox, Edge | TC-GUI-080, TC-GUI-081, TC-GUI-082 | Full |

---

## 4. Test Case to Requirements Mapping

| Test Case ID | Test Case Name | Requirements Covered |
|--------------|----------------|---------------------|
| TC-GUI-001 | Dashboard Displays All Modules | FR-002.1, UI-001 |
| TC-GUI-002 | Module Tile Content | UI-005 |
| TC-GUI-003 | Active Module Visual Style | FR-002.2, UI-002 |
| TC-GUI-004 | Coming Soon Module Visual Style | FR-002.2, UI-002 |
| TC-GUI-005 | Active Module Navigation | UI-003 |
| TC-GUI-006 | Coming Soon Module Navigation | UI-004 |
| TC-GUI-007 | All Coming Soon Modules Show Placeholder | UI-004 |
| TC-GUI-008 | Dashboard Header | UI Design |
| TC-GUI-009 | Dashboard Responsive Layout | Usability |
| TC-GUI-010 | Upload Page Content | UI-010 |
| TC-GUI-011 | File Input Field | FR-002.3, UI-011 |
| TC-GUI-012 | Single File Upload | FR-002.3 |
| TC-GUI-013 | Multiple File Upload | FR-002.4 |
| TC-GUI-014 | Drag and Drop Upload | UI-012 |
| TC-GUI-015 | Analyze Button | UI-014 |
| TC-GUI-016 | Loading Indicator During Analysis | NFR-001.3 |
| TC-GUI-017 | Upload Without File | Error Handling |
| TC-GUI-018 | Back to Dashboard Link | Navigation |
| TC-GUI-019 | Invalid File Type Handling | Error Handling |
| TC-GUI-020 | Results Page Display | FR-002.5, UI-020 |
| TC-GUI-021 | Stage 1 Output Content | UI-020 |
| TC-GUI-022 | AI Expert Review Button | UI-021 |
| TC-GUI-023 | Loading During AI Review | NFR-001.2, NFR-001.3, UI-023 |
| TC-GUI-024 | New Analysis Link | Navigation |
| TC-GUI-025 | AI Results Page Display | UI-030 |
| TC-GUI-026 | Verdict Section Highlighted | UI-031 |
| TC-GUI-027 | Unicode Characters Display | Encoding |
| TC-GUI-028 | Results Page Scrolling | Usability |
| TC-GUI-029 | Results Page with No Issues | Functional |
| TC-GUI-030 | Download Button Presence | FR-002.6, UI-022 |
| TC-GUI-031 | HTML Report Download | FR-002.6, UI-032 |
| TC-GUI-032 | Downloaded Report Opens Standalone | FR-006.4 |
| TC-GUI-033 | Final Report Contains Both Stages | FR-003.4, FR-006.2, FR-006.3 |
| TC-GUI-034 | Download from AI Results Page | UI-032 |
| TC-GUI-040 | Knowledge Base Section | FR-005.1, UI-013 |
| TC-GUI-041 | Upload to Knowledge Base | FR-005.2 |
| TC-GUI-042 | Delete from Knowledge Base | File Management |
| TC-GUI-050 | Server Accessibility | NFR-001.1 |
| TC-GUI-051 | Page Load Speed | Performance |
| TC-GUI-060 | Error on No Files Selected | NFR-001.4 |
| TC-GUI-061 | Error on Invalid File | NFR-001.4 |
| TC-GUI-062 | Error on Empty File | NFR-001.4 |
| TC-GUI-063 | Error on Claude CLI Timeout | FR-004.2, NFR-001.4 |
| TC-GUI-064 | Error on Claude CLI Not Installed | NFR-001.4 |
| TC-GUI-065 | 404 Page | Error Handling |
| TC-GUI-070 | Maximum File Size Upload | NFR-002.3 |
| TC-GUI-071 | Long Filename Handling | Usability |
| TC-GUI-072 | Special Characters in Filename | Security |
| TC-GUI-080 | Chrome Compatibility | NFR-005.3 |
| TC-GUI-081 | Firefox Compatibility | NFR-005.3 |
| TC-GUI-082 | Edge Compatibility | NFR-005.3 |

---

## 5. Coverage Summary

### 5.1 Requirements Coverage Statistics

| Category | Total Requirements | Covered | Coverage % |
|----------|-------------------|---------|------------|
| Functional (FR-*) | 13 | 13 | 100% |
| UI (UI-*) | 17 | 17 | 100% |
| Non-Functional (NFR-*) | 6 | 6 | 100% |
| **Total** | **36** | **36** | **100%** |

### 5.2 Test Case Distribution

| Category | Test Cases | % of Total |
|----------|------------|------------|
| Dashboard | 9 | 18% |
| Upload Page | 10 | 20% |
| Results Page | 10 | 20% |
| Download | 5 | 10% |
| Knowledge Base | 3 | 6% |
| Accessibility | 2 | 4% |
| Error Handling | 6 | 12% |
| Boundary | 3 | 6% |
| Compatibility | 3 | 6% |
| **Total** | **51** | **100%** |

### 5.3 Priority Distribution

| Priority | Count | % |
|----------|-------|---|
| High | 32 | 63% |
| Medium | 14 | 27% |
| Low | 5 | 10% |
| **Total** | **51** | **100%** |

---

## 6. Gaps and Notes

### 6.1 Requirements Without Explicit Test Cases

| Requirement | Reason | Mitigation |
|-------------|--------|------------|
| None | All GUI requirements have test coverage | N/A |

### 6.2 Test Cases Without Requirement Mapping

| Test Case | Reason |
|-----------|--------|
| TC-GUI-008 | UI Design (implicit requirement) |
| TC-GUI-009 | Usability (implicit requirement) |
| TC-GUI-017 | Error Handling (implicit requirement) |
| TC-GUI-018 | Navigation (implicit requirement) |
| TC-GUI-019 | Error Handling (implicit requirement) |
| TC-GUI-024 | Navigation (implicit requirement) |
| TC-GUI-027 | Encoding (implicit requirement) |
| TC-GUI-028 | Usability (implicit requirement) |
| TC-GUI-029 | Functional verification |
| TC-GUI-042 | File Management (implicit requirement) |
| TC-GUI-051 | Performance (implicit requirement) |
| TC-GUI-065 | Error Handling (implicit requirement) |
| TC-GUI-071 | Usability (implicit requirement) |
| TC-GUI-072 | Security (implicit requirement) |

These test cases address implicit requirements that enhance usability, security, and reliability.

---

## 7. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
