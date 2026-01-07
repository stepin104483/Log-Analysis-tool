@echo off
REM ============================================================================
REM Band Combos Analyzer - Full Analysis Pipeline (3 Stages)
REM ============================================================================

cd /d "%~dp0"

echo ============================================================
echo           BAND COMBOS ANALYZER TOOL
echo ============================================================
echo.

REM ============================================================================
REM CONFIGURATION - Edit these paths if your files have different names
REM ============================================================================
set RFC_FILE=Input\rfc_hwid966_Q6515_v2_APT_ag.xml
set HW_FILTER_FILE=Input\hardware_band_filtering.xml
set CARRIER_FILE=Input\carrier_policy.xml
set GENERIC_FILE=Input\generic_band_restrictions.xml
set MDB_FILE=Input\MDB\mcc2bands\mcc2bands.xml
set QXDM_FILE=Input\PM_RF_Band_1.txt
set UE_CAP_FILE=Input\UE_capability_information_NR_LTE_notENDC.txt
set TARGET_MCC=310

REM ============================================================================
REM STAGE 1: Python Analysis
REM ============================================================================
echo [STAGE 1] Running Python Analysis...
echo.

set CMD=python -m src.main

REM Add files only if they exist
if exist "%RFC_FILE%" set CMD=%CMD% --rfc "%RFC_FILE%"
if exist "%HW_FILTER_FILE%" set CMD=%CMD% --hw-filter "%HW_FILTER_FILE%"
if exist "%CARRIER_FILE%" set CMD=%CMD% --carrier "%CARRIER_FILE%"
if exist "%GENERIC_FILE%" set CMD=%CMD% --generic "%GENERIC_FILE%"
if exist "%MDB_FILE%" set CMD=%CMD% --mdb "%MDB_FILE%" --mcc %TARGET_MCC%
if exist "%QXDM_FILE%" set CMD=%CMD% --qxdm "%QXDM_FILE%"
if exist "%UE_CAP_FILE%" set CMD=%CMD% --ue-cap "%UE_CAP_FILE%"

echo Running: %CMD%
echo.
call %CMD%

set STAGE1_ERROR=%ERRORLEVEL%
if %STAGE1_ERROR% NEQ 0 (
    echo.
    echo [WARNING] Stage 1 completed with anomalies detected.
)

REM Verify Stage 1 outputs exist
if not exist "output\prompt.txt" (
    echo [ERROR] prompt.txt not found. Stage 1 failed.
    goto :END
)
if not exist "output\analysis_state.json" (
    echo [ERROR] analysis_state.json not found. Stage 1 failed.
    goto :END
)

echo.
echo ============================================================
echo [STAGE 2] Claude AI Review
echo ============================================================
echo.

echo Running Claude CLI review...
echo Command: claude -p --dangerously-skip-permissions
echo.

REM Run Claude CLI and capture output
call claude -p --dangerously-skip-permissions < output\prompt.txt > output\claude_review.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Claude CLI may have encountered an issue.
)

REM Check if claude_review.txt was created and has content
if not exist "output\claude_review.txt" (
    echo [WARNING] Claude review not generated. Proceeding without it.
) else (
    for %%A in ("output\claude_review.txt") do (
        if %%~zA GTR 100 (
            echo Claude review saved to: output\claude_review.txt
        ) else (
            echo [WARNING] Claude review file is too small. May be empty or failed.
        )
    )
)

echo.
echo ============================================================
echo [STAGE 3] Generating Integrated HTML Report
echo ============================================================
echo.

echo Running report generator...
call python -m src.merge_report

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Stage 3 failed to generate HTML report.
    goto :END
)

REM Verify HTML was generated
if not exist "output\band_analysis_report.html" (
    echo [ERROR] HTML report was not generated.
    goto :END
)

echo.
echo ============================================================
echo                     ANALYSIS COMPLETE
echo ============================================================
echo.
echo Output files in 'output' folder:
echo   - prompt.txt                : Stage 1 analysis data
echo   - analysis_state.json       : Stage 1 state (for Stage 3)
echo   - claude_review.txt         : Stage 2 Claude review
echo   - band_analysis_report.html : INTEGRATED REPORT (Stage 1 + 2)
echo.

:END
pause
