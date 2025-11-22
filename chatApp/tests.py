from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
import time

class AdminDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Admin user
        self.admin_user = User.objects.create_user('admin', 'admin@example.com', 'password', is_staff=True)
        self.admin_profile = UserProfile.objects.get(user=self.admin_user)
        self.admin_profile.role = 'admin'
        self.admin_profile.save()

        # Regular users
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        time.sleep(0.1) # ensure different creation times
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.user2_profile = UserProfile.objects.get(user=self.user2)
        self.user2_profile.role = 'admin' # Make one other user an admin for sorting
        self.user2_profile.save()


    def test_admin_dashboard_unauthenticated_redirect(self):
        response = self.client.get(reverse('chatApp:admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_non_admin_redirect(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('chatApp:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chatApp:index'))

    def test_admin_dashboard_admin_access(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('chatApp:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatApp/admin_dashboard.html')

    def test_admin_dashboard_search(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('chatApp:admin_dashboard'), {'search': 'user1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['user_profiles']), 1)
        self.assertEqual(response.context['user_profiles'][0].user.username, 'user1')

    def test_admin_dashboard_sort_by_date(self):
        self.client.login(username='admin', password='password')
        
        # Test ascending date
        response = self.client.get(reverse('chatApp:admin_dashboard'), {'sort': 'date_asc'})
        self.assertEqual(response.status_code, 200)
        profiles = list(response.context['user_profiles'])
        self.assertTrue(profiles[0].user.date_joined < profiles[1].user.date_joined)

        # Test descending date
        response = self.client.get(reverse('chatApp:admin_dashboard'), {'sort': 'date_desc'})
        self.assertEqual(response.status_code, 200)
        profiles = list(response.context['user_profiles'])
        self.assertTrue(profiles[0].user.date_joined > profiles[1].user.date_joined)

    def test_admin_dashboard_sort_by_role(self):
        self.client.login(username='admin', password='password')

        # Test ascending role
        response = self.client.get(reverse('chatApp:admin_dashboard'), {'sort': 'role_asc'})
        self.assertEqual(response.status_code, 200)
        profiles = response.context['user_profiles']
        # 'admin' comes before 'user' alphabetically
        self.assertTrue(profiles[0].role <= profiles[1].role)

        # Test descending role
        response = self.client.get(reverse('chatApp:admin_dashboard'), {'sort': 'role_desc'})
        self.assertEqual(response.status_code, 200)
        profiles = response.context['user_profiles']
        self.assertTrue(profiles[0].role >= profiles[1].role)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')

    def test_profile_view_returns_200(self):
        response = self.client.get(reverse('chatApp:profile'))
        self.assertEqual(response.status_code, 200)

    def test_delete_account_api_success(self):
        response = self.client.post(
            reverse('chatApp:delete_account'), 
            {'password': 'testpassword'}, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_delete_account_api_wrong_password(self):
        response = self.client.post(
            reverse('chatApp:delete_account'), 
            {'password': 'wrongpassword'}, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Contraseña incorrecta')