# Banco de Dados

## 1. Visão geral

O **TechLegacy Agendamento** utiliza o **PostgreSQL 16** como banco de dados principal.

O banco foi escolhido para armazenar os dados relacionais do sistema, incluindo:

- Estabelecimentos;
- Usuários;
- Serviços;
- Horários de funcionamento;
- Exceções de agenda;
- Agendamentos.

A aplicação utiliza **SQLAlchemy** como ORM e **Flask-Migrate/Alembic** para controle das alterações estruturais do banco.

---

## 2. Stack de persistência

A camada de persistência utiliza:

```text
PostgreSQL 16
      │
      ▼
SQLAlchemy
      │
      ▼
Flask-SQLAlchemy
      │
      ▼
Flask-Migrate
      │
      ▼
Alembic
```

Responsabilidades:

| Tecnologia       | Responsabilidade                        |
| ---------------- | --------------------------------------- |
| PostgreSQL       | Persistência dos dados                  |
| SQLAlchemy       | ORM e acesso aos dados                  |
| Flask-SQLAlchemy | Integração do SQLAlchemy com Flask      |
| Flask-Migrate    | Gerenciamento das migrations            |
| Alembic          | Controle das alterações estruturais     |

---

## 3. Estrutura atual

O banco possui atualmente as seguintes entidades:

```text
establishments
users
services
schedules
schedule_exceptions
appointments
```

Visão geral:

```text
                         establishments
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
            users            services         schedules
                                │
                                │
                                ▼
                           appointments

              establishments
                     │
                     ▼
             schedule_exceptions
```

O `establishments` funciona como a entidade central do modelo.

---

## 4. Establishments

Representa um estabelecimento que utiliza o sistema.

Tabela:

```text
establishments
```

Campos:

| Campo           | Tipo         | Obrigatório | Descrição                            |
| --------------- | ------------ | ----------- | ------------------------------------ |
| `id`            | Integer      | Sim         | Identificador                        |
| `name`          | String(120)  | Sim         | Nome do estabelecimento              |
| `slug`          | String(120)  | Sim         | Identificador textual único          |
| `phone`         | String(20)   | Não         | Telefone                             |
| `trial_ends_at` | DateTime     | Não         | Data de término do período de teste  |
| `created_at`    | DateTime     | Sim         | Data de criação                      |

O campo:

```text
slug
```

possui restrição de unicidade.

---

## 5. Users

Representa os usuários associados a um estabelecimento.

Tabela:

```text
users
```

Campos:

| Campo              | Tipo         | Obrigatório | Descrição                    |
| ------------------ | ------------ | ----------- | ---------------------------- |
| `id`               | Integer      | Sim         | Identificador                |
| `establishment_id` | Integer      | Sim         | Estabelecimento associado    |
| `email`            | String(255)  | Sim         | E-mail                       |
| `password_hash`    | String(255)  | Sim         | Senha armazenada como hash   |
| `created_at`       | DateTime     | Sim         | Data de criação              |

Relacionamento:

```text
establishments
       │
       │ 1:N
       ▼
     users
```

A chave estrangeira é:

```text
users.establishment_id
        ↓
establishments.id
```

O modelo já está preparado para associar usuários ao contexto de um estabelecimento.

---

## 6. Services

Representa os serviços oferecidos pelo estabelecimento.

Tabela:

```text
services
```

Campos:

| Campo              | Tipo           | Obrigatório | Descrição                    |
| ------------------ | -------------- | ----------- | ---------------------------- |
| `id`               | Integer        | Sim         | Identificador                |
| `establishment_id` | Integer        | Sim         | Estabelecimento proprietário |
| `name`             | String(120)    | Sim         | Nome do serviço              |
| `description`      | Text           | Não         | Descrição                    |
| `duration_minutes` | Integer        | Sim         | Duração em minutos           |
| `price`            | Numeric(10,2)  | Sim         | Preço                        |
| `active`           | Boolean        | Sim         | Status do serviço            |
| `created_at`       | DateTime       | Sim         | Data de criação              |

Relacionamento:

```text
establishments
       │
       │ 1:N
       ▼
    services
```

Chave estrangeira:

```text
services.establishment_id
        ↓
establishments.id
```

### 6.1 Soft Delete

Services utilizam exclusão lógica.

Quando um serviço é removido através da API, o registro permanece no banco.

O campo:

```text
active
```

é alterado para:

```text
false
```

Exemplo:

```text
Service
 ├── id: 10
 ├── name: "Barba"
 └── active: false
```

O registro continua disponível para preservação do histórico, mas deixa de aparecer nas consultas que consideram apenas serviços ativos.

---

## 7. Schedules

Representa o horário padrão de funcionamento do estabelecimento.

Tabela:

```text
schedules
```

Campos:

| Campo              | Tipo     | Obrigatório | Descrição                 |
| ------------------ | -------- | ----------- | ------------------------- |
| `id`               | Integer  | Sim         | Identificador             |
| `establishment_id` | Integer  | Sim         | Estabelecimento           |
| `weekday`          | Integer  | Sim         | Dia da semana             |
| `opening_time`     | Time     | Sim         | Horário de abertura       |
| `closing_time`     | Time     | Sim         | Horário de fechamento     |
| `active`           | Boolean  | Sim         | Indica se está ativo      |
| `created_at`       | DateTime | Sim         | Data de criação           |

Relacionamento:

```text
establishments
       │
       │ 1:N
       ▼
   schedules
```

### 7.1 Representação do dia da semana

O campo:

```text
weekday
```

utiliza a seguinte convenção:

| Valor | Dia           |
| ----- | ------------- |
| 0     | Segunda-feira |
| 1     | Terça-feira   |
| 2     | Quarta-feira  |
| 3     | Quinta-feira  |
| 4     | Sexta-feira   |
| 5     | Sábado        |
| 6     | Domingo       |

Essa representação é compatível com:

```text
date.weekday()
```

do Python.

---

## 8. Schedule Exceptions

Representa alterações específicas no horário padrão de funcionamento.

Tabela:

```text
schedule_exceptions
```

Campos:

| Campo              | Tipo     | Obrigatório | Descrição                        |
| ------------------ | -------- | ----------- | -------------------------------- |
| `id`               | Integer  | Sim         | Identificador                    |
| `establishment_id` | Integer  | Sim         | Estabelecimento                  |
| `date`             | Date     | Sim         | Data da exceção                  |
| `opening_time`     | Time     | Não         | Novo horário de abertura         |
| `closing_time`     | Time     | Não         | Novo horário de fechamento       |
| `closed`           | Boolean  | Sim         | Indica estabelecimento fechado   |
| `created_at`       | DateTime | Sim         | Data de criação                  |

Relacionamento:

```text
establishments
       │
       │ 1:N
       ▼
schedule_exceptions
```

### 8.1 Tipos de exceção

Uma exceção pode representar, por exemplo:

#### Alteração da abertura

```text
Horário normal:
08:00 → 18:00

Exceção:
10:00 → 18:00
```

#### Alteração do fechamento

```text
Horário normal:
08:00 → 18:00

Exceção:
08:00 → 15:00
```

#### Fechamento completo

```text
closed = true
```

Nesse caso, nenhum horário deve ser disponibilizado para a data.

---

## 9. Appointments

Representa os agendamentos realizados.

Tabela:

```text
appointments
```

Campos:

| Campo              | Tipo         | Obrigatório | Descrição               |
| ------------------ | ------------ | ----------- | ----------------------- |
| `id`               | Integer      | Sim         | Identificador           |
| `establishment_id` | Integer      | Sim         | Estabelecimento         |
| `service_id`       | Integer      | Sim         | Serviço agendado        |
| `customer_name`    | String(120)  | Sim         | Nome do cliente         |
| `customer_phone`   | String(20)   | Sim         | Telefone                |
| `starts_at`        | DateTime     | Sim         | Início                  |
| `ends_at`          | DateTime     | Sim         | Fim                     |
| `status`           | String(20)   | Sim         | Status do agendamento   |
| `created_at`       | DateTime     | Sim         | Data de criação         |

Relacionamentos:

```text
establishments
       │
       └──────────────┐
                      │
                      ▼
                appointments
                      ▲
                      │
                      │
                  services
```

Chaves estrangeiras:

```text
appointments.establishment_id
        ↓
establishments.id
```

e:

```text
appointments.service_id
        ↓
services.id
```

---

## 10. Status de Appointment

O status possui atualmente valor padrão:

```text
scheduled
```

Agendamentos cancelados utilizam:

```text
cancelled
```

A regra de disponibilidade ignora agendamentos cancelados ao verificar conflitos.

---

## 11. Relacionamentos

O relacionamento geral do banco pode ser representado da seguinte maneira:

```text
                         ┌─────────────────────┐
                         │    establishments   │
                         └──────────┬──────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           │                        │                        │
           ▼                        ▼                        ▼
     ┌──────────┐             ┌──────────┐             ┌───────────┐
     │  users   │             │ services │             │ schedules │
     └──────────┘             └─────┬────┘             └───────────┘
                                    │
                                    │
                                    ▼
                              ┌──────────────┐
                              │ appointments │
                              └──────────────┘

                         ┌──────────────────────┐
                         │ schedule_exceptions  │
                         └──────────────────────┘
                                    ▲
                                    │
                                    │
                           establishments
```

---

## 12. Estratégia de Multi-tenancy

O banco foi projetado considerando múltiplos estabelecimentos.

As principais tabelas de negócio possuem:

```text
establishment_id
```

Isso permite associar os dados ao estabelecimento correspondente.

Exemplo:

```text
Establishment 1
    │
    ├── Service 1
    ├── Service 2
    ├── Schedule 1
    └── Appointment 1

Establishment 2
    │
    ├── Service 3
    ├── Schedule 2
    └── Appointment 2
```

Os dados dos estabelecimentos são logicamente separados através das chaves estrangeiras.

---

## 13. Integridade referencial

As relações entre as entidades são estabelecidas através de chaves estrangeiras.

Exemplo:

```text
services.establishment_id
        │
        ▼
establishments.id
```

Isso permite que o banco mantenha a relação entre o serviço e seu estabelecimento.

As principais foreign keys são:

```text
users.establishment_id
    → establishments.id

services.establishment_id
    → establishments.id

schedules.establishment_id
    → establishments.id

schedule_exceptions.establishment_id
    → establishments.id

appointments.establishment_id
    → establishments.id

appointments.service_id
    → services.id
```

---

## 14. Timestamps

As principais entidades possuem:

```text
created_at
```

O valor é gerado pelo banco através de:

```python
server_default=func.now()
```

Isso permite registrar o momento em que o registro foi criado.

---

## 15. Migrations

As alterações estruturais do banco são controladas através de migrations.

Estrutura:

```text
migrations/
├── versions/
│   ├── ...
│   └── ...
├── alembic.ini
├── env.py
└── script.py.mako
```

O fluxo utilizado é:

```text
Alteração do Model
        │
        ▼
flask db migrate
        │
        ▼
Migration
        │
        ▼
flask db upgrade
        │
        ▼
PostgreSQL
```

---

## 16. Migration atual

A versão atual do banco é:

```text
6604689ef554
```

O histórico foi construído incrementalmente:

```text
<base>
   │
   ▼
8096f976d54b
   │
   ▼
f1e3c650f8d3
   │
   ▼
b70c5f3160c7
   │
   ▼
a362d7bab9d5
   │
   ▼
6b39cfd8c020
   │
   ▼
6604689ef554
```

As migrations representam a evolução da estrutura do banco junto com a evolução do código.

---

## 17. Comandos de Migration

### Verificar versão atual

```bash
flask --app app db current
```

Resultado esperado atualmente:

```text
6604689ef554 (head)
```

### Verificar heads

```bash
flask --app app db heads
```

Resultado esperado:

```text
6604689ef554 (head)
```

### Criar migration

Após alterar um model:

```bash
flask --app app db migrate -m "descrição da alteração"
```

Exemplo:

```bash
flask --app app db migrate -m "add service category"
```

### Aplicar migration

```bash
flask --app app db upgrade
```

---

## 18. Docker e banco

Durante o desenvolvimento, PostgreSQL é executado através do Docker Compose.

Arquitetura:

```text
Docker Compose
      │
      ├───────────────┐
      │               │
      ▼               ▼
 Flask App        PostgreSQL
 :5000               :5432
                        │
                        ▼
                 postgres_data
```

O banco utiliza um volume persistente:

```text
postgres_data
```

Isso evita que os dados sejam perdidos simplesmente ao recriar o container.

---

## 19. Configuração de conexão

A aplicação utiliza variáveis de ambiente para configurar a conexão com o PostgreSQL.

Principais variáveis:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
```

Exemplo conceitual:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=techlegacy
POSTGRES_USER=postgres
POSTGRES_PASSWORD=********
```

A senha real não deve ser armazenada no Git.

O arquivo:

```text
.env
```

deve permanecer fora do versionamento.

O projeto utiliza:

```text
.env.example
```

para documentar as variáveis necessárias sem expor credenciais reais.

---

## 20. Banco de testes

Os testes automatizados não utilizam o PostgreSQL de desenvolvimento.

A suíte de testes utiliza:

```text
SQLite
```

em memória:

```text
sqlite:///:memory:
```

Isso permite que os testes sejam executados rapidamente e de forma isolada.

Fluxo:

```text
pytest
  │
  ▼
SQLite em memória
  │
  ├── create_all()
  │
  ├── executa testes
  │
  └── drop_all()
```

O banco de testes é criado e destruído durante a execução da fixture.

---

## 21. Isolamento dos testes

Cada execução de teste utiliza um ambiente de banco isolado.

A fixture realiza:

```python
db.create_all()
```

antes dos testes e:

```python
db.session.remove()
db.drop_all()
```

após sua execução.

Isso evita que dados criados por um teste contaminem outros testes.

---

## 22. Regras relacionadas ao banco

Algumas regras importantes do domínio dependem diretamente dos dados persistidos.

### Serviços

Somente Services ativos são considerados pela API atual.

```text
active = true
```

### Disponibilidade

A disponibilidade considera:

- Serviço;
- Estabelecimento;
- Dia da semana;
- Horário;
- Exceções;
- Agendamentos existentes.

### Agendamentos cancelados

Agendamentos com:

```text
status = cancelled
```

não bloqueiam um horário.

### Multi-tenancy

Consultas de Services consideram:

```text
establishment_id
```

para limitar os registros ao estabelecimento correspondente.

---

## 23. Índices e constraints

Atualmente existem constraints importantes no modelo.

O campo:

```text
establishments.slug
```

é único.

Os relacionamentos utilizam foreign keys.

O modelo ainda pode evoluir para adicionar índices específicos conforme o volume de dados e os padrões de consulta forem conhecidos.

Exemplos de possíveis índices futuros:

```text
appointments.establishment_id
appointments.starts_at
appointments.ends_at
appointments.status
services.establishment_id
services.active
schedules.establishment_id
schedules.weekday
```

Esses índices são uma evolução futura e não devem ser considerados parte da estrutura atual.

---

## 24. Considerações sobre concorrência

A lógica atual de disponibilidade consulta os agendamentos existentes para verificar conflitos.

Fluxo:

```text
Consultar horário
      │
      ▼
Consultar appointments
      │
      ▼
Verificar sobreposição
      │
      ▼
Retornar disponibilidade
```

Em uma futura versão de produção, será necessário considerar cenários de concorrência.

Por exemplo:

```text
Cliente A ─────┐
               ├── tenta reservar 10:00
Cliente B ─────┘
```

Os dois clientes podem consultar a disponibilidade simultaneamente.

A implementação definitiva do processo de criação de agendamento deverá utilizar mecanismos apropriados de transação e/ou restrições para evitar reservas conflitantes.

Essa proteção ainda não faz parte da implementação atual.

---

## 25. Timezone

Os campos de data e hora dos agendamentos utilizam:

```python
DateTime(timezone=True)
```

A estratégia completa de timezone ainda será definida durante a implementação do agendamento público e do ambiente de produção.

Esse ponto será especialmente importante quando o sistema começar a atender estabelecimentos em diferentes regiões.

---

## 26. Evolução futura do banco

Conforme o projeto evoluir, o banco poderá receber novas entidades.

Possível evolução:

```text
establishments
      │
      ├── users
      ├── services
      ├── schedules
      ├── schedule_exceptions
      ├── appointments
      │
      ├── subscription
      ├── notifications
      └── customization
```

Essas entidades ainda não fazem parte do banco atual.

---

## 27. Possível evolução para planos e assinatura

O produto prevê inicialmente um período de teste.

O campo atual:

```text
trial_ends_at
```

já permite armazenar a data de término do período de teste do estabelecimento.

No futuro, poderá ser criado um domínio específico para assinatura e planos, por exemplo:

```text
plans
subscriptions
payments
```

Essa estrutura ainda não está implementada.

---

## 28. Princípios de modelagem

A modelagem atual segue alguns princípios:

- Utilizar banco relacional;
- Manter integridade referencial;
- Associar dados ao estabelecimento;
- Evitar duplicação desnecessária;
- Utilizar migrations para alterações estruturais;
- Preservar registros através de soft delete quando necessário;
- Separar banco de desenvolvimento e testes;
- Evitar otimizações prematuras;
- Adicionar índices conforme os padrões reais de consulta forem conhecidos.

---

## 29. Estado atual

```text
PostgreSQL 16             ✅
SQLAlchemy                ✅
Flask-Migrate             ✅
Alembic                   ✅
Establishments            ✅
Users                     ✅
Services                  ✅
Schedules                 ✅
Schedule Exceptions       ✅
Appointments              ✅
Foreign Keys              ✅
Soft Delete               ✅
Multi-tenancy estrutural  ✅
Índices específicos       ⏳
Concorrência de booking   ⏳
Timezone definitivo       ⏳
Subscriptions             ⏳
Notifications             ⏳
```

---

## 30. Resumo

O banco de dados foi estruturado para suportar o núcleo do sistema de agendamento mantendo uma arquitetura relacional simples.

A entidade central é:

```text
establishments
```

A partir dela são relacionados:

```text
users
services
schedules
schedule_exceptions
appointments
```

A estrutura utiliza PostgreSQL, SQLAlchemy e migrations para permitir evolução controlada.

O modelo atual já contempla os principais fundamentos necessários para evoluir o projeto para autenticação, agendamento público, dashboard, integrações, CI/CD e ambiente de produção.