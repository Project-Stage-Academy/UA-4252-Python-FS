# ===============================
# 🧪  Run Django tests with coverage
# ===============================

Write-Host "▶ Activating virtual environment..." -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated." -ForegroundColor Green
} else {
    Write-Host "⚠️  No .venv found. Continuing with system Python." -ForegroundColor Yellow
}

Write-Host "`n▶ Running tests with coverage..." -ForegroundColor Cyan

coverage run --rcfile=backend/.coveragerc -m pytest -vv

Write-Host "`n📊 Generating coverage report..." -ForegroundColor Cyan
coverage report --rcfile=backend/.coveragerc

Write-Host "`n🌐 Creating HTML report..." -ForegroundColor Cyan
coverage html --rcfile=backend/.coveragerc

Write-Host "`n✅ Coverage complete! Open coverage_html\index.html in your browser." -ForegroundColor Green
