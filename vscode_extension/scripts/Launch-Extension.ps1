# Launch-Extension.ps1
# Script for launching VS Code with the extension in development mode

# Set environment variables for debugging
$env:PROJECT_S_DEV_MODE = "true"

# Create a temporary workspace if none is provided
$workspacePath = $args[0]
if (-not $workspacePath) {
    $tempWorkspacePath = Join-Path -Path $env:TEMP -ChildPath "project-s-test-workspace"
    if (-not (Test-Path $tempWorkspacePath)) {
        New-Item -ItemType Directory -Path $tempWorkspacePath | Out-Null
        New-Item -ItemType File -Path "$tempWorkspacePath\README.md" -Value "# Project-S Test Workspace`n`nThis is a temporary workspace for testing the Project-S VSCode extension." | Out-Null
    }
    $workspacePath = $tempWorkspacePath
}

# Check if the extension is being developed
$vscodeLaunchJson = Join-Path -Path $PSScriptRoot -ChildPath "..\.vscode\launch.json"
if (Test-Path $vscodeLaunchJson) {
    Write-Host "Launching VS Code in extension development mode..." -ForegroundColor Blue
    Write-Host "Using workspace: $workspacePath" -ForegroundColor Blue
    
    # Launch VS Code with the extension
    & code --extensionDevelopmentPath="$PSScriptRoot\.." $workspacePath
} else {
    Write-Host "VS Code launch configuration not found. Please run this script from the extension root directory." -ForegroundColor Red
    exit 1
}
