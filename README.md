# API de Faturamento de Energia

API REST desenvolvida em **Python** com **FastAPI** para gerenciamento de concessionárias, titulares, unidades consumidoras e cálculo de faturamento de energia elétrica.

O projeto foi desenvolvido com foco em boas práticas de arquitetura, organização de código, testes automatizados e conteinerização utilizando Docker.

---

# Tecnologias utilizadas

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Docker
- Docker Compose
- Pytest
- Ruff
- Uvicorn

---

# Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/juiax/Faturamento_de_Energia.git
```

```bash
cd Faturamento_de_Energia
```

### 2. Execute utilizando Docker

```bash
docker compose up --build
```

Após iniciar o container, a aplicação estará disponível em:

```
http://localhost:8000
```

---

# Como executar os testes

Execute:

```bash
docker compose run --rm api uv run pytest
```

---

# Como executar o Ruff

Verificar problemas de lint:

```bash
ruff check .
```

Formatar automaticamente:

```bash
ruff format .
```

---

# Como acessar a documentação

A documentação interativa da API é disponibilizada automaticamente pelo FastAPI.

Após iniciar a aplicação:

```
http://localhost:8000/docs
```

# Decisões técnicas

## Modelagem

A modelagem foi dividida em quatro entidades principais:

- **Concessionária**
- **Titular**
- **Unidade Consumidora**
- **Fatura**

Os relacionamentos foram definidos utilizando SQLAlchemy:

- Uma concessionária possui diversas unidades consumidoras;
- Um titular pode possuir diversas unidades consumidoras;
- Uma unidade consumidora possui diversas faturas.

Essa modelagem evita duplicidade de informações e facilita futuras expansões do sistema.

---

## Seed de concessionárias

Foi implementado um processo de seed executado na inicialização da aplicação.

Caso não existam registros, são inseridas automaticamente as concessionárias padrão:

- Copel
- Celesc

Essa estratégia garante que a API possua dados mínimos para funcionamento sem gerar registros duplicados.

---

## Cálculo de faturamento

O valor da fatura é calculado automaticamente no momento da criação.

O cálculo considera:

```
Valor Total = Consumo (kWh) × Preço do kWh da concessionária
```

O preço do kWh é obtido a partir da concessionária vinculada à unidade consumidora, garantindo que alterações futuras nas tarifas não afetem faturas já emitidas.

---

## Paginação

As listagens utilizam paginação através dos parâmetros:

- page
- per_page

As respostas retornam:

- página atual
- quantidade por página
- total de registros
- lista de itens

Essa estratégia reduz o volume de dados trafegados e melhora a escalabilidade da API.

---

## Decisões arquiteturais

O projeto foi organizado em camadas para separar responsabilidades:

- **models.py** → definição das tabelas do banco
- **schemas.py** → validação de entrada e saída (Pydantic)
- **routers/** → definição dos endpoints
- **database.py** → configuração da conexão com o banco
- **seed.py** → inserção de dados iniciais

Também foram adotadas boas práticas como:

- tratamento de exceções utilizando HTTPException;
- utilização de SQLAlchemy ORM;
- validação automática com Pydantic;
- testes automatizados utilizando Pytest;
- conteinerização utilizando Docker.

---

# Estrutura do projeto

```
app/
├── routers/
├── database.py
├── main.py
├── models.py
├── schemas.py
└── seed.py

tests/
├── conftest.py
├── test_concessionarias.py
├── test_faturas.py
├── test_titulares.py
└── test_unidades.py
```

# Funcionalidades

- Cadastro de titulares
- Cadastro de concessionárias
- Cadastro de unidades consumidoras
- Emissão de faturas
- Cálculo automático do valor da fatura
- Consulta paginada
- Atualização de registros
- Exclusão com validações de integridade
- Documentação automática com Swagger
- Testes automatizados
- Execução via Docker
