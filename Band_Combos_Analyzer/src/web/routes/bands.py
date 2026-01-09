"""
Bands Module Routes
"""
import os
import sys
import uuid
import shutil
from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, jsonify
from werkzeug.utils import secure_filename

bands_bp = Blueprint('bands', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def get_kb_files():
    """Get list of files in knowledge base library."""
    kb_path = current_app.config['KNOWLEDGE_LIBRARY']
    files = []
    if os.path.exists(kb_path):
        for filename in sorted(os.listdir(kb_path)):
            filepath = os.path.join(kb_path, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
    return files


@bands_bp.route('/')
def upload():
    """Render bands upload page."""
    kb_files = get_kb_files()
    return render_template('bands/upload.html', kb_files=kb_files)


def detect_file_type(filename):
    """
    Auto-detect file type based on filename patterns.
    Returns the attribute name for AnalysisInput.
    """
    lower = filename.lower()

    if lower.endswith('.xml'):
        if 'rfc' in lower:
            return 'rfc_path'
        if ('hardware' in lower and 'filter' in lower) or ('hw' in lower and 'filter' in lower):
            return 'hw_filter_path'
        if 'carrier' in lower and 'policy' in lower:
            return 'carrier_policy_path'
        if 'generic' in lower:
            return 'generic_restriction_path'
        if 'mcfg' in lower:
            return 'mcfg_path'
        if 'mcc2bands' in lower or 'mdb' in lower:
            return 'mdb_path'

    if lower.endswith('.txt'):
        if 'qxdm' in lower or 'pm_rf' in lower or '0x1cca' in lower or 'pm rf' in lower:
            return 'qxdm_log_path'
        if 'ue_cap' in lower or 'capability' in lower or 'ue cap' in lower:
            return 'ue_capability_path'

    return None


@bands_bp.route('/analyze', methods=['POST'])
def analyze():
    """Handle file uploads and run band analysis."""
    # Generate unique session ID for this analysis
    session_id = str(uuid.uuid4())[:8]
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(upload_dir, exist_ok=True)

    try:
        # Collect uploaded input files (multi-file upload)
        input_files = {}

        if 'input_files' in request.files:
            files = request.files.getlist('input_files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)

                    # Auto-detect file type
                    attr_name = detect_file_type(file.filename)
                    if attr_name:
                        input_files[attr_name] = filepath

        # Get target MCC if provided
        target_mcc = request.form.get('target_mcc', '').strip() or None

        # Get selected KB files
        selected_kb = request.form.getlist('kb_files')

        # Check if at least one input file was provided
        if not input_files:
            flash('Please upload at least one input document. Make sure filenames contain recognizable patterns (e.g., "rfc", "carrier_policy", "qxdm").', 'error')
            return redirect(url_for('bands.upload'))

        # Run analysis and capture CLI output
        cli_output, html_report_path, prompt_path, error = run_band_analysis(
            input_files, target_mcc, selected_kb, session_id
        )

        # Clean up uploaded files
        shutil.rmtree(upload_dir, ignore_errors=True)

        if error:
            flash(f'Analysis error: {error}', 'error')
            return redirect(url_for('bands.upload'))

        # Store results in session or pass to template
        return render_template(
            'bands/results.html',
            cli_output=cli_output,
            html_report=os.path.basename(html_report_path) if html_report_path else None,
            prompt_file=os.path.basename(prompt_path) if prompt_path else None
        )

    except Exception as e:
        # Clean up on error
        shutil.rmtree(upload_dir, ignore_errors=True)
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('bands.upload'))


def run_band_analysis(input_files, target_mcc, selected_kb, session_id):
    """
    Run band analysis and return CLI output, HTML report path, and prompt path.

    Returns:
        tuple: (cli_output, html_report_path, prompt_path, error)
    """
    cli_output = ""
    html_report_path = None
    prompt_path = None
    error = None

    try:
        # Get the Band_Combos_Analyzer directory (parent of src/)
        web_dir = os.path.dirname(os.path.abspath(__file__))  # routes/
        routes_dir = os.path.dirname(web_dir)  # web/
        src_dir = os.path.dirname(routes_dir)  # src/
        band_combos_dir = os.path.dirname(src_dir)  # Band_Combos_Analyzer/

        print(f"[DEBUG] band_combos_dir: {band_combos_dir}", flush=True)

        if band_combos_dir not in sys.path:
            sys.path.insert(0, band_combos_dir)

        # Import using package path from Band_Combos_Analyzer/
        from src.core.analyzer import BandAnalyzer, AnalysisInput
        from src.output.html_report import generate_html_report
        from src.output.console_report import print_console_report
        from src.core.prompt_generator import generate_prompt

        print(f"[DEBUG] Imports successful", flush=True)
        print(f"[DEBUG] Input files: {input_files}", flush=True)

        # Create AnalysisInput
        inputs = AnalysisInput(
            rfc_path=input_files.get('rfc_path'),
            hw_filter_path=input_files.get('hw_filter_path'),
            carrier_policy_path=input_files.get('carrier_policy_path'),
            generic_restriction_path=input_files.get('generic_restriction_path'),
            mcfg_path=input_files.get('mcfg_path'),
            mdb_path=input_files.get('mdb_path'),
            qxdm_log_path=input_files.get('qxdm_log_path'),
            ue_capability_path=input_files.get('ue_capability_path'),
            target_mcc=target_mcc
        )

        print(f"[DEBUG] AnalysisInput created", flush=True)

        # Capture stdout for CLI output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # Run analysis
            print("[DEBUG] Starting BandAnalyzer...", flush=True)
            analyzer = BandAnalyzer()
            result = analyzer.analyze(inputs)
            print("[DEBUG] Analysis complete", flush=True)

            # Print console report
            print_console_report(result)

        finally:
            sys.stdout = old_stdout
            cli_output = captured_output.getvalue()

        print(f"[DEBUG] CLI output length: {len(cli_output)}", flush=True)

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Generate HTML report
        html_filename = f'band_analysis_{timestamp}.html'
        html_report_path = os.path.join(current_app.config['OUTPUT_FOLDER'], html_filename)
        generate_html_report(result, html_report_path)
        print(f"[DEBUG] HTML report saved to: {html_report_path}", flush=True)

        # Generate prompt file for Claude CLI
        prompt_filename = f'prompt_{timestamp}.txt'
        prompt_path = os.path.join(current_app.config['OUTPUT_FOLDER'], prompt_filename)
        generate_prompt(result, output_path=prompt_path)
        print(f"[DEBUG] Prompt saved to: {prompt_path}", flush=True)

    except Exception as e:
        error = str(e)
        import traceback
        cli_output = f"Error during analysis:\n{traceback.format_exc()}"
        print(f"[ERROR] {cli_output}", flush=True)

    return cli_output, html_report_path, prompt_path, error


@bands_bp.route('/download/<filename>')
def download(filename):
    """Download HTML report."""
    filepath = os.path.join(current_app.config['OUTPUT_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    flash('Report file not found.', 'error')
    return redirect(url_for('bands.upload'))


@bands_bp.route('/kb/upload', methods=['POST'])
def kb_upload():
    """Upload files to knowledge base library."""
    if 'kb_new_files' not in request.files:
        flash('No files selected.', 'error')
        return redirect(url_for('bands.upload'))

    files = request.files.getlist('kb_new_files')
    uploaded_count = 0

    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['KNOWLEDGE_LIBRARY'], filename)
            file.save(filepath)
            uploaded_count += 1

    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s) to library.', 'success')
    else:
        flash('No valid files were uploaded.', 'error')

    return redirect(url_for('bands.upload'))


@bands_bp.route('/kb/delete/<filename>', methods=['POST'])
def kb_delete(filename):
    """Delete file from knowledge base library."""
    filepath = os.path.join(current_app.config['KNOWLEDGE_LIBRARY'], secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Deleted {filename} from library.', 'success')
    else:
        flash('File not found.', 'error')
    return redirect(url_for('bands.upload'))


@bands_bp.route('/generate-final-report', methods=['POST'])
def generate_final_report():
    """Generate final HTML report with Claude's review included."""
    html_report = request.form.get('html_report', '')
    claude_review = request.form.get('claude_review', '').strip()

    if not html_report:
        flash('Original HTML report not found.', 'error')
        return redirect(url_for('bands.upload'))

    if not claude_review:
        flash('Please paste Claude\'s review before generating the final report.', 'error')
        return redirect(url_for('bands.upload'))

    try:
        # Read the original HTML report
        original_path = os.path.join(current_app.config['OUTPUT_FOLDER'], secure_filename(html_report))
        if not os.path.exists(original_path):
            flash('Original HTML report file not found.', 'error')
            return redirect(url_for('bands.upload'))

        with open(original_path, 'r', encoding='utf-8') as f:
            original_html = f.read()

        # Generate final report with Claude review
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_filename = f'band_analysis_final_{timestamp}.html'
        final_path = os.path.join(current_app.config['OUTPUT_FOLDER'], final_filename)

        # Insert Claude review into the HTML report
        final_html = inject_claude_review(original_html, claude_review)

        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"[DEBUG] Final report saved to: {final_path}", flush=True)

        # Return the file for download
        return send_file(final_path, as_attachment=True, download_name=final_filename)

    except Exception as e:
        flash(f'Error generating final report: {str(e)}', 'error')
        return redirect(url_for('bands.upload'))


def inject_claude_review(html_content, claude_review):
    """Inject Claude's review into the HTML report."""
    # Escape HTML in the review text
    import html
    escaped_review = html.escape(claude_review)

    # Create the Claude review section HTML
    claude_section = f'''
    <div class="section claude-review-section">
        <h2>Stage 2: Claude Expert Review</h2>
        <div class="claude-review-content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: inherit; margin: 0; line-height: 1.6;">{escaped_review}</pre>
        </div>
    </div>
    <style>
        .claude-review-section {{
            margin-top: 30px;
            padding: 20px;
            background-color: #f0f7ff;
            border: 1px solid #b8daff;
            border-radius: 8px;
        }}
        .claude-review-section h2 {{
            color: #004085;
            margin-bottom: 15px;
            border-bottom: 2px solid #004085;
            padding-bottom: 10px;
        }}
        .claude-review-content {{
            background-color: white;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
        }}
    </style>
    '''

    # Try to insert before </body> tag
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', f'{claude_section}</body>')
    else:
        # Append at the end if no body tag
        html_content += claude_section

    return html_content


def run_claude_cli(prompt_path):
    """Execute Claude CLI with prompt file and return output."""
    import subprocess

    try:
        # Read prompt content
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        print(f"[DEBUG] Executing Claude CLI with prompt length: {len(prompt_content)}", flush=True)

        # Execute Claude CLI (Windows compatible)
        result = subprocess.run(
            ['claude', '-p', '--dangerously-skip-permissions'],
            input=prompt_content,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            shell=True
        )

        print(f"[DEBUG] Claude CLI return code: {result.returncode}", flush=True)

        if result.returncode == 0:
            return result.stdout, None
        else:
            return None, f"Claude CLI error: {result.stderr}"

    except subprocess.TimeoutExpired:
        return None, "Claude CLI timed out after 5 minutes"
    except FileNotFoundError:
        return None, "Claude CLI not found. Ensure 'claude' is installed and in PATH"
    except Exception as e:
        return None, f"Error: {str(e)}"


@bands_bp.route('/ai-review', methods=['POST'])
def ai_review():
    """Execute Claude CLI and generate final report with AI review."""
    html_report = request.form.get('html_report', '')
    prompt_file = request.form.get('prompt_file', '')

    if not html_report or not prompt_file:
        flash('Missing report or prompt file.', 'error')
        return redirect(url_for('bands.upload'))

    # Get full paths
    prompt_path = os.path.join(current_app.config['OUTPUT_FOLDER'], secure_filename(prompt_file))
    html_path = os.path.join(current_app.config['OUTPUT_FOLDER'], secure_filename(html_report))

    if not os.path.exists(prompt_path):
        flash('Prompt file not found.', 'error')
        return redirect(url_for('bands.upload'))

    if not os.path.exists(html_path):
        flash('HTML report file not found.', 'error')
        return redirect(url_for('bands.upload'))

    # Execute Claude CLI
    print("[DEBUG] Running Claude CLI...", flush=True)
    claude_review, error = run_claude_cli(prompt_path)

    if error:
        flash(f'AI Review error: {error}', 'error')
        return redirect(url_for('bands.upload'))

    if not claude_review:
        flash('Claude returned empty response.', 'error')
        return redirect(url_for('bands.upload'))

    print(f"[DEBUG] Claude review length: {len(claude_review)}", flush=True)

    # Read original HTML and inject Claude review
    with open(html_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    final_html = inject_claude_review(original_html, claude_review)

    # Save final report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    final_filename = f'band_analysis_final_{timestamp}.html'
    final_path = os.path.join(current_app.config['OUTPUT_FOLDER'], final_filename)

    with open(final_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"[DEBUG] Final report saved to: {final_path}", flush=True)

    # Render results page with Claude review displayed
    return render_template(
        'bands/ai_results.html',
        claude_review=claude_review,
        final_report=final_filename,
        original_report=html_report
    )
