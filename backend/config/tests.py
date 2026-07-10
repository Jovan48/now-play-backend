from django.test import SimpleTestCase
from django.urls import reverse


class SwaggerDocsTests(SimpleTestCase):
    def test_swagger_ui_is_available(self):
        response = self.client.get(reverse("swagger-ui"))
        self.assertEqual(response.status_code, 200)
