"""Registo de modelos no admin Django para o app inventory."""

from django.contrib import admin

from .models import Desejo, Divisao, Item

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
