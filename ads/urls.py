from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, ProposalViewSet

router = DefaultRouter()
router.register(r'ads', AdViewSet)  # Эндпоинт: /api/ads/
router.register(r'proposals', ProposalViewSet, basename='proposal')  # Эндпоинт: /api/proposals/

urlpatterns = [
    path('', include(router.urls)),

    # кастомные маршруты
    path('ads/search/', AdViewSet.as_view({'get': 'search'}), name='ad-search'),
    path(
        'proposals/<int:pk>/status/',
        ProposalViewSet.as_view({'patch': 'update_status'}),
        name='proposal-update-status'
    ),
]