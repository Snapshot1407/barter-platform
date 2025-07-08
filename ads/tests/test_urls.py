from django.urls import reverse, resolve
from django.test import TestCase
from ..views import AdViewSet, ProposalViewSet

class UrlsTests(TestCase):
    def test_ad_list_url(self):
        url = reverse('ad-list')
        self.assertEqual(url, '/api/ads/')
        self.assertEqual(resolve(url).func.cls, AdViewSet)

    def test_ad_detail_url(self):
        url = reverse('ad-detail', args=[1])
        self.assertEqual(url, '/api/ads/1/')
        self.assertEqual(resolve(url).func.cls, AdViewSet)

    def test_search_url(self):
        url = reverse('ad-search')
        self.assertEqual(url, '/api/ads/search/')
        view = resolve(url).func
        self.assertTrue(hasattr(view, 'cls') and view.cls == AdViewSet)

    def test_proposal_status_url(self):
        url = reverse('proposal-update-status', args=[1])
        self.assertEqual(url, '/api/proposals/1/status/')
        view = resolve(url).func
        self.assertTrue(hasattr(view, 'cls') and view.cls == ProposalViewSet)