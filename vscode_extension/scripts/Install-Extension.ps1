# Install-Extension.ps1
# Script for installing the Project-S VSCode extension for testing

# Check if the extension is already installed and uninstall it
$extensionId = "project-s.project-s-vscode"
$installedExtensions = & code --list-extensions

if ($installedExtensions -contains $extensionId) {
    Write-Host "Extension $extensionId is already installed. Uninstalling..." -ForegroundColor Yellow
    & code --uninstall-extension $extensionId
}

# Build the extension
Write-Host "Building extension..." -ForegroundColor Blue
npm run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build the extension." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Package the extension
Write-Host "Packaging extension..." -ForegroundColor Blue
npm run package

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to package the extension." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Find the created VSIX file
$vsixFile = Get-ChildItem -Path "dist" -Filter "*.vsix" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($null -eq $vsixFile) {
    Write-Host "No VSIX file found in the dist directory." -ForegroundColor Red
    exit 1
}

# Install the extension
Write-Host "Installing extension..." -ForegroundColor Blue
& code --install-extension $vsixFile.FullName

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install the extension." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Extension installed successfully!" -ForegroundColor Green
Write-Host "Restart VS Code to activate the extension." -ForegroundColor Green
