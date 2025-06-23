# Project-S PowerShell Status Checker
# ==================================
# PowerShell-compatible script to check Project-S system status

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PROJECT-S SYSTEM STATUS CHECKER (PowerShell)" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "c:\project_s_agent"
Write-Host "[DIR] Working directory: $(Get-Location)" -ForegroundColor Green

Write-Host ""
Write-Host "[CHECK] CHECKING CORE FILES:" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Gray

# Check if core files exist
$coreFiles = @(
    @("WORKING_MINIMAL_VERSION.py", "Working minimal system"),
    @("main_multi_model.py", "Multi-model AI system"),
    @("core\cognitive_core.py", "Cognitive Core"),
    @("core\smart_orchestrator.py", "Smart Tool Orchestrator"),
    @("integrations\multi_model_ai_client.py", "Multi-model AI client"),
    @("integrations\advanced_langgraph_workflow.py", "Advanced LangGraph"),
    @("stable_website_analyzer.py", "Website Analyzer"),
    @("fix_unicode_encoding.py", "Unicode encoding fixes")
)

$filesFound = 0
foreach ($fileInfo in $coreFiles) {
    $file = $fileInfo[0]
    $description = $fileInfo[1]
    
    if (Test-Path $file) {
        Write-Host "[OK] $file - $description" -ForegroundColor Green
        $filesFound++
    } else {
        Write-Host "[MISSING] $file - $description - File not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[TEST] TESTING PYTHON IMPORTS:" -ForegroundColor Yellow
Write-Host "---------------------------" -ForegroundColor Gray

# Test basic Python imports
try {
    $pythonTest = python -c "import sys; print('[OK] Python', sys.version.split()[0], 'working')"
    Write-Host $pythonTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not working: $_" -ForegroundColor Red
}

# Test Unicode encoding fix
try {
    $unicodeTest = python -c "import fix_unicode_encoding; print('[OK] Unicode encoding fixes: Available')"
    Write-Host $unicodeTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Unicode encoding fixes: $_" -ForegroundColor Red
}

# Test YAML support
try {
    $yamlTest = python -c "import yaml; print('[OK] YAML support: Available')"
    Write-Host $yamlTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] YAML support: $_" -ForegroundColor Red
}

# Test asyncio
try {
    $asyncTest = python -c "import asyncio; print('[OK] Asyncio support: Available')"
    Write-Host $asyncTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Asyncio support: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[ADVANCED] TESTING SOPHISTICATED COMPONENTS:" -ForegroundColor Yellow
Write-Host "------------------------------------" -ForegroundColor Gray

# Test working minimal version
try {
    $minimalTest = python -c "import WORKING_MINIMAL_VERSION; print('[OK] Working minimal version: Available')"
    Write-Host $minimalTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Working minimal version: $_" -ForegroundColor Red
}

# Test website analyzer
try {
    $analyzerTest = python -c "import stable_website_analyzer; print('[OK] Website analyzer: Available')"
    Write-Host $analyzerTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Website analyzer: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[MULTIMODEL] TESTING MULTI-MODEL SYSTEM:" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Gray

# Test if the multi-model system can start (just imports, no execution)
try {
    Write-Host "Testing multi-model system startup..." -ForegroundColor Cyan
    $multiModelTest = python -c "import fix_unicode_encoding; from integrations.multi_model_ai_client import multi_model_ai_client; print('[OK] Multi-model AI system: Successfully imported'); print('[OK] Unicode encoding: Fixed'); print('[OK] AI Client: Available')"
    Write-Host $multiModelTest -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Multi-model system: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[SUMMARY] SYSTEM STATUS SUMMARY:" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Gray

$totalFiles = $coreFiles.Count
$completionPercentage = [math]::Round(($filesFound / $totalFiles) * 100, 1)

Write-Host "Files Found: $filesFound/$totalFiles" -ForegroundColor Cyan
Write-Host "Completion: $completionPercentage%" -ForegroundColor Cyan

if ($completionPercentage -ge 90) {
    Write-Host ""
    Write-Host "[SUCCESS] PROJECT-S RESTORATION IS NEARLY COMPLETE!" -ForegroundColor Green
    Write-Host "   Most sophisticated components are available." -ForegroundColor Green
    Write-Host "   Focus: Fix remaining import/syntax issues." -ForegroundColor Green
} elseif ($completionPercentage -ge 70) {
    Write-Host ""
    Write-Host "[PROGRESS] PROJECT-S RESTORATION IS WELL UNDERWAY!" -ForegroundColor Yellow
    Write-Host "   Core components exist but may need fixes." -ForegroundColor Yellow
    Write-Host "   Focus: Test and debug existing components." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[BUILDING] PROJECT-S RESTORATION IN PROGRESS!" -ForegroundColor Magenta
    Write-Host "   Foundation exists, building more components." -ForegroundColor Magenta
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STATUS CHECK COMPLETE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[NEXT ACTIONS] RECOMMENDED NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Test individual sophisticated components" -ForegroundColor White
Write-Host "2. Run the multi-model system demo" -ForegroundColor White
Write-Host "3. Add missing API keys for full functionality" -ForegroundColor White
Write-Host "4. Integration testing of all components" -ForegroundColor White

Write-Host ""
Write-Host "[TIP] TO TEST THE MULTI-MODEL SYSTEM:" -ForegroundColor Cyan
Write-Host "   python main_multi_model.py" -ForegroundColor White
Write-Host ""
Write-Host "[TIP] TO TEST THE MINIMAL SYSTEM:" -ForegroundColor Cyan
Write-Host "   python WORKING_MINIMAL_VERSION.py" -ForegroundColor White
