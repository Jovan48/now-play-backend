.PHONY: install setup migrate run test clean

# Install all Python dependencies from requirements.txt.
install:
	pip install -r requirements.txt

# One-shot onboarding: apply migrations and seed the database.
# Run this instead of deleting db.sqlite3 by hand.
setup: migrate
	cd backend && python manage.py seed

# Generate any pending migrations, then apply all migrations.
migrate:
	cd backend && python manage.py makemigrations
	cd backend && python manage.py migrate

# Start the local development server.
run:
	cd backend && python manage.py runserver

# Run the test suite.
test:
	cd backend && python manage.py test

# Remove the local SQLite database and all Python bytecode caches,
# giving a clean slate. Follow up with `make setup` to rebuild.
clean:
	rm -f backend/db.sqlite3
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
