# API

## 1. Visão geral

A API do **TechLegacy Agendamento** é construída utilizando Flask e segue uma abordagem REST.

A API expõe os recursos do sistema e centraliza a comunicação entre clientes e as regras de negócio da aplicação.

A **Fase 3 — REST API** está praticamente concluída. Atualmente estão implementados os endpoints dos seguintes domínios:

- Health Check
- Services
- Schedules
- Schedule Exceptions
- Appointments

A autenticação JWT e o isolamento por estabelecimento baseado no usuário autenticado ainda fazem parte da próxima fase.

---

## 2. Tecnologias

A API utiliza:

- Python 3.11
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-Migrate / Alembic
- Pytest
- Docker
- Docker Compose

---

## 3. Base URL

Durante o desenvolvimento local:

```text
http://localhost:5000
```

Exemplo:

```text
http://localhost:5000/services
```

---

# 4. Health Check

Permite verificar se a aplicação está funcionando.

### Endpoint

```http
GET /health
```

### Resposta

```json
{
  "status": "ok",
  "message": "TechLegacy Agendamento API is running"
}
```

### Status

`200 OK`

---

# 5. Padrão de contexto do estabelecimento

Na implementação atual, os endpoints administrativos utilizam `establishment_id` para identificar o estabelecimento.

Por exemplo:

```http
GET /services?establishment_id=1
```

ou:

```http
GET /appointments?establishment_id=1
```

Esse mecanismo é **temporário**.

Na Fase 4, o contexto do estabelecimento deverá ser obtido a partir do usuário autenticado através de JWT. Dessa forma, o cliente não poderá escolher livremente o `establishment_id` da operação.

Fluxo planejado:

```text
Login
  |
  v
JWT
  |
  v
Usuário autenticado
  |
  v
Establishment
  |
  v
Recursos autorizados
```

---

# 6. Services

O recurso `Services` representa os serviços oferecidos por um estabelecimento.

### Rota base

```text
/services
```

### Modelo

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id | integer | Sim | Identificador |
| establishment_id | integer | Sim | Estabelecimento proprietário |
| name | string | Sim | Nome |
| description | string | Não | Descrição |
| duration_minutes | integer | Sim | Duração em minutos |
| price | decimal | Sim | Preço |
| active | boolean | Sim | Indica se está ativo |

### Exemplo

```json
{
  "id": 1,
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.0,
  "active": true
}
```

## 6.1 Criar Service

```http
POST /services
```

### Body

```json
{
  "establishment_id": 1,
  "name": "Corte de cabelo",
  "description": "Corte masculino tradicional",
  "duration_minutes": 30,
  "price": 45.0
}
```

### Resposta

`201 Created`

---

## 6.2 Listar Services

```http
GET /services?establishment_id=1
```

Retorna somente serviços ativos do estabelecimento.

### Resposta

`200 OK`

---

## 6.3 Buscar Service

```http
GET /services/<service_id>?establishment_id=1
```

Exemplo:

```http
GET /services/1?establishment_id=1
```

Se o serviço não existir, não pertencer ao estabelecimento ou estiver inativo:

```json
{
  "error": "Service not found"
}
```

Status:

`404 Not Found`

---

## 6.4 Atualizar Service

```http
PUT /services/<service_id>?establishment_id=1
```

O endpoint aceita atualização parcial.

Exemplo:

```json
{
  "price": 55.0
}
```

### Resposta

`200 OK`

---

## 6.5 Excluir Service

A exclusão utiliza **soft delete**.

```http
DELETE /services/<service_id>?establishment_id=1
```

O registro não é removido fisicamente.

Seu campo:

```text
active = false
```

é aplicado.

### Resposta

```json
{
  "message": "Service deactivated successfully"
}
```

Status:

`200 OK`

Serviços desativados não aparecem na listagem de serviços ativos.

---

# 7. Schedules

O recurso `Schedules` representa o horário padrão de funcionamento do estabelecimento por dia da semana.

### Rota base

```text
/schedules
```

### Modelo

| Campo | Tipo | Descrição |
|---|---|---|
| id | integer | Identificador |
| establishment_id | integer | Estabelecimento |
| weekday | integer | Dia da semana |
| opening_time | time | Horário de abertura |
| closing_time | time | Horário de fechamento |
| active | boolean | Indica se está ativo |

### Dias da semana

A API utiliza o padrão do Python:

| Valor | Dia |
|---:|---|
| 0 | Segunda-feira |
| 1 | Terça-feira |
| 2 | Quarta-feira |
| 3 | Quinta-feira |
| 4 | Sexta-feira |
| 5 | Sábado |
| 6 | Domingo |

## 7.1 Criar Schedule

```http
POST /schedules
```

Exemplo:

```json
{
  "establishment_id": 1,
  "weekday": 0,
  "opening_time": "08:00",
  "closing_time": "18:00"
}
```

Não é permitido criar duas agendas ativas para o mesmo estabelecimento e dia da semana.

### Status

`201 Created`

---

## 7.2 Listar Schedules

```http
GET /schedules?establishment_id=1
```

### Status

`200 OK`

---

## 7.3 Buscar Schedule

```http
GET /schedules/<schedule_id>?establishment_id=1
```

### Status

`200 OK`

Caso não exista ou não pertença ao estabelecimento:

`404 Not Found`

---

## 7.4 Atualizar Schedule

```http
PUT /schedules/<schedule_id>?establishment_id=1
```

Permite atualizar os horários e os demais campos aceitos pela validação da rota.

### Status

`200 OK`

---

## 7.5 Excluir Schedule

O schedule utiliza soft delete.

```http
DELETE /schedules/<schedule_id>?establishment_id=1
```

O registro permanece no banco e é marcado como inativo.

### Status

`200 OK`

---

# 8. Schedule Exceptions

O recurso `Schedule Exceptions` permite alterar o funcionamento normal do estabelecimento para uma data específica.

Pode ser utilizado para:

- Fechamento excepcional;
- Abertura em horário diferente;
- Fechamento antecipado;
- Alteração do horário de funcionamento em uma data específica.

### Rota base

```text
/schedule-exceptions
```

### Modelo

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id | integer | Sim | Identificador |
| establishment_id | integer | Sim | Estabelecimento |
| date | date | Sim | Data da exceção |
| opening_time | time | Não | Nova abertura |
| closing_time | time | Não | Novo fechamento |
| closed | boolean | Sim | Indica se estará fechado |

## 8.1 Criar exceção

```http
POST /schedule-exceptions
```

Exemplo de fechamento:

```json
{
  "establishment_id": 1,
  "date": "2026-09-28",
  "closed": true
}
```

Exemplo de alteração de horário:

```json
{
  "establishment_id": 1,
  "date": "2026-09-28",
  "opening_time": "09:00",
  "closing_time": "15:00",
  "closed": false
}
```

Não é permitido cadastrar duas exceções para o mesmo estabelecimento e data.

### Status

`201 Created`

---

## 8.2 Listar exceções

```http
GET /schedule-exceptions?establishment_id=1
```

### Status

`200 OK`

---

## 8.3 Buscar exceção

```http
GET /schedule-exceptions/<exception_id>?establishment_id=1
```

### Status

`200 OK`

---

## 8.4 Atualizar exceção

```http
PUT /schedule-exceptions/<exception_id>?establishment_id=1
```

A atualização considera o **estado final** da exceção.

Por exemplo, uma exceção inicialmente configurada como:

```json
{
  "closed": true
}
```

pode ser alterada para:

```json
{
  "closed": false,
  "opening_time": "08:00",
  "closing_time": "14:00"
}
```

Quando `closed` for `false`, os horários de abertura e fechamento precisam formar um intervalo válido.

### Status

`200 OK`

---

## 8.5 Excluir exceção

```http
DELETE /schedule-exceptions/<exception_id>?establishment_id=1
```

### Status

`200 OK`

---

# 9. Availability

A disponibilidade é implementada atualmente como uma **regra de negócio interna**, utilizada pelo fluxo de agendamentos.

O motor considera:

1. Serviço solicitado;
2. Estabelecimento;
3. Dia da semana;
4. Horário padrão;
5. Exceção de agenda;
6. Duração do serviço;
7. Agendamentos existentes;
8. Status do agendamento.

A função principal é:

```text
get_available_slots()
```

O motor:

- retorna `[]` quando o serviço não existe ou está inativo;
- retorna `[]` quando não existe agenda para o dia;
- retorna `[]` quando a data está fechada por uma exceção;
- aplica abertura/fechamento definidos pela exceção;
- respeita a duração do serviço;
- não cria horários que ultrapassem o fechamento;
- bloqueia horários que possuem conflito;
- ignora agendamentos cancelados;
- permite excluir um agendamento específico da verificação durante uma atualização.

### Disponibilidade e agendamentos

A disponibilidade ainda **não possui endpoint público próprio**.

A implementação atual é utilizada internamente pelo recurso `Appointments`.

---

# 10. Appointments

O recurso `Appointments` representa os agendamentos realizados para os serviços.

### Rota base

```text
/appointments
```

### Modelo

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id | integer | Sim | Identificador |
| establishment_id | integer | Sim | Estabelecimento |
| service_id | integer | Sim | Serviço |
| customer_name | string | Sim | Nome do cliente |
| customer_phone | string | Sim | Telefone |
| starts_at | datetime | Sim | Início |
| ends_at | datetime | Sim | Fim |
| status | string | Sim | Estado do agendamento |

### Status atualmente utilizados

```text
scheduled
cancelled
```

---

## 10.1 Criar Appointment

```http
POST /appointments
```

Exemplo:

```json
{
  "establishment_id": 1,
  "service_id": 1,
  "customer_name": "João Silva",
  "customer_phone": "11999999999",
  "starts_at": "2026-09-28T08:00:00"
}
```

A API:

1. valida o payload;
2. verifica se o serviço existe e está ativo;
3. calcula o horário de término com base na duração do serviço;
4. verifica a disponibilidade;
5. rejeita conflitos;
6. cria o agendamento.

### Sucesso

`201 Created`

### Horário indisponível

```json
{
  "error": "Selected time slot is not available"
}
```

Status:

`409 Conflict`

---

## 10.2 Listar Appointments

```http
GET /appointments?establishment_id=1
```

Os agendamentos são retornados ordenados por `starts_at`.

### Status

`200 OK`

---

## 10.3 Buscar Appointment

```http
GET /appointments/<appointment_id>?establishment_id=1
```

### Status

`200 OK`

Caso não exista ou não pertença ao estabelecimento:

`404 Not Found`

---

## 10.4 Atualizar Appointment

```http
PUT /appointments/<appointment_id>?establishment_id=1
```

Pode atualizar dados do cliente, horário e status.

Exemplo:

```json
{
  "starts_at": "2026-09-28T09:00:00"
}
```

A API recalcula `ends_at` utilizando a duração do serviço.

Quando o agendamento permanecer como `scheduled`, o novo horário passa novamente pelo motor de disponibilidade.

O próprio agendamento é excluído da verificação para evitar conflito falso ao manter o mesmo horário.

### Status

`200 OK`

### Horário indisponível

`409 Conflict`

---

## 10.5 Cancelar Appointment

O cancelamento utiliza alteração de status.

```http
DELETE /appointments/<appointment_id>?establishment_id=1
```

O registro permanece no banco e passa para:

```text
status = cancelled
```

### Resposta

```json
{
  "message": "Appointment cancelled successfully"
}
```

### Status

`200 OK`

Agendamentos cancelados deixam de bloquear horários disponíveis.

---

## 10.6 Reativação de Appointment

Um agendamento cancelado pode ser atualizado novamente para:

```text
scheduled
```

Porém, antes da reativação, a API verifica novamente a disponibilidade.

Isso impede que um agendamento cancelado seja reativado sobre um horário que já foi ocupado.

---

# 11. Validação

Os endpoints possuem validações específicas de payload.

Entre os casos tratados estão:

- campos obrigatórios;
- tipos dos campos;
- strings vazias;
- datas;
- horários;
- valores booleanos;
- status de agendamento;
- existência do serviço;
- existência do recurso;
- associação do recurso ao estabelecimento;
- conflitos de horário.

Quando ocorre erro de validação, a API utiliza uma resposta padronizada.

Exemplo:

```json
{
  "error": "Validation error",
  "details": {
    "customer_name": "Must not be empty"
  }
}
```

---

# 12. Tratamento de erros

A aplicação possui uma exceção específica:

```text
APIError
```

Ela permite padronizar erros da API.

Exemplo:

```json
{
  "error": "Service not found"
}
```

Quando existem detalhes adicionais:

```json
{
  "error": "Validation error",
  "details": {
    "duration_minutes": "Must be an integer"
  }
}
```

Também existem handlers globais para:

- `400 Bad Request`
- `404 Not Found`
- `405 Method Not Allowed`

---

# 13. Status HTTP utilizados

| Código | Significado | Utilização |
|---:|---|---|
| 200 | OK | Operações realizadas com sucesso |
| 201 | Created | Criação de recursos |
| 400 | Bad Request | Payload ou parâmetros inválidos |
| 404 | Not Found | Recurso inexistente ou fora do contexto |
| 405 | Method Not Allowed | Método HTTP não suportado |
| 409 | Conflict | Conflito de disponibilidade |

---

# 14. Isolamento por estabelecimento

Todos os principais recursos de negócio possuem associação com:

```text
establishment_id
```

Atualmente, esse identificador é informado diretamente na requisição.

Exemplo:

```http
GET /appointments?establishment_id=1
```

A rota também verifica a associação entre o recurso e o estabelecimento.

Exemplo:

```http
GET /services/10?establishment_id=1
```

Um serviço pertencente a outro estabelecimento não deve ser retornado como recurso daquele contexto.

### Limitação atual

Essa abordagem ainda não representa o multi-tenancy completo de um SaaS, pois o cliente pode informar o `establishment_id`.

A correção será realizada na Fase 4 através de autenticação e autorização.

---

# 15. Testes automatizados

A API possui testes automatizados utilizando Pytest.

Os testes cobrem os principais fluxos dos domínios implementados.

Entre os cenários protegidos estão:

### Services

- criação;
- listagem;
- busca;
- atualização;
- atualização parcial;
- serviço inexistente;
- soft delete;
- serviço desativado não aparece na listagem.

### Schedules

- criação;
- listagem;
- atualização;
- exclusão;
- validação de horários;
- prevenção de duplicidade.

### Schedule Exceptions

- criação;
- listagem;
- atualização;
- exclusão;
- estabelecimento fechado;
- alteração de abertura;
- alteração de fechamento;
- fechamento antecipado;
- validação do estado final.

### Appointments

- criação;
- conflito de horário;
- horário fora da agenda;
- listagem;
- busca;
- cancelamento;
- liberação do horário após cancelamento;
- atualização mantendo o mesmo horário;
- atualização para horário disponível;
- atualização para horário ocupado;
- reativação de cancelado;
- bloqueio de reativação em horário ocupado;
- atualização dos dados do cliente;
- status inválido;
- isolamento entre estabelecimentos.

### Execução

```powershell
pytest -q
```

A suíte completa está passando após a conclusão das correções da API.

---

# 16. Endpoints atuais

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Health Check |
| POST | `/services` | Cria serviço |
| GET | `/services` | Lista serviços ativos |
| GET | `/services/<id>` | Busca serviço |
| PUT | `/services/<id>` | Atualiza serviço |
| DELETE | `/services/<id>` | Desativa serviço |
| POST | `/schedules` | Cria agenda |
| GET | `/schedules` | Lista agendas |
| GET | `/schedules/<id>` | Busca agenda |
| PUT | `/schedules/<id>` | Atualiza agenda |
| DELETE | `/schedules/<id>` | Desativa agenda |
| POST | `/schedule-exceptions` | Cria exceção |
| GET | `/schedule-exceptions` | Lista exceções |
| GET | `/schedule-exceptions/<id>` | Busca exceção |
| PUT | `/schedule-exceptions/<id>` | Atualiza exceção |
| DELETE | `/schedule-exceptions/<id>` | Remove exceção |
| POST | `/appointments` | Cria agendamento |
| GET | `/appointments` | Lista agendamentos |
| GET | `/appointments/<id>` | Busca agendamento |
| PUT | `/appointments/<id>` | Atualiza agendamento |
| DELETE | `/appointments/<id>` | Cancela agendamento |

> Os endpoints acima representam a implementação atual da API.

---

# 17. Fluxo de disponibilidade

O fluxo de criação de um agendamento é:

```text
Cliente/API
    |
    v
Validação do payload
    |
    v
Serviço existe e está ativo?
    |
    v
Agenda do estabelecimento
    |
    v
Existe exceção para a data?
    |
    +---- Sim ---> Aplica exceção
    |
    v
Calcula duração do serviço
    |
    v
Gera horários possíveis
    |
    v
Verifica conflitos
    |
    +---- Conflito ---> 409 Conflict
    |
    v
Cria Appointment
```

Esse fluxo garante que a criação não dependa apenas de uma validação superficial do horário enviado pelo cliente.

---

# 18. Soft Delete

O sistema utiliza soft delete em recursos nos quais o histórico deve ser preservado.

Atualmente:

- Services usam `active`;
- Schedules usam `active`;
- Appointments usam `status = cancelled`.

A ideia é evitar remoções físicas desnecessárias e preservar informações que podem ser importantes para histórico e auditoria.

---

# 19. Autenticação futura

A área administrativa será protegida futuramente por JWT.

Fluxo planejado:

```text
┌──────────────┐
│    Login     │
└──────┬───────┘
       |
       v
┌──────────────┐
│ JWT Token    │
└──────┬───────┘
       |
       v
Authorization: Bearer <token>
       |
       v
┌──────────────┐
│ Protected API│
└──────────────┘
```

Endpoints planejados:

```http
POST /auth/register
POST /auth/login
GET /users/me
GET /establishments/me
PUT /establishments/me
```

Essa implementação pertence à **Fase 4**.

---

# 20. API pública futura

O sistema terá posteriormente uma área pública para clientes realizarem agendamentos sem criar uma conta.

Fluxo planejado:

```text
Link público
     |
     v
Estabelecimento
     |
     v
Serviço
     |
     v
Data
     |
     v
Horários disponíveis
     |
     v
Dados do cliente
     |
     v
Agendamento
```

Essa camada será implementada posteriormente, após a autenticação da área administrativa.

---

# 21. OpenAPI

A documentação atual é mantida em Markdown.

Conforme a API evoluir, será adicionada uma especificação OpenAPI para facilitar:

- integração com frontend;
- testes;
- integração com sistemas externos;
- geração de documentação;
- exploração dos endpoints.

---

# 22. Evoluções futuras

Entre as próximas evoluções planejadas:

### Fase 4

- autenticação;
- JWT;
- usuários;
- autorização;
- multi-tenancy real;
- remoção da dependência de `establishment_id` informado pelo cliente.

### Fase 5

- dashboard administrativo;
- gerenciamento visual de serviços;
- gerenciamento de agendas;
- visão geral de agendamentos;
- personalização básica.

### Fase 6

- página pública do estabelecimento;
- seleção de serviço;
- consulta de disponibilidade;
- criação de agendamento;
- confirmação via WhatsApp.

### Fase 7

- segurança;
- testes adicionais;
- tratamento de concorrência;
- rate limiting;
- melhoria das validações;
- observabilidade.

### Fase 8

- CI/CD;
- GitHub Actions;
- execução automática de testes;
- build de Docker;
- validação antes do deploy.

### Fase 9

- deploy em produção;
- servidor Contabo;
- configuração de ambiente;
- monitoramento;
- backup;
- operação do SaaS.

---

# 23. Princípios da API

A evolução da API seguirá:

- endpoints orientados a recursos;
- uso consistente dos métodos HTTP;
- respostas JSON;
- separação entre API e regras de negócio;
- isolamento por estabelecimento;
- autenticação para operações administrativas;
- validação de dados;
- testes automatizados;
- preservação de histórico quando necessário;
- baixo acoplamento;
- evolução incremental;
- evitar complexidade desnecessária.

---

# 24. Estado atual

| Componente | Estado |
|---|---|
| Health Check | ✅ |
| Services CRUD | ✅ |
| Schedules CRUD | ✅ |
| Schedule Exceptions CRUD | ✅ |
| Appointments CRUD | ✅ |
| Motor de disponibilidade | ✅ |
| Validação de payloads | ✅ |
| Tratamento padronizado de erros | ✅ |
| Testes automatizados | ✅ |
| Isolamento por estabelecimento | 🟡 Inicial |
| JWT | ⏳ |
| Multi-tenancy real | ⏳ |
| Dashboard | ⏳ |
| API pública | ⏳ |
| OpenAPI | ⏳ |
| CI/CD | ⏳ |
| Deploy de produção | ⏳ |

A API concluiu a implementação dos principais recursos de negócio da Fase 3. O próximo grande passo é a Fase 4, na qual a identificação do estabelecimento deixará de depender diretamente dos parâmetros enviados pelo cliente e passará a ser derivada do usuário autenticado.
