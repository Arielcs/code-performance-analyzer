# Anti-padrões de Performance — Java

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Strings e Coleções

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Concatenação com `+` em loop | 🟠 | LOOP/MEMORY | Cria muitos objetos `String` imutáveis | `StringBuilder` |
| Autoboxing/unboxing em loop intensivo | 🟡 | MEMORY | `Integer`, `Long`, `Double` geram objetos desnecessários | Tipos primitivos (`int`, `long`, `double`) onde possível |
| `ArrayList` com remoções frequentes no meio | 🟡 | ALGORITHM | Remoção desloca elementos — O(n) | `LinkedList`, `ArrayDeque`, `Set` ou estrutura adequada ao acesso |
| `new ArrayList()` sem capacidade estimada em loop | 🟡 | MEMORY | Realoca array interno ao crescer | `new ArrayList<>(capacidadeEstimada)` |
| `HashMap` com capacidade padrão para muitas entradas | 🟡 | MEMORY | Rehash frequente com fator padrão | `new HashMap<>(capacidade, loadFactor)` calculado |
| Uso de `Vector`/`Hashtable` sem necessidade de sincronização | 🟢 | CONCURRENCY | Lock em todo método sem ganho | `ArrayList`/`HashMap` + sincronização explícita quando necessário |

---

## JPA / Hibernate / Spring Data

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| N+1 com JPA/Hibernate | 🔴 | DB | Lazy loading em loop gera N consultas adicionais | `JOIN FETCH`, `EntityGraph`, `@BatchSize`, fetch manual por lista de IDs |
| Relacionamento `EAGER` desnecessário | 🔴 | DB/MEMORY | Carrega dados não usados em toda query da entidade | `LAZY` + busca sob demanda ou projeção explícita |
| Buscar entidade completa para poucos campos | 🟠 | DB/MEMORY | ORM hidrata objeto inteiro para 1–2 campos | DTO/interface projection, `@Query` com `SELECT new` |
| `findAll()` sem filtro ou paginação | 🔴 | DB/MEMORY | Carrega tabela inteira em memória | `findAll(Pageable)`, `findBy...`, cursor-based pagination |
| Operação de banco dentro de loop de serviço | 🔴 | DB | Query por item processado | Batch fetch antes do loop, bulk insert/update |
| `save()` em loop sem `saveAll()` | 🟠 | DB | Possível overhead por operação, a depender da transação e do ORM | `saveAll()` e batching **quando comprovadamente suportados**; confira flush e IDs gerados |
| Query JPQL/HQL sem índice correspondente | 🟠 | DB | Filtros em campos sem índice | `EXPLAIN ANALYZE`, criar índice conforme plano |
| `@Transactional` em método com I/O ou chamada externa | 🟠 | DB | Mantém conexão e lock enquanto espera rede/arquivo | Separar transação da I/O externa |

---

## Concorrência

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `synchronized` amplo cobrindo lógica não crítica | 🟠 | CONCURRENCY | Bloqueia mais do que necessário, reduz throughput | Reduzir região crítica, usar `ReentrantLock` ou estruturas concorrentes |
| `ConcurrentHashMap` com operações compostas não atômicas | 🟠 | CONCURRENCY | `get` + `put` separados não são atômicos | `computeIfAbsent`, `merge`, `compute` |
| `Stream.parallelStream()` sem critério | 🟡 | CONCURRENCY | Pode piorar com I/O-bound, datasets pequenos ou por usar pool comum | Medir; usar `parallelStream()` só para CPU-bound com volume justificado |
| `new Thread()` a cada tarefa | 🟠 | CONCURRENCY | Custo de criação de thread + risco de esgotamento | `ExecutorService`, `CompletableFuture`, virtual threads (Java 21+) |
| `CompletableFuture` sem timeout | 🟠 | CONCURRENCY | Future pode ficar pendente indefinidamente | `.orTimeout()` ou `.completeOnTimeout()` |

---

## Objetos e GC

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Criação de objeto pesado dentro de loop quente | 🟡 | MEMORY | Pressiona GC repetidamente | Reusar quando seguro, mover instanciação para fora do loop |
| `ObjectMapper` (Jackson) instanciado por request | 🟠 | MEMORY/CONFIG | `ObjectMapper` é thread-safe e caro para criar | Instância singleton injetada (Spring bean) |
| Stream sem terminal operation curto-circuitante | 🟡 | ALGORITHM | `filter().map().collect()` percorre tudo quando só o primeiro era necessário | `.findFirst()`, `.anyMatch()`, `.limit()` conforme o caso |

---

## Configuração e Infraestrutura

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Conexão de banco sem pool | 🔴 | DB/CONFIG | Abrir/fechar conexão por operação | HikariCP configurado adequadamente |
| `spring.jpa.show-sql=true` em produção | 🟡 | CONFIG | Logging de SQL por query impacta throughput | Desabilitar; usar ferramentas de APM para diagnóstico |
| Thread pool do servidor subdimensionado | 🟠 | CONFIG | Poucos threads para a demanda de requests | Ajustar `server.tomcat.threads.max` com base em carga real |
| Cache de segundo nível Hibernate mal configurado | 🟠 | CACHE | Pode causar inconsistência ou ausência de ganho | Revisar região, TTL, invalidação e estratégia |

---

## Validação recomendada

- Java Flight Recorder (JFR), VisualVM, async-profiler para CPU e memória;
- Métricas de HikariCP (pool wait time, active connections);
- Logs Hibernate com `hibernate.format_sql` e `hibernate.use_sql_comments` para diagnóstico pontual;
- `EXPLAIN ANALYZE` nas queries críticas;
- JMeter, Gatling ou k6 para teste de carga.
