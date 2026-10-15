# Project Scan — Guia de Análise de Projeto Inteiro

Use este guia quando a análise envolver um projeto, repositório, pasta grande ou zip com muitos arquivos.

---

## 1. Princípio central

Projeto inteiro não deve ser analisado como uma sequência de arquivos isolados.

A análise deve seguir esta ordem:

1. Inventariar estrutura;
2. Identificar stack e tipo de projeto;
3. Ignorar ruído;
4. Classificar arquivos por papel arquitetural;
5. Priorizar arquivos com maior risco de performance;
6. Fazer varredura ampla;
7. Fazer deep dive nos pontos críticos;
8. Relatar cobertura, limitações e próximos passos de validação.

---

## 2. Pastas e arquivos normalmente ignorados

Ignore dependências, artefatos gerados, build, cache, IDE e arquivos minificados:

```text
.git/
node_modules/
dist/
build/
target/
out/
coverage/
.cache/
.next/
.nuxt/
.angular/
.gradle/
.mvn/
vendor/
bin/
obj/
.idea/
.vscode/
*.min.js
*.map
```

Arquivos de lock (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Gemfile.lock`, `poetry.lock`) podem ajudar a reconhecer stack, mas não devem ser analisados profundamente para performance da aplicação.

---

## 3. Sinais de stack e framework

### Java/Spring

Sinais:

- `pom.xml`, `build.gradle`, `settings.gradle`;
- `@SpringBootApplication`, `@RestController`, `@Service`, `@Repository`, `@Entity`;
- `application.properties`, `application.yml`.

Priorizar:

- Controllers de listagem/exportação/importação;
- Services com loops e transações;
- Repositories/JPA/queries nativas;
- Jobs/schedulers;
- Configurações de HikariCP, cache, thread pool e batch.

### Angular

Sinais:

- `angular.json`, `package.json`, `*.component.ts`, `*.component.html`;
- `HttpClient`, RxJS, `*ngFor`, pipes.

Priorizar:

- Components com listas/tabelas grandes;
- Templates com pipes/funções chamadas no template;
- Services com chamadas HTTP repetidas;
- Resolvers/guards que bloqueiam navegação;
- Uso de subscriptions sem controle em telas muito acessadas.

### Node/NestJS

Sinais:

- `nest-cli.json`, `package.json`, `*.controller.ts`, `*.service.ts`, `*.module.ts`;
- Prisma, TypeORM, Sequelize, Mongoose.

Priorizar:

- Controllers/handlers;
- Services com loops e awaits sequenciais;
- Queries Prisma/TypeORM/Mongoose;
- Middlewares globais;
- Jobs, queues, consumers;
- Configuração de timeout, pool, cache.

### Python

Sinais:

- `requirements.txt`, `pyproject.toml`, `setup.py`, `manage.py`, `app.py`, `main.py`;
- Django, FastAPI, Flask, SQLAlchemy, Celery.

Priorizar:

- Endpoints;
- ORM queries;
- Processamento de arquivos;
- Celery/tasks/jobs;
- Pandas/dataframes grandes;
- Loops com I/O ou chamadas externas.

---

## 4. Heurística de priorização

Ao escolher arquivos para deep dive, use pontuação aproximada.

| Sinal | Pontos |
|------|--------|
| Repository/DAO/query/ORM | +5 |
| Job/scheduler/worker/consumer | +5 |
| Endpoint de listagem, relatório, importação, exportação ou download | +4 |
| Loop com DB, rede, arquivo ou serialização | +4 |
| Arquivo com transação ampla | +4 |
| Componente frontend com tabela/lista grande | +4 |
| Configuração de pool/cache/thread/timeout/batch | +3 |
| Arquivo grande ou com muitas responsabilidades | +2 |
| Utilitário chamado por muitos módulos | +2 |
| Teste, mock, fixture, build ou gerado | -5 |

Deep dive deve começar pelos arquivos com maior pontuação **somente quando também houver um fluxo relevante**. A heurística não comprova problema, não mede frequência e pode omitir gargalos reais; use métricas, chamadores e conhecimento de workload para reordenar candidatos.

---

## 5. Padrões de risco por camada

### API/Controller

- Endpoint sem paginação;
- Retorno de payload muito grande;
- Serialização de entidades completas;
- Chamada síncrona para operação lenta;
- Falta de timeout/cancelamento;
- Acoplamento direto com operação de banco pesada.

### Service/Use Case

- Loop com chamada a repository/client externo;
- Transação envolvendo chamada de rede ou I/O;
- Reprocessamento sem cache;
- Conversões repetidas e cópias grandes;
- Falta de batch/chunk em processamento massivo.

### Repository/DB

- N+1;
- Query sem filtro/paginação;
- `SELECT *` em tabela grande;
- Filtro com função na coluna indexável;
- `LIKE '%termo%'` sem estratégia apropriada;
- Ordenação sem índice;
- Join amplo sem necessidade;
- Falta de `EXPLAIN` para query crítica.

### Frontend/Renderização

- Função chamada direto no template;
- Pipe impuro em lista grande;
- `*ngFor` sem `trackBy`;
- Renderização de tabela grande sem paginação/virtual scroll;
- Subscriptions acumuladas;
- Requisições repetidas ao trocar filtros sem debounce/cancelamento.

### Jobs/Workers

- Processar tudo em memória;
- Falta de paginação/chunk;
- Ausência de checkpoint/retry controlado;
- Paralelismo sem limite;
- I/O ou rede dentro de loop sem batch.

### Configuração

- Pool de conexão pequeno para carga real;
- Pool excessivo causando pressão no banco;
- Timeout ausente ou alto demais;
- Cache sem TTL ou sem invalidação;
- Batch size inadequado;
- Logs síncronos excessivos em produção.

---

## 6. Cobertura obrigatória do relatório

Em `project-scan`, sempre registrar:

- Total aproximado de arquivos encontrados;
- Total de arquivos ignorados;
- Critérios de ignorados;
- Arquivos mapeados;
- Arquivos analisados superficialmente;
- Arquivos analisados profundamente;
- Motivo da escolha dos arquivos de deep dive;
- Limitações da análise;
- Pontos que precisam de profiling, logs, APM ou `EXPLAIN ANALYZE`.

---

## 7. Linguagem do relatório

Evite afirmar:

> “Este ponto é o gargalo do sistema.”

Prefira, quando não houver medição:

> “Este ponto é candidato a gargalo e deve ser validado com profiling, porque combina alto volume potencial, acesso a banco e ausência de paginação.”

Use severidade crítica apenas quando o código e o contexto sustentarem essa conclusão.


## V3 — Escopo, segurança e custo

- Não crie relatório/inventário se o usuário não solicitou entregável e for possível responder no chat. Se a varredura exigir inventário temporário, mantenha-o fora do repositório por padrão.
- Se gerar inventário, registre cobertura parcial e amostra limitada a 8 KiB por arquivo; não confunda arquivos inventariados com analisados profundamente.
- Inicie pelos fluxos acionados com frequência ou que manipulem maior volume; rastreie API → service → repository → IO/rede → resposta.
- Audite efeitos das mudanças em paginação, cardinalidade, ordem, locking, transações e concorrência.
- Use `references/evidence_severity.md`; classifique heurísticas como **triagem**, não evidência de defeito.
