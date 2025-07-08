from django.urls import path, include
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns = [
    path('', include('ads.urls')),  # Подключение URLs приложения ads
    path('admin/', admin.site.urls),

    # Генерация файла схемы
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Документация Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/', include('ads.urls')),  # Подключаем маршруты приложения ads
]

