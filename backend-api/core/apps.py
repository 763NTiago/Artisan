from django.apps import AppConfig

class CoreConfig(AppConfig):
    """
    Configuração principal do aplicativo 'core'.
    Define o tipo de chave primária padrão para os modelos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Gestão Artisan'  # Nome bonito para aparecer no Admin