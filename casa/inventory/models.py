"""Modelos do app inventory.

Define os modelos `Divisao`, `Item` e `Desejo` utilizados pela aplicação.
"""

from django.db import models


class Divisao(models.Model):
    """Representa uma divisão/compartimento da casa (ex.: cozinha, sala)."""

    nome = models.CharField(max_length=255)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Item(models.Model):
    """Item físico registado na casa, com quantidade e valor."""

    divisao = models.ForeignKey(Divisao, on_delete=models.CASCADE, related_name="itens")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.IntegerField(default=1)
    imagem = models.ImageField(upload_to="itens/", blank=True, null=True)
    data_adicionado = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_aquisicao = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["nome", "id"]

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"


class Consumivel(models.Model):
    """Produto consumível identificado por nome, quantidade e divisão."""

    nome = models.CharField(max_length=100)
    quantidade = models.IntegerField(default=1)
    quantidade_compra = models.IntegerField(default=1)
    comprado = models.BooleanField(default=False)
    divisao = models.ForeignKey(Divisao, on_delete=models.CASCADE, related_name="consumiveis")

    class Meta:
        ordering = ["nome", "id"]

    def __str__(self):
        return self.nome


class Desejo(models.Model):
    """Representa um item desejado (wishlist) que ainda não foi comprado."""

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagem = models.ImageField(upload_to="desejos/", blank=True, null=True)
    divisao = models.ForeignKey(Divisao, on_delete=models.SET_NULL, null=True)
    quantidade = models.IntegerField(default=1)

    class Meta:
        ordering = ["nome", "id"]

    def __str__(self):
        return self.nome
