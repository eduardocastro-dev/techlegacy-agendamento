# Arquitetura

## 1. Visão geral

O **TechLegacy Agendamento** utiliza inicialmente uma arquitetura de **monólito modular**.

A aplicação é executada como um único serviço Flask, porém suas responsabilidades são organizadas em módulos e domínios independentes.

A escolha do monólito modular tem como objetivo manter o projeto simples durante as primeiras etapas de desenvolvimento, evitando complexidade prematura e permitindo que novas funcionalidades sejam adicionadas de forma organizada.

A arquitetura atual foi construída considerando uma futura evolução para autenticação, multi-tenancy, dashboard, agendamento público, integrações e CI/CD.

---

## 2. Arquitetura atual

A estrutura atual pode ser representada da seguinte forma:

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
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      Establishments            Services              Schedules
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                           Business Rules
                                    │
                                    ▼
                             Appointments
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    PostgreSQL 16    │
                         └─────────────────────┘
```

---

## 3. Componentes principais

### 3.1 Flask

O Flask é responsável pela aplicação HTTP.

Suas principais responsabilidades são:

- Inicialização da aplicação;
- Configuração;
- Registro de blueprints;
- Exposição dos endpoints;
- Integração com SQLAlchemy;
- Integração com Flask-Migrate.

O ponto principal de inicialização está em:

```text
app/__init__.py
```

### 3.2 Configuration

As configurações da aplicação estão centralizadas em:

```text
app/config.py
```

As configurações utilizam variáveis de ambiente.

Entre as configurações utilizadas estão:

- `SECRET_KEY`;
- conexão com PostgreSQL;
- usuário do banco;
- senha;
- host;
- porta;
- nome do banco.

Informações sensíveis não devem ser armazenadas diretamente no código ou versionadas no Git.

### 3.3 Extensions

As extensões utilizadas pela aplicação são inicializadas em:

```text
app/extensions.py
```

Atualmente:

- SQLAlchemy
- Flask-Migrate

A centralização dessas extensões evita que sua inicialização fique acoplada a módulos específicos.

---

## 4. Organização por domínio

A aplicação está organizada de acordo com as responsabilidades do sistema.

```text
app/
│
├── core/
│
├── models/
│
├── services/
│
├── config.py
├── extensions.py
└── __init__.py
```

### 4.1 Models

Os modelos representam as entidades persistidas no banco de dados.

Localização:

```text
app/models/
```

Atualmente existem:

- Establishment
- User
- Service
- Schedule
- ScheduleException
- Appointment

#### Relacionamento conceitual

```text
                    Establishment
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        Users         Services       Schedules
                         │
                         │
                         ▼
                    Appointments

                    Establishment
                         │
                         ▼
                 ScheduleException
```

O `Establishment` funciona como a entidade central para isolamento dos dados.

---

## 5. Core — Regras de negócio

As regras de negócio que não pertencem diretamente à camada HTTP ficam em:

```text
app/core/
```

Atualmente existe:

```text
app/core/availability.py
```

Esse módulo é responsável pelo cálculo de disponibilidade.

### 5.1 Regra de disponibilidade

A disponibilidade considera:

- Estabelecimento;
- Serviço;
- Serviço ativo;
- Data solicitada;
- Dia da semana;
- Horário configurado;
- Exceções de agenda;
- Agendamentos existentes;
- Conflitos de horário;
- Duração do serviço.

Fluxo:

```text
Solicitação de disponibilidade
            │
            ▼
       Serviço existe?
            │
       ┌────┴────┐
       │         │
      Não       Sim
       │         │
       ▼         ▼
    []       Serviço ativo?
                    │
               ┌────┴────┐
               │         │
              Não       Sim
               │         │
               ▼         ▼
              []     Horário existe?
                            │
                            ▼
                     Verificar exceção
                            │
                            ▼
                    Verificar conflitos
                            │
                            ▼
                  Gerar horários disponíveis
```

---

## 6. Services

As rotas relacionadas aos serviços estão em:

```text
app/services/routes.py
```

O blueprint utiliza:

```text
/services
```

Atualmente estão implementados:

```text
POST   /services
GET    /services
GET    /services/<id>
PUT    /services/<id>
DELETE /services/<id>
```

O CRUD de Services representa a primeira implementação completa da camada de API REST do projeto.

---

## 7. Banco de dados

O sistema utiliza:

```text
PostgreSQL 16
```

A comunicação é realizada através do SQLAlchemy.

O controle de alterações estruturais utiliza:

```text
Flask-Migrate
       │
       ▼
    Alembic
       │
       ▼
 PostgreSQL
```

As migrations ficam armazenadas em:

```text
migrations/
```

A migration atual do projeto é:

```text
6604689ef554
```

---

## 8. Containerização

O ambiente de desenvolvimento utiliza Docker e Docker Compose.

Arquitetura atual:

```text
                 Docker Compose
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
      Flask Application       PostgreSQL
          :5000                  :5432
```

A aplicação Flask é executada em um container separado do banco de dados.

Isso permite que o ambiente seja reproduzido de forma mais consistente em diferentes máquinas.

---

## 9. Testes

Os testes automatizados estão localizados em:

```text
tests/
```

Atualmente existem testes para:

- `test_health.py`
- `test_availability.py`
- `test_services.py`

A aplicação possui atualmente:

```text
17 testes passando
```

Execução:

```bash
pytest -v
```

Os testes verificam principalmente:

- Health check;
- disponibilidade;
- conflitos de horários;
- exceções de agenda;
- CRUD de Services;
- soft delete;
- recursos inexistentes.

---

## 10. Multi-tenancy

O modelo de dados foi projetado considerando múltiplos estabelecimentos.

As entidades relacionadas ao estabelecimento possuem:

```text
establishment_id
```

Exemplo:

```text
Service
   │
   └── establishment_id
```

Isso permite associar cada registro ao estabelecimento correspondente.

### Estado atual

Neste estágio, o `establishment_id` ainda pode ser informado diretamente na requisição da API.

Exemplo:

```text
GET /services?establishment_id=1
```

Essa abordagem é utilizada apenas durante a implementação inicial.

### Evolução planejada

Posteriormente será implementada autenticação através de JWT.

O fluxo planejado será:

```text
Usuário
   │
   ▼
Login
   │
   ▼
JWT
   │
   ▼
Usuário autenticado
   │
   ▼
Establishment associado
   │
   ▼
Dados do estabelecimento
```

Dessa forma, o cliente não precisará informar livremente o `establishment_id` para determinar o contexto da operação.

---

## 11. Segurança

A segurança será evoluída gradualmente.

Atualmente:

- Variáveis sensíveis são mantidas através de ambiente;
- `.env` não deve ser versionado;
- Os dados possuem `establishment_id`;
- Consultas de Services consideram o estabelecimento.

Ainda não implementado:

- JWT;
- Autorização;
- Controle de permissões;
- Rate limiting;
- HTTPS no ambiente de produção;
- Hardening da aplicação.

Esses itens fazem parte das etapas futuras do projeto.

---

## 12. Fluxo de dados

Um exemplo do fluxo atual para criação de um serviço:

```text
Cliente
   │
   │ POST /services
   ▼
Flask Route
   │
   ▼
Validação básica
   │
   ▼
Service Model
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
   │
   ▼
Response JSON
```

---

## 13. Fluxo de disponibilidade

Para consultar horários disponíveis:

```text
Cliente
   │
   ▼
Data + Serviço
   │
   ▼
Availability Engine
   │
   ├── Verifica serviço
   │
   ├── Verifica estabelecimento
   │
   ├── Verifica dia da semana
   │
   ├── Verifica horário
   │
   ├── Aplica exceção
   │
   ├── Consulta agendamentos
   │
   └── Verifica conflitos
   │
   ▼
Horários disponíveis
```

A lógica está centralizada em:

```text
app/core/availability.py
```

---

## 14. Soft Delete

Services utilizam exclusão lógica.

Quando o endpoint:

```text
DELETE /services/<id>
```

é executado, o registro não é removido fisicamente.

O campo:

```text
active
```

é alterado para:

```text
false
```

Fluxo:

```text
DELETE /services/1
        │
        ▼
Service encontrado
        │
        ▼
active = false
        │
        ▼
Commit no banco
        │
        ▼
Service deixa de aparecer
nas consultas de ativos
```

Essa estratégia preserva o registro no banco e evita a remoção física de dados relacionados ao histórico do sistema.

---

## 15. Decisões arquiteturais

### Monólito modular

Foi escolhido para manter a implementação inicial simples e organizada.

Não existe necessidade atual de dividir o sistema em múltiplos serviços independentes.

### PostgreSQL

Foi escolhido como banco principal por ser adequado ao domínio relacional do sistema e permitir uma evolução consistente do modelo de dados.

### SQLAlchemy

É utilizado como ORM para reduzir o acoplamento da aplicação à implementação específica das consultas SQL.

### Flask-Migrate

As migrations permitem versionar a estrutura do banco junto com o código da aplicação.

### Soft Delete

Foi adotado inicialmente para Services para evitar a remoção física desnecessária de registros.

### Regras de negócio separadas das rotas

A lógica de disponibilidade está em:

```text
app/core/availability.py
```

em vez de ficar diretamente dentro das rotas HTTP.

Isso facilita testes e evolução futura.

---

## 16. Evolução arquitetural planejada

A evolução prevista é:

```text
FASE 1
Fundação
   │
   ▼
FASE 2
Núcleo de negócio
   │
   ▼
FASE 3
API REST
   │
   ▼
FASE 4
JWT + Multi-tenancy
   │
   ▼
FASE 5
Dashboard
   │
   ▼
FASE 6
Agendamento público
   │
   ▼
FASE 7
Integrações
   │
   ▼
FASE 8
Qualidade + CI/CD
   │
   ▼
FASE 9
Produção
```

---

## 17. CI/CD futuro

A arquitetura de entrega planejada será:

```text
Developer
    │
    ▼
Git Push
    │
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Lint
    │
    ├── Tests
    │
    ├── Build Docker
    │
    └── Validation
            │
            ▼
          Deploy
```

O objetivo é evitar que uma alteração com testes quebrados seja publicada no ambiente de produção.

---

## 18. Princípios arquiteturais

O projeto segue os seguintes princípios:

- Simplicidade antes de complexidade;
- Separação de responsabilidades;
- Regras de negócio independentes da camada HTTP quando possível;
- Banco de dados versionado;
- Testes automatizados;
- Evolução incremental;
- Preparação para multi-tenancy;
- Preparação para CI/CD;
- Evitar tecnologias sem necessidade real;
- Manter o sistema executável durante toda a evolução.

---

## 19. Estado atual

A arquitetura atualmente possui:

```text
Flask                  ✅
SQLAlchemy             ✅
PostgreSQL             ✅
Docker                 ✅
Docker Compose         ✅
Migrations             ✅
Models                 ✅
Business Rules         ✅
Availability Engine    ✅
Services CRUD          ✅
Automated Tests        ✅
JWT                    ⏳
Multi-tenancy real     ⏳
Dashboard              ⏳
Public Booking         ⏳
CI/CD                  ⏳
Production Deploy      ⏳
```

A próxima evolução arquitetural será a expansão da API REST para os demais domínios do sistema.