from django import forms
from .models import Item, Divisao, Desejo, Compra


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "divisao": forms.Select(attrs={"class": "form-control"}),
            "data_aquisicao": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class DivisaoForm(forms.ModelForm):
    class Meta:
        model = Divisao
        fields = ["nome"]


class DesejoForm(forms.ModelForm):
    class Meta:
        model = Desejo
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "divisao": forms.Select(attrs={"class": "form-control"}),
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ["nome", "quantidade", "comprado", "divisao"]
