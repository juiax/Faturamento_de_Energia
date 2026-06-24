from decimal import Decimal
from http import HTTPStatus


def test_deve_criar_concessionarias_padrao(client):
    response = client.get('/concessionarias/')

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    nomes = [item['nome'] for item in data['items']]

    assert 'copel' in nomes
    assert 'celesc' in nomes

    copel = next(item for item in data['items'] if item['nome'] == 'copel')
    celesc = next(item for item in data['items'] if item['nome'] == 'celesc')

    assert Decimal(copel['preco_por_kwh']) == Decimal('0.64242')
    assert Decimal(celesc['preco_por_kwh']) == Decimal('0.69568')
