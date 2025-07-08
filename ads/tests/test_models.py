from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Ad, ExchangeProposal


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Item',
            description='Test Description',
            category='BOOKS',
            condition='NEW'
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.title, 'Test Item')
        self.assertEqual(self.ad.description, 'Test Description')
        self.assertEqual(self.ad.category, 'BOOKS')
        self.assertEqual(self.ad.condition, 'NEW')
        self.assertIsNotNone(self.ad.created_at)  # Проверяем авто-заполнение даты
        # self.assertEqual(self.ad.status, 'ACTIVE')  # Проверяем статус по умолчанию

    # def test_status_choices(self):
    #     """Тест доступных статусов"""
    #     choices = dict(Ad.STATUS_CHOICES)
    #     self.assertEqual(len(choices), 3)
    #     self.assertIn('ACTIVE', choices)
    #     self.assertIn('CLOSED', choices)
    #     self.assertIn('ARCHIVED', choices)

    def test_exchange_proposal(self):
        ad2 = Ad.objects.create(
            user=self.user,
            title='Another Item',
            description='Test',
            category='ELECTRONICS',
            condition='USED'
        )
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad,
            ad_receiver=ad2
        )
        self.assertEqual(proposal.status, 'PENDING')