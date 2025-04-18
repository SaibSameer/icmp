# Create deployment package
$packageName = "eb-package-$(Get-Date -Format 'yyyyMMddHHmmss').zip"

# Remove any existing package with the same name
if (Test-Path $packageName) {
    Remove-Item $packageName
}

# Create the zip file excluding unnecessary files/directories
Compress-Archive -Path @(
    'backend',
    'application.py',
    'requirements.txt',
    'Procfile',
    '.ebignore'
) -DestinationPath $packageName

Write-Host "Created deployment package: $packageName" 