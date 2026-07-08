# now-play-backend

This workspace contains the Django REST backend and a Vite React frontend scaffold for Now Play for Creators.

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