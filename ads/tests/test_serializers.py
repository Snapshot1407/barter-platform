from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from ..models import Ad, ExchangeProposal
from ..serializers import AdSerializer, ProposalSerializer, ProposalCreateSerializer


class AdSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test description',
            category='BOOKS',
            condition='NEW'
        )

    def test_ad_serializer(self):
        """Тест сериализации объявления"""
        serializer = AdSerializer(instance=self.ad)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Ad')
        self.assertEqual(data['category'], 'BOOKS')
        self.assertEqual(data['user']['username'], 'testuser')

    def test_ad_deserialization(self):
        """Тест десериализации объявления"""
        data = {
            'title': 'New Ad',
            'description': 'New description',
            'category': 'ELECTRONICS',
            'condition': 'USED'
        }
        serializer = AdSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ProposalSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.ad1 = Ad.objects.create(
            user=self.user,
            title='Ad 1',
            description='...',
            category='BOOKS',
            condition='NEW'
        )
        self.ad2 = Ad.objects.create(
            user=self.user,
            title='Ad 2',
            description='...',
            category='ELECTRONICS',
            condition='USED'
        )
        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Test comment'
        )

    def test_proposal_serializer(self):
        """Тест сериализации предложения"""
        serializer = ProposalSerializer(instance=self.proposal)
        data = serializer.data
        self.assertEqual(data['comment'], 'Test comment')
        self.assertEqual(data['ad_sender']['title'], 'Ad 1')
        self.assertEqual(data['status'], 'PENDING')

    def test_proposal_create_serializer(self):
        """Тест сериализатора создания предложения"""
        data = {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad2.id,
            'comment': 'New proposal'
        }
        serializer = ProposalCreateSerializer(
            data=data,
            context={'request': self.ad1}
        )
        self.assertTrue(serializer.is_valid())

        # Проверка сохранения
        proposal = serializer.save(ad_sender=self.ad1)
        self.assertEqual(proposal.comment, 'New proposal')
        self.assertEqual(proposal.ad_sender, self.ad1)

    def test_invalid_ad_receiver(self):
        """Тест несуществующего ad_receiver"""
        data = {
            'ad_receiver': 999,  # Несуществующий ID
            'comment': 'Test'
        }
        serializer = ProposalCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ad_receiver', serializer.errors)

    def test_self_exchange_validation(self):
        """Тест валидации попытки обмена с самим собой"""
        data = {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad1.id,
            'comment': 'Invalid'
        }
        serializer = ProposalCreateSerializer(
            data=data,
            context={'ad_sender': self.ad1}  # Передаем отправителя в контексте
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            "Нельзя предлагать обмен товара на самого себя"
        )
