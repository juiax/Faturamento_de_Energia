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


def test_deve_listar_titulares(client):
    client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )

    response = client.get('/titulares/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['page'] == 1
    assert response.json()['per_page'] == 10
    assert response.json()['total'] == 1
    assert response.json()['items'][0]['nome'] == 'Jullia Vitoria'


def test_deve_buscar_titular_por_id(client):
    titular = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    ).json()

    response = client.get(f'/titulares/{titular["id"]}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == titular


def test_deve_retornar_404_ao_buscar_titular_inexistente(client):
    response = client.get('/titulares/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Titular não encontrado'}


def test_deve_atualizar_titular(client):
    titular = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    ).json()

    response = client.put(
        f'/titulares/{titular["id"]}',
        json={
            'nome': 'Maria Silva',
            'cpf': '12345678901',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': titular['id'],
        'nome': 'Maria Silva',
        'cpf': '12345678901',
    }


def test_deve_retornar_404_ao_atualizar_titular_inexistente(client):
    response = client.put(
        '/titulares/999',
        json={
            'nome': 'Maria Silva',
            'cpf': '12345678901',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Titular não encontrado'}


def test_nao_deve_atualizar_titular_para_cpf_duplicado(client):
    client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )

    titular = client.post(
        '/titulares/',
        json={
            'nome': 'Maria Silva',
            'cpf': '12345678901',
        },
    ).json()

    response = client.put(
        f'/titulares/{titular["id"]}',
        json={
            'nome': 'Maria Silva Atualizada',
            'cpf': '12345678910',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'CPF já cadastrado'}


def test_deve_deletar_titular(client):
    titular = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    ).json()

    response = client.delete(f'/titulares/{titular["id"]}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


def test_deve_retornar_404_ao_deletar_titular_inexistente(client):
    response = client.delete('/titulares/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Titular não encontrado'}