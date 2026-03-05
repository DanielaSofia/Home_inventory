from django import forms
from .models import Item, Divisao, Desejo

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['divisao', 'nome', 'descricao', 'quantidade', 'valor_estimado', 'imagem']

class DivisaoForm(forms.ModelForm):
    class Meta:
        model = Divisao
        fields = ['nome']

class DesejoForm(forms.ModelForm):
    class Meta:
        model = Desejo
        fields = ["nome", "descricao", "valor_estimado", "divisao", "imagem"]