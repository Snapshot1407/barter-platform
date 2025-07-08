from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Ad
from rest_framework import status


class AdPermissionsTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')

        self.ad = Ad.objects.create(
            user=self.owner,
            title='Test Ad',
            description='Test',
            category='BOOKS',
            condition='NEW'
        )

    def test_permission_logic(self):
        """Проверяем логику разрешений напрямую"""
        from ads.views import IsOwnerOrReadOnly
        permission = IsOwnerOrReadOnly()

        # Создаем mock-запрос
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()

        # GET запрос - должен разрешаться всем
        request = factory.get('/')
        self.assertTrue(permission.has_object_permission(request, None, self.ad))

        # PATCH запрос от владельца
        request = factory.patch('/')
        request.user = self.owner
        self.assertTrue(permission.has_object_permission(request, None, self.ad))

        # PATCH запрос от чужого пользователя
        request.user = self.other_user
        self.assertFalse(permission.has_object_permission(request, None, self.ad))

    def test_owner_can_update(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('ad-detail', args=[self.ad.id])
        response = self.client.patch(url, {'title': 'New Title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_update(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('ad-detail', args=[self.ad.id])
        response = self.client.patch(url, {'title': 'Hacked Title'})

        # Добавляем отладочную информацию
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        print(f"Ad owner: {self.ad.user}, Current user: {self.other_user}")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)