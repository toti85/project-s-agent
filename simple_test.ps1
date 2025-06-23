# Simple PowerShell test
Write-Host "=== SIMPLE PROJECT-S TEST ===" -ForegroundColor Cyan
Write-Host "Testing basic functionality..." -ForegroundColor Yellow

# Test current directory
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Green

# Test file existence
if (Test-Path "main_multi_model.py") {
    Write-Host "✅ main_multi_model.py exists" -ForegroundColor Green
} else {
    Write-Host "❌ main_multi_model.py not found" -ForegroundColor Red
}

# Test Python
try {
    $pythonTest = python -c "print('Python OK')"
    Write-Host "✅ Python: $pythonTest" -ForegroundColor Green
} catch {
    Write-Host "❌ Python error: $_" -ForegroundColor Red
}

Write-Host "=== TEST COMPLETE ===" -ForegroundColor Cyan
