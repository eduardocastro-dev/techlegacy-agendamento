# 🚀 TechLegacy Agendamento

Sistema de agendamento para pequenos estabelecimentos.

O projeto tem como objetivo disponibilizar uma plataforma simples para que estabelecimentos possam configurar seus serviços, horários de atendimento e receber agendamentos de clientes através de uma página pública.

O sistema está sendo desenvolvido de forma incremental, com foco em organização de código, regras de negócio, testes automatizados, containerização, autenticação, multi-tenancy e, posteriormente, CI/CD e deploy.

---

## 🎯 Objetivo

O TechLegacy Agendamento pretende permitir que um estabelecimento:

- Cadastre sua conta;
- Utilize um período de teste gratuito;
- Cadastre seus serviços;
- Configure seus horários de atendimento;
- Defina exceções de agenda;
- Consulte sua disponibilidade;
- Receba agendamentos;
- Gerencie seus horários;
- Disponibilize uma página pública para seus clientes;
- Acompanhe seus agendamentos através de um dashboard;
- Configure informações do estabelecimento;
- Gerencie sua conta e credenciais.

A primeira versão está sendo desenvolvida como um **monólito modular**, mantendo os domínios organizados para permitir evolução futura.

---

## 🛠️ Stack

### Backend
- Python 3.11
- Flask
- SQLAlchemy
- Flask-Migrate
- Alembic
- Flask-JWT-Extended
- Werkzeug

### Frontend
- HTML5
- CSS3
- JavaScript
- Fetch API
- Session Storage

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
- Backup
- Integrações externas
- Notificações

---

# 📌 Status atual

🚧 **Projeto em desenvolvimento**

## Fase 1 — Fundação
- [x] Estrutura inicial
- [x] Flask
- [x] Configuração de ambiente
- [x] Docker
- [x] Docker Compose
- [x] PostgreSQL
- [x] Endpoint `/health`
- [x] Estrutura inicial de testes

## Fase 2 — Núcleo de negócio
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

## Fase 3 — API REST
- [x] API de Services
- [x] API de Schedules
- [x] API de Schedule Exceptions
- [x] API de Appointments
- [x] Validação de entrada
- [x] Tratamento padronizado de erros
- [x] Isolamento por estabelecimento
- [x] Testes automatizados dos endpoints

## Fase 4 — Autenticação e Multi-tenancy
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
- [x] Trial gratuito de 30 dias

## Fase 5 — Dashboard e Área Administrativa
- [x] Dashboard administrativo
- [x] Gerenciamento de serviços
- [x] Gerenciamento de horários
- [x] Gerenciamento de exceções de agenda
- [x] Visualização da agenda
- [x] Gerenciamento de agendamentos
- [x] Visão geral do estabelecimento
- [x] Configurações do estabelecimento
- [x] Configuração de dados da conta
- [x] Alteração de senha
- [x] Logout
- [x] Interface administrativa
- [x] Validação de dados no frontend
- [x] Integração frontend com API

## Fase 5.5 — Interface de Autenticação
- [x] Página de login
- [x] Página de cadastro
- [x] Validação de formulário
- [x] Integração com API de autenticação
- [x] Armazenamento do JWT no navegador
- [x] Redirecionamento após login
- [x] Redirecionamento após cadastro
- [x] Mensagens de sucesso e erro
- [x] Identidade visual consistente com o dashboard

## Fase 6 — Agendamento público
- [x] Página pública do estabelecimento
- [x] Identificação do estabelecimento por slug
- [x] Seleção de serviço
- [x] Consulta de disponibilidade
- [x] Seleção de data
- [x] Seleção de horário
- [x] Cadastro do cliente
- [x] Criação do agendamento
- [x] Confirmação
- [x] Tratamento de conflitos em tempo real

## Fase 7 — Qualidade e Segurança
- [ ] Lint
- [ ] Padronização de código
- [ ] Logging
- [ ] Revisão de segurança
- [ ] Testes de integração
- [ ] Testes de cenários críticos
- [ ] Rate limiting
- [ ] Melhorias no tratamento de erros

## Fase 8 — CI/CD e Automação de Pipeline
- [ ] GitHub Actions
- [ ] Lint automatizado
- [ ] Execução de testes no Pull Request
- [ ] Build Docker automatizado
- [ ] Pipeline CI
- [ ] Pipeline CD
- [ ] Deploy automatizado

## Fase 9 — Produção
- [ ] Configuração do ambiente de produção
- [ ] Deploy no servidor Contabo
- [ ] Banco de produção
- [ ] Variáveis de ambiente
- [ ] HTTPS
- [ ] Monitoramento
- [ ] Backup
- [ ] Estratégia de recuperação

## Fase 10 — Evolução SaaS e ML
- [ ] Evolução para modelo SaaS
- [ ] Métricas de uso
- [ ] Previsão de demanda
- [ ] Insights sobre agendamentos
- [ ] Experimentação com modelos de Machine Learning
- [ ] Monitoramento de modelos
- [ ] Automação de pipelines de ML

---

# 🔐 Autenticação e Multi-tenancy

A área administrativa utiliza autenticação baseada em JWT.

O usuário autenticado está associado a um estabelecimento e o contexto do estabelecimento é obtido através do usuário autenticado.

Dessa forma, endpoints administrativos não dependem de `establishment_id` enviado pelo cliente para determinar o tenant.

O sistema também possui testes de isolamento para garantir que um usuário de um estabelecimento não consiga acessar recursos pertencentes a outro estabelecimento.

### Fluxo de autenticação

```text
Cadastro
   │
   ▼
Establishment + User
   │
   ▼
Trial de 30 dias
   │
   ▼
Login
   │
   ▼
JWT
   │
   ▼
Dashboard
   │
   ├── Serviços
   ├── Agenda
   ├── Horários
   └── Configurações
```

---

# 🏢 Trial gratuito

Durante o cadastro, o estabelecimento recebe automaticamente um período de teste de **30 dias**.

O término do período é armazenado no campo:

```text
Establishment.trial_ends_at
```

O período é calculado no momento da criação do estabelecimento.

---

# 🗄️ Banco de dados

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

# ⏰ Disponibilidade

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
- Conflitos de horário;
- Agendamentos cancelados;
- Exclusão de agendamento durante edição, quando aplicável.

A implementação principal está localizada em:

```text
app/core/availability.py
```

---

# 🧩 Dashboard

A área administrativa possui uma interface web integrada à API.

Principais áreas:

```text
Dashboard
   │
   ├── Visão geral
   ├── Agenda
   ├── Serviços
   ├── Horários
   └── Configurações
```

### Serviços

Permite criar, consultar, editar e desativar serviços.

### Horários

Permite configurar horários semanais, abertura, fechamento, dias ativos, exceções e dias fechados.

### Configurações

Permite gerenciar nome do estabelecimento, telefone, identificador público, e-mail e senha.

---

# 🔑 Interface de autenticação

O sistema possui interfaces próprias para autenticação:

```text
/login
/cadastro
```

Após autenticação, o JWT é armazenado no `sessionStorage` do navegador e o usuário é direcionado para o dashboard.

---

# 🧩 API

Principais recursos implementados:

```text
/auth
    POST /auth/register
    POST /auth/login

/dashboard
    GET /dashboard

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

/schedule-exceptions
    POST   /schedule-exceptions
    GET    /schedule-exceptions
    GET    /schedule-exceptions/<id>
    PUT    /schedule-exceptions/<id>
    DELETE /schedule-exceptions/<id>

/appointments
    POST   /appointments
    GET    /appointments
    GET    /appointments/<id>
    PUT    /appointments/<id>
    DELETE /appointments/<id>

/settings
    GET /settings
    PUT /settings

/settings/account
    GET /settings/account
    PUT /settings/account

/settings/password
    PUT /settings/password
```

Os endpoints administrativos são protegidos por JWT e utilizam o estabelecimento associado ao usuário autenticado.

Mais detalhes:

- [Documentação da API](docs/api.md)

---

# 🧪 Testes

O projeto utiliza Pytest.

Executar todos os testes:

```bash
pytest -v
```

Os testes cobrem health check, disponibilidade, serviços, horários, exceções, agendamentos, autenticação, autorização, isolamento entre estabelecimentos, timezone e configurações de conta.

---

# 🐳 Executando com Docker

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

Login:

```text
http://localhost:5000/login
```

Cadastro:

```text
http://localhost:5000/cadastro
```

Para parar:

```bash
docker compose down
```

---

# 🗃️ Migrations

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

# 📁 Estrutura do projeto

```text
techlegacy-agendamento/
│
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── views.py
│   │   ├── context.py
│   │   └── decorators.py
│   │
│   ├── core/
│   │   ├── availability.py
│   │   └── errors.py
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── agenda_service.py
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
│   ├── appointments/
│   │   ├── routes.py
│   │   └── validation.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── validation.py
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── cadastro.html
│   │   └── dashboard/
│   │       ├── index.html
│   │       ├── agenda.html
│   │       ├── services.html
│   │       ├── horarios.html
│   │       └── configuracoes.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── dashboard.css
│   │   │   ├── agenda.css
│   │   │   ├── services.css
│   │   │   ├── horarios.css
│   │   │   ├── configuracoes.css
│   │   │   ├── login.css
│   │   │   └── cadastro.css
│   │   └── js/
│   │       ├── dashboard.js
│   │       ├── agenda.js
│   │       ├── services.js
│   │       ├── horarios.js
│   │       ├── configuracoes.js
│   │       ├── login.js
│   │       └── cadastro.js
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
├── tests/
│   ├── conftest.py
│   ├── test_availability.py
│   ├── test_health.py
│   ├── test_services.py
│   ├── test_schedules.py
│   ├── test_schedule_exceptions.py
│   ├── test_appointments.py
│   ├── test_settings_account.py
│   └── test_settings_password.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 📚 Documentação

| Documento | Descrição |
|---|---|
| [Architecture](docs/architecture.md) | Arquitetura e organização |
| [Database](docs/database.md) | Modelos e banco |
| [Business Rules](docs/business-rules.md) | Regras de negócio |
| [API](docs/api.md) | Endpoints |
| [Development](docs/development.md) | Ambiente de desenvolvimento |
| [Roadmap](docs/roadmap.md) | Evolução do projeto |

---

# 🔄 Fluxo de desenvolvimento

O fluxo adotado para novas funcionalidades é:

```text
Definir funcionalidade
       │
       ▼
Implementar código
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
Criar migration, se necessário
       │
       ▼
Aplicar migration
       │
       ▼
Executar testes novamente
       │
       ▼
Revisar código
       │
       ▼
Commit
       │
       ▼
Push
```

Com a implementação futura de CI/CD, parte dessas validações será automatizada através do GitHub Actions.

---

# 🎯 Princípios do projeto

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
- Frontend simples integrado à API;
- Manter ML como evolução do produto, não como complexidade prematura do MVP.

---

# 📄 Licença

Projeto desenvolvido para fins de estudo, portfólio e evolução profissional.

A licença definitiva será definida posteriormente.
