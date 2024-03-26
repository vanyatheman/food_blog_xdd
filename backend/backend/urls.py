from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('api/', include('custom_users.urls')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    # path('api/', include('djoser.urls')),  # Работа с пользователями.
    # path('api/v1/', include('users.urls', namespace='users')),  # Работа с токенами.
]
