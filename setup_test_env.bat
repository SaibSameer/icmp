@echo off
echo Setting up test environment...

REM Load environment variables from .env.test
for /f "tokens=*" %%a in (.env.test) do set %%a

echo Environment variables loaded.

REM Set up the test database
echo Setting up test database...
python tests/setup_test_database.py

REM Seed test data
echo Seeding test data...
python tests/utils/seed_test_data.py

echo Test environment setup complete!
pause 