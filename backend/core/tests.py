from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from core.models import Project


class SeedCommandTests(TestCase):
    def test_seed_creates_superuser_and_projects(self):
        stdout = StringIO()

        call_command("seed", count=2, stdout=stdout, stderr=StringIO())

        user_model = get_user_model()
        self.assertTrue(user_model.objects.filter(email="admin@example.com").exists())
        self.assertEqual(Project.objects.count(), 2)
