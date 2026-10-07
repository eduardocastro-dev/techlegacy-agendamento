# 🚀 TechLegacy Agendamento

Sistema de agendamento para pequenos estabelecimentos.

O projeto tem como objetivo disponibilizar uma plataforma simples para que estabelecimentos possam configurar seus serviços, horários de atendimento e receber agendamentos de clientes através de uma página pública.

O sistema está sendo desenvolvido de forma incremental, com foco em organização de código, regras de negócio, testes automatizados, containerização, autenticação, multi-tenancy e, posteriormente, CI/CD e deploy.

---

## 🎯 Objetivo

O TechLegacy Agendamento pretende permitir que um estabelecimento:

- Cadastre seus serviços;
- Configure seus horários de atendimento;
- Defina exceções de agenda;
- Consulte sua disponibilidade;
- Receba agendamentos;
- Gerencie seus horários;
- Disponibilize uma página pública para seus clientes;
- Acompanhe seus agendamentos através de um dashboard.

A primeira versão está sendo desenvolvida como um **monólito modular**, mantendo os domínios organizados para permitir evolução futura.

---

## 🏗️ Arquitetura

A arquitetura utiliza um monólito modular baseado em Flask.

```text
                         ┌─────────────────────┐
                         │       Cliente       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Flask API      │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
        Authentication        Business Rules        Public Booking
              │                     │                     │
              ▼                     ▼                     ▼
         Multi-tenancy        Appointments           Future
              │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                               PostgreSQL
```

Mais detalhes:

- [Arquitetura](docs/architecture.md)
- [Banco de dados](docs/database.md)
- [Regras de negócio](docs/business-rules.md)
- [API](docs/api.md)
- [Desenvolvimento](docs/development.md)
- [Roadmap](docs/roadmap.md)

---

## 🛠️ Stack

### Backend

- Python 3.11
- Flask
- SQLAlchemy
- Flask-Migrate
- Alembic
- Flask-JWT-Extended

### Banco de dados

- PostgreSQL 16

### Infraestrutura

- Docker
- Docker Compose

### Testes

- Pytest

### Planejado

- GitHub Actions
- CI/CD
- Deploy no servidor Contabo
- HTTPS
- Monitoramento
- Integrações externas
- Notificações

---

## 📌 Status atual

🚧 **Projeto em desenvolvimento**

### Fase 1 — Fundação

- [x] Estrutura inicial
- [x] Flask
- [x] Configuração de ambiente
- [x] Docker
- [x] Docker Compose
- [x] PostgreSQL
- [x] Endpoint `/health`
- [x] Estrutura inicial de testes

### Fase 2 — Núcleo de negócio

- [x] Models
- [x] SQLAlchemy
- [x] PostgreSQL
- [x] Flask-Migrate
- [x] Alembic
- [x] Migrations
- [x] Establishment
- [x] User
- [x] Service
- [x] Schedule
- [x] ScheduleException
- [x] Appointment
- [x] Regras de disponibilidade
- [x] Tratamento de exceções de agenda
- [x] Detecção de conflitos
- [x] CRUD de Services
- [x] Soft delete de Services
- [x] Testes automatizados

### Fase 3 — API REST

- [x] API de Services
- [x] API de Schedules
- [x] API de Schedule Exceptions
- [x] API de Appointments
- [x] Validação de entrada
- [x] Tratamento padronizado de erros
- [x] Isolamento por estabelecimento
- [x] Testes automatizados dos endpoints

### Fase 4 — Autenticação e Multi-tenancy

- [x] Cadastro de usuário
- [x] Login
- [x] JWT
- [x] Autorização
- [x] Identificação do estabelecimento pelo usuário autenticado
- [x] Isolamento entre estabelecimentos
- [x] Proteção dos endpoints administrativos
- [x] Testes de autenticação
- [x] Testes de isolamento entre tenants
- [x] Padronização de timezone nos horários de agendamento

### Fase 5 — Dashboard

- [ ] Dashboard administrativo
- [ ] Gerenciamento de serviços
- [ ] Gerenciamento de horários
- [ ] Gerenciamento de agendamentos
- [ ] Visão geral do estabelecimento
- [ ] Personalização básica

### Fase 6 — Agendamento público

- [ ] Página pública do estabelecimento
- [ ] Seleção de serviço
- [ ] Consulta de disponibilidade
- [ ] Seleção de data
- [ ] Seleção de horário
- [ ] Cadastro do cliente
- [ ] Criação do agendamento
- [ ] Confirmação

### Fase 7 — Qualidade e Segurança

- [ ] Lint
- [ ] Padronização de código
- [ ] Logging
- [ ] Revisão de segurança
- [ ] Testes de integração
- [ ] Testes de cenários críticos

### Fase 8 — CI/CD e Automação de Pipeline

- [ ] GitHub Actions
- [ ] Lint automatizado
- [ ] Execução de testes no Pull Request
- [ ] Build Docker automatizado
- [ ] Pipeline CI
- [ ] Pipeline CD
- [ ] Deploy automatizado

### Fase 9 — Produção

- [ ] Configuração do ambiente de produção
- [ ] Deploy no servidor
- [ ] Banco de produção
- [ ] Variáveis de ambiente
- [ ] HTTPS
- [ ] Monitoramento
- [ ] Backup

### Fase 10 — Evolução SaaS e ML

- [ ] Evolução para modelo SaaS
- [ ] Métricas de uso
- [ ] Previsão de demanda
- [ ] Insights sobre agendamentos
- [ ] Experimentação com modelos de Machine Learning
- [ ] Monitoramento de modelos

---

## 🔐 Autenticação e Multi-tenancy

A área administrativa utiliza autenticação baseada em JWT.

O usuário autenticado está associado a um estabelecimento e o contexto do estabelecimento é obtido através do usuário autenticado.

Dessa forma, endpoints administrativos não dependem de `establishment_id` enviado pelo cliente para determinar o tenant.

O sistema também possui testes de isolamento para garantir que um usuário de um estabelecimento não consiga acessar agendamentos pertencentes a outro estabelecimento.

---

## 🗄️ Banco de dados

O projeto utiliza PostgreSQL 16.

As alterações estruturais são controladas através de:

```text
SQLAlchemy
     │
     ▼
Flask-Migrate
     │
     ▼
Alembic
     │
     ▼
PostgreSQL
```

Modelos atuais:

```text
Establishment
     │
     ├── User
     ├── Service
     ├── Schedule
     ├── ScheduleException
     └── Appointment
```

Mais detalhes:

- [Documentação do banco](docs/database.md)

---

## ⏰ Disponibilidade

A regra de disponibilidade considera:

- Estabelecimento;
- Serviço;
- Dia da semana;
- Horário de abertura;
- Horário de fechamento;
- Duração do serviço;
- Exceções de agenda;
- Estabelecimento fechado;
- Agendamentos existentes;
- Conflitos de horário.

A implementação principal está localizada em:

```text
app/core/availability.py
```

---

## 🧩 API

Principais recursos implementados:

```text
/auth
    POST /auth/register
    POST /auth/login

/services
    POST   /services
    GET    /services
    GET    /services/<id>
    PUT    /services/<id>
    DELETE /services/<id>

/schedules
    POST   /schedules
    GET    /schedules
    GET    /schedules/<id>
    PUT    /schedules/<id>
    DELETE /schedules/<id>

/appointments
    POST   /appointments
    GET    /appointments
    GET    /appointments/<id>
    PUT    /appointments/<id>
    DELETE /appointments/<id>
```

Os endpoints administrativos são protegidos por JWT e utilizam o estabelecimento associado ao usuário autenticado.

Mais detalhes:

- [Documentação da API](docs/api.md)

---

## 🧪 Testes

O projeto utiliza Pytest.

Executar todos os testes:

```bash
pytest -v
```

Os testes cobrem:

- Health check;
- Disponibilidade;
- Conflitos de horário;
- Exceções de horário;
- Criação de serviços;
- Listagem;
- Consulta individual;
- Atualização;
- Atualização parcial;
- Exclusão lógica;
- Recursos inexistentes;
- Autenticação;
- Autorização;
- Isolamento entre estabelecimentos;
- Criação e gerenciamento de agendamentos;
- Cancelamento e reativação de agendamentos;
- Validação de horários e timezone.

---

## 🐳 Executando com Docker

Subir a aplicação:

```bash
docker compose up --build
```

Verificar containers:

```bash
docker compose ps
```

A aplicação ficará disponível em:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/health
```

Para parar:

```bash
docker compose down
```

---

## 🗃️ Migrations

Criar uma migration:

```bash
flask --app app db migrate -m "descricao da alteracao"
```

Aplicar:

```bash
flask --app app db upgrade
```

Verificar migration atual:

```bash
flask --app app db current
```

Verificar head:

```bash
flask --app app db heads
```

Estado atual da cadeia de migrations:

```text
6604689ef554 (head)
```

---

## 📁 Estrutura do projeto

```text
techlegacy-agendamento/
│
├── app/
│   ├── auth/
│   │   ├── routes.py
│   │   ├── context.py
│   │   └── decorators.py
│   │
│   ├── core/
│   │   ├── availability.py
│   │   └── errors.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── establishment.py
│   │   ├── user.py
│   │   ├── service.py
│   │   ├── schedule.py
│   │   ├── schedule_exception.py
│   │   └── appointment.py
│   │
│   ├── services/
│   │   └── routes.py
│   │
│   ├── appointments/
│   │   ├── routes.py
│   │   └── validation.py
│   │
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── business-rules.md
│   ├── api.md
│   ├── development.md
│   └── roadmap.md
│
├── migrations/
│
├── tests/
│   ├── conftest.py
│   ├── test_availability.py
│   ├── test_health.py
│   ├── test_services.py
│   ├── test_schedules.py
│   ├── test_schedule_exceptions.py
│   └── test_appointments.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [Architecture](docs/architecture.md) | Arquitetura e organização |
| [Database](docs/database.md) | Modelos e banco |
| [Business Rules](docs/business-rules.md) | Regras de negócio |
| [API](docs/api.md) | Endpoints |
| [Development](docs/development.md) | Ambiente de desenvolvimento |
| [Roadmap](docs/roadmap.md) | Evolução do projeto |

---

## 🔄 Fluxo de desenvolvimento

O fluxo adotado para novas funcionalidades é:

```text
Alterar código
      │
      ▼
Criar/atualizar testes
      │
      ▼
Executar pytest
      │
      ▼
Alterar models, se necessário
      │
      ▼
Criar migration
      │
      ▼
Aplicar migration
      │
      ▼
Executar testes novamente
      │
      ▼
Commit
```

---

## 🎯 Princípios do projeto

O desenvolvimento segue alguns princípios:

- Código simples antes de código complexo;
- Separação por domínio;
- Regras de negócio fora das rotas quando possível;
- Banco versionado através de migrations;
- Testes automatizados;
- Evolução incremental;
- Evitar complexidade prematura;
- Preparação para CI/CD;
- Arquitetura preparada para multi-tenancy;
- Segurança e isolamento por tenant;
- Manter ML como evolução do produto, não como complexidade prematura do MVP.

---

## 📄 Licença

Projeto desenvolvido para fins de estudo, portfólio e evolução profissional.

A licença definitiva será definida posteriormente.
