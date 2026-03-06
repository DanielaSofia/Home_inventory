from django.db import models


class Divisao(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Item(models.Model):
    divisao = models.ForeignKey(Divisao, on_delete=models.CASCADE, related_name="itens")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.IntegerField(default=1)
    imagem = models.ImageField(upload_to="itens/", blank=True, null=True)
    data_adicionado = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_aquisicao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"


class Desejo(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagem = models.ImageField(upload_to="desejos/", blank=True, null=True)
    divisao = models.ForeignKey(Divisao, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nome
