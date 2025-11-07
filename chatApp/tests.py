from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from chatApp.models import UserProfile

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')

    def test_profile_view_returns_200(self):
        response = self.client.get(reverse('chatApp:profile'))
        self.assertEqual(response.status_code, 200)

                        def test_delete_account_api(self):

                            response = self.client.post(reverse('chatApp:delete_account'), {'password': 'testpassword'}, content_type='application/json')

                            self.assertEqual(response.status_code, 200)

                    

                

            

        

    