"""Forms Django para o app inventory.

Contém forms de modelo usados nas views para criar/editar objetos.
"""

from django import forms

from .models import Compra, Desejo, Divisao, Item


class ItemForm(forms.ModelForm):
    """Formulário de `Item` usado para criação/edição via interface."""

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
    """Formulário para criar/editar uma `Divisao`."""

    class Meta:
        model = Divisao
        fields = ["nome"]


class DesejoForm(forms.ModelForm):
    """Formulário para o modelo `Desejo`."""

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
    """Formulário para gerir `Compra` (lista de compras)."""

    class Meta:
        model = Compra
        fields = ["nome", "quantidade", "comprado", "divisao"]
