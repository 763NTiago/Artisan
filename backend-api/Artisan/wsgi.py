"""
Configuração WSGI para o projeto Artisan.

Expõe a chamada WSGI como uma variável de nível de módulo chamada ``application``.
Documentação: https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Define o arquivo de configurações padrão para produção
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artisan.settings')

application = get_wsgi_application()