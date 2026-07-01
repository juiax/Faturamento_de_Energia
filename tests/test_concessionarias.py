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


def test_deve_criar_concessionaria(client):
    response = client.post(
        '/concessionarias/',
        json={
            'nome': 'energisa',
            'preco_por_kwh': '0.70000',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'energisa'
    assert response.json()['preco_por_kwh'] == '0.70000'


def test_nao_deve_criar_concessionaria_duplicada(client):
    client.post(
        '/concessionarias/',
        json={
            'nome': 'energisa',
            'preco_por_kwh': '0.70000',
        },
    )

    response = client.post(
        '/concessionarias/',
        json={
            'nome': 'energisa',
            'preco_por_kwh': '0.80000',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Concessionária já cadastrada'}


def test_deve_buscar_concessionaria_por_id(client):
    response = client.get('/concessionarias/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['nome'] == 'copel'


def test_deve_retornar_404_ao_buscar_concessionaria_inexistente(client):
    response = client.get('/concessionarias/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Concessionária não encontrada'}


def test_deve_atualizar_concessionaria(client):
    response = client.put(
        '/concessionarias/1',
        json={
            'nome': 'copel-atualizada',
            'preco_por_kwh': '0.75000',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['nome'] == 'copel-atualizada'
    assert response.json()['preco_por_kwh'] == '0.75000'


def test_deve_retornar_404_ao_atualizar_concessionaria_inexistente(client):
    response = client.put(
        '/concessionarias/999',
        json={
            'nome': 'inexistente',
            'preco_por_kwh': '0.75000',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Concessionária não encontrada'}


def test_nao_deve_atualizar_concessionaria_para_nome_duplicado(client):
    response = client.put(
        '/concessionarias/1',
        json={
            'nome': 'celesc',
            'preco_por_kwh': '0.75000',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Concessionária já cadastrada'}


def test_deve_retornar_404_ao_deletar_concessionaria_inexistente(client):
    response = client.delete('/concessionarias/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Concessionária não encontrada'}


def test_deve_deletar_concessionaria_sem_unidade_vinculada(client):
    concessionaria = client.post(
        '/concessionarias/',
        json={
            'nome': 'equatorial',
            'preco_por_kwh': '0.81000',
        },
    ).json()

    response = client.delete(f'/concessionarias/{concessionaria["id"]}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''