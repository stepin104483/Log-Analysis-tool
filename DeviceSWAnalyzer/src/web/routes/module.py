"""
Generic Module Routes

Provides common route handlers for all analysis modules.
Routes are generated dynamically based on module configuration.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file

# Add paths for imports
base_dir = Path(__file__).parent.parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core import ModuleRegistry, AIReviewService, FileHandler
from core.base_analyzer import AnalysisInput

module_bp = Blueprint('module', __name__)


def get_file_handler():
    """Get file handler instance."""
    return FileHandler(
        upload_folder=current_app.config['UPLOAD_FOLDER'],
        kb_folder=current_app.config['KNOWLEDGE_LIBRARY'],
        output_folder=current_app.config['OUTPUT_FOLDER']
    )


@module_bp.route('/<module_id>')
def upload(module_id):
    """Render module upload page."""
    module = ModuleRegistry.get_module(module_id)

    if not module:
        flash(f'Module "{module_id}" not found.', 'error')
        return redirect(url_for('main.index'))

    # If coming soon, show placeholder
    if module.status == 'coming_soon':
        return render_template('module/coming_soon.html', module=module.get_module_info())

    file_handler = get_file_handler()
    kb_files = file_handler.get_kb_files()

    return render_template(
        'module/upload.html',
        module=module.get_module_info(),
        kb_files=kb_files
    )


@module_bp.route('/<module_id>/analyze', methods=['POST'])
def analyze(module_id):
    """Handle file uploads and run analysis."""
    module = ModuleRegistry.get_module(module_id)

    if not module:
        flash(f'Module "{module_id}" not found.', 'error')
        return redirect(url_for('main.index'))

    if module.status == 'coming_soon':
        flash(f'{module.display_name} is coming soon!', 'info')
        return redirect(url_for('module.upload', module_id=module_id))

    file_handler = get_file_handler()
    session_id = file_handler.create_session()

    try:
        # Process uploaded files
        input_files = {}

        if 'input_files' in request.files:
            files = request.files.getlist('input_files')
            for file in files:
                if file and file.filename:
                    filepath = file_handler.save_uploaded_file(file, session_id)
                    if filepath:
                        # Auto-detect file type
                        field_name = module.detect_file_type(file.filename)
                        if field_name:
                            input_files[field_name] = filepath

        # Get parameters
        parameters = {}
        for param in module.parameters:
            value = request.form.get(param['name'], '').strip()
            if value:
                parameters[param['name']] = value

        # Get selected KB files
        selected_kb = request.form.getlist('kb_files')

        # Check if at least one input file was provided
        if not input_files:
            flash('Please upload at least one input document with a recognizable filename pattern.', 'error')
            file_handler.cleanup_session(session_id)
            return redirect(url_for('module.upload', module_id=module_id))

        # Create analysis input
        analysis_input = AnalysisInput(
            files=input_files,
            parameters=parameters,
            kb_files=selected_kb
        )

        # Run analysis
        print(f"[DEBUG] Running {module.display_name} analysis...", flush=True)
        result = module.analyze(analysis_input)

        # Clean up uploaded files
        file_handler.cleanup_session(session_id)

        if not result.success:
            flash(f'Analysis error: {", ".join(result.errors)}', 'error')
            return redirect(url_for('module.upload', module_id=module_id))

        # Render results
        return render_template(
            'module/results.html',
            module=module.get_module_info(),
            cli_output=result.cli_output,
            html_report=os.path.basename(result.html_report_path) if result.html_report_path else None,
            prompt_file=os.path.basename(result.prompt_path) if result.prompt_path else None
        )

    except Exception as e:
        file_handler.cleanup_session(session_id)
        flash(f'An error occurred: {str(e)}', 'error')
        import traceback
        print(f"[ERROR] {traceback.format_exc()}", flush=True)
        return redirect(url_for('module.upload', module_id=module_id))


@module_bp.route('/<module_id>/ai-review', methods=['POST'])
def ai_review(module_id):
    """Execute Claude CLI and generate final report with AI review."""
    module = ModuleRegistry.get_module(module_id)

    if not module:
        flash(f'Module "{module_id}" not found.', 'error')
        return redirect(url_for('main.index'))

    html_report = request.form.get('html_report', '')
    prompt_file = request.form.get('prompt_file', '')

    if not html_report or not prompt_file:
        flash('Missing report or prompt file.', 'error')
        return redirect(url_for('module.upload', module_id=module_id))

    file_handler = get_file_handler()

    # Get full paths
    prompt_path = file_handler.get_output_path(prompt_file)
    html_path = file_handler.get_output_path(html_report)

    if not file_handler.output_exists(prompt_file):
        flash('Prompt file not found.', 'error')
        return redirect(url_for('module.upload', module_id=module_id))

    if not file_handler.output_exists(html_report):
        flash('HTML report file not found.', 'error')
        return redirect(url_for('module.upload', module_id=module_id))

    # Execute Claude CLI
    print("[DEBUG] Running Claude CLI...", flush=True)
    ai_service = AIReviewService(timeout=300)
    claude_review, error = ai_service.run_review(prompt_path)

    if error:
        flash(f'AI Review error: {error}', 'error')
        return redirect(url_for('module.upload', module_id=module_id))

    if not claude_review:
        flash('Claude returned empty response.', 'error')
        return redirect(url_for('module.upload', module_id=module_id))

    print(f"[DEBUG] Claude review length: {len(claude_review)}", flush=True)

    # Read original HTML and inject Claude review
    original_html = file_handler.read_output(html_report)
    final_html = ai_service.inject_review_into_html(original_html, claude_review)

    # Save final report
    final_filename = file_handler.generate_output_filename(f'{module_id}_analysis_final', 'html')
    file_handler.save_output(final_html, final_filename)

    print(f"[DEBUG] Final report saved: {final_filename}", flush=True)

    # Render AI results page
    return render_template(
        'module/ai_results.html',
        module=module.get_module_info(),
        claude_review=claude_review,
        final_report=final_filename,
        original_report=html_report
    )


@module_bp.route('/download/<filename>')
def download(filename):
    """Download a report file."""
    file_handler = get_file_handler()
    filepath = file_handler.get_output_path(filename)

    if file_handler.output_exists(filename):
        return send_file(filepath, as_attachment=True)

    flash('Report file not found.', 'error')
    return redirect(url_for('main.index'))


@module_bp.route('/kb/upload', methods=['POST'])
def kb_upload():
    """Upload files to knowledge base library."""
    if 'kb_new_files' not in request.files:
        flash('No files selected.', 'error')
        return redirect(request.referrer or url_for('main.index'))

    file_handler = get_file_handler()
    files = request.files.getlist('kb_new_files')
    uploaded_count = 0

    for file in files:
        if file_handler.save_kb_file(file):
            uploaded_count += 1

    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s) to library.', 'success')
    else:
        flash('No valid files were uploaded.', 'error')

    return redirect(request.referrer or url_for('main.index'))


@module_bp.route('/kb/delete/<filename>', methods=['POST'])
def kb_delete(filename):
    """Delete file from knowledge base library."""
    file_handler = get_file_handler()

    if file_handler.delete_kb_file(filename):
        flash(f'Deleted {filename} from library.', 'success')
    else:
        flash('File not found.', 'error')

    return redirect(request.referrer or url_for('main.index'))
