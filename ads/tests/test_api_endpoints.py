from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class EndpointAvailabilityTests(APITestCase):
    def test_ad_list_available(self):
        url = reverse('ad-list')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_search_endpoint_available(self):
        url = reverse('ad-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_proposal_status_endpoint_requires_auth(self):
        url = reverse('proposal-update-status', args=[1])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)