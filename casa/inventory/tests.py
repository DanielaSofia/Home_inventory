"""Testes para o app inventory."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from casa.inventory.models import Consumivel, Desejo, Divisao, Item

@pytest.fixture
def user(db):
    """Cria um usuário de teste."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def api_client(user):
    """Cria um cliente API autenticado."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def divisao(db):
    """Cria uma divisão de teste."""
    return Divisao.objects.create(nome='Cozinha')


@pytest.fixture
def item(db, divisao):
    """Cria um item de teste."""
    return Item.objects.create(
        nome='Arroz',
        divisao=divisao,
        quantidade=2,
        valor=5.00
    )


@pytest.mark.django_db
class TestDivisaoViewSet:
    """Testes para o ViewSet de Divisões."""

    def test_list_divisoes(self, api_client):
        """Testa listagem de divisões."""
        response = api_client.get('/api/divisoes/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_divisao(self, api_client):
        """Testa criação de uma divisão."""
        data = {'nome': 'Sala'}
        response = api_client.post('/api/divisoes/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == 'Sala'

    def test_unauthenticated_access(self):
        """Testa que acesso não autenticado é bloqueado."""
        client = APIClient()
        response = client.get('/api/divisoes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestItemViewSet:
    """Testes para o ViewSet de Itens."""

    def test_list_itens(self, api_client, item):
        """Testa listagem de itens."""
        response = api_client.get('/api/itens/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_create_item(self, api_client, divisao):
        """Testa criação de um item."""
        data = {
            'nome': 'Feijão',
            'divisao': divisao.id,
            'quantidade': 1,
            'valor': 3.00
        }
        response = api_client.post('/api/itens/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_total_valor(self, api_client, item):
        """Testa cálculo do valor total dos itens."""
        response = api_client.get('/api/itens/total_valor/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_valor_casa' in response.data

    def test_filter_by_divisao(self, api_client, item):
        """Testa filtro de itens por divisão."""
        response = api_client.get(f'/api/itens/?divisao={item.divisao.id}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestDesejoViewSet:
    """Testes para o ViewSet de Desejos."""

    def test_list_desejos(self, api_client):
        """Testa listagem de desejos."""
        response = api_client.get('/api/desejos/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_desejo(self, api_client, divisao):
        """Testa criação de um desejo."""
        data = {
            'nome': 'Livro',
            'divisao': divisao.id,
            'quantidade': 1,
            'valor': 15.00
        }
        response = api_client.post('/api/desejos/', data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestDespensaView:
    """Testes da página de consumíveis comprados."""

    @pytest.mark.parametrize("path", ["/itens/", "/desejos/", "/lista-compras/"])
    def test_filter_by_divisao_renders_selected_option(self, client, divisao, path):
        """Renderiza filtros de divisão sem erros de sintaxe nos templates."""
        Consumivel.objects.create(
            nome="Arroz",
            divisao=divisao,
            comprado=True,
        )

        response = client.get(path, {"divisao": divisao.id})

        assert response.status_code == status.HTTP_200_OK
        assert f'<option value="{divisao.id}" selected>' in response.content.decode()


@pytest.mark.django_db
class TestConsumivelQuantities:
    """Testes para quantidades fracionárias de consumíveis."""

    @pytest.mark.parametrize("quantidade", ["0.5", "1/2"])
    def test_creates_consumivel_with_fractional_quantity(self, client, divisao, quantidade):
        """Aceita valores decimais e frações na criação de um consumível."""
        response = client.post(
            "/lista-compras/",
            {"nome": "Pizza", "quantidade": quantidade, "divisao": divisao.id},
        )

        consumivel = Consumivel.objects.get(nome="Pizza")
        assert response.status_code == status.HTTP_302_FOUND
        assert consumivel.quantidade == Decimal("0.50")

    def test_adds_fractional_purchase_quantity_to_stock(self, client, divisao):
        """Soma uma quantidade fracionária ao marcar uma compra."""
        consumivel = Consumivel.objects.create(
            nome="Pizza",
            quantidade=Decimal("1.00"),
            divisao=divisao,
        )

        response = client.post(
            f"/marcar-consumivel-comprado/{consumivel.id}/",
            {"comprado": "on", "quantidade_compra": "1/2"},
        )

        consumivel.refresh_from_db()
        assert response.status_code == status.HTTP_302_FOUND
        assert consumivel.quantidade_compra == Decimal("0.50")
        assert consumivel.quantidade == Decimal("1.50")


@pytest.mark.django_db
class TestShoppingListSuggestions:
    def test_reuses_pantry_item_when_adding_it_to_shopping_list(self, client, divisao):
        consumivel = Consumivel.objects.create(
            nome="Arroz",
            quantidade=Decimal("3.00"),
            quantidade_compra=Decimal("1.00"),
            comprado=True,
            divisao=divisao,
        )

        response = client.post(
            "/adicionar-compra/",
            {"nome": "arroz", "quantidade": "2", "divisao": divisao.id},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert Consumivel.objects.filter(nome__iexact="arroz", divisao=divisao).count() == 1
        consumivel.refresh_from_db()
        assert consumivel.na_lista_compras is True
        assert consumivel.comprado is True
        assert consumivel.quantidade == Decimal("3.00")
        assert consumivel.quantidade_compra == Decimal("2.00")
