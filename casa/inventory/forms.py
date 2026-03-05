from django import forms
from .models import Item, Divisao

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['divisao', 'nome', 'descricao', 'quantidade', 'valor_estimado', 'imagem', 'is_desejo']

class DivisaoForm(forms.ModelForm):
    class Meta:
        model = Divisao
        fields = ['nome']
