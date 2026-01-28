from django.contrib import admin
from .models import (
    Cliente, Material, Arquiteto, Agenda, 
    Orcamento, Recebimento, Parcela, Comissao
)

# Configuração do cabeçalho do painel administrativo
admin.site.site_header = "Administração Artisan"
admin.site.site_title = "Portal Artisan"
admin.site.index_title = "Bem-vindo ao Sistema de Gestão"

# Registro dos modelos para aparecerem no painel
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')

@admin.register(Arquiteto)
class ArquitetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'porcentagem_padrao')

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'cliente', 'data_inicio', 'data_previsao_termino')
    list_filter = ('data_inicio', 'data_previsao_termino')

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nome', 'valor_total_final', 'data_criacao')
    search_fields = ('cliente_nome', 'cliente_cpf')

@admin.register(Recebimento)
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'valor_total', 'tipo_pagamento')
    list_filter = ('tipo_pagamento',)

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('recebimento', 'num_parcela', 'valor_parcela', 'data_vencimento', 'valor_recebido')
    list_filter = ('data_vencimento', 'data_recebimento')

@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    list_display = ('beneficiario', 'valor', 'data', 'porcentagem')
    list_filter = ('data',)