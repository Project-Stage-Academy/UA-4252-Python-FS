from http.cookies import SimpleCookie

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class JWTAuthTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.email = "test@email.com"
        self.password = "test123test"
        self.user = User.objects.create_user(email=self.email, password=self.password, first_name='Test', last_name='User')

        self.login_url = reverse('login')
        self.refresh_url = reverse('refresh-token')
        self.logout_url = reverse('logout')

    def test_login_success(self):
        data = {
            "email": self.email,
            "password": self.password
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access_token', self.client.cookies)
        self.assertIn('refresh_token', self.client.cookies)

    def test_login_fail(self):
        data = {
            "email": "somewrongmail@email.com",
            "password": "somewrongpass",
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_throttled(self):
        data = {
            "email": "somemail@email.com",
            "password": "somepass123"
        }

        for i in range(0, 10):
            self.client.post(
                self.login_url,
                data,
                format='json'
            )

        response =  self.client.post(
            self.login_url,
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_logout_success(self):
        data = {
            "email": self.email,
            "password": self.password
        }

        login_response = self.client.post(
            self.login_url,
            data,
            format='json'
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        refresh_cookie = self.client.cookies.get('refresh_token')
        refresh_token = refresh_cookie.value

        logout_data = {
            'refresh': refresh_token
        }

        logout_response = self.client.post(
            self.logout_url,
            logout_data,
            format='json'
        )

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_refresh_token_success(self):
        login_data = {
            "email": self.email,
            "password": self.password
        }

        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        refresh_cookie = self.client.cookies.get('refresh_token')
        refresh_token = refresh_cookie.value
        self.assertIsNotNone(refresh_token)

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        invalid_token = "someinvalidtoken"

        response = self.client.post(
            self.refresh_url,
            {"refresh": invalid_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

