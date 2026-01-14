# GUI Test Plan

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | TP-GUI-001 |
| **Version** | 1.0 |
| **Created** | 2026-01-14 |
| **Author** | DeviceSWAnalyzer Team |
| **Status** | Draft |

---

## 1. Introduction

### 1.1 Purpose
This document defines the test plan for the Graphical User Interface (GUI) of the DeviceSWAnalyzer tool. It covers all web-based UI components including dashboard, module pages, file uploads, results display, and report downloads.

### 1.2 Scope

**In Scope:**
- Dashboard functionality
- Module navigation
- File upload interface
- Analysis results display
- AI Expert Review interface
- Report download functionality
- Error handling and user feedback
- Browser compatibility

**Out of Scope:**
- Backend analysis logic (covered in module-specific test plans)
- Claude CLI integration testing (covered in AI Integration test plan)
- Performance/load testing
- Security testing

### 1.3 References

| Document | Location |
|----------|----------|
| Overall Requirements | `docs/Overall_Requirements.md` |
| Overall Architecture | `docs/Overall_Architecture.md` |
| UI Design | `docs/UI_Design.md` |
| GUI Test Cases | `docs/testing/GUI/test_cases/TC_GUI.md` |

---

## 2. Test Items

### 2.1 Features to Test

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| GUI-F01 | Dashboard | Main page with module tiles |
| GUI-F02 | Module Navigation | Navigation between modules |
| GUI-F03 | Upload Page | File upload interface |
| GUI-F04 | Results Page | Stage 1 analysis results display |
| GUI-F05 | AI Review Page | Stage 2 AI review display |
| GUI-F06 | Report Download | HTML report download |
| GUI-F07 | Knowledge Base | KB file management |
| GUI-F08 | Error Handling | Error messages and feedback |
| GUI-F09 | Loading States | Loading indicators |
| GUI-F10 | Coming Soon | Placeholder pages |

### 2.2 Features NOT to Test

| Feature | Reason |
|---------|--------|
| Analysis algorithms | Covered in Bands module test plan |
| Claude CLI execution | Covered in AI Integration test plan |
| File parsing logic | Covered in module-specific test plans |

---

## 3. Test Approach

### 3.1 Test Types

| Test Type | Description | Priority |
|-----------|-------------|----------|
| **Functional** | Verify features work as specified | High |
| **Negative** | Verify error handling | High |
| **Usability** | Verify user experience | Medium |
| **Compatibility** | Verify browser support | Medium |
| **Boundary** | Verify edge cases | Medium |

### 3.2 Test Levels

| Level | Description |
|-------|-------------|
| **Component** | Individual UI components |
| **Integration** | UI + Backend interaction |
| **System** | End-to-end user workflows |

### 3.3 Test Execution Approach

- **Manual Testing**: Primary approach for UI validation
- **Checklist-Based**: Structured test case execution
- **Exploratory**: Ad-hoc testing for edge cases

---

## 4. Entry Criteria

Testing can begin when:

- [ ] Flask application is running at localhost:5000
- [ ] All 7 modules are registered and visible
- [ ] Test data files are available in `test_data/` folder
- [ ] Test cases are reviewed and approved
- [ ] Test environment (browser) is ready

---

## 5. Exit Criteria

Testing is complete when:

- [ ] All High priority test cases executed
- [ ] All High priority test cases passed (or defects documented)
- [ ] All Medium priority test cases executed
- [ ] No Critical/Blocker defects remain open
- [ ] Test report is generated and reviewed

---

## 6. Test Environment

### 6.1 Software Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 |
| **Python** | 3.8+ |
| **Flask** | Running at localhost:5000 |
| **Browser** | Chrome (primary), Firefox, Edge |

### 6.2 Test Data

| Data Type | Location | Description |
|-----------|----------|-------------|
| Valid RFC | `test_data/valid/` | Valid XML files for testing |
| Invalid Files | `test_data/invalid/` | Malformed files for negative testing |
| Large Files | `test_data/boundary/` | Files near size limits |

---

## 7. Test Schedule

| Phase | Activities | Duration |
|-------|------------|----------|
| Preparation | Setup environment, prepare test data | 1 day |
| Execution - High Priority | Execute critical test cases | 2 days |
| Execution - Medium Priority | Execute remaining test cases | 1 day |
| Defect Fixes | Retest fixed defects | As needed |
| Reporting | Generate test report | 0.5 day |

---

## 8. Requirements Traceability

### 8.1 Functional Requirements Coverage

| Requirement ID | Requirement Description | Test Case ID |
|----------------|------------------------|--------------|
| FR-002.1 | Web-based dashboard showing all modules | TC-GUI-001, TC-GUI-002 |
| FR-002.2 | Dashboard displays module status | TC-GUI-003, TC-GUI-004 |
| FR-002.3 | File upload interface for active modules | TC-GUI-010, TC-GUI-011 |
| FR-002.4 | Support multiple file uploads | TC-GUI-012, TC-GUI-013 |
| FR-002.5 | Display analysis results in browser | TC-GUI-020, TC-GUI-021 |
| FR-002.6 | Download option for HTML reports | TC-GUI-030, TC-GUI-031 |
| FR-005.1 | Knowledge base file library | TC-GUI-040 |
| FR-005.2 | Upload files to knowledge base | TC-GUI-041 |

### 8.2 UI Requirements Coverage

| Requirement ID | Requirement Description | Test Case ID |
|----------------|------------------------|--------------|
| UI-001 | Dashboard displays all registered modules as tiles | TC-GUI-001 |
| UI-002 | Active modules visually distinct from coming soon | TC-GUI-003 |
| UI-003 | Clicking active module navigates to upload page | TC-GUI-005 |
| UI-004 | Clicking coming soon module shows placeholder | TC-GUI-006 |
| UI-005 | Module tiles display name, description, icon | TC-GUI-002 |
| UI-010 | Upload page shows module name and description | TC-GUI-010 |
| UI-011 | File input for each required field | TC-GUI-011 |
| UI-012 | Support drag-and-drop file upload | TC-GUI-014 |
| UI-013 | Knowledge base file selector | TC-GUI-040 |
| UI-014 | Analyze button to start analysis | TC-GUI-015 |
| UI-020 | Results page displays Stage 1 output | TC-GUI-020 |
| UI-021 | AI Expert Review button | TC-GUI-022 |
| UI-022 | Download Report option | TC-GUI-030 |
| UI-023 | Loading indicator during AI review | TC-GUI-023 |
| UI-030 | AI results display Claude's review | TC-GUI-025 |
| UI-031 | Verdict section highlighted | TC-GUI-026 |
| UI-032 | Final report download | TC-GUI-031 |

### 8.3 Non-Functional Requirements Coverage

| Requirement ID | Requirement Description | Test Case ID |
|----------------|------------------------|--------------|
| NFR-001.1 | UI accessible at localhost:5000 | TC-GUI-050 |
| NFR-001.2 | Clear feedback during long operations | TC-GUI-023 |
| NFR-001.3 | Loading indicators during analysis | TC-GUI-016, TC-GUI-023 |
| NFR-001.4 | User-friendly error messages | TC-GUI-060 to TC-GUI-065 |
| NFR-002.3 | Maximum upload file size 50MB | TC-GUI-070 |
| NFR-005.3 | Support Chrome, Firefox, Edge | TC-GUI-080 to TC-GUI-082 |

---

## 9. Test Cases Summary

| Category | TC ID Range | Count | Priority |
|----------|-------------|-------|----------|
| Dashboard | TC-GUI-001 to TC-GUI-009 | 9 | High |
| Upload Page | TC-GUI-010 to TC-GUI-019 | 10 | High |
| Results Page | TC-GUI-020 to TC-GUI-029 | 10 | High |
| Download | TC-GUI-030 to TC-GUI-034 | 5 | High |
| Knowledge Base | TC-GUI-040 to TC-GUI-042 | 3 | Medium |
| Accessibility | TC-GUI-050 to TC-GUI-051 | 2 | Medium |
| Error Handling | TC-GUI-060 to TC-GUI-065 | 6 | High |
| Boundary | TC-GUI-070 to TC-GUI-072 | 3 | Medium |
| Compatibility | TC-GUI-080 to TC-GUI-082 | 3 | Medium |
| **Total** | | **51** | |

Detailed test cases are documented in: `docs/testing/test_cases/TC_GUI.md`

---

## 10. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Flask server not running | Low | High | Document startup steps |
| Browser compatibility issues | Medium | Medium | Test on multiple browsers |
| Test data not available | Low | High | Prepare test data in advance |
| Claude CLI not installed | Medium | Medium | Document as prerequisite |
| File upload failures | Low | Medium | Test with various file types |

---

## 11. Defect Management

### 11.1 Defect Severity

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Application crash, data loss | Upload crashes server |
| **Major** | Feature not working | Cannot download report |
| **Minor** | Feature works with issues | Styling problems |
| **Trivial** | Cosmetic issues | Typo in label |

### 11.2 Defect Priority

| Priority | Description | Resolution Time |
|----------|-------------|-----------------|
| **P1** | Fix immediately | Same day |
| **P2** | Fix before release | 2-3 days |
| **P3** | Fix if time permits | Next release |
| **P4** | Nice to have | Backlog |

---

## 12. Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Test Plan | `docs/testing/GUI/Test_Plan.md` | This document |
| Test Cases | `docs/testing/GUI/test_cases/TC_GUI.md` | Detailed test cases |
| Traceability Matrix | `docs/testing/GUI/Traceability_Matrix.md` | Requirements-to-test mapping |
| E2E Tests | `tests/e2e/GUI/` | Playwright E2E tests |
| Test Data | `docs/testing/test_data/` | Test input files |
| Test Report | `docs/testing/test_reports/` | Execution results |

---

## 13. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | | | |
| Developer | | | |
| Product Owner | | | |

---

## 14. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | DeviceSWAnalyzer Team | Initial version |
