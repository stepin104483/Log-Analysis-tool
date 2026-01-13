"""
AI Review Service

Shared service for running Claude AI expert reviews across all modules.
Handles Claude CLI execution, markdown rendering, and verdict extraction.
"""

import os
import re
import subprocess
import logging
from typing import Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIReviewService:
    """
    Service for running AI expert reviews using Claude CLI.

    This service is shared across all analysis modules and handles:
    - Claude CLI execution
    - Response encoding
    - Markdown to HTML conversion
    - Verdict extraction
    """

    def __init__(self, timeout: int = 300):
        """
        Initialize the AI Review Service.

        Args:
            timeout: Maximum time to wait for Claude CLI (seconds)
        """
        self.timeout = timeout

    def run_review(self, prompt_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Execute Claude CLI with the given prompt file.

        Args:
            prompt_path: Path to the prompt file

        Returns:
            Tuple of (review_text, error_message)
        """
        try:
            # Read prompt content
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()

            logger.info(f"Executing Claude CLI with prompt length: {len(prompt_content)}")

            # Set environment for UTF-8 encoding on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # Execute Claude CLI with explicit UTF-8 encoding
            result = subprocess.run(
                ['claude', '-p', '--dangerously-skip-permissions'],
                input=prompt_content,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=self.timeout,
                shell=True,
                env=env
            )

            logger.info(f"Claude CLI return code: {result.returncode}")

            if result.returncode == 0:
                return result.stdout, None
            else:
                return None, f"Claude CLI error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return None, f"Claude CLI timed out after {self.timeout // 60} minutes"
        except FileNotFoundError:
            return None, "Claude CLI not found. Ensure 'claude' is installed and in PATH"
        except Exception as e:
            logger.exception("Error running Claude CLI")
            return None, f"Error: {str(e)}"

    def render_markdown(self, content: str) -> str:
        """
        Convert markdown content to styled HTML.

        Args:
            content: Markdown content

        Returns:
            Rendered HTML
        """
        import markdown

        # Fix Unicode characters
        content = self._fix_unicode(content)

        # Convert Markdown to HTML
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br'
        ])

        return md.convert(content)

    def _fix_unicode(self, content: str) -> str:
        """
        Replace Unicode symbols with HTML entities.

        Args:
            content: Text content

        Returns:
            Content with HTML entities
        """
        unicode_replacements = {
            '\u2713': '&#10003;',      # ✓ Checkmark
            '\u2714': '&#10004;',      # ✔ Heavy checkmark
            '\u2717': '&#10007;',      # ✗ Ballot X
            '\u2718': '&#10008;',      # ✘ Heavy ballot X
            '\u2705': '&#9989;',       # ✅ White heavy checkmark
            '\u274C': '&#10060;',      # ❌ Cross mark
            '\u26A0': '&#9888;',       # ⚠ Warning sign
            '\u2192': '&rarr;',        # → Right arrow
            '\u2190': '&larr;',        # ← Left arrow
            '\u2022': '&bull;',        # • Bullet
            '\u2014': '&mdash;',       # — Em dash
            '\u2013': '&ndash;',       # – En dash
            '\u201C': '&ldquo;',       # " Left double quote
            '\u201D': '&rdquo;',       # " Right double quote
            '\u2018': '&lsquo;',       # ' Left single quote
            '\u2019': '&rsquo;',       # ' Right single quote
            '\u2026': '&hellip;',      # … Ellipsis
        }

        for char, entity in unicode_replacements.items():
            content = content.replace(char, entity)

        return content

    def extract_verdict(self, content: str) -> Tuple[str, str]:
        """
        Extract the verdict section from Claude's review.

        Args:
            content: Full review content

        Returns:
            Tuple of (verdict_content, verdict_class)
            verdict_class is one of: 'verdict-safe', 'verdict-warning', 'verdict-unsafe'
        """
        # Match various verdict patterns
        verdict_patterns = [
            r'(#{1,3}\s*\d*\.?\s*Overall Verdict\s*\n.*?)(?=\n#{1,3}\s|\Z|^\s*---)',
            r'(#{1,3}\s*\d*\.?\s*Final Verdict\s*\n.*?)(?=\n#{1,3}\s|\Z|^\s*---)',
            r'(#{1,3}\s*\d*\.?\s*Verdict\s*\n.*?)(?=\n#{1,3}\s|\Z|^\s*---)',
            r'(#{1,3}\s*\d*\.?\s*Conclusion\s*\n.*?)(?=\n#{1,3}\s|\Z|^\s*---)',
        ]

        verdict_content = ""
        for pattern in verdict_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if match:
                verdict_content = match.group(1).strip()
                logger.debug(f"Verdict found, length: {len(verdict_content)}")
                break

        if not verdict_content:
            logger.debug("No verdict section found in review")
            return "", "verdict-safe"

        # Determine verdict status for styling
        verdict_class = "verdict-safe"
        verdict_lower = verdict_content.lower()

        if any(word in verdict_lower for word in ['unsafe', 'fail', 'not recommended', 'critical']):
            verdict_class = "verdict-unsafe"
        elif any(word in verdict_lower for word in ['warning', 'caution', 'review', 'attention']):
            verdict_class = "verdict-warning"

        return verdict_content, verdict_class

    def inject_review_into_html(self, html_content: str, review: str) -> str:
        """
        Inject Claude's review into an existing HTML report.

        Args:
            html_content: Original HTML report
            review: Claude's review (markdown)

        Returns:
            HTML with review injected
        """
        # Fix unicode and render markdown
        review = self._fix_unicode(review)

        import markdown
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br'])
        rendered_review = md.convert(review)

        # Extract verdict
        verdict_content, verdict_class = self.extract_verdict(review)
        md_verdict = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
        rendered_verdict = md_verdict.convert(verdict_content) if verdict_content else ""

        # Create verdict section
        verdict_section = ""
        if rendered_verdict:
            verdict_section = f'''
    <div class="section verdict-section {verdict_class}">
        <div class="section-header verdict-header">
            <h2>Claude Expert Review Verdict</h2>
            <span class="toggle-icon">&#9660;</span>
        </div>
        <div class="section-content">
            <div class="verdict-content">
                {rendered_verdict}
            </div>
        </div>
    </div>
            '''

        # Create full review section
        claude_section = f'''
    <div class="section claude-review-section">
        <div class="section-header claude-header">
            <h2>Stage 2: Claude Expert Review (Full Analysis)</h2>
            <span class="toggle-icon">&#9660;</span>
        </div>
        <div class="section-content">
            <div class="claude-review-content">
                {rendered_review}
            </div>
        </div>
    </div>
        '''

        # CSS styles
        styles = self._get_review_styles()

        # Find Summary section and insert verdict after it
        summary_patterns = [
            r'(<div class="section">\s*<div class="section-header">.*?<h2>Summary</h2>.*?</div>\s*</div>\s*</div>)',
            r'(<div class="section">.*?<h2>Summary</h2>.*?</div>\s*</div>)',
        ]

        summary_match = None
        for pattern in summary_patterns:
            summary_match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if summary_match:
                break

        if summary_match and verdict_section:
            insert_pos = summary_match.end()
            html_content = html_content[:insert_pos] + verdict_section + html_content[insert_pos:]

        # Insert full review before </body>
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{claude_section}{styles}</body>')
        else:
            html_content += claude_section + styles

        return html_content

    def _get_review_styles(self) -> str:
        """Get CSS styles for the review sections."""
        return '''
    <style>
        /* Verdict Section Styles */
        .verdict-section {
            margin-bottom: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .verdict-section.verdict-safe { border: 2px solid #28a745; }
        .verdict-section.verdict-warning { border: 2px solid #ffc107; }
        .verdict-section.verdict-unsafe { border: 2px solid #dc3545; }
        .verdict-header {
            background: linear-gradient(135deg, #28a745, #20c997) !important;
        }
        .verdict-section.verdict-warning .verdict-header {
            background: linear-gradient(135deg, #ffc107, #fd7e14) !important;
        }
        .verdict-section.verdict-unsafe .verdict-header {
            background: linear-gradient(135deg, #dc3545, #c82333) !important;
        }
        .verdict-content {
            background-color: white;
            padding: 20px 25px;
            line-height: 1.7;
        }
        .verdict-content h2, .verdict-content h3 { margin-top: 0; color: #28a745; }
        .verdict-section.verdict-warning .verdict-content h2,
        .verdict-section.verdict-warning .verdict-content h3 { color: #d39e00; }
        .verdict-section.verdict-unsafe .verdict-content h2,
        .verdict-section.verdict-unsafe .verdict-content h3 { color: #dc3545; }
        .verdict-content ul, .verdict-content ol { margin: 10px 0 10px 25px; }
        .verdict-content li { margin: 6px 0; }
        .verdict-content strong { color: inherit; }

        /* Claude Review Section Styles */
        .claude-review-section {
            margin-top: 30px;
            background-color: #f0f7ff;
            border: 1px solid #b8daff;
            border-radius: 10px;
            overflow: hidden;
        }
        .claude-header {
            background: linear-gradient(135deg, #1a73e8, #4285f4) !important;
        }
        .claude-review-content {
            background-color: white;
            padding: 25px;
            line-height: 1.7;
            color: #333;
        }
        .claude-review-content h1 {
            color: #1a73e8;
            font-size: 1.8em;
            margin: 25px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #1a73e8;
        }
        .claude-review-content h2 {
            color: #1a73e8;
            font-size: 1.4em;
            margin: 20px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid #ddd;
        }
        .claude-review-content h3 {
            color: #333;
            font-size: 1.15em;
            margin: 18px 0 10px 0;
        }
        .claude-review-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9em;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .claude-review-content table th {
            background: linear-gradient(135deg, #1a73e8, #4285f4);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }
        .claude-review-content table td {
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }
        .claude-review-content table tr:nth-child(even) { background-color: #f8f9fa; }
        .claude-review-content table tr:hover { background-color: #e8f0fe; }
        .claude-review-content pre {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            margin: 15px 0;
        }
        .claude-review-content code {
            background-color: #f1f3f4;
            color: #d93025;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }
        .claude-review-content pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
        }
        .claude-review-content ul, .claude-review-content ol { margin: 10px 0 10px 25px; }
        .claude-review-content li { margin: 6px 0; }
        .claude-review-content blockquote {
            border-left: 4px solid #1a73e8;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            color: #555;
        }
        .claude-review-content hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 25px 0;
        }
        .claude-review-content strong { color: #1a73e8; }
    </style>
        '''
