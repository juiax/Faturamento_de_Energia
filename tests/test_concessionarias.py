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


def test_nao_deve_deletar_concessionaria_com_unidade_vinculada(client):
    titular = client.post(
        '/titulares/',
        json={'nome': 'Maria Silva', 'cpf': '12345678901'},
    ).json()

    client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    response = client.delete('/concessionarias/1')

    assert response.status_code == HTTPStatus.CONFLICT