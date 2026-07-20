<#
PowerShell helper to set up the backend for local development.
Usage: open PowerShell in the `backend` folder and run `./setup_backend.ps1`.
This will create a virtualenv, install requirements, run migrations, and attempt to create a superuser
if `SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD` are set in the environment or in `.env`.
#>

$VENV = ".venv"
if (-Not (Test-Path $VENV)) {
    python -m venv $VENV
}

& "$VENV\Scripts\Activate.ps1"

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate

# create superuser from env using the helper script
python scripts/create_superuser.py

Write-Host 'Setup complete. Activate the venv with: .\.venv\Scripts\Activate.ps1 and run the server: python manage.py runserver'
