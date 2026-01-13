# Analysis Tool - Web UI Design Document

**Version**: 2.0
**Last Updated**: 2026-01-13
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
| Markdown Rendering | Python `markdown` library |
| AI Integration | Claude CLI (local execution) |

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
    │       ├── results.html        # Stage 1 analysis results
    │       └── ai_results.html     # AI Expert Review results
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
| `/bands/analyze` | POST | Run band analysis (Stage 1) |
| `/bands/ai-review` | POST | Run Claude AI Expert Review (Stage 2) |
| `/bands/download/<file>` | GET | Download HTML report |
| `/bands/generate-final-report` | POST | Generate final report with manual Claude review |
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

### 3.3 Results Page (Stage 1)

Displays automated analysis output with AI review option:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Analysis Tool > Bands > Results                                     │
├─────────────────────────────────────────────────────────────────────┤
│  [← New Analysis]                        [Download HTML Report]      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─ Stage 1: Automated Analysis (CLI Output) ──────────────────────┐ │
│  │ ================================================================ │
│  │ BAND COMBOS ANALYZER - Stage 1: Automated Analysis              │
│  │ ...                                                             │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                          (Scrollable, dark theme)    │
│                                                                      │
│                    [ AI Expert Review ]                              │
│         Click to get Claude's expert analysis (runs locally)         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.4 AI Review Results Page (Stage 2)

Displays Claude's expert review with download option:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Analysis Tool > Bands > AI Review                                   │
├─────────────────────────────────────────────────────────────────────┤
│  [← New Analysis]                     [Download Final Report (HTML)] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─ Stage 2: Claude AI Expert Review ──────────────────────────────┐ │
│  │                                                                  │ │
│  │  # Band Analysis Expert Review                                   │ │
│  │                                                                  │ │
│  │  ## Executive Summary                                            │ │
│  │  The automated analysis shows a well-configured modem...         │ │
│  │                                                                  │ │
│  │  ## Overall Verdict                                              │ │
│  │  ✅ SAFE FOR DEPLOYMENT                                          │ │
│  │                                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                   (Rendered Markdown with styled tables)             │
│                                                                      │
│                    [ Download Final Report ]                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.5 Final HTML Report Structure

The downloaded final report includes both stages with verdict at top:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Band Analysis Report                                                │
│  Generated: 2026-01-13                                               │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ Document Status                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ Summary                                                           │
│    GSM: 4/4 | WCDMA: 17/26 | LTE: 27/28 | NR SA: 20/23              │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ Claude Expert Review Verdict        [Green/Yellow/Red border]    │
│    ✅ SAFE FOR DEPLOYMENT                                            │
│    - All PASS/FAIL determinations correct                            │
│    - No unexplained anomalies                                        │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ GSM (2G)                                                          │
│  ▼ WCDMA (3G)                                                        │
│  ▼ LTE (4G)                                                          │
│  ▼ NR SA (5G Standalone)                                             │
│  ▼ NR NSA (5G Non-Standalone)                                        │
│  ▼ Anomalies                                                         │
├─────────────────────────────────────────────────────────────────────┤
│  ▼ Stage 2: Claude Expert Review (Full Analysis)                     │
│    - Executive Summary                                               │
│    - Validation of Findings                                          │
│    - Anomaly Analysis                                                │
│    - Impact Assessment                                               │
│    - Observations & Recommendations                                  │
│    - Overall Verdict                                                 │
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

## 6. AI Expert Review Integration

### 6.1 Claude CLI Integration

The AI Expert Review feature executes Claude CLI locally via subprocess:

```python
def run_claude_cli(prompt_path):
    result = subprocess.run(
        ['claude', '-p', '--dangerously-skip-permissions'],
        input=prompt_content,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minute timeout
        shell=True
    )
    return result.stdout, None if result.returncode == 0 else result.stderr
```

### 6.2 Markdown Rendering

Claude's response (Markdown format) is converted to styled HTML:

```python
import markdown

md = markdown.Markdown(extensions=[
    'tables',           # Render Markdown tables
    'fenced_code',      # Code blocks with ```
    'codehilite',       # Syntax highlighting
    'toc',              # Table of contents
    'nl2br'             # Line breaks
])
rendered_html = md.convert(claude_review)
```

### 6.3 Unicode Character Handling

Special characters are converted to HTML entities to prevent encoding issues:

| Character | Entity | Description |
|-----------|--------|-------------|
| ✓ | `&#10003;` | Checkmark |
| ✔ | `&#10004;` | Heavy checkmark |
| ✅ | `&#9989;` | Green checkmark |
| ❌ | `&#10060;` | Red X |
| ⚠ | `&#9888;` | Warning sign |
| → | `&rarr;` | Right arrow |

### 6.4 Verdict Extraction

The "Overall Verdict" section is extracted and placed at the top of the report:

```python
# Regex pattern to extract verdict section
verdict_pattern = r'(#{1,2}\s*\d*\.?\s*Overall Verdict.*?)(?=#{1,2}\s|\Z|---)'
verdict_match = re.search(verdict_pattern, claude_review, re.DOTALL)
```

**Verdict Color Coding:**
| Status | Border Color | Header Gradient |
|--------|--------------|-----------------|
| Safe | Green (#28a745) | Green to Teal |
| Warning | Yellow (#ffc107) | Yellow to Orange |
| Unsafe | Red (#dc3545) | Red to Dark Red |

---

## 7. Integration with Analysis Engine

### 7.1 Analysis Flow

```
Stage 1: Automated Analysis
1. User uploads files via web form
2. Files saved to temp directory with unique session ID
3. AnalysisInput created with file paths
4. BandAnalyzer.analyze() executed
5. CLI output captured via StringIO redirect
6. HTML report + prompt file generated
7. Results displayed to user
8. Temp files cleaned up

Stage 2: AI Expert Review (Optional)
9. User clicks "AI Expert Review" button
10. Claude CLI executed with prompt file
11. Response rendered as HTML (Markdown → HTML)
12. Verdict extracted and placed after Summary
13. Final report available for download
```

### 7.2 Code Integration

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

## 8. Running the Web UI

### 8.1 Prerequisites

- Python 3.9+
- Claude CLI installed and in PATH (for AI Expert Review)

### 8.2 Installation

```bash
cd Log-Analysis-tool
pip install -r requirements.txt
```

**Dependencies (requirements.txt):**
```
flask>=2.3.0
werkzeug>=2.3.0
markdown>=3.4.0
```

### 8.3 Starting the Server

```bash
python run_web.py
```

### 8.4 Access

Open browser to: `http://localhost:5000`

---

## 9. Future Enhancements

### 9.1 Planned Modules

| Module | Description | Status |
|--------|-------------|--------|
| Combos (CA, ENDC) | Carrier aggregation analysis | Planned |
| IMS Support | IMS capability analysis | Planned |
| Supplementary Services | SS feature analysis | Planned |
| PICS | Protocol conformance | Planned |

### 9.2 Potential Features

- User authentication
- Analysis history/saved sessions
- Batch analysis mode
- API endpoints for automation
- Dark mode theme option
- Export to PDF format

---

## 10. Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial web UI design and implementation |
| 2.0 | 2026-01-13 | Added AI Expert Review with Claude CLI integration, Markdown rendering, verdict extraction, Unicode handling |

---

*Document Version: 2.0*
*Related: [Architecture_Design.md](./Architecture_Design.md) for backend analysis details*
