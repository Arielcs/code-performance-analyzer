# Anti-padrões de Performance — SQL

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte `general.md` para padrões transversais de banco. Esta referência foca em SQL e modelagem.

> **Regra de ouro:** nunca afirme ganho de performance em SQL sem `EXPLAIN` / `EXPLAIN ANALYZE`. Plano de execução real pode surpreender.

---

## Índices e Plano de Execução

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Coluna de filtro / JOIN sem índice | 🔴 | DB | Possível custo alto dependendo do plano e seletividade | Considerar índice apenas após verificar workload, custo de escrita e plano |
| Função sobre coluna filtrada | 🟠 | DB | `WHERE DATE(criado_em) = '...'` impede uso de índice | Range query: `WHERE criado_em >= '...' AND criado_em < '...'` ou índice funcional |
| `LIKE '%termo%'` em tabela grande | 🟠 | DB | Índice B-tree comum não ajuda | Full-text search, índice GIN/trigram (PostgreSQL), FULLTEXT (MySQL) |
| `OR` amplo em colunas indexadas | 🟡 | DB | Pode impedir uso eficiente de índice | Avaliar plano/semântica; `UNION ALL` apenas quando duplicatas forem permitidas ou impossíveis, ou outras estratégias equivalentes |
| Índice na coluna de baixa cardinalidade sem justificativa | 🟡 | DB | Índice em coluna booleana/status pode ser ignorado ou prejudicar | Índice parcial (`WHERE ativo = TRUE`) ou índice composto com coluna seletiva |
| Índice composto na ordem errada | 🟠 | DB | `(b, a)` quando queries filtram por `a` primeiro | Ordem das colunas deve seguir seletividade e padrão de uso das queries |

---

## Queries e Joins

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `SELECT *` | 🟡 | DB | Trafega e projeta colunas não usadas | Selecionar apenas colunas necessárias |
| N+1 queries | 🔴 | DB | Query executada repetidamente por item da coleção externa | JOIN, CTE, subquery com `IN`, batch |
| Subquery correlacionada pesada | 🟠 | DB | Pode executar repetidamente dependendo do otimizador e do plano | Reescrever com JOIN, CTE ou window function |
| `DISTINCT` para esconder duplicidade de JOIN | 🟡 | DB | Pode mascarar JOIN incorreto e forçar sort/hash extra | Corrigir cardinalidade do JOIN ou usar agregação adequada |
| `ORDER BY` em coluna sem índice correspondente | 🟡 | DB | Sort em memória / temporário em disco para volumes grandes | Índice composto que cubra filtro + ordem |
| JOIN sem condição (produto cartesiano acidental) | 🔴 | DB | Multiplica linhas das duas tabelas | Verificar cláusula ON; usar EXPLAIN para confirmar estimativa de linhas |
| Múltiplos JOINs desnecessários para poucos campos | 🟠 | DB | Payload de linhas intermediário enorme | Projeção explícita, materializar CTE, ou denormalização pontual |

---

## Volume e Paginação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Falta de `LIMIT` em listagens | 🔴 | DB | Retorna volume indefinido | `LIMIT` + `OFFSET` ou keyset pagination |
| `OFFSET` alto em paginação tradicional | 🟠 | DB | `OFFSET 100000` força o banco a percorrer e descartar linhas | Keyset pagination: `WHERE id > :last_seen_id ORDER BY id LIMIT n` |
| `COUNT(*)` em tabela grande sem aproximação | 🟡 | DB | Pode ser caro em algumas engines; aproximação pode bastar | `reltuples` (PostgreSQL), cache do total, ou aceitar contagem aproximada |
| Cursor-based pagination não usada em export/relatório | 🟠 | DB | Exportar tudo de uma vez esgota memória | Paginar com cursor, streaming ou `\copy` (PostgreSQL) |

---

## Transações e Locks

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Transação longa com lógica de aplicação ou I/O externo | 🟠 | DB | Segura locks por mais tempo do que necessário | Separar leitura, processamento e escrita; reduzir escopo da transação |
| Cursor / loop linha a linha dentro de transação | 🔴 | ALGORITHM/DB | Processamento procedural em vez de set-based | `UPDATE ... FROM`, `INSERT ... SELECT`, `DELETE ... WHERE`, CTE com escrita |
| Nível de isolamento mais alto que o necessário | 🟡 | DB | `SERIALIZABLE` para operação que `READ COMMITTED` resolveria | Usar nível adequado ao caso de uso |
| `SELECT ... FOR UPDATE` em tabela inteira | 🟠 | DB | Lock em volume grande bloqueia outros escritores | Restringir com `WHERE`, usar lock advisory ou `SKIP LOCKED` |

---

## Modelagem e Design

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Coluna de texto longo em tabela frequentemente listada | 🟡 | DB/MEMORY | `TEXT`/`BLOB` pesado trafegado desnecessariamente | Separar em tabela auxiliar ou carregar sob demanda |
| Tabela EAV (Entity-Attribute-Value) para dados consultados | 🟠 | ALGORITHM/DB | Joins complexos para reconstruir entidade; índices ineficazes | Schema estruturado, JSONB (PostgreSQL), ou colunas geradas |
| JSONB/JSON sem índice para campos consultados frequentemente | 🟠 | DB | Extração de campo JSON sem índice é full scan | Índice em expressão: `CREATE INDEX ON t((dados->>'campo'))` |

---

## Validação recomendada

- `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` no PostgreSQL; `EXPLAIN FORMAT=JSON` no MySQL;
- Verificar: tipo de scan (Seq Scan vs Index Scan), estimativa vs real de linhas, buffers hit/read;
- `pg_stat_statements` (PostgreSQL) para identificar queries mais lentas por tempo total;
- `slow_query_log` (MySQL/MariaDB) para queries acima do threshold;
- Conferir cardinalidade real de colunas com `SELECT COUNT(DISTINCT col) FROM t` antes de criar índices.
