# Analysis Tool - Web UI Design Document

**Version**: 1.0
**Last Updated**: 2026-01-09
**Related Document**: [Architecture_Design.md](./Architecture_Design.md)

---

## 1. Overview

This document describes the web-based user interface for the Analysis Tool, built using Flask. The UI provides a user-friendly way to perform various modem/device analysis tasks without requiring command-line knowledge.

### 1.1 Design Goals

- **Accessibility**: Non-technical users can run analysis with file upload and button clicks
- **Modularity**: Multiple analysis modules accessible from a single dashboard
- **Extensibility**: Easy to add new analysis modules in the future
- **Clean Design**: Professional, modern interface with red/white color scheme

### 1.2 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask (Python) |
| Frontend | HTML5, CSS3, JavaScript |
| Templates | Jinja2 |
| Styling | Custom CSS (no frameworks) |

---

## 2. Architecture

### 2.1 Directory Structure

```
Log-Analysis-tool/
├── run_web.py                        # Web server entry point
├── requirements.txt                  # Flask dependencies
├── uploads/                          # Temporary file uploads
│   └── input/                        # Session-based input files
├── knowledge_library/                # Permanent KB storage
│
└── Band_Combos_Analyzer/
    ├── src/
    │   ├── web/                      # Flask web application
    │   │   ├── __init__.py
    │   │   ├── app.py               # App factory & configuration
    │   │   └── routes/
    │   │       ├── __init__.py
    │   │       ├── main.py          # Dashboard routes
    │   │       └── bands.py         # Bands module routes
    │   ├── core/                    # (existing) Analysis engine
    │   ├── parsers/                 # (existing) File parsers
    │   └── output/                  # (existing) Report generators
    │
    ├── templates/                   # Jinja2 templates
    │   ├── base.html               # Base layout
    │   ├── index.html              # Main dashboard
    │   ├── coming_soon.html        # Placeholder page
    │   └── bands/
    │       ├── upload.html         # File upload form
    │       └── results.html        # Analysis results
    │
    └── static/
        └── css/
            └── style.css           # Main stylesheet
```

### 2.2 URL Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main dashboard with module tiles |
| `/coming-soon/<module>` | GET | Placeholder for future modules |
| `/bands` | GET | Bands upload page |
| `/bands/analyze` | POST | Run band analysis |
| `/bands/download/<file>` | GET | Download HTML report |
| `/bands/kb/upload` | POST | Upload to KB library |
| `/bands/kb/delete/<file>` | POST | Delete from KB library |

---

## 3. User Interface

### 3.1 Main Dashboard

The landing page displays 6 analysis modules in a grid layout:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Analysis Tool                                │
│                   Select a module to begin analysis                  │
│                                                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│   │         │  │ Combos  │  │   IMS   │  │  Supp   │  │         │  │ Future  │
│   │  Bands  │  │  (CA,   │  │ Support │  │Services │  │  PICS   │  │ Purpose │
│   │         │  │  ENDC)  │  │         │  │         │  │         │  │         │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘
│    [Active]   [Coming Soon][Coming Soon][Coming Soon][Coming Soon][Coming Soon]
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Module Status**:
- **Bands**: Active (implemented)
- **Combos, IMS Support, Supplementary Services, PICS, Future Purpose**: Coming Soon

### 3.2 Bands Upload Page

Two-section form for input files and knowledge base:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Analysis Tool > Bands                              [← Back]         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─ Input Documents ──────────────────────────────────────────────┐ │
│  │  RFC XML, HW Filter, Carrier Policy, Generic Restrictions,     │ │
│  │  MCFG, MDB, Target MCC, QXDM Log, UE Capability                │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─ Knowledge Base Library ───────────────────────────────────────┐ │
│  │  [✓] file1.pdf  [X]                                            │ │
│  │  [✓] file2.png  [X]                                            │ │
│  │  Add to library: [Choose Files] [Upload]                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│                      [ Analyze ]                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Input Documents** (all optional):
| Field | File Type | Description |
|-------|-----------|-------------|
| RFC XML | .xml | RF Card capability file |
| HW Filter XML | .xml | Hardware band filtering |
| Carrier Policy XML | .xml | Carrier-specific exclusions |
| Generic Restrictions XML | .xml | Generic band restrictions |
| MCFG XML | .xml | NV band preferences |
| MDB XML | .xml | mcc2bands mapping |
| Target MCC | text | MCC for MDB lookup |
| QXDM Log | .txt | 0x1CCA PM RF Band Info |
| UE Capability | .txt | UE Capability Information |

**Knowledge Base Library**:
- Files stored permanently in `knowledge_library/` folder
- Checkbox to select files for current analysis
- Upload new files to library
- Delete files from library

### 3.3 Results Page

Displays analysis output with download option:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Analysis Tool > Bands > Results                                     │
├─────────────────────────────────────────────────────────────────────┤
│  [← New Analysis]                        [Download HTML Report]      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─ CLI Output ───────────────────────────────────────────────────┐ │
│  │ ================================================================ │
│  │ BAND COMBOS ANALYZER - Stage 1: Automated Analysis              │
│  │ ...                                                             │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                          (Scrollable, dark theme)    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Design Specifications

### 4.1 Color Scheme

| Element | Color | Hex Code |
|---------|-------|----------|
| Primary (Red) | Red | #DC3545 |
| Primary Hover | Dark Red | #C82333 |
| Background | Light Gray | #F8F9FA |
| Card Background | White | #FFFFFF |
| Text | Dark Gray | #333333 |
| Text Muted | Gray | #6C757D |
| Border | Light Gray | #DEE2E6 |
| Success | Green | #28A745 |
| Error | Red | #DC3545 |

### 4.2 Typography

- **Font Family**: System fonts (SF, Segoe UI, Roboto)
- **Base Size**: 16px
- **Headings**: Bold, primary color
- **Code/CLI**: Consolas, Monaco (monospace)

### 4.3 Component Styling

- **Border Radius**: 8px
- **Box Shadow**: `0 2px 8px rgba(0,0,0,0.1)`
- **Transitions**: 0.2s ease

---

## 5. File Upload Handling

### 5.1 Allowed Extensions

```python
ALLOWED_EXTENSIONS = {'xml', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'bin', 'hex'}
```

### 5.2 Storage Strategy

| File Type | Storage Location | Lifecycle |
|-----------|-----------------|-----------|
| Input Documents | `uploads/input/<session_id>/` | Temporary (deleted after analysis) |
| Knowledge Base | `knowledge_library/` | Permanent (user managed) |
| HTML Reports | `Band_Combos_Analyzer/output/` | Permanent |

### 5.3 Max Upload Size

```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
```

---

## 6. Integration with Analysis Engine

### 6.1 Analysis Flow

```
1. User uploads files via web form
2. Files saved to temp directory with unique session ID
3. AnalysisInput created with file paths
4. BandAnalyzer.analyze() executed
5. CLI output captured via StringIO redirect
6. HTML report generated
7. Results displayed to user
8. Temp files cleaned up
```

### 6.2 Code Integration

```python
# Create input from uploaded files
inputs = AnalysisInput(
    rfc_path=uploaded_files.get('rfc'),
    hw_filter_path=uploaded_files.get('hw_filter'),
    # ... other fields
)

# Run analysis (existing code)
analyzer = BandAnalyzer()
result = analyzer.analyze(inputs)

# Generate report (existing code)
generate_html_report(result, output_path)
```

---

## 7. Running the Web UI

### 7.1 Installation

```bash
cd Log-Analysis-tool
pip install -r requirements.txt
```

### 7.2 Starting the Server

```bash
python run_web.py
```

### 7.3 Access

Open browser to: `http://localhost:5000`

---

## 8. Future Enhancements

### 8.1 Planned Modules

| Module | Description | Status |
|--------|-------------|--------|
| Combos (CA, ENDC) | Carrier aggregation analysis | Planned |
| IMS Support | IMS capability analysis | Planned |
| Supplementary Services | SS feature analysis | Planned |
| PICS | Protocol conformance | Planned |

### 8.2 Potential Features

- User authentication
- Analysis history/saved sessions
- Batch analysis mode
- API endpoints for automation
- Dark mode theme option

---

## 9. Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial web UI design and implementation |

---

*Document Version: 1.0*
*Related: [Architecture_Design.md](./Architecture_Design.md) for backend analysis details*
