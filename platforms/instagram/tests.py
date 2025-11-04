from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from platforms.instagram.models import InstagramAccount


class InstagramConnectTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', email='tester@example.com', password='pass12345')

    def test_connect_requires_login(self):
        resp = self.client.get('/dashboard/instagram/connect/')
        self.assertIn(resp.status_code, (302, 301))
        self.assertIn('/accounts/login', resp.headers.get('Location', ''))

    def test_connect_redirects_back_when_missing_config(self):
        self.client.login(username='tester', password='pass12345')
        # No INSTAGRAM_* provided here, view should redirect back to dashboard
        resp = self.client.get('/dashboard/instagram/connect/')
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp.headers.get('Location', '').startswith('/dashboard/'))

    def test_connect_redirects_back_when_already_connected(self):
        self.client.login(username='tester', password='pass12345')
        InstagramAccount.objects.create(
            user=self.user,
            instagram_user_id='1789',
            username='igtester',
            access_token='token',
            is_active=True,
        )
        resp = self.client.get('/dashboard/instagram/connect/')
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp.headers.get('Location', '').startswith('/dashboard/'))

    @override_settings(
        INSTAGRAM_CLIENT_ID='1234567890',
        INSTAGRAM_CLIENT_SECRET='secret',
        INSTAGRAM_REDIRECT_URI='http://testserver/dashboard/instagram/callback/',
        FACEBOOK_GRAPH_VERSION='v23.0',
    )
    def test_connect_builds_oauth_redirect_when_configured(self):
        self.client.login(username='tester', password='pass12345')
        resp = self.client.get('/dashboard/instagram/connect/')
        # Should redirect to Facebook dialog oauth
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp.headers.get('Location', '').startswith('https://www.facebook.com/'))


