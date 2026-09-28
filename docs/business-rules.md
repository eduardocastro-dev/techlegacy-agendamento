# Regras de Negócio

## 1. Visão geral

Este documento descreve as principais regras de negócio do **TechLegacy Agendamento**.

As regras definem como o sistema deve se comportar independentemente da tecnologia utilizada para implementá-las.

O objetivo é manter uma separação clara entre:

- Regras do negócio;
- Implementação técnica;
- Persistência dos dados;
- Interface da API;
- Interface do usuário.

A implementação atual concentra parte das regras de disponibilidade em:

```text
app/core/availability.py
```

---

## 2. Conceitos principais

O sistema possui os seguintes conceitos centrais:

```text
Estabelecimento
      │
      ├── Usuários
      ├── Serviços
      ├── Horários
      ├── Exceções de agenda
      └── Agendamentos
```

O estabelecimento é a entidade responsável por agrupar os dados de uma operação.

---

## 3. Regra: todo recurso pertence a um estabelecimento

Os principais recursos do sistema devem estar associados a um estabelecimento.

Exemplo:

```text
Service
   │
   └── establishment_id
```

O mesmo conceito é aplicado a:

```text
User
Service
Schedule
ScheduleException
Appointment
```

Isso permite que o sistema mantenha os dados separados entre diferentes estabelecimentos.

---

## 4. Regra: isolamento dos dados

Os dados de um estabelecimento não devem ser tratados como pertencentes a outro estabelecimento.

Exemplo:

```text
Estabelecimento 1
    ├── Serviço A
    └── Serviço B

Estabelecimento 2
    ├── Serviço C
    └── Serviço D
```

Uma operação relacionada ao Estabelecimento 1 não deve retornar os serviços pertencentes ao Estabelecimento 2.

Na implementação atual do CRUD de Services, esse isolamento é realizado através do:

```text
establishment_id
```

---

## 5. Regra: serviços possuem duração

Todo serviço deve possuir uma duração definida.

Campo:

```text
duration_minutes
```

Exemplo:

```text
Corte de cabelo
Duração: 30 minutos
```

A duração é utilizada pelo mecanismo de disponibilidade para determinar o tamanho dos horários disponíveis.

---

## 6. Regra: serviços possuem preço

Todo Service possui um preço.

Campo:

```text
price
```

Exemplo:

```text
Corte de cabelo
Preço: R$ 45,00
```

O preço pertence ao serviço e será utilizado futuramente durante o processo de agendamento e apresentação ao cliente.

---

## 7. Regra: serviços podem estar ativos ou inativos

Cada serviço possui o campo:

```text
active
```

Os estados possíveis são:

```text
true
false
```

### Serviço ativo

```text
active = true
```

Pode ser utilizado normalmente.

### Serviço inativo

```text
active = false
```

Não deve aparecer nas consultas que retornam somente serviços ativos.

---

## 8. Regra: exclusão de serviço é lógica

A exclusão de um Service não remove fisicamente o registro do banco.

Quando o usuário solicita:

```text
DELETE /services/<id>
```

o sistema altera:

```text
active = false
```

Fluxo:

```text
DELETE
  │
  ▼
Service encontrado
  │
  ▼
active = false
  │
  ▼
Registro permanece no banco
```

Essa estratégia é chamada de soft delete.

---

## 9. Regra: serviço inativo não pode ser utilizado

Um serviço com:

```text
active = false
```

não deve ser considerado um serviço disponível para novas operações.

Atualmente, as consultas da API de Services filtram os registros ativos.

Isso também é aplicado ao mecanismo de disponibilidade.

---

## 10. Regra: serviço deve pertencer ao estabelecimento

Para calcular a disponibilidade, o serviço deve:

- Existir;
- Pertencer ao estabelecimento informado;
- Estar ativo.

Fluxo:

```text
Serviço solicitado
       │
       ▼
Existe?
       │
       ▼
Pertence ao estabelecimento?
       │
       ▼
Está ativo?
       │
       ▼
Pode ser utilizado
```

Se qualquer uma dessas condições não for atendida, nenhum horário é disponibilizado.

---

## 11. Regra: disponibilidade depende do dia da semana

A disponibilidade de um estabelecimento depende do horário configurado para o dia da semana.

O sistema utiliza a representação:

```text
0 = Segunda-feira
1 = Terça-feira
2 = Quarta-feira
3 = Quinta-feira
4 = Sexta-feira
5 = Sábado
6 = Domingo
```

Essa representação é compatível com:

```text
date.weekday()
```

---

## 12. Regra: estabelecimento precisa possuir horário configurado

Para que existam horários disponíveis em determinado dia, deve existir um Schedule ativo correspondente ao dia da semana.

Exemplo:

```text
Segunda-feira
08:00 → 18:00
```

Se não houver um horário ativo para o dia solicitado:

```text
Disponibilidade = []
```

---

## 13. Regra: horário possui abertura e fechamento

Cada Schedule possui:

```text
opening_time
closing_time
```

Exemplo:

```text
08:00 → 18:00
```

O mecanismo de disponibilidade utiliza esses valores como limite para geração dos horários.

---

## 14. Regra: exceções podem alterar o horário padrão

Uma ScheduleException pode modificar o horário normal de determinado dia.

Exemplo:

```text
Horário padrão:
08:00 → 18:00

Exceção:
10:00 → 18:00
```

Nesse caso, a disponibilidade será calculada utilizando:

```text
10:00 → 18:00
```

em vez do horário padrão.

---

## 15. Regra: exceção pode alterar somente a abertura

Uma exceção pode definir somente:

```text
opening_time
```

Exemplo:

```text
Horário padrão:
08:00 → 18:00

Exceção:
10:00 → null
```

Resultado:

```text
10:00 → 18:00
```

O horário de fechamento original é preservado.

---

## 16. Regra: exceção pode alterar somente o fechamento

Uma exceção também pode definir somente:

```text
closing_time
```

Exemplo:

```text
Horário padrão:
08:00 → 18:00

Exceção:
null → 15:00
```

Resultado:

```text
08:00 → 15:00
```

O horário de abertura original é preservado.

---

## 17. Regra: estabelecimento pode estar fechado em uma data específica

Uma ScheduleException pode indicar:

```text
closed = true
```

Quando isso acontece, o estabelecimento não possui disponibilidade naquela data.

Resultado:

```text
[]
```

Exemplo:

```text
25/12
closed = true
```

Nenhum horário será disponibilizado nessa data.

---

## 18. Regra: disponibilidade considera a duração do serviço

A geração de horários utiliza a duração do serviço.

Exemplo:

```text
Horário:
08:00 → 12:00

Serviço:
duração = 60 minutos
```

Os horários possíveis serão gerados respeitando a duração configurada.

Conceitualmente:

```text
08:00 → 09:00
09:00 → 10:00
10:00 → 11:00
11:00 → 12:00
```

O sistema não deve gerar um horário cujo término ultrapasse o fechamento.

---

## 19. Regra: horários não podem ultrapassar o fechamento

Se o estabelecimento fecha às:

```text
18:00
```

e o serviço possui:

```text
duração = 60 minutos
```

um horário iniciado às:

```text
18:00
```

não pode ser oferecido.

Isso ocorre porque:

```text
18:00 + 60 minutos = 19:00
```

e o horário ultrapassaria o fechamento.

---

## 20. Regra: agendamentos ocupam períodos

Um Appointment possui:

```text
starts_at
ends_at
```

O período do agendamento representa o intervalo em que o estabelecimento estará ocupado.

Exemplo:

```text
Agendamento:
14:00 → 14:30
```

Outro serviço não deve ocupar o mesmo período.

---

## 21. Regra: horários conflitantes não ficam disponíveis

A disponibilidade verifica os agendamentos existentes.

Existe conflito quando:

```text
appointment.starts_at < slot_end
AND
appointment.ends_at > slot_start
```

Conceitualmente:

```text
Agendamento existente
14:00 ───────── 15:00

Novo horário
        14:30 ───────── 15:30

Resultado:
CONFLITO
```

O horário conflitante não é disponibilizado.

---

## 22. Regra: agendamentos cancelados não bloqueiam horários

Agendamentos com:

```text
status = cancelled
```

não são considerados como bloqueio de disponibilidade.

Exemplo:

```text
Agendamento:
14:00 → 15:00

Status:
cancelled
```

Outro cliente poderá utilizar esse período, desde que as demais regras sejam atendidas.

---

## 23. Regra: disponibilidade é específica por estabelecimento

A consulta de agendamentos considera o estabelecimento.

Isso significa que um agendamento de:

```text
Estabelecimento 1
```

não deve bloquear a disponibilidade de:

```text
Estabelecimento 2
```

Fluxo:

```text
Estabelecimento 1
    │
    └── Appointment 10:00 → 11:00

Estabelecimento 2
    │
    └── 10:00 continua disponível
```

---

## 24. Regra: disponibilidade é específica por serviço

O serviço solicitado precisa pertencer ao estabelecimento e estar ativo.

Exemplo:

```text
Estabelecimento
      │
      ├── Corte
      └── Barba
```

Se o cliente solicitar:

```text
Barba
```

o mecanismo de disponibilidade utilizará a duração da Barba.

Exemplo:

```text
Corte = 60 minutos
Barba = 30 minutos
```

Os intervalos disponíveis podem ser diferentes para cada serviço.

---

## 25. Fluxo completo de disponibilidade

A regra de disponibilidade pode ser resumida em:

```text
                    Data + Serviço
                          │
                          ▼
                Serviço existe e está ativo?
                          │
                    ┌─────┴─────┐
                    │           │
                   Não         Sim
                    │           │
                    ▼           ▼
                   []      Pertence ao
                           estabelecimento?
                                │
                           ┌────┴────┐
                           │         │
                          Não       Sim
                           │         │
                           ▼         ▼
                          []    Existe Schedule?
                                      │
                                 ┌────┴────┐
                                 │         │
                                Não       Sim
                                 │         │
                                 ▼         ▼
                                []    Verificar exceção
                                            │
                                            ▼
                                    Estabelecimento fechado?
                                            │
                                       ┌────┴────┐
                                       │         │
                                      Sim       Não
                                       │         │
                                       ▼         ▼
                                      []    Definir horário
                                                  │
                                                  ▼
                                        Buscar appointments
                                                  │
                                                  ▼
                                         Verificar conflitos
                                                  │
                                                  ▼
                                      Gerar horários disponíveis
```

---

## 26. Regra: disponibilidade é calculada dinamicamente

Os horários não são armazenados previamente como uma lista fixa.

Eles são calculados a partir de:

```text
Serviço
+
Data
+
Schedule
+
ScheduleException
+
Appointments
```

Isso permite que uma alteração na agenda ou um novo agendamento reflita na disponibilidade.

---

## 27. Regra: histórico deve ser preservado quando necessário

O sistema utiliza soft delete em Services para evitar a remoção física de registros.

Isso é importante porque dados históricos podem futuramente estar relacionados a:

```text
Appointments
```

e outras informações do sistema.

A estratégia permite manter o registro original mesmo quando o serviço deixa de ser oferecido.

---

## 28. Regra: usuário pertence a um estabelecimento

Cada User possui:

```text
establishment_id
```

Isso permite identificar o estabelecimento associado ao usuário.

Conceitualmente:

```text
User
  │
  ▼
Establishment
```

Essa relação será utilizada futuramente na autenticação e autorização.

---

## 29. Regra: período de teste

O estabelecimento possui o campo:

```text
trial_ends_at
```

Esse campo representa a data de término do período de teste.

A regra comercial completa do trial ainda não está implementada.

Atualmente o campo existe no modelo para suportar essa evolução.

---

## 30. Regra: clientes não precisam de conta no fluxo público

A visão planejada do produto prevê que o cliente final possa realizar um agendamento através de um link público.

O fluxo esperado é:

```text
Link público
      │
      ▼
Nome + telefone
      │
      ▼
Serviço
      │
      ▼
Data
      │
      ▼
Horário
      │
      ▼
Agendamento
```

A implementação desse fluxo ainda não está concluída.

---

## 31. Regra: área administrativa e área pública

O sistema terá dois contextos principais.

### Área administrativa

Utilizada pelo estabelecimento.

Responsável por:

- Serviços;
- Agenda;
- Exceções;
- Agendamentos;
- Configurações.

Essa área deverá utilizar autenticação.

### Área pública

Utilizada pelo cliente final.

Responsável por:

- Visualizar serviços;
- Consultar disponibilidade;
- Informar dados;
- Realizar agendamento.

A área pública deverá funcionar sem necessidade de login do cliente.

Essas funcionalidades ainda estão em desenvolvimento.

---

## 32. Regras de autenticação futuras

A área administrativa deverá utilizar autenticação baseada em JWT.

O princípio será:

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
API protegida
```

O `establishment_id` deverá ser obtido a partir do usuário autenticado, evitando depender de um valor fornecido livremente pelo cliente.

Essa regra ainda não está implementada.

---

## 33. Regra de autorização futura

Autenticação e autorização são conceitos diferentes.

Autenticação:

> "Quem é o usuário?"

Autorização:

> "O que esse usuário pode fazer?"

No futuro, as operações administrativas deverão validar:

```text
usuário autenticado
        +
estabelecimento associado
        +
permissão necessária
```

---

## 34. Regra de criação de agendamento futura

A criação de um Appointment deverá considerar, no mínimo:

```text
Estabelecimento
+
Serviço
+
Data
+
Horário
+
Cliente
```

Antes da criação, a disponibilidade deverá ser validada novamente.

Fluxo planejado:

```text
Cliente escolhe horário
        │
        ▼
Validar disponibilidade
        │
        ▼
Horário ainda disponível?
        │
   ┌────┴────┐
   │         │
  Não       Sim
   │         │
   ▼         ▼
 Erro      Criar
           Appointment
```

Essa validação será importante para evitar reservas conflitantes.

---

## 35. Concorrência

Em um ambiente com múltiplos clientes, duas pessoas podem tentar reservar o mesmo horário.

Exemplo:

```text
Cliente A ──────┐
                ├── 10:00
Cliente B ──────┘
```

A implementação futura deverá garantir que somente uma reserva válida seja confirmada quando houver conflito.

A proteção contra condições de corrida ainda não faz parte da implementação atual.

---

## 36. Regras de cancelamento futuras

O sistema possui atualmente o status:

```text
cancelled
```

para representar agendamentos cancelados.

A política completa de cancelamento ainda deverá ser definida.

Possíveis regras futuras incluem:

- Quem pode cancelar;
- Prazo mínimo para cancelamento;
- Alteração do horário;
- Reagendamento;
- Notificação do cliente.

Essas regras ainda não estão implementadas.

---

## 37. Regras de notificações futuras

O produto poderá futuramente enviar notificações relacionadas aos agendamentos.

Exemplos:

```text
Agendamento criado
       │
       ▼
Confirmação

Agendamento próximo
       │
       ▼
Lembrete

Agendamento cancelado
       │
       ▼
Notificação
```

A integração com WhatsApp ou outros canais ainda não faz parte da implementação atual.

---

## 38. Regras de consistência

As regras de negócio devem ser aplicadas de forma consistente independentemente do cliente utilizado.

Por exemplo:

```text
Frontend
    │
    ▼
API
    │
    ▼
Business Rules
    │
    ▼
Database
```

O frontend não deve ser responsável por garantir sozinho regras importantes do domínio.

A API e a camada de negócio devem validar as condições necessárias.

---

## 39. Regras de validação

A API atualmente possui validação básica dos recursos.

A validação mais robusta ainda será implementada.

Futuramente deverão ser considerados:

- Campos obrigatórios;
- Tipos;
- Valores mínimos;
- Valores máximos;
- Duração válida;
- Preço válido;
- Horários válidos;
- Datas válidas;
- Consistência entre abertura e fechamento;
- Serviço pertencente ao estabelecimento.

---

## 40. Regras de horário

As regras de horário devem garantir que:

```text
opening_time < closing_time
```

e que a duração do serviço permita que o atendimento termine dentro do horário de funcionamento.

Exemplo válido:

```text
08:00 → 18:00
Serviço: 60 minutos
```

Exemplo que não deve gerar horário:

```text
17:30 → 18:30
```

quando o estabelecimento fecha às:

```text
18:00
```

---

## 41. Separação entre regra de negócio e API

As regras de negócio não devem depender diretamente da estrutura de uma requisição HTTP.

Por exemplo, a lógica de disponibilidade está em:

```text
app/core/availability.py
```

e não diretamente dentro da rota.

Isso permite que a mesma regra seja reutilizada futuramente por:

```text
API
Dashboard
Agendamento público
Jobs
Integrações
```

---

## 42. Regras e testes

As principais regras de negócio devem possuir testes automatizados.

Atualmente existem testes para:

```text
Health check
Disponibilidade
Conflitos
Exceções
Services CRUD
Soft delete
```

A suíte atual possui:

```text
17 testes passando
```

Execução:

```bash
pytest -v
```

---

## 43. Matriz de regras atuais

| Regra                                        | Status |
| -------------------------------------------- | ------ |
| Serviço pertence a estabelecimento           | ✅     |
| Serviço possui duração                       | ✅     |
| Serviço possui preço                         | ✅     |
| Serviço pode ser ativo/inativo               | ✅     |
| Soft delete de Service                       | ✅     |
| Serviço inativo não aparece na listagem      | ✅     |
| Schedule por dia da semana                   | ✅     |
| Exceção de horário                           | ✅     |
| Exceção de fechamento                        | ✅     |
| Conflito de agendamento                      | ✅     |
| Agendamento cancelado não bloqueia horário   | ✅     |
| Disponibilidade por estabelecimento          | ✅     |
| Disponibilidade por serviço                  | ✅     |
| JWT                                          | ⏳     |
| Autorização                                  | ⏳     |
| Agendamento público                          | ⏳     |
| Concorrência de reservas                     | ⏳     |
| Notificações                                 | ⏳     |
| Regras de cancelamento                       | ⏳     |
| Regras comerciais do trial                   | ⏳     |

---

## 44. Princípios das regras de negócio

O projeto segue os seguintes princípios:

- Regras importantes devem ser centralizadas;
- Regras não devem depender exclusivamente do frontend;
- Dados devem ser isolados por estabelecimento;
- Serviços inativos não devem ser oferecidos;
- Conflitos de horário devem ser evitados;
- Exceções devem sobrescrever o horário padrão quando aplicável;
- Histórico importante deve ser preservado;
- Regras devem ser testáveis;
- Novas regras devem ser acompanhadas de testes;
- Funcionalidades futuras devem ser implementadas somente quando suas regras estiverem definidas.

---

## 45. Estado atual

```text
Estabelecimentos             ✅
Services                     ✅
Soft Delete                  ✅
Schedules                    ✅
Schedule Exceptions          ✅
Availability Engine          ✅
Appointment Model            ✅
Conflict Detection           ✅
Cancelled Appointment Rule   ✅
JWT                          ⏳
Authorization                ⏳
Public Booking               ⏳
Booking Concurrency          ⏳
Notifications                ⏳
Trial Rules                  ⏳
Cancellation Policy          ⏳
```

---

## 46. Resumo

As regras de negócio do TechLegacy Agendamento são construídas em torno de três conceitos principais:

```text
             ESTABELECIMENTO
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    SERVIÇOS     AGENDA    AGENDAMENTOS
                    │
                    ▼
               DISPONIBILIDADE
```

O mecanismo de disponibilidade atualmente considera:

```text
Serviço
+
Estabelecimento
+
Dia da semana
+
Horário
+
Exceções
+
Agendamentos
+
Duração
```

Essa estrutura fornece a base para a evolução do sistema para autenticação, agendamento público, dashboard, notificações e operação em produção.