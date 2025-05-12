# PowerShell script to set up the test environment
# Run this script with: .\setup_test_env.ps1

# Check if .env.test exists
if (-not (Test-Path .env.test)) {
    Write-Error "Error: .env.test file not found. Please create it first."
    exit 1
}

# Load environment variables from .env.test
Get-Content .env.test | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}

# Activate virtual environment if it exists
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..."
    .\venv\Scripts\Activate.ps1
}

# Run the test database setup script
Write-Host "Setting up test database..."
python tests/setup_test_database.py

# Run the test data seeding script
Write-Host "Seeding test data..."
python tests/utils/seed_test_data.py

Write-Host "Test environment setup completed successfully!" 
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 