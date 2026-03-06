from django import forms
from .models import Item, Divisao, Desejo


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["divisao", "nome", "descricao", "quantidade", "valor", "data_aquisicao", "imagem"]
        widgets = {"data_aquisicao": forms.DateInput(attrs={"type": "date"})}


class DivisaoForm(forms.ModelForm):
    class Meta:
        model = Divisao
        fields = ["nome"]


class DesejoForm(forms.ModelForm):
    class Meta:
        model = Desejo
        fields = ["nome", "descricao", "valor", "divisao", "imagem"]
