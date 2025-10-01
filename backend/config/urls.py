from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('people.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('scheduling.urls')),
    path('api/', include('financial.urls')),

    # API Documentation (drf-spectacular with OpenAPI 3.0)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
    path('', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-swagger-ui'),
]