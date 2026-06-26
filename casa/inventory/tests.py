"""Testes para o app inventory."""

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from casa.inventory.models import Compra, Consumivel, Desejo, Divisao, Item


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
        assert len(response.data) == 1

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
        assert len(response.data) == 1


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
class TestConsumvelViewSet:
    """Testes para o ViewSet de Consumíveis."""

    def test_list_consumiveis(self, api_client):
        """Testa listagem de consumíveis."""
        response = api_client.get('/api/consumiveis/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_consumivel(self, api_client, divisao):
        """Testa criação de um consumível."""
        data = {
            'nome': 'Sal',
            'quantidade': 1,
            'quantidade_minima': 2,
            'divisao': divisao.id,
            'preco': 1.50,
            'loja': 'Carrefour'
        }
        response = api_client.post('/api/consumiveis/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_consumir_action(self, api_client, divisao):
        """Testa ação de consumir um item."""
        consumivel = Consumivel.objects.create(
            nome='Açúcar',
            quantidade=5,
            divisao=divisao
        )
        response = api_client.post(f'/api/consumiveis/{consumivel.id}/consumir/')
        assert response.status_code == status.HTTP_200_OK
        consumivel.refresh_from_db()
        assert consumivel.quantidade == 4
