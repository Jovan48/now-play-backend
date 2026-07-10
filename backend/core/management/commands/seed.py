"""Idempotent database seeding for local development."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

try:
    from faker import Faker
except ImportError:  # pragma: no cover
    Faker = None

from core.models import Project

User = get_user_model()

# NOTE: This fallback exists purely to unblock local make setup runs.
# It is intentionally weak and must never be used outside development.
# Override it via DJANGO_SUPERUSER_PASSWORD in your .env / CI secrets.
DEFAULT_DEV_PASSWORD = "devpassword123"


class Command(BaseCommand):
    help = "Seed the local database with a superuser and sample Project data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of dummy Project records to create (default: 10).",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing seeded Projects before creating new ones.",
        )

    def handle(self, *args, **options):
        if Faker is None:
            raise CommandError(
                "The 'faker' package is required for seeding. "
                "Install it with `pip install faker`."
            )

        try:
            with transaction.atomic():
                self._create_superuser()
                if options["flush"]:
                    self._flush_projects()
                self._create_projects(options["count"])
        except Exception as exc:  # pragma: no cover
            raise CommandError(f"Seeding failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("Database seeding complete."))

    def _create_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", DEFAULT_DEV_PASSWORD)

        if password == DEFAULT_DEV_PASSWORD:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PASSWORD not set — using the insecure "
                    "default dev password. Do not use this outside local dev."
                )
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password", "is_staff", "is_superuser"])
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser '{username}' already exists — skipped.")
            )

    def _flush_projects(self):
        deleted_count, _ = Project.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(f"Flushed {deleted_count} existing Project record(s).")
        )

    def _create_projects(self, count: int):
        fake = Faker()
        created_count = 0

        for _ in range(count):
            name = fake.unique.catch_phrase()
            _, created = Project.objects.get_or_create(
                name=name,
                defaults={"description": fake.paragraph(nb_sentences=3)},
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} new Project record(s) "
                f"({count - created_count} already existed)."
            )
        )
