from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import UserProfile


class AccountFlowTests(TestCase):
    """Basic tests for signup and login flows."""

    def test_signup_creates_user_and_profile(self):
        signup_url = reverse('signup')
        data = {
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        response = self.client.post(signup_url, data)
        self.assertEqual(response.status_code, 302)

        User = get_user_model()
        user_exists = User.objects.filter(email='testuser@example.com').exists()
        self.assertTrue(user_exists)

        user = User.objects.get(email='testuser@example.com')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_login_with_valid_credentials(self):
        User = get_user_model()
        user = User.objects.create_user(email='login@example.com', password='StrongPass123')
        UserProfile.objects.create(user=user)

        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'login@example.com',
            'password': 'StrongPass123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
