from django.test import TestCase, Client, override_settings


class PublicPagesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_privacy_public(self):
        resp = self.client.get('/privacy/')
        self.assertEqual(resp.status_code, 200)

    def test_terms_public(self):
        resp = self.client.get('/terms/')
        self.assertEqual(resp.status_code, 200)

    def test_data_deletion_public(self):
        resp = self.client.get('/data-deletion/')
        self.assertEqual(resp.status_code, 200)

    def test_instagram_callback_public_redirects_without_code(self):
        resp = self.client.get('/dashboard/instagram/callback/')
        # Callback without code should redirect back to dashboard
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp.headers.get('Location', '').startswith('/dashboard/'))





