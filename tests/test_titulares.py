from http import HTTPStatus


def test_criar_titular(client):
    response = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'nome': 'Jullia Vitoria',
        'cpf': '12345678910',
    }


def test_cpf_duplicado(client):
    client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )

    response = client.post(
        '/titulares/',
        json={
            'nome': 'Outro Nome',
            'cpf': '12345678910',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'CPF já cadastrado'}


def test_cpf_invalido(client):
    response = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '123',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_listar_titulares(client):
    client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )

    response = client.get('/titulares/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['total'] == 1
    assert response.json()['items'][0]['nome'] == 'Jullia Vitoria'
