Claro. Como a API atual já possui o CRUD completo de Services, eu documentaria o docs/api.md refletindo somente o que está implementado hoje, deixando JWT, agendamento público e demais endpoints como evolução futura.

Crie o arquivo:

docs/api.md

com este conteúdo:

# API

## 1. Visão geral

A API do **TechLegacy Agendamento** é construída utilizando Flask e segue inicialmente uma abordagem REST.

A API é responsável por expor operações relacionadas aos recursos do sistema e servir como camada de comunicação entre clientes e as regras de negócio da aplicação.

Atualmente, o primeiro domínio disponibilizado através da API é o gerenciamento de **Services**.

---

# 2. Tecnologias

A API utiliza:

- Python 3.11
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-Migrate
- Pytest
- Docker

---

# 3. Base URL

Durante o desenvolvimento local, a aplicação é executada em:

```text
http://localhost:5000

Portanto, os endpoints podem ser acessados através de:

http://localhost:5000/services
4. Health Check

O endpoint de health check permite verificar se a aplicação Flask está funcionando corretamente.

Endpoint
GET /health
Resposta
{
  "status": "ok",
  "message": "TechLegacy Agendamento API is running"
}
Status HTTP
200 OK
5. Services

O recurso Services representa os serviços oferecidos por um estabelecimento.

Cada serviço possui informações como:

Nome;
Descrição;
Duração;
Preço;
Status;
Estabelecimento ao qual pertence.

A rota base é:

/services
6. Modelo de Service

Um Service possui atualmente a seguinte estrutura:

Campo	Tipo	Obrigatório	Descrição
id	integer	Sim	Identificador do serviço
establishment_id	integer	Sim	Estabelecimento proprietário
name	string	Sim	Nome do serviço
description	string	Não	Descrição do serviço
duration_minutes	integer	Sim	Duração em minutos
price	decimal	Sim	Preço do serviço
active	boolean	Sim	Indica se o serviço está ativo

Exemplo:

{
  "id": 1,
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.00,
  "active": true
}
7. Criar Service

Cria um novo serviço para um estabelecimento.

Endpoint
POST /services
Body
{
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.00
}
Campos
establishment_id

Identifica o estabelecimento ao qual o serviço pertence.

Tipo:

integer

Obrigatório:

Sim
name

Nome do serviço.

Tipo:

string

Obrigatório:

Sim
description

Descrição opcional do serviço.

Tipo:

string

Obrigatório:

Não
duration_minutes

Duração do serviço em minutos.

Tipo:

integer

Obrigatório:

Sim
price

Preço do serviço.

Tipo:

number

Obrigatório:

Sim
Resposta
{
  "id": 1,
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.0,
  "active": true
}
Status HTTP
201 Created
8. Listar Services

Retorna os serviços ativos de um estabelecimento.

Endpoint
GET /services?establishment_id=1
Parâmetro
establishment_id

Identifica o estabelecimento.

Tipo:

integer

Obrigatório:

Sim
Exemplo de resposta
[
  {
    "id": 1,
    "establishment_id": 1,
    "name": "Corte de cabelo",
    "description": "Corte masculino tradicional",
    "duration_minutes": 30,
    "price": 45.0,
    "active": true
  },
  {
    "id": 2,
    "establishment_id": 1,
    "name": "Barba",
    "description": "Barba tradicional",
    "duration_minutes": 20,
    "price": 30.0,
    "active": true
  }
]
Status HTTP
200 OK
9. Buscar Service

Retorna um serviço específico.

Endpoint
GET /services/<service_id>?establishment_id=1
Exemplo
GET /services/1?establishment_id=1
Resposta
{
  "id": 1,
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.0,
  "active": true
}
Status HTTP
200 OK
10. Service não encontrado

Quando o serviço não existe, não pertence ao estabelecimento informado ou está inativo, a API retorna:

{
  "error": "Service not found"
}

Status HTTP:

404 Not Found
11. Atualizar Service

Atualiza um serviço existente.

Endpoint
PUT /services/<service_id>?establishment_id=1
Exemplo
PUT /services/1?establishment_id=1
Body
{
  "name": "Corte masculino",
  "description": "Corte masculino atualizado",
  "duration_minutes": 40,
  "price": 50.00
}

Todos os campos são opcionais na atualização.

Isso permite realizar tanto atualizações completas quanto parciais.

Atualização parcial

Exemplo:

{
  "price": 55.00
}

Nesse caso, somente o preço será alterado.

Resposta
{
  "id": 1,
  "establishment_id": 1,
  "name": "Corte masculino",
  "description": "Corte masculino atualizado",
  "duration_minutes": 40,
  "price": 50.0,
  "active": true
}
Status HTTP
200 OK
12. Excluir Service

A exclusão de serviços utiliza soft delete.

O registro não é removido fisicamente do banco de dados.

Em vez disso:

active = false

é aplicado ao serviço.

Endpoint
DELETE /services/<service_id>?establishment_id=1
Exemplo
DELETE /services/1?establishment_id=1
Resposta
{
  "message": "Service deactivated successfully"
}
Status HTTP
200 OK
13. Comportamento após exclusão

Depois de executar:

DELETE /services/1?establishment_id=1

o serviço permanece armazenado no banco, porém deixa de aparecer nas consultas de serviços ativos.

Por exemplo:

GET /services?establishment_id=1

não retornará mais o serviço desativado.

Essa estratégia preserva o registro e evita a remoção física dos dados.

14. Isolamento por estabelecimento

A API foi projetada considerando o conceito de multi-tenancy.

Os recursos possuem associação com:

establishment_id

Atualmente essa identificação ainda é informada diretamente pela requisição.

Exemplo:

GET /services?establishment_id=1

ou:

PUT /services/10?establishment_id=1
Evolução futura

Com a implementação da autenticação JWT, o estabelecimento deverá ser identificado através do usuário autenticado.

Fluxo planejado:

Login
  │
  ▼
JWT
  │
  ▼
Usuário autenticado
  │
  ▼
Establishment
  │
  ▼
Recursos autorizados

Dessa forma, o cliente não precisará enviar livremente o establishment_id para definir o contexto da operação.

15. Status HTTP utilizados

A API utiliza códigos HTTP de acordo com o resultado da operação.

Código	Significado	Utilização
200	OK	Operações realizadas com sucesso
201	Created	Criação de Service
404	Not Found	Recurso inexistente ou indisponível
16. Formato das respostas

As respostas da API utilizam JSON.

Exemplo:

{
  "id": 1,
  "name": "Corte de cabelo",
  "duration_minutes": 30,
  "price": 45.0
}

Respostas de coleção utilizam arrays:

[
  {
    "id": 1,
    "name": "Corte de cabelo"
  },
  {
    "id": 2,
    "name": "Barba"
  }
]

Erros utilizam uma estrutura simples:

{
  "error": "Service not found"
}
17. Endpoints atuais

A API atualmente possui:

Método	Endpoint	Descrição
GET	/health	Verifica o funcionamento da aplicação
POST	/services	Cria um serviço
GET	/services	Lista serviços ativos
GET	/services/<id>	Busca um serviço
PUT	/services/<id>	Atualiza um serviço
DELETE	/services/<id>	Desativa um serviço
18. Fluxo CRUD

O fluxo completo de um Service é:

                 ┌───────────────┐
                 │    CREATE     │
                 │ POST /services│
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │     READ      │
                 │ GET /services │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │     UPDATE    │
                 │ PUT /services │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ SOFT DELETE   │
                 │DELETE /service│
                 └───────────────┘
19. Testes da API

Os endpoints de Services possuem testes automatizados.

Os testes estão localizados em:

tests/test_services.py

As operações testadas incluem:

Criação de Service;
Listagem;
Busca individual;
Serviço inexistente;
Atualização completa;
Atualização parcial;
Atualização de serviço inexistente;
Exclusão lógica;
Serviço excluído não aparece na listagem;
Exclusão de serviço inexistente.

A execução completa da suíte atualmente apresenta:

17 passed

Comando:

pytest -v
20. Validação

A API ainda possui validação básica dos dados recebidos.

Por exemplo, a criação de um Service utiliza os campos esperados no JSON:

{
  "establishment_id": 1,
  "name": "Corte",
  "duration_minutes": 30,
  "price": 45.00
}

A validação estruturada de payloads ainda será evoluída.

21. Melhorias planejadas

A API deverá evoluir para incluir:

Autenticação
POST /auth/register
POST /auth/login
Usuários
GET /users/me
Estabelecimentos
GET /establishments/me
PUT /establishments/me
Agenda
GET    /schedules
POST   /schedules
PUT    /schedules/<id>
DELETE /schedules/<id>
Exceções
GET    /schedule-exceptions
POST   /schedule-exceptions
PUT    /schedule-exceptions/<id>
DELETE /schedule-exceptions/<id>
Disponibilidade
GET /availability
Agendamentos
POST   /appointments
GET    /appointments
GET    /appointments/<id>
PUT    /appointments/<id>
DELETE /appointments/<id>

Esses endpoints fazem parte da evolução planejada e não estão implementados atualmente.

22. Autenticação futura

A autenticação da área administrativa será baseada em JWT.

Fluxo planejado:

                 ┌──────────────┐
                 │    Login     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ JWT Token    │
                 └──────┬───────┘
                        │
                        ▼
               Authorization Header
                        │
                        ▼
                 ┌──────────────┐
                 │ Protected API│
                 └──────────────┘

Exemplo futuro:

Authorization: Bearer <token>

A implementação dessa camada ainda não faz parte da API atual.

23. API pública futura

O sistema terá posteriormente uma área pública para que clientes realizem agendamentos.

O fluxo planejado será:

Link público
     │
     ▼
Estabelecimento
     │
     ▼
Serviço
     │
     ▼
Data
     │
     ▼
Horários disponíveis
     │
     ▼
Dados do cliente
     │
     ▼
Agendamento

O cliente final não deverá precisar criar uma conta para realizar um agendamento.

Essa funcionalidade ainda não está implementada.

24. Documentação futura

Conforme a API crescer, será adicionada documentação OpenAPI.

A intenção é disponibilizar uma especificação estruturada dos endpoints, permitindo integração mais simples com:

Frontend;
Aplicativos;
Sistemas externos;
Ferramentas de teste;
Documentação interativa.
25. Princípios da API

A evolução da API seguirá alguns princípios:

Endpoints orientados a recursos;
Uso consistente de métodos HTTP;
Respostas JSON;
Separação entre API e regras de negócio;
Isolamento por estabelecimento;
Autenticação para operações administrativas;
Testes automatizados;
Validação de dados;
Compatibilidade com evolução futura;
Evitar complexidade desnecessária.
26. Estado atual
Health Check             ✅
Services CRUD            ✅
Soft Delete              ✅
Isolamento por tenant    🟡 Inicial
Validação avançada       ⏳
JWT                      ⏳
API de Schedules         ⏳
API de Availability      ⏳
API de Appointments      ⏳
API Pública              ⏳
OpenAPI                  ⏳
Rate Limiting            ⏳

A API encontra-se em evolução incremental, começando pelo CRUD de Services e expandindo progressivamente para os demais domínios do sistema.