# Log Analysis Tool - Overall Architecture

## 1. Overview

The Log Analysis Tool is a modular, plugin-based application for analyzing wireless device configurations and logs. It uses a two-stage analysis approach:

1. **Stage 1: Automated Analysis** - Python-based parsing and comparison logic
2. **Stage 2: AI Expert Review** - Claude CLI integration for intelligent insights

The tool is designed with extensibility in mind, allowing new analysis modules to be added with minimal changes to the core framework.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
+-----------------------------------------------------------------------------+
|                          LOG ANALYSIS TOOL                                   |
+-----------------------------------------------------------------------------+
|                                                                              |
|  +------------------------+    +------------------------+                    |
|  |      WEB UI LAYER      |    |    CLI ENTRY POINT     |                    |
|  |  (Flask Application)   |    |    (run_analysis.bat)  |                    |
|  +------------------------+    +------------------------+                    |
|              |                            |                                  |
|              +------------+---------------+                                  |
|                           |                                                  |
|                           v                                                  |
|  +-------------------------------------------------------------------+      |
|  |                      CORE FRAMEWORK                                |      |
|  |  +------------------+  +------------------+  +------------------+  |      |
|  |  | Module Registry  |  | Base Analyzer    |  | AI Review Service|  |      |
|  |  | (Auto-Discovery) |  | (Abstract Base)  |  | (Claude CLI)     |  |      |
|  |  +------------------+  +------------------+  +------------------+  |      |
|  |                                                                    |      |
|  |  +------------------+                                              |      |
|  |  | File Handler     |                                              |      |
|  |  | (Upload/Output)  |                                              |      |
|  |  +------------------+                                              |      |
|  +-------------------------------------------------------------------+      |
|                           |                                                  |
|                           v                                                  |
|  +-------------------------------------------------------------------+      |
|  |                      ANALYSIS MODULES                              |      |
|  |  +--------+  +--------+  +--------+  +--------+  +--------+       |      |
|  |  | Bands  |  | Combos |  |  IMS   |  |  SS    |  | PICS   |  ...  |      |
|  |  +--------+  +--------+  +--------+  +--------+  +--------+       |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+-----------------------------------------------------------------------------+
```

### 2.2 Component Overview

| Component | Description | Location |
|-----------|-------------|----------|
| Web UI | Flask-based web interface | `src/web/` |
| Core Framework | Plugin architecture, shared services | `core/` |
| Modules | Individual analysis modules | `modules/` |
| Templates | Jinja2 HTML templates | `templates/` |
| Static Assets | CSS, JS, images | `static/` |

---

## 3. Core Framework

### 3.1 Module Registry (`core/module_registry.py`)

The ModuleRegistry is a singleton that handles automatic discovery and registration of analysis modules.

**Key Features:**
- Auto-discovers modules from `modules/` directory
- Singleton pattern ensures single registry instance
- Provides module lookup by ID
- Separates active vs coming-soon modules

```python
# Auto-discovery on startup
ModuleRegistry.discover_modules(modules_path)

# Get a specific module
module = ModuleRegistry.get_module('bands')

# Get all registered modules
all_modules = ModuleRegistry.get_all_modules()
```

**Discovery Process:**
```
modules/
├── bands/
│   ├── __init__.py
│   └── analyzer.py      <-- Must contain BaseAnalyzer subclass
├── combos/
│   ├── __init__.py
│   └── analyzer.py
└── ...
```

### 3.2 Base Analyzer (`core/base_analyzer.py`)

Abstract base class that all analysis modules must inherit.

**Required Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `module_id` | str | Unique identifier (e.g., 'bands') |
| `display_name` | str | Human-readable name |
| `description` | str | Short description |
| `status` | str | 'active' or 'coming_soon' |
| `input_fields` | List | File input field configurations |

**Required Methods:**
| Method | Description |
|--------|-------------|
| `analyze(inputs)` | Run analysis, return AnalysisResult |
| `generate_prompt(result)` | Generate Claude prompt |

**Data Classes:**
- `AnalysisInput` - Input files, parameters, KB files
- `AnalysisResult` - Success flag, CLI output, report paths, errors
- `InputFieldConfig` - File field name, patterns, required flag

### 3.3 Placeholder Analyzer (`core/placeholder_analyzer.py`)

Base class for "coming soon" modules. Inherits from BaseAnalyzer with:
- `status = "coming_soon"`
- Default `analyze()` returns "not implemented"
- Empty `input_fields`

### 3.4 AI Review Service (`core/ai_review.py`)

Shared service for Claude CLI integration.

**Key Features:**
- Executes Claude CLI with prompt file
- Renders Markdown to HTML
- Extracts verdict section from Claude response
- Injects AI review into HTML report

```python
ai_service = AIReviewService(timeout=300)
review, error = ai_service.run_review(prompt_path)
final_html = ai_service.inject_review_into_html(original_html, review)
```

### 3.5 File Handler (`core/file_handler.py`)

Shared file operations for all modules.

**Key Features:**
- Upload session management (creates temp folders)
- Knowledge base file operations
- Output file management
- Automatic cleanup

---

## 4. Web UI Architecture

### 4.1 Flask Application Structure

```
src/web/
├── app.py              # Application factory
└── routes/
    ├── main.py         # Dashboard routes
    ├── bands.py        # Legacy bands routes (backward compat)
    └── module.py       # Generic module routes
```

### 4.2 Blueprint Structure

| Blueprint | URL Prefix | Purpose |
|-----------|------------|---------|
| `main_bp` | `/` | Dashboard, home page |
| `bands_bp` | `/bands` | Legacy bands routes |
| `module_bp` | `/module` | Generic module routes |

### 4.3 Generic Module Routes (`/module/<module_id>`)

| Route | Method | Description |
|-------|--------|-------------|
| `/<module_id>` | GET | Upload page for module |
| `/<module_id>/analyze` | POST | Run analysis |
| `/<module_id>/ai-review` | POST | Get AI expert review |
| `/download/<filename>` | GET | Download report |

### 4.4 Template Structure

```
templates/
├── base.html                  # Base layout
├── index.html                 # Dashboard
├── bands/                     # Bands-specific templates
│   ├── upload.html
│   └── results.html
└── module/                    # Generic module templates
    ├── upload.html            # Generic upload page
    ├── results.html           # Analysis results
    ├── ai_results.html        # AI review results
    └── coming_soon.html       # Placeholder page
```

---

## 5. Analysis Flow

### 5.1 Two-Stage Analysis

```
+------------------+     +------------------+     +------------------+
|   STAGE 1        |     |   STAGE 2        |     |   OUTPUT         |
|   Python Code    | --> |   Claude CLI     | --> |   Final Report   |
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| - Parse inputs   |     | - Read prompt    |     | - Stage 1 output |
| - Run analysis   |     | - AI analysis    |     | - Stage 2 review |
| - Generate       |     | - Expert review  |     | - Combined HTML  |
|   prompt.txt     |     | - Verdict        |     |   report         |
| - Generate HTML  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

### 5.2 User Flow (Web UI)

```
1. User visits dashboard (/)
2. Clicks on module tile (e.g., "Bands")
3. Upload page shown (/module/bands or /bands)
4. User uploads files, clicks "Analyze"
5. Stage 1 runs, results page shown
6. User clicks "AI Expert Review"
7. Stage 2 runs (Claude CLI)
8. Final report available for download
```

---

## 6. Module List

| Module ID | Display Name | Status | Description |
|-----------|--------------|--------|-------------|
| `bands` | Band Analysis | Active | Band filtering analysis across config layers |
| `combos` | Combos (CA, ENDC) | Coming Soon | Carrier aggregation analysis |
| `ims` | IMS Support | Coming Soon | IMS capability analysis |
| `supplementary_services` | Supp Services | Coming Soon | SS feature analysis |
| `pics` | PICS | Coming Soon | Protocol Implementation Conformance |
| `band_explorer` | Band Explorer | Coming Soon | Band info search (BW, SCS, combos) |
| `future` | Future Purpose | Coming Soon | Reserved for future modules |

---

## 7. Directory Structure

### 7.1 Current Structure

```
DeviceSWAnalyzer/
├── core/                      # Plugin framework
│   ├── __init__.py
│   ├── base_analyzer.py       # Abstract base class
│   ├── module_registry.py     # Auto-discovery
│   ├── ai_review.py           # Claude CLI integration
│   ├── file_handler.py        # File operations
│   └── placeholder_analyzer.py
│
├── modules/                   # Analysis modules
│   ├── bands/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── combos/
│   ├── ims/
│   ├── supplementary_services/
│   ├── pics/
│   ├── band_explorer/
│   └── future/
│
├── src/                       # Legacy code (to be migrated)
│   ├── core/                  # Old analyzer code
│   ├── parsers/               # Document parsers
│   └── web/                   # Flask application
│
├── templates/                 # Jinja2 templates
├── static/                    # CSS, JS, images
├── docs/                      # Documentation
├── input/                     # Input files
└── output/                    # Generated reports
```

### 7.2 Target Structure (Future)

```
DeviceSWAnalyzer/
├── core/                      # Plugin framework only
├── modules/                   # All module code
│   └── bands/
│       ├── analyzer.py
│       ├── parsers/           # Module-specific parsers
│       └── tracer/            # Module-specific logic
├── web/                       # Flask app (moved from src/)
├── templates/
├── static/
├── docs/
│   ├── Overall_Architecture.md
│   ├── Overall_Requirements.md
│   └── modules/
│       ├── bands/
│       │   ├── Architecture.md
│       │   └── Requirements.md
│       └── ...
└── output/
```

---

## 8. Adding a New Module

### 8.1 Steps to Add a New Module

1. Create module directory: `modules/<module_id>/`
2. Create `__init__.py` and `analyzer.py`
3. Implement `BaseAnalyzer` subclass
4. Module is auto-discovered on next startup

### 8.2 Minimal Module Example

```python
# modules/my_module/analyzer.py
from core import BaseAnalyzer, AnalysisInput, AnalysisResult

class MyModuleAnalyzer(BaseAnalyzer):
    @property
    def module_id(self) -> str:
        return "my_module"

    @property
    def display_name(self) -> str:
        return "My Module"

    @property
    def description(self) -> str:
        return "Description of my module"

    @property
    def status(self) -> str:
        return "active"

    @property
    def input_fields(self):
        return [
            InputFieldConfig(name='input_file', patterns=['*.xml'], required=True)
        ]

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        # Implementation
        pass

    def generate_prompt(self, result: AnalysisResult) -> str:
        # Generate Claude prompt
        pass
```

---

## 9. Related Documentation

| Document | Description |
|----------|-------------|
| [Overall_Requirements.md](./Overall_Requirements.md) | System-level requirements |
| [UI_Design.md](./UI_Design.md) | Web UI design details |
| [modules/bands/Architecture.md](./modules/bands/Architecture.md) | Bands module architecture |

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-13 | Plugin-based modular architecture |
| 1.0 | 2026-01-07 | Initial monolithic architecture |
