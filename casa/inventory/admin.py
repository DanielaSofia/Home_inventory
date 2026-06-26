"""Registo de modelos no admin Django para o app inventory."""

from django.contrib import admin

from .models import Compra, Consumivel, Desejo, Divisao, HistoricoCompra, Item


@admin.register(Divisao)
class DivisaoAdmin(admin.ModelAdmin):
    """Admin para gerir divisões da casa."""
    
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin para gerir itens do inventário."""
    
    list_display = ['nome', 'divisao', 'quantidade', 'valor', 'data_aquisicao']
    list_filter = ['divisao', 'data_adicionado', 'data_aquisicao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_adicionado']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'divisao', 'quantidade')
        }),
        ('Valores', {
            'fields': ('valor', 'data_aquisicao')
        }),
        ('Imagem', {
            'fields': ('imagem',)
        }),
        ('Metadados', {
            'fields': ('data_adicionado',)
        }),
    )


@admin.register(Desejo)
class DesejoAdmin(admin.ModelAdmin):
    """Admin para gerir lista de desejos."""
    
    list_display = ['nome', 'divisao', 'quantidade', 'valor']
    list_filter = ['divisao']
    search_fields = ['nome', 'descricao']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'divisao', 'quantidade')
        }),
        ('Valores', {
            'fields': ('valor',)
        }),
        ('Imagem', {
            'fields': ('imagem',)
        }),
    )


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    """Admin para gerir lista de compras."""
    
    list_display = ['nome', 'quantidade', 'comprado', 'divisao']
    list_filter = ['comprado', 'divisao']
    search_fields = ['nome']
    readonly_fields = ['consumivel']
    
    fieldsets = (
        ('Informações da Compra', {
            'fields': ('nome', 'quantidade', 'comprado', 'divisao')
        }),
        ('Relação com Consumível', {
            'fields': ('consumivel',)
        }),
    )


@admin.register(Consumivel)
class ConsumvelAdmin(admin.ModelAdmin):
    """Admin para gerir consumíveis (despensa)."""
    
    list_display = ['nome', 'divisao', 'quantidade', 'quantidade_minima', 'preco', 'loja']
    list_filter = ['divisao']
    search_fields = ['nome', 'loja']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'divisao', 'loja')
        }),
        ('Quantidades', {
            'fields': ('quantidade', 'quantidade_minima')
        }),
        ('Preço', {
            'fields': ('preco',)
        }),
    )


@admin.register(HistoricoCompra)
class HistoricoCompraAdmin(admin.ModelAdmin):
    """Admin para visualizar histórico de compras de consumíveis."""
    
    list_display = ['consumivel', 'quantidade', 'preco', 'loja', 'data']
    list_filter = ['data', 'loja']
    search_fields = ['consumivel__nome', 'loja']
    readonly_fields = ['data', 'consumivel']
    date_hierarchy = 'data'
