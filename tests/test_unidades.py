from http import HTTPStatus


def criar_titular(client):
    response = client.post(
        '/titulares/',
        json={
            'nome': 'Maria Silva',
            'cpf': '12345678901',
        },
    )

    return response.json()


def test_criar_unidade(client):
    titular = criar_titular(client)

    response = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'codigo': 'UC-0001',
        'titular_id': titular['id'],
        'concessionaria_id': 1,
    }


def test_codigo_duplicado(client):
    titular = criar_titular(client)

    client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    response = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Unidade já cadastrada'}


def test_nao_criar_unidade_para_titular_inexistente(client):
    response = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': 999,
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Titular não encontrado'}
