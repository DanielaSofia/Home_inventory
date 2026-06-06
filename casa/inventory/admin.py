"""Registo de modelos no admin Django para o app inventory."""

from django.contrib import admin

from .models import Desejo, Divisao, Item

admin.site.register(Divisao)
admin.site.register(Item)
admin.site.register(Desejo)
