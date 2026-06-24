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
