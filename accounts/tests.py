from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from accounts.models import Role, Permission

User = get_user_model()


class AccountViewsTestCase(APITestCase):
    def setUp(self):
        self.base_role = Role.objects.get(name="base")
        self.admin_role = Role.objects.get(name="admin")

        self.user = User.objects.create_user(
            username="test", password="password", first_name="Test", last_name="Test",
            national_id="1234567890", phone="1234567890", email="test@test.com"
        )
        self.user.roles.add(self.base_role)

        self.admin_user = User.objects.create_user(
            username="admin", password="password", first_name="Admin", last_name="Admin",
            national_id="0987654321", phone="0987654321", email="admin@test.com"
        )
        self.admin_user.roles.add(self.admin_role)

        self.register_url = reverse('register')
        self.profile_url = reverse('profile')
        self.user_list_url = reverse('user-list')
        self.num_employees_url = reverse('num-employees')
        self.client = APIClient()

    def become(self, username):
        self.client.logout()
        self.client.login(username=username, password='password')
        tok = self.client.post(path='/auth/login', data={"username": username, "password": "password"})
        self.client_headers = {"Authorization": "Token " + tok.data["key"]}

    def test_register_user(self):
        data = {
            "username": "new",
            "password": "password",
            "first_name": "New",
            "last_name": "New",
            "email": "new@test.com",
            "national_id": "1111111111",
            "phone": "1111111111"
        }

        response = self.client.put(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_user_profile_get(self):
        self.become("test")
        response = self.client.get(self.profile_url, headers=self.client_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_user_profile_patch(self):
        self.become("test")
        new_data = {"first_name": "Updated", "last_name": "Name"}

        response = self.client.patch(self.profile_url, new_data, headers=self.client_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["last_name"], "Name")

    def test_list_users_permission(self):
        self.become("test")

        response = self.client.patch(self.user_list_url, headers=self.client_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_num_employees(self):
        # Test the number of employees excluding "base" role
        self.become("admin")
        response = self.client.get(self.num_employees_url, headers=self.client_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
