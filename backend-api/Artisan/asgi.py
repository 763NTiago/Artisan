"""
Configuração ASGI para o projeto Artisan.

Expõe a chamada ASGI como uma variável de nível de módulo chamada ``application``.
Documentação: https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Aponta para o módulo de configurações do 'artisan'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artisan.settings')

application = get_asgi_application()