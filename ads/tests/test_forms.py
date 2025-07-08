from django.test import TestCase
from django.contrib.auth.models import User
from ..forms import AdForm, ProposalForm
from ..models import Ad

class AdFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.valid_data = {
            'title': 'Test Ad',
            'description': 'Test description',
            'category': 'BOOKS',
            'condition': 'NEW',
            'image_url': 'http://example.com/image.jpg'
        }

    def test_valid_form(self):
        """Тест валидной формы"""
        form = AdForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_missing_title(self):
        """Тест отсутствия обязательного поля title"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        form = AdForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_category(self):
        """Тест неверной категории"""
        invalid_data = self.valid_data.copy()
        invalid_data['category'] = 'INVALID_CATEGORY'
        form = AdForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

class ProposalFormTest(TestCase):
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

    def test_valid_proposal_form(self):
        """Тест валидной формы предложения"""
        form = ProposalForm(data={
            'ad_receiver': self.ad2.id,
            'comment': 'Want to exchange!'
        })
        self.assertTrue(form.is_valid())

    def test_empty_comment(self):
        """Тест формы с пустым комментарием"""
        form = ProposalForm(data={
            'ad_receiver': self.ad2.id,
            'comment': ''
        })
        self.assertTrue(form.is_valid())  # Комментарий не обязателен