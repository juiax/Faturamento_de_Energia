from decimal import Decimal
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


def test_criar_fatura_calculando_valor(client):
    unidade = criar_unidade(client)

    response = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()

    assert data['unidade_consumidora_id'] == unidade['id']
    assert data['consumo_total_kwh'] == '150.00'
    assert Decimal(data['preco_por_kwh_aplicado']) == Decimal('0.64242')
    assert Decimal(data['valor_total']) == Decimal('96.36')


def test_nao_deve_permitir_duas_faturas_no_mesmo_mes(client):
    unidade = criar_unidade(client)

    client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    response = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-15',
            'consumo_total_kwh': 200,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Já existe fatura para esta unidade neste mês'
    }


def test_nao_deve_permitir_consumo_menor_ou_igual_a_zero(client):
    unidade = criar_unidade(client)

    response = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 0,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_deve_retornar_historico_de_faturamento(client):
    unidade = criar_unidade(client)

    client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    response = client.get(f'/unidades/{unidade["id"]}/faturas')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['page'] == 1
    assert response.json()['per_page'] == 10
    assert response.json()['total'] == 1
    assert len(response.json()['items']) == 1


def test_deve_paginar_historico_de_faturamento(client):
    unidade = criar_unidade(client)

    datas = [
        '2026-01-01',
        '2026-02-01',
        '2026-03-01',
        '2026-04-01',
        '2026-05-01',
        '2026-06-01',
        '2026-07-01',
        '2026-08-01',
        '2026-09-01',
        '2026-10-01',
        '2026-11-01',
        '2026-12-01',
        '2027-01-01',
        '2027-02-01',
        '2027-03-01',
    ]

    for data_referencia in datas:
        client.post(
            '/faturas/',
            json={
                'unidade_consumidora_id': unidade['id'],
                'data_referencia': data_referencia,
                'consumo_total_kwh': 100,
            },
        )

    response = client.get(
        f'/unidades/{unidade["id"]}/faturas?page=2&per_page=10'
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['page'] == 2
    assert response.json()['per_page'] == 10
    assert response.json()['total'] == 15
    assert len(response.json()['items']) == 5

def test_nao_deve_criar_fatura_para_unidade_inexistente(client):
    response = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': 999,
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade consumidora não encontrada'}


def test_deve_listar_faturas(client):
    unidade = criar_unidade(client)

    client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    response = client.get('/faturas/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['total'] == 1
    assert len(response.json()['items']) == 1


def test_deve_buscar_fatura_por_id(client):
    unidade = criar_unidade(client)

    fatura = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    ).json()

    response = client.get(f'/faturas/{fatura["id"]}')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == fatura['id']


def test_deve_retornar_404_ao_buscar_fatura_inexistente(client):
    response = client.get('/faturas/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Fatura não encontrada'}


def test_deve_atualizar_fatura(client):
    unidade = criar_unidade(client)

    fatura = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    ).json()

    response = client.put(
        f'/faturas/{fatura["id"]}',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-02-01',
            'consumo_total_kwh': 200,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data_referencia'] == '2026-02-01'
    assert response.json()['consumo_total_kwh'] == '200.00'
    assert response.json()['valor_total'] == '128.48'


def test_deve_retornar_404_ao_atualizar_fatura_inexistente(client):
    unidade = criar_unidade(client)

    response = client.put(
        '/faturas/999',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Fatura não encontrada'}


def test_nao_deve_atualizar_fatura_para_unidade_inexistente(client):
    unidade = criar_unidade(client)

    fatura = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    ).json()

    response = client.put(
        f'/faturas/{fatura["id"]}',
        json={
            'unidade_consumidora_id': 999,
            'data_referencia': '2026-02-01',
            'consumo_total_kwh': 200,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Unidade consumidora não encontrada'}


def test_nao_deve_atualizar_fatura_para_mes_duplicado(client):
    unidade = criar_unidade(client)

    primeira_fatura = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    ).json()

    client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-02-01',
            'consumo_total_kwh': 200,
        },
    )

    response = client.put(
        f'/faturas/{primeira_fatura["id"]}',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-02-15',
            'consumo_total_kwh': 300,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Já existe fatura para esta unidade neste mês'
    }


def test_deve_deletar_fatura(client):
    unidade = criar_unidade(client)

    fatura = client.post(
        '/faturas/',
        json={
            'unidade_consumidora_id': unidade['id'],
            'data_referencia': '2026-01-01',
            'consumo_total_kwh': 150,
        },
    ).json()

    response = client.delete(f'/faturas/{fatura["id"]}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


def test_deve_retornar_404_ao_deletar_fatura_inexistente(client):
    response = client.delete('/faturas/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Fatura não encontrada'}