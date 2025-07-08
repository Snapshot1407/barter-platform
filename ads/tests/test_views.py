from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from ..models import Ad, ExchangeProposal


class AdViewSetTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.client = APIClient()

        # Создаем тестовые объявления
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Книга Python',
            description='Новая книга',
            category='BOOKS',
            condition='NEW'
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Наушники',
            description='Б/у наушники',
            category='ELECTRONICS',
            condition='USED'
        )

    def test_create_ad_authenticated(self):
        """Тест создания объявления авторизованным пользователем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('ad-list')
        data = {
            'title': 'Новый товар',
            'description': 'Описание',
            'category': 'OTHER',
            'condition': 'NEW'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ad.objects.count(), 3)
        self.assertEqual(Ad.objects.last().user, self.user1)

    def test_create_ad_unauthenticated(self):
        """Тест создания объявления без авторизации"""
        url = reverse('ad-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ad_owner(self):
        """Тест обновления объявления владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('ad-detail', args=[self.ad1.id])
        data = {'title': 'Обновленное название'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Обновленное название')

    def test_search_and_filter(self):
        """Тест поиска и фильтрации объявлений"""
        url = reverse('ad-search')
        response = self.client.get(url, {
            'search': 'книга',
            'category': 'BOOKS',
            'page': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.ad1.id)


class ProposalViewSetTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.client = APIClient()

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Книга',
            description='...',
            category='BOOKS',
            condition='NEW'
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Гитара',
            description='...',
            category='OTHER',
            condition='USED'
        )

        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Предложение'
        )

    def test_create_proposal(self):
        """Тест создания предложения обмена"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('proposal-list')
        data = {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad2.id,
            'comment': 'Новое предложение'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExchangeProposal.objects.count(), 2)

    def test_self_exchange_protection(self):
        """Тест защиты от обмена товара с самим собой"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('proposal-list')
        data = {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad1.id,
            'comment': 'Неверное предложение'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_status_by_receiver(self):
        """Тест обновления статуса получателем"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('proposal-update-status', args=[self.proposal.id])
        data = {'status': 'ACCEPTED'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, 'ACCEPTED')

    def test_filter_proposals(self):
        """Тест фильтрации предложений"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('proposal-list')
        response = self.client.get(url, {'sender': self.ad1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.proposal.id)