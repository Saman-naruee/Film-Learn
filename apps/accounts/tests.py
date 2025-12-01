from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.user = User.objects.create_user(email="user@example.com", password="password", first_name="User")
        self.client.force_authenticate(user=self.admin)

    def test_list_users_admin(self):
        resp = self.client.get("/api/users/")
        assert resp.status_code == status.HTTP_200_OK
        assert any(u["email"] == "admin@example.com" for u in resp.json())

    def test_create_user_register(self):
        self.client.force_authenticate(user=None)  # unauthenticated registration
        payload = {"email": "new@example.com", "password": "pass1234", "first_name": "New"}
        resp = self.client.post("/api/users/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="new@example.com").exists()

    def test_retrieve_self(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f"/api/users/{self.user.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["email"] == "user@example.com"

    def test_update_password_self(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/users/{self.user.id}/set-password/", {"password": "newpass"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.check_password("newpass")
