# Roadmap

## 1. Visão geral

O **TechLegacy Agendamento** está sendo desenvolvido de forma incremental, priorizando primeiro a construção de um núcleo de negócio sólido e testável e, posteriormente, a evolução para autenticação, interface, agendamento público, automação e produção.

O roadmap é dividido em fases para que cada etapa entregue uma parte funcional do sistema.

A estratégia é:

```text
Fundação
   ↓
Núcleo de negócio
   ↓
API
   ↓
Autenticação
   ↓
Dashboard
   ↓
Agendamento público
   ↓
Qualidade
   ↓
CI/CD
   ↓
Produção
```

---

## 2. Princípios do roadmap

O desenvolvimento segue alguns princípios:

- Evolução incremental;
- Entregas funcionais por fase;
- Testes acompanhando as funcionalidades;
- Banco de dados versionado;
- Documentação evoluindo junto com o código;
- Evitar complexidade prematura;
- Adicionar tecnologias somente quando houver necessidade real;
- Manter o sistema executável durante todo o desenvolvimento;
- Preparar o projeto para automação e produção desde o início.

---

## 3. Status geral

| Fase    | Descrição                     | Status          |
| ------- | ----------------------------- | --------------- |
| Fase 1  | Fundação do projeto           | ✅ Concluída    |
| Fase 2  | Núcleo de negócio             | ✅ Concluída    |
| Fase 3  | API REST                      | 🟡 Em evolução  |
| Fase 4  | Autenticação e multi-tenancy  | ⏳ Planejada    |
| Fase 5  | Dashboard administrativo      | ⏳ Planejada    |
| Fase 6  | Agendamento público           | ⏳ Planejada    |
| Fase 7  | Qualidade e segurança         | ⏳ Planejada    |
| Fase 8  | CI/CD                         | ⏳ Planejada    |
| Fase 9  | Produção e deploy             | ⏳ Planejada    |
| Fase 10 | Evoluções futuras             | ⏳ Planejada    |

---

## 4. Fase 1 — Fundação

### Objetivo

Criar a estrutura inicial do projeto e garantir que a aplicação possa ser executada de maneira reproduzível.

### Entregas

- [x] Estrutura inicial do projeto
- [x] Flask
- [x] Configuração por variáveis de ambiente
- [x] Dockerfile
- [x] Docker Compose
- [x] PostgreSQL
- [x] Endpoint `/health`
- [x] Pytest
- [x] Estrutura inicial de testes

### Resultado

A aplicação passou a possuir uma base executável utilizando:

```text
Flask
 +
Docker
 +
PostgreSQL
 +
Pytest
```

---

## 5. Fase 2 — Núcleo de negócio

### Objetivo

Construir as entidades principais e as regras fundamentais do sistema.

### Banco de dados

- [x] Establishment
- [x] User
- [x] Service
- [x] Schedule
- [x] ScheduleException
- [x] Appointment

### Migrations

- [x] Flask-Migrate
- [x] Alembic
- [x] Migrations versionadas
- [x] PostgreSQL atualizado através das migrations

### Regras de negócio

- [x] Associação por estabelecimento
- [x] Serviços ativos/inativos
- [x] Soft delete de Services
- [x] Horários por dia da semana
- [x] Exceções de agenda
- [x] Estabelecimento fechado em determinada data
- [x] Duração dos serviços
- [x] Detecção de conflitos
- [x] Agendamentos cancelados não bloqueiam disponibilidade

### Disponibilidade

- [x] Availability Engine
- [x] Cálculo de horários
- [x] Consideração da duração do serviço
- [x] Consideração dos horários de funcionamento
- [x] Aplicação das exceções
- [x] Verificação de agendamentos existentes

### Testes

- [x] Testes de disponibilidade
- [x] Testes de conflitos
- [x] Testes de exceções
- [x] Testes de Services
- [x] Teste de health check

### Resultado atual

```text
17 testes passando
```

---

## 6. Fase 3 — API REST

### Objetivo

Disponibilizar o núcleo do sistema através de uma API REST organizada por domínio.

### Services

- [x] `POST /services`
- [x] `GET /services`
- [x] `GET /services/<id>`
- [x] `PUT /services/<id>`
- [x] `DELETE /services/<id>`

### API

- [x] Flask Blueprint
- [x] Respostas JSON
- [x] Códigos HTTP básicos
- [x] Tratamento de recurso inexistente
- [x] Isolamento inicial por `establishment_id`

### Testes

- [x] POST
- [x] GET
- [x] GET individual
- [x] PUT
- [x] Atualização parcial
- [x] DELETE
- [x] Soft delete

### Melhorias ainda previstas

- [ ] Validação estruturada de payloads
- [ ] Padronização global de erros
- [ ] Paginação
- [ ] OpenAPI
- [ ] Melhor tratamento de tipos e valores
- [ ] Logging

---

## 7. Fase 4 — Autenticação e Multi-tenancy

### Objetivo

Substituir o `establishment_id` informado diretamente pela aplicação por um contexto obtido através do usuário autenticado.

### Autenticação

- [ ] Cadastro
- [ ] Login
- [ ] JWT
- [ ] Refresh token
- [ ] Logout/invalidação quando aplicável
- [ ] Endpoint de usuário autenticado

### Autorização

- [ ] Usuário associado ao estabelecimento
- [ ] Validação de acesso aos recursos
- [ ] Proteção das rotas administrativas
- [ ] Impedir acesso cruzado entre estabelecimentos

### Evolução

Atualmente:

```text
GET /services?establishment_id=1
```

Futuro:

```text
Authorization: Bearer <token>
        │
        ▼
Usuário autenticado
        │
        ▼
Establishment associado
        │
        ▼
Recursos autorizados
```

---

## 8. Fase 5 — Dashboard administrativo

### Objetivo

Criar uma interface para que o estabelecimento possa administrar sua operação.

### Dashboard

- [ ] Login
- [ ] Tela inicial
- [ ] Visão geral
- [ ] Total de agendamentos
- [ ] Próximos agendamentos
- [ ] Status da agenda

### Serviços

- [ ] Listagem
- [ ] Criar serviço
- [ ] Editar serviço
- [ ] Desativar serviço
- [ ] Reativar serviço

### Agenda

- [ ] Visualização semanal
- [ ] Visualização mensal
- [ ] Configuração de horários
- [ ] Exceções
- [ ] Dias fechados

### Agendamentos

- [ ] Listagem
- [ ] Detalhes
- [ ] Cancelamento
- [ ] Alteração de horário
- [ ] Filtros

---

## 9. Fase 6 — Agendamento público

### Objetivo

Permitir que o cliente realize um agendamento através de um link público do estabelecimento.

Fluxo planejado:

```text
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
Nome + telefone
      │
      ▼
Confirmação
```

### Funcionalidades

- [ ] Link público por estabelecimento
- [ ] Página pública
- [ ] Listagem de serviços
- [ ] Consulta de disponibilidade
- [ ] Seleção de horário
- [ ] Nome do cliente
- [ ] Telefone do cliente
- [ ] Criação do Appointment
- [ ] Confirmação do agendamento

### Regras importantes

- [ ] Revalidar disponibilidade antes da criação
- [ ] Evitar agendamento duplicado
- [ ] Tratar concorrência
- [ ] Validar dados do cliente
- [ ] Garantir isolamento entre estabelecimentos

---

## 10. Fase 7 — Qualidade e segurança

### Objetivo

Aumentar a confiabilidade da aplicação antes do ambiente de produção.

### Qualidade

- [ ] Lint
- [ ] Formatter
- [ ] Type checking
- [ ] Test coverage
- [ ] Testes de integração
- [ ] Testes de API
- [ ] Testes de concorrência

### Segurança

- [ ] JWT seguro
- [ ] Hash de senha
- [ ] Validação de entrada
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Headers de segurança
- [ ] Proteção contra exposição de informações sensíveis
- [ ] Secrets fora do código

### Observabilidade

- [ ] Logging estruturado
- [ ] Logs de erros
- [ ] Logs de operações importantes
- [ ] Health check mais completo
- [ ] Monitoramento

---

## 11. Fase 8 — CI/CD

### Objetivo

Automatizar a validação e entrega do projeto.

Pipeline planejado:

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
    ├── Security Checks
    │
    └── Validation
            │
            ▼
          Deploy
```

### CI

- [ ] GitHub Actions
- [ ] Instalação das dependências
- [ ] Lint
- [ ] Testes
- [ ] Coverage
- [ ] Docker build
- [ ] Validação de migrations

### CD

- [ ] Ambiente de staging
- [ ] Deploy automatizado
- [ ] Migrations controladas
- [ ] Health check pós-deploy
- [ ] Rollback

### Regra principal

```text
Se os testes falharem
        ↓
Deploy bloqueado
```

---

## 12. Fase 9 — Produção e deploy

### Objetivo

Colocar o sistema em um ambiente de produção estável.

### Infraestrutura

- [ ] Servidor Contabo
- [ ] Docker Compose de produção
- [ ] PostgreSQL de produção
- [ ] Reverse proxy
- [ ] HTTPS
- [ ] Domínio
- [ ] DNS

### Segurança

- [ ] Secrets de produção
- [ ] Firewall
- [ ] Portas necessárias
- [ ] HTTPS
- [ ] Usuários sem privilégios desnecessários
- [ ] Backup do banco

### Operação

- [ ] Logs
- [ ] Monitoramento
- [ ] Health checks
- [ ] Backup automático
- [ ] Procedimento de restauração
- [ ] Processo de rollback

---

## 13. Fase 10 — Notificações e integrações

### Objetivo

Adicionar comunicação automática relacionada aos agendamentos.

Possíveis funcionalidades:

- [ ] Confirmação de agendamento
- [ ] Lembrete
- [ ] Cancelamento
- [ ] Reagendamento
- [ ] Integração com WhatsApp
- [ ] Integração com e-mail

A escolha das ferramentas deverá ocorrer somente quando existir uma necessidade concreta.

---

## 14. Fase 11 — Personalização

### Objetivo

Permitir que cada estabelecimento personalize sua página pública.

### Funcionalidades

- [ ] Logo
- [ ] Nome
- [ ] Cores
- [ ] Imagem de capa
- [ ] Informações de contato
- [ ] Descrição
- [ ] Serviços em destaque
- [ ] Personalização do link público

Exemplo conceitual:

```text
Estabelecimento
      │
      ▼
Personalização
      │
      ├── Logo
      ├── Cores
      ├── Capa
      └── Informações
             │
             ▼
       Página pública
```

---

## 15. Fase 12 — Planos e assinatura

### Objetivo

Transformar o sistema em um produto SaaS com possibilidade de planos comerciais.

O modelo já possui:

```text
trial_ends_at
```

para suportar o período de teste.

### Futuramente

- [ ] Definição de planos
- [ ] Limites por plano
- [ ] Assinatura
- [ ] Controle de status
- [ ] Upgrade
- [ ] Downgrade
- [ ] Cancelamento
- [ ] Integração de pagamento

Essa fase depende da definição do modelo comercial do produto.

---

## 16. Evolução do banco de dados

O banco poderá evoluir para incluir entidades adicionais.

Estado atual:

```text
establishments
      │
      ├── users
      ├── services
      ├── schedules
      ├── schedule_exceptions
      └── appointments
```

Possível evolução:

```text
establishments
      │
      ├── users
      ├── services
      ├── schedules
      ├── schedule_exceptions
      ├── appointments
      ├── subscriptions
      ├── notifications
      └── customization
```

Cada alteração estrutural deverá possuir uma migration correspondente.

---

## 17. Evolução da API

A API deverá crescer de acordo com os domínios do sistema.

### Atual

```text
GET    /health

POST   /services
GET    /services
GET    /services/<id>
PUT    /services/<id>
DELETE /services/<id>
```

### Futuro

```text
/auth
/establishments
/users
/services
/schedules
/schedule-exceptions
/availability
/appointments
/notifications
```

A implementação desses endpoints ocorrerá de forma incremental.

---

## 18. Possível arquitetura futura

A arquitetura continuará inicialmente como monólito modular.

Evolução esperada:

```text
                         ┌──────────────────┐
                         │      Cliente     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Página pública  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Flask API     │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
           Auth               Services            Schedule
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                            Availability
                                  │
                                  ▼
                            Appointments
                                  │
                                  ▼
                             PostgreSQL
```

A divisão em microsserviços não faz parte do roadmap atual.

---

## 19. Machine Learning e MLOps

Machine Learning não faz parte do núcleo inicial do produto.

A intenção é evitar adicionar ML apenas para utilizar uma tecnologia.

Caso surja uma necessidade real baseada em dados, uma evolução futura poderá utilizar ML para problemas como:

```text
Histórico de agendamentos
        │
        ▼
Análise de demanda
        │
        ▼
Previsão de horários de maior procura
        │
        ▼
Apoio à gestão do estabelecimento
```

Possíveis aplicações futuras:

- Previsão de demanda;
- Identificação de horários de maior procura;
- Previsão de cancelamentos;
- Sugestão de capacidade;
- Recomendação de horários.

Caso essa etapa seja implementada, o projeto poderá evoluir para práticas de MLOps como:

```text
Dados
  │
  ▼
Treinamento
  │
  ▼
Avaliação
  │
  ▼
Model Registry
  │
  ▼
Deploy
  │
  ▼
Monitoramento
```

Essa evolução somente deverá ocorrer quando houver dados e uma necessidade de negócio que justifique o uso de Machine Learning.

---

## 20. Critérios para considerar uma fase concluída

Uma fase não será considerada concluída apenas porque o código foi escrito.

Sempre que aplicável, uma fase deverá possuir:

- [ ] Implementação
- [ ] Testes
- [ ] Banco atualizado
- [ ] Migrations
- [ ] Documentação
- [ ] Validação manual
- [ ] Código versionado

Para fases de infraestrutura:

- [ ] Ambiente reproduzível
- [ ] Health check
- [ ] Logs
- [ ] Processo de recuperação

Para fases de CI/CD:

- [ ] Pipeline funcionando
- [ ] Testes automatizados
- [ ] Build validado
- [ ] Deploy controlado

---

## 21. Estratégia de releases

O projeto deverá evoluir através de versões incrementais.

Exemplo:

```text
v0.1.0
Fundação

v0.2.0
Núcleo de negócio

v0.3.0
API

v0.4.0
Autenticação

v0.5.0
Dashboard

v0.6.0
Agendamento público

v0.7.0
Qualidade e segurança

v0.8.0
CI/CD

v1.0.0
Produção
```

As versões são uma referência de evolução e poderão ser ajustadas conforme o escopo real de cada entrega.

---

## 22. Roadmap visual

```text
                    TECHLEGACY AGENDAMENTO

                           START
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 1          │
                    │ Fundação        │
                    │       ✅        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 2          │
                    │ Núcleo negócio  │
                    │       ✅        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 3          │
                    │ API REST        │
                    │       🟡        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 4          │
                    │ Auth + Tenant   │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 5          │
                    │ Dashboard       │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 6          │
                    │ Booking público │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 7          │
                    │ Qualidade       │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 8          │
                    │ CI/CD           │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FASE 9          │
                    │ Produção        │
                    │       ⏳        │
                    └────────┬────────┘
                             │
                             ▼
                           v1.0
```

---

## 23. Estado atual

No momento:

```text
FASE 1 — Fundação
████████████████████ 100%

FASE 2 — Núcleo de negócio
████████████████████ 100%

FASE 3 — API REST
████████████████░░░░ 80%

FASE 4 — Auth + Multi-tenancy
░░░░░░░░░░░░░░░░░░░░ 0%

FASE 5 — Dashboard
░░░░░░░░░░░░░░░░░░░░ 0%

FASE 6 — Agendamento público
░░░░░░░░░░░░░░░░░░░░ 0%

FASE 7 — Qualidade
░░░░░░░░░░░░░░░░░░░░ 0%

FASE 8 — CI/CD
░░░░░░░░░░░░░░░░░░░░ 0%

FASE 9 — Produção
░░░░░░░░░░░░░░░░░░░░ 0%
```

Os percentuais são apenas uma referência visual e não representam métricas formais de progresso.

---

## 24. Próxima etapa

Com a fundação, banco, regras de negócio, disponibilidade e CRUD de Services implementados, a próxima evolução deve continuar a API REST e preparar o projeto para a camada de autenticação.

Prioridades:

```text
1. Finalizar documentação atual
        │
        ▼
2. Consolidar API
        │
        ▼
3. Melhorar validações
        │
        ▼
4. Implementar autenticação
        │
        ▼
5. Consolidar multi-tenancy
```

---

## 25. Visão de longo prazo

A visão do TechLegacy Agendamento é evoluir de um MVP funcional para uma aplicação SaaS de agendamento com:

```text
                    TechLegacy
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   Administração     Cliente          Dados
        │               │               │
        ▼               ▼               ▼
     Dashboard      Booking          Analytics
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
                    Automação
                        │
                        ▼
                     CI/CD
                        │
                        ▼
                   Produção
                        │
                        ▼
                  Futuro: ML
```

O objetivo é construir essa evolução sem perder a simplicidade do núcleo do sistema.

---

## 26. Resumo

O roadmap do projeto segue uma estratégia de crescimento gradual:

```text
Fundação
   ↓
Domínio
   ↓
API
   ↓
Autenticação
   ↓
Dashboard
   ↓
Booking
   ↓
Qualidade
   ↓
CI/CD
   ↓
Produção
   ↓
Evoluções orientadas por dados
```

Cada etapa deverá aumentar a capacidade do sistema sem introduzir complexidade que ainda não seja necessária.

O foco principal é construir um produto funcional, testável, documentado, automatizável e preparado para evolução.