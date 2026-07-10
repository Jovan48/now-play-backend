# now-play-backend

This workspace contains the Django REST backend and a Vite React frontend scaffold for Now Play for Creators.

## Getting Started

This project uses a Makefile to keep the local Django database in sync and remove manual setup steps.

First time on this repo?

```bash
make install
make setup
make run
```

After pulling changes that include new migrations, run:

```bash
make setup
```

This applies pending migrations and re-seeds sample data without duplicating existing records. Superuser credentials can be overridden via a .env file using DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD; otherwise a dev-only fallback is used.

Run backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

Run frontend:

```powershell
cd frontend
npm install
npm run dev
```
# now-play-backend