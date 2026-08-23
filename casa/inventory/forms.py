"""Forms Django para o app inventory.

Contém forms de modelo usados nas views para criar/editar objetos.
"""

from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError

from .models import Consumivel, Desejo, Divisao, Item


def parse_fractional_decimal(value):
    """Converte valores decimais ou frações simples em Decimal."""
    value = str(value).strip().replace(",", ".")
    if "/" not in value:
        return Decimal(value)

    numerator, *denominators = value.split("/")
    if len(denominators) != 1:
        raise InvalidOperation

    denominator = denominators[0].strip()
    if Decimal(denominator) == 0:
        raise InvalidOperation
    return Decimal(numerator.strip()) / Decimal(denominator)


class FractionalDecimalField(forms.DecimalField):
    """Campo decimal que também aceita frações, como ``1/2``."""

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            return parse_fractional_decimal(value)
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(self.error_messages["invalid"], code="invalid")


class ItemForm(forms.ModelForm):
    """Formulário de `Item` usado para criação/edição via interface."""

    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex.: Aspirador"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Detalhes opcionais"}
            ),
            "quantidade": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "inputmode": "numeric"}
            ),
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01", "placeholder": "0,00"}
            ),
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
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex.: Máquina de café"}
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Por que gostaria deste item?",
                }
            ),
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01", "placeholder": "0,00"}
            ),
            "divisao": forms.Select(attrs={"class": "form-control"}),
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ConsumivelForm(forms.ModelForm):
    """Formulário para cadastrar produtos consumíveis."""

    quantidade = FractionalDecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = Consumivel
        fields = ["nome", "quantidade", "divisao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "quantidade": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "Ex.: 0,5 ou 1/2",
                }
            ),
            "divisao": forms.Select(attrs={"class": "form-control"}),
        }
