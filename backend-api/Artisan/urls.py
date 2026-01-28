from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Prefixo 'api/' garante organização (ex: site.com/api/clientes)
    path('api/', include('core.urls')), 
]