from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Theme, Setting


class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def test_register_new_user(self):
        data = {
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'jane',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resp'], 'success')
        self.assertTrue(Token.objects.filter(
            user__username=data['username']).exists())

    def test_register_existing_username(self):
        User.objects.create_user(
            username='johndoe', email='johndoe@example.com', password='doe')
        data = {
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'doe',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resp'], 'failed')
        self.assertIn('Username already exists', response.json()['message'])

    def test_user_login_success(self):
        user = User.objects.create_user(
            username='janedoe', password='jane')
        data = {
            'username': 'janedoe',
            'password': 'jane',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resp'], 'success')
        self.assertTrue('token' in response.json())


class ReminderViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='john', password='doe')
        self.token = Token.objects.create(user=self.user)
        self.client = Client()

    def test_create_reminder(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # self.client.force_login(self.user)
        data = {
            'content': 'Stretch Break: Stretch Those Limbs!',
            'reminderDateTime': '2023-08-09T11:17:00Z',
            'repeat': True,
            'reminderType': 'Weekly',
            'soundName': 'Bubbles',
            'soundUrl': './assets/sounds/cartoon-bubbles.mp3',
            'animationName': 'Strech Limbs',
            'animationUrl': './assets/images/breaks/stretch-limbs.jpg',
            'breakTime': '600',
            'breakDuration': '300'
        }
        url = reverse('create-reminder')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # You can add more assertions here

    def test_get_reminders_list(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        url = reverse('reminders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # You can add more assertions here

    def test_update_reminder(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        reminder_id = 1
        data = {
            'content': 'Stretch Break: Stretch Those Limbs!',
            'reminderDateTime': '2023-08-09T11:17:00Z',
            'repeat': False,
            'reminderType': 'Weekly',
            'soundName': 'Bubbles',
            'soundUrl': './assets/sounds/cartoon-bubbles.mp3',
            'animationName': 'Strech Limbs',
            'animationUrl': './assets/images/breaks/stretch-limbs.jpg',
            'breakTime': '600',
            'breakDuration': '300'
        }

        url = reverse('update-reminder', args=[reminder_id])
        response = self.client.put(
            url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_reminder(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        reminder_id = 1
        url = reverse('delete-reminder', args=[reminder_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_reminders(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        url = reverse('delete_all')

        data = {
            'reminder_ids': [1, 2]
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ThemeAndSettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jane', password='janepwd')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_set_theme(self):
        theme_data = {'theme': 'Sanguine'}
        response = self.client.post(reverse('set-theme'), data=theme_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_theme(self):
        theme = Theme.objects.create(user=self.user, theme_name='Sanguine')
        response = self.client.get(reverse('get-theme'))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['theme'], theme.theme_name)

    def test_set_settings(self):
        settings_data = {
            'isScreenOn': True,
            'isSoundOn': False,
            'isDndOn': True,
            'defaultSoundName': 'Chime',
            'defaultSoundUrl': './assets/sounds/chime.mp3'
        }
        response = self.client.post(
            reverse('set-settings'), data=settings_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_settings(self):
        settings = Setting.objects.create(
            user=self.user,
            isScreenOn=True,
            isSoundOn=False,
            isDndOn=True,
            defaultSoundName='Bell',
            defaultSoundUrl='./assets/sounds/bell.mp3'
        )
        response = self.client.get(reverse('get-settings'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        settings_data = response_data['data']
        self.assertEqual(
            settings_data['defaultSoundName'], settings.defaultSoundName)
