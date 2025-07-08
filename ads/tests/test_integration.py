from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class FullFlowTest(APITestCase):
    def test_full_ad_flow(self):
        # 1. Регистрация пользователя
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=user)

        # 2. Создание объявления
        create_url = reverse('ad-list')
        response = self.client.post(create_url, {
            'title': 'New Item',
            'description': 'Description',
            'category': 'BOOKS',
            'condition': 'NEW'
        })
        self.assertEqual(response.status_code, 201)
        ad_id = response.data['id']

        # 3. Поиск объявления
        search_url = reverse('ad-search')
        response = self.client.get(search_url, {'search': 'item'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # 4. Обновление объявления
        update_url = reverse('ad-detail', args=[ad_id])
        response = self.client.patch(update_url, {'title': 'Updated Title'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Title')