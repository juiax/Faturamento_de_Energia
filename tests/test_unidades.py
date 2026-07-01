from http import HTTPStatus


def criar_titular(client):
    response = client.post(
        '/titulares/',
        json={
            'nome': 'Jullia Vitoria',
            'cpf': '12345678910',
        },
    )
    return response.json()


def criar_unidade(client):
    titular = criar_titular(client)

    response = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    return response.json()


def test_deve_criar_unidade(client):
    unidade = criar_unidade(client)

    assert unidade == {
        'id': 1,
        'codigo': 'UC-0001',
        'titular_id': 1,
        'concessionaria_id': 1,
    }


def test_nao_deve_criar_unidade_com_codigo_duplicado(client):
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


def test_nao_deve_criar_unidade_para_titular_inexistente(client):
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


def test_deve_listar_unidades(client):
    criar_unidade(client)

    response = client.get('/unidades/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['page'] == 1
    assert response.json()['per_page'] == 10
    assert response.json()['total'] == 1
    assert response.json()['items'][0]['codigo'] == 'UC-0001'


def test_deve_buscar_unidade_por_id(client):
    unidade = criar_unidade(client)

    response = client.get(f'/unidades/{unidade["id"]}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == unidade


def test_deve_retornar_404_ao_buscar_unidade_inexistente(client):
    response = client.get('/unidades/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade não encontrada'}


def test_deve_retornar_404_ao_criar_unidade_com_concessionaria_inexistente(
    client,
):
    titular = criar_titular(client)

    response = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 999,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Concessionária não encontrada'}


def test_deve_atualizar_unidade(client):
    unidade = criar_unidade(client)

    response = client.put(
        f'/unidades/{unidade["id"]}',
        json={
            'codigo': 'UC-0002',
            'titular_id': unidade['titular_id'],
            'concessionaria_id': 2,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['codigo'] == 'UC-0002'
    assert response.json()['concessionaria_id'] == 2


def test_deve_retornar_404_ao_atualizar_unidade_inexistente(client):
    titular = criar_titular(client)

    response = client.put(
        '/unidades/999',
        json={
            'codigo': 'UC-0002',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade não encontrada'}


def test_deve_retornar_404_ao_atualizar_unidade_com_titular_inexistente(
    client,
):
    unidade = criar_unidade(client)

    response = client.put(
        f'/unidades/{unidade["id"]}',
        json={
            'codigo': 'UC-0002',
            'titular_id': 999,
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Titular não encontrado'}


def test_deve_retornar_404_ao_atualizar_unidade_com_concessionaria_inexistente(
    client,
):
    unidade = criar_unidade(client)

    response = client.put(
        f'/unidades/{unidade["id"]}',
        json={
            'codigo': 'UC-0002',
            'titular_id': unidade['titular_id'],
            'concessionaria_id': 999,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Concessionária não encontrada'}


def test_nao_deve_atualizar_unidade_para_codigo_duplicado(client):
    titular = criar_titular(client)

    client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    unidade = client.post(
        '/unidades/',
        json={
            'codigo': 'UC-0002',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    ).json()

    response = client.put(
        f'/unidades/{unidade["id"]}',
        json={
            'codigo': 'UC-0001',
            'titular_id': titular['id'],
            'concessionaria_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Unidade já cadastrada'}


def test_deve_deletar_unidade(client):
    unidade = criar_unidade(client)

    response = client.delete(f'/unidades/{unidade["id"]}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


def test_deve_retornar_404_ao_deletar_unidade_inexistente(client):
    response = client.delete('/unidades/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade não encontrada'}


def test_nao_deve_deletar_unidade_com_fatura_vinculada(client):
    unidade = criar_unidade(client)

    client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    response = client.delete(f'/unidades/{unidade["id"]}')

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': (
            'Não é possível deletar a unidade, '
            'pois existem faturas associadas a ela'
        )
    }


def test_deve_retornar_404_ao_buscar_historico_de_unidade_inexistente(client):
    response = client.get('/unidades/999/faturas')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade não encontrada'}
