from pathlib import Path
import os

# ==============================================================================
# CONFIGURAÇÕES GERAIS DO PROJETO ARTISAN
# ==============================================================================

# Constrói caminhos dentro do projeto. Ex: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURANÇA: Mantenha a chave secreta em segredo usada em produção!
# Em um ambiente real, usamos variáveis de ambiente para esconder isso.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-artisan-dev-key-changeme')

# SEGURANÇA: Não execute com debug ligado em produção.
# True mostra erros detalhados (bom para dev), False esconde (seguro para prod).
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # Para desenvolvimento, aceita tudo. Em produção, liste seu domínio.


# ==============================================================================
# APLICAÇÕES INSTALADAS
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bibliotecas de Terceiros
    'rest_framework',  # Ferramenta para criar a API
    'corsheaders',     # Permite acesso de outros locais (Mobile/Desktop)

    # Apps do Projeto
    'core',            # Onde está a lógica de negócio do Artisan
]


# ==============================================================================
# MIDDLEWARE (Segurança e Processamento de Requisições)
# ==============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',            # Deve ser o primeiro para tratar conexões externas
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Serve arquivos estáticos de forma otimizada
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração de rotas principais
ROOT_URLCONF = 'artisan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'artisan.wsgi.application'


# ==============================================================================
# BANCO DE DADOS
# ==============================================================================
# Por padrão usamos SQLite para desenvolvimento local pela simplicidade.
# Para produção, o código abaixo suporta PostgreSQL via variáveis de ambiente.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==============================================================================
# INTERNACIONALIZAÇÃO
# ==============================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# ARQUIVOS ESTÁTICOS (CSS, JavaScript, Imagens)
# ==============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuração de armazenamento para produção com WhiteNoise
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Tipo de campo padrão para chaves primárias (IDs)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# CONFIGURAÇÕES EXTRAS (CORS e REST FRAMEWORK)
# ==============================================================================

# Permite que qualquer origem acesse a API (Cuidado: usar apenas em Dev ou APIs públicas)
CORS_ALLOW_ALL_ORIGINS = True