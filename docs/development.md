# Desenvolvimento

## 1. Visão geral

Este documento descreve como configurar, executar, testar e evoluir o **TechLegacy Agendamento** durante o desenvolvimento.

O projeto utiliza um ambiente baseado em:

- Python 3.11;
- Flask;
- PostgreSQL 16;
- SQLAlchemy;
- Flask-Migrate;
- Docker;
- Docker Compose;
- Pytest.

A aplicação foi estruturada para permitir desenvolvimento incremental, mantendo o sistema executável a cada etapa.

---

## 2. Pré-requisitos

Antes de iniciar o desenvolvimento, é necessário possuir:

- Python 3.11;
- Docker Desktop;
- Docker Compose;
- Git.

Verifique as instalações:

```powershell
python --version
docker --version
docker compose version
git --version
```

O projeto utiliza Python 3.11 como versão de referência.

---

## 3. Estrutura do projeto

A estrutura principal atualmente é:

```text
techlegacy-agendamento/
│
├── app/
│   ├── core/
│   │   └── availability.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── appointment.py
│   │   ├── establishment.py
│   │   ├── schedule.py
│   │   ├── schedule_exception.py
│   │   ├── service.py
│   │   └── user.py
│   │
│   ├── services/
│   │   └── routes.py
│   │
│   ├── __init__.py
│   ├── config.py
│   └── extensions.py
│
├── migrations/
│
├── tests/
│   ├── conftest.py
│   ├── test_availability.py
│   ├── test_health.py
│   └── test_services.py
│
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 4. Configuração do ambiente

### 4.1 Variáveis de ambiente

O projeto utiliza variáveis de ambiente para configurar a aplicação e o banco de dados.

Arquivo de referência:

```text
.env.example
```

As variáveis principais são:

```text
SECRET_KEY
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
```

O arquivo:

```text
.env
```

contém os valores utilizados localmente e não deve ser versionado.

---

## 5. Ambiente virtual Python

O desenvolvimento local pode utilizar um ambiente virtual Python.

No Windows PowerShell:

```powershell
python -m venv .venv
```

Ativação:

```powershell
.\.venv\Scripts\Activate.ps1
```

Após ativar, o terminal deverá indicar o ambiente virtual.

Exemplo:

```text
(.venv) PS C:\...
```

---

## 6. Instalação das dependências

Com o ambiente virtual ativo:

```bash
pip install -r requirements.txt
```

Para verificar as dependências instaladas:

```bash
pip list
```

---

## 7. Executando com Docker

O ambiente principal de desenvolvimento utiliza Docker Compose.

Para iniciar os containers:

```bash
docker compose up -d
```

Para verificar o estado:

```bash
docker compose ps
```

A arquitetura local é:

```text
Docker Compose
      │
      ├───────────────┐
      │               │
      ▼               ▼
 Flask App        PostgreSQL
 :5000               :5432
```

---

## 8. Parando o ambiente

Para parar os containers:

```bash
docker compose down
```

Os dados do PostgreSQL são mantidos no volume Docker:

```text
postgres_data
```

Portanto, parar os containers não significa necessariamente apagar os dados.

---

## 9. Visualizar logs

Para visualizar os logs da aplicação:

```bash
docker compose logs app
```

Para acompanhar os logs em tempo real:

```bash
docker compose logs -f app
```

Para visualizar os logs do PostgreSQL:

```bash
docker compose logs postgres
```

---

## 10. Health Check

Após iniciar a aplicação, o endpoint:

```text
GET /health
```

pode ser utilizado para verificar se a aplicação está funcionando.

Localmente:

```text
http://localhost:5000/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "message": "TechLegacy Agendamento API is running"
}
```

---

## 11. Execução da aplicação

A aplicação Flask pode ser executada utilizando:

```bash
flask --app app run
```

Para desenvolvimento local:

```bash
flask --app app run --debug
```

Quando a aplicação estiver sendo executada através do Docker Compose, o container da aplicação será responsável pela execução do Flask.

---

## 12. Banco de dados

O PostgreSQL é executado através do Docker Compose.

Configuração conceitual:

```text
Host: localhost
Port: 5432
Database: definido em POSTGRES_DB
User: definido em POSTGRES_USER
Password: definido em POSTGRES_PASSWORD
```

Quando a aplicação é executada dentro do Docker Compose, o serviço PostgreSQL é acessado através do hostname:

```text
postgres
```

Durante comandos executados diretamente no ambiente Windows, o host utilizado localmente é:

```text
localhost
```

Essa diferença ocorre porque os containers utilizam a rede interna do Docker Compose.

---

## 13. Migrations

As alterações estruturais do banco são controladas através do Flask-Migrate.

Fluxo padrão:

```text
Alterar Model
     │
     ▼
Criar Migration
     │
     ▼
Revisar Migration
     │
     ▼
Aplicar Migration
     │
     ▼
Testar
```

### 13.1 Verificar migration atual

```bash
flask --app app db current
```

Atualmente o banco está na migration:

```text
6604689ef554
```

### 13.2 Verificar heads

```bash
flask --app app db heads
```

Resultado esperado:

```text
6604689ef554 (head)
```

### 13.3 Criar migration

Depois de alterar um model:

```bash
flask --app app db migrate -m "descrição da alteração"
```

Exemplo:

```bash
flask --app app db migrate -m "add service category"
```

### 13.4 Aplicar migration

```bash
flask --app app db upgrade
```

---

## 14. Regra importante para migrations

Alterações nos Models não devem ser consideradas aplicadas ao banco automaticamente.

O fluxo correto é:

```text
Model alterado
      │
      ▼
flask db migrate
      │
      ▼
Migration criada
      │
      ▼
Revisar arquivo
      │
      ▼
flask db upgrade
```

A migration deve fazer parte do versionamento do projeto.

---

## 15. Testes

Os testes automatizados utilizam Pytest.

Para executar toda a suíte:

```bash
pytest -v
```

Atualmente o projeto possui:

```text
17 testes passando
```

---

## 16. Banco utilizado nos testes

Os testes utilizam SQLite em memória:

```text
sqlite:///:memory:
```

Isso permite executar os testes de maneira rápida e isolada.

A fixture cria as tabelas:

```python
db.create_all()
```

e posteriormente remove:

```python
db.session.remove()
db.drop_all()
```

Dessa maneira, os testes não dependem dos dados existentes no PostgreSQL de desenvolvimento.

---

## 17. Estrutura dos testes

Os testes estão organizados em:

```text
tests/
├── conftest.py
├── test_health.py
├── test_availability.py
└── test_services.py
```

### `test_health.py`

Testa o endpoint:

```text
GET /health
```

### `test_availability.py`

Testa regras relacionadas à disponibilidade.

Entre elas:

- Horários disponíveis;
- Conflitos;
- Exceções;
- Estabelecimento fechado;
- Alterações de abertura;
- Alterações de fechamento.

### `test_services.py`

Testa o CRUD de Services:

- Criação;
- Listagem;
- Busca;
- Atualização;
- Atualização parcial;
- Exclusão lógica;
- Recursos inexistentes.

---

## 18. Executando testes específicos

Para executar somente os testes de Services:

```bash
pytest tests/test_services.py -v
```

Para executar somente os testes de disponibilidade:

```bash
pytest tests/test_availability.py -v
```

Para executar somente o health check:

```bash
pytest tests/test_health.py -v
```

---

## 19. Desenvolvimento orientado a testes

Novas funcionalidades devem preferencialmente seguir:

```text
Regra
  │
  ▼
Teste
  │
  ▼
Implementação
  │
  ▼
Teste passando
  │
  ▼
Refatoração
```

A intenção é evitar implementar funcionalidades sem uma forma automatizada de verificar seu comportamento.

---

## 20. Fluxo para adicionar uma funcionalidade

O desenvolvimento deve seguir um processo incremental.

### 1. Definir a regra

Antes de implementar, definir:

- O que a funcionalidade faz;
- Quais são suas entradas;
- Quais são suas saídas;
- Quais situações são inválidas;
- Como ela afeta o banco.

### 2. Alterar o Model, se necessário

Caso a funcionalidade exija novos dados:

```text
app/models/
```

deve ser atualizado.

### 3. Criar migration

```bash
flask --app app db migrate -m "..."
```

### 4. Aplicar migration

```bash
flask --app app db upgrade
```

### 5. Implementar regra de negócio

Quando a lógica for independente de HTTP, ela deve preferencialmente ficar em:

```text
app/core/
```

### 6. Implementar API

As rotas devem ficar organizadas por domínio.

### 7. Criar testes

Adicionar testes para os comportamentos esperados.

### 8. Executar a suíte completa

```bash
pytest -v
```

### 9. Revisar documentação

Atualizar os arquivos em:

```text
docs/
```

quando a mudança alterar comportamento, arquitetura, banco ou API.

---

## 21. Exemplo de evolução de Model

Supondo que seja necessário adicionar uma categoria ao Service.

Primeiro:

```text
app/models/service.py
```

é alterado.

Depois:

```bash
flask --app app db migrate -m "add service category"
```

Em seguida:

```bash
flask --app app db upgrade
```

Depois:

```text
tests/
```

deve receber os testes relacionados à nova funcionalidade.

Por fim:

```text
docs/database.md
docs/api.md
```

devem ser atualizados caso a mudança afete esses contratos.

---

## 22. Organização das responsabilidades

As responsabilidades devem permanecer separadas.

```text
HTTP
 │
 ▼
Routes
 │
 ▼
Business Rules
 │
 ▼
Models / ORM
 │
 ▼
PostgreSQL
```

Exemplo:

```text
app/services/routes.py
        │
        ▼
    Service
        │
        ▼
    SQLAlchemy
        │
        ▼
   PostgreSQL
```

Regras mais complexas não devem ser concentradas diretamente nas rotas.

---

## 23. Desenvolvimento do Availability Engine

A lógica de disponibilidade está em:

```text
app/core/availability.py
```

Ela recebe:

```text
establishment_id
service_id
target_date
```

e retorna uma lista de horários disponíveis.

Fluxo:

```text
establishment_id
        +
service_id
        +
target_date
        │
        ▼
Availability Engine
        │
        ├── Service
        ├── Schedule
        ├── ScheduleException
        └── Appointment
        │
        ▼
Available Slots
```

---

## 24. Desenvolvimento da API

A API atual utiliza Flask Blueprints.

Services:

```text
app/services/routes.py
```

Blueprint:

```python
services_bp = Blueprint(
    "services",
    __name__,
    url_prefix="/services",
)
```

Endpoints atuais:

```text
POST   /services
GET    /services
GET    /services/<id>
PUT    /services/<id>
DELETE /services/<id>
```

---

## 25. Boas práticas para novos endpoints

Novos endpoints devem:

- Utilizar métodos HTTP adequados;
- Retornar JSON;
- Utilizar códigos HTTP apropriados;
- Validar recursos relacionados ao estabelecimento;
- Possuir testes;
- Evitar duplicação de regras;
- Manter as responsabilidades separadas.

---

## 26. Tratamento de erros

A API atual possui tratamento básico para recursos inexistentes.

Exemplo:

```json
{
  "error": "Service not found"
}
```

Retorno:

```text
404 Not Found
```

O tratamento de erros será evoluído conforme a API crescer.

Possíveis melhorias futuras:

- Padronização global de erros;
- Validação de payload;
- Mensagens consistentes;
- Tratamento de exceções inesperadas;
- Logging estruturado.

---

## 27. Debug

Durante o desenvolvimento, o Flask pode ser executado em modo debug:

```bash
flask --app app run --debug
```

O modo debug deve ser utilizado apenas em desenvolvimento.

Não deve ser utilizado no ambiente de produção.

---

## 28. Git

O projeto utiliza Git para versionamento.

Fluxo básico:

```text
Alteração
   │
   ▼
Testes
   │
   ▼
Git status
   │
   ▼
Git add
   │
   ▼
Git commit
   │
   ▼
Git push
```

Verificar alterações:

```bash
git status
```

Adicionar arquivos:

```bash
git add .
```

Criar commit:

```bash
git commit -m "descrição da alteração"
```

Enviar para o repositório:

```bash
git push origin main
```

---

## 29. Commits

Os commits devem representar mudanças pequenas e compreensíveis.

Exemplos:

```text
feat: add services CRUD
test: add availability conflict tests
fix: correct service availability
docs: add database documentation
chore: update dependencies
```

A intenção é facilitar a leitura do histórico do projeto.

---

## 30. Fluxo de desenvolvimento recomendado

O fluxo recomendado para cada funcionalidade é:

```text
┌───────────────────────┐
│ Definir funcionalidade│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Definir regra negócio │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Criar/alterar Model   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Criar Migration       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Implementar regra     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Implementar API       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Criar testes          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ pytest -v             │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Atualizar documentação│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Commit + Push         │
└───────────────────────┘
```

---

## 31. CI/CD futuro

O processo manual atual deverá evoluir para automação através do GitHub Actions.

Fluxo planejado:

```text
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Lint
   │
   ├── Tests
   │
   ├── Docker Build
   │
   └── Validation
           │
           ▼
         Deploy
```

A ideia é impedir que alterações com testes quebrados avancem para produção.

---

## 32. Qualidade de código

A qualidade será evoluída gradualmente.

Itens planejados:

```text
Lint
Formatting
Type checking
Automated tests
Coverage
Logging
Security checks
Docker validation
CI/CD
```

Nem todos esses mecanismos estão implementados atualmente.

---

## 33. Ambiente de produção

O ambiente de produção deverá utilizar configuração diferente do desenvolvimento.

Princípios:

- Não utilizar Flask debug;
- Utilizar variáveis de ambiente;
- Utilizar credenciais próprias;
- Utilizar HTTPS;
- Utilizar banco de produção separado;
- Executar migrations de forma controlada;
- Monitorar logs;
- Possuir processo de backup;
- Automatizar deploy quando o CI/CD estiver implementado.

O deploy em produção ainda faz parte do roadmap.

---

## 34. Checklist antes de um commit

Antes de realizar um commit:

- [ ] Código implementado
- [ ] Regra de negócio revisada
- [ ] Testes adicionados
- [ ] `pytest -v` executado
- [ ] Migration criada, se necessário
- [ ] Migration aplicada, se necessário
- [ ] Documentação atualizada
- [ ] `.env` não está sendo versionado
- [ ] `git status` revisado

---

## 35. Checklist antes de um Pull Request

Quando o projeto passar a utilizar Pull Requests:

- [ ] Funcionalidade descrita
- [ ] Testes passando
- [ ] Migration revisada
- [ ] API documentada
- [ ] Regras de negócio documentadas
- [ ] Sem credenciais no código
- [ ] Sem arquivos temporários
- [ ] Docker funcionando
- [ ] CI passando

---

## 36. Troubleshooting

### Docker não inicia

Verificar se o Docker Desktop está em execução:

```bash
docker version
```

Depois:

```bash
docker compose ps
```

### Container da aplicação não inicia

Verificar logs:

```bash
docker compose logs app
```

### PostgreSQL não está disponível

Verificar:

```bash
docker compose ps
```

O container PostgreSQL deve estar saudável.

Também é possível consultar:

```bash
docker compose logs postgres
```

### Migration não funciona

Verificar:

```bash
flask --app app db current
```

e:

```bash
flask --app app db heads
```

O objetivo é garantir que a versão do banco esteja alinhada com o código.

### Testes utilizando banco incorreto

Os testes devem utilizar:

```text
sqlite:///:memory:
```

A configuração de testes está em:

```text
tests/conftest.py
```

Caso os testes tentem acessar o PostgreSQL de desenvolvimento, a configuração de teste deve ser revisada.

---

## 37. Estado atual

```text
Python 3.11              ✅
Flask                    ✅
SQLAlchemy               ✅
PostgreSQL 16            ✅
Docker                   ✅
Docker Compose           ✅
Flask-Migrate            ✅
Pytest                   ✅
Models                   ✅
Availability Engine      ✅
Services CRUD            ✅
17 testes passando       ✅
JWT                      ⏳
Validação avançada       ⏳
Lint                     ⏳
Logging                  ⏳
CI/CD                    ⏳
Deploy                   ⏳
```

---

## 38. Princípios de desenvolvimento

O desenvolvimento do projeto segue alguns princípios:

- Implementação incremental;
- Código simples antes de abstrações complexas;
- Testes acompanhando funcionalidades;
- Migrations versionadas;
- Separação de responsabilidades;
- Regras de negócio independentes da camada HTTP;
- Documentação evoluindo junto com o sistema;
- Nenhuma credencial no código;
- Automação progressiva;
- CI/CD como etapa natural da evolução;
- Evitar adicionar tecnologias sem necessidade real.

---

## 39. Resumo

O processo de desenvolvimento do TechLegacy Agendamento é baseado em evolução incremental.

O ciclo principal é:

```text
Planejar
   ↓
Implementar
   ↓
Testar
   ↓
Documentar
   ↓
Commitar
   ↓
Evoluir
```

A estrutura atual permite que novas funcionalidades sejam adicionadas sem comprometer a organização do projeto.

À medida que o sistema evoluir, práticas adicionais de qualidade, automação, CI/CD e deploy serão incorporadas ao fluxo de desenvolvimento.