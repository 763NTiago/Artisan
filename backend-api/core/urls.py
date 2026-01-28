from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Criação automática de rotas para os ViewSets
router = DefaultRouter()
router.register(r'usuarios', UserViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'materiais', MaterialViewSet)
router.register(r'arquitetos', ArquitetoViewSet)
router.register(r'agenda', AgendaViewSet)
router.register(r'orcamentos', OrcamentoViewSet)
router.register(r'recebimentos', RecebimentoViewSet)
router.register(r'parcelas', ParcelaViewSet)
router.register(r'comissoes', ComissaoViewSet)

urlpatterns = [
    # Inclui as rotas padrão (ex: /api/clientes/)
    path('', include(router.urls)),
    
    # Rotas específicas
    path('login/', LoginView.as_view()),
    path('dashboard/financeiro/', DashboardFinanceiroView.as_view()),
    path('dashboard/projetos/', DashboardProjetosView.as_view()),
    path('dashboard/eventos/', DashboardEventosView.as_view()),
    path('relatorios/completo/', RelatorioCompletoView.as_view()),
]