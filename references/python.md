# Anti-padrões de Performance — Python

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Strings e Coleções

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Concatenação de string em loop | 🟠 | LOOP/MEMORY | `s += parte` cria nova string imutável a cada iteração | Lista + `''.join(partes)` ao final |
| `append` em loop quando comprehension resolve | 🟢 | LOOP | Menos direto que comprehension para transformação simples | List comprehension / generator expression |
| Busca repetida em lista | 🟠 | ALGORITHM | `x in lista` dentro de loop é O(n) por verificação | Converter para `set` ou `dict` antes do loop |
| Ordenação desnecessária em resultado parcial | 🟡 | ALGORITHM | `sorted()` quando só os N menores/maiores são necessários | `heapq.nsmallest`/`nlargest` ou seleção parcial |
| `dict` com `setdefault` ou `get` repetido quando `defaultdict` resolve | 🟢 | ALGORITHM | Código mais verboso e lento para acumuladores | `collections.defaultdict` ou `Counter` |

---

## Loops e Iteração

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `range(len(lista))` para iterar | 🟢 | LOOP | Menos eficiente e menos legível | `for item in lista` ou `enumerate(lista)` |
| Regex recompilada em loop | 🟠 | LOOP | `re.match(pattern, valor)` compila o padrão a cada chamada | `re.compile(pattern)` fora do loop |
| Imports dentro de loops ou funções muito chamadas | 🟡 | LOOP | Import em caminho quente adiciona overhead de lookup | Mover para o topo do módulo |
| Computação idêntica dentro de loop sem cache | 🟠 | LOOP/CACHE | Valor que não muda por iteração recalculado repetidamente | Calcular antes do loop ou usar `functools.lru_cache` |
| Loop Python onde operação nativa ou vetorizada existe | 🟠 | ALGORITHM | `for` em Python puro onde `sum()`, `map()`, `filter()` ou operação C-level resolve | Preferir builtins e funções nativas |

---

## Memória e Cópias

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `deepcopy` sem necessidade | 🟠 | MEMORY | Cópia profunda de objetos grandes pressiona memória e CPU | Cópia rasa, imutabilidade ou copiar só campos necessários |
| Materializar generator desnecessariamente | 🟡 | MEMORY | `list(generator)` quando iteração única bastaria | Manter como generator/iterador |
| Carregar arquivo inteiro sem necessidade | 🟠 | IO/MEMORY | `read()`/`readlines()` em arquivo grande | Iterar linha a linha, usar `with open(...) as f: for line in f:` |
| Criar DataFrame para operação que lista resolve | 🟡 | MEMORY | Overhead de Pandas para dados pequenos ou simples | `dict`, lista, `csv.reader` conforme o caso |

---

## Pandas e Dados

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `.iterrows()` / `.itertuples()` em DataFrame grande | 🔴 | ALGORITHM | Loop Python linha a linha em DataFrame é ordens mais lento que vetorização | Operações vetorizadas, `merge`, `groupby`, `apply` com cuidado, NumPy |
| `apply` com função Python pura em coluna grande | 🟠 | ALGORITHM | `apply` chama Python por linha; pode ser substituído | Operação vetorizada direta ou `np.vectorize` com teste |
| `pd.concat` em loop | 🟠 | MEMORY | Recria DataFrame a cada iteração | Acumular lista e chamar `pd.concat` uma vez ao final |
| Sem `dtype` explícito ao criar DataFrame | 🟡 | MEMORY | Inferência automática pode alocar tipos maiores que o necessário | Especificar `dtype` adequado |

---

## Banco e ORM

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| N+1 com ORM (SQLAlchemy, Django ORM) | 🔴 | DB | Acesso a relacionamento lazy em loop dispara N queries adicionais | `select_related`, `prefetch_related`, `.options(joinedload/subqueryload)` |
| Carregar objetos completos para poucos campos | 🟠 | DB/MEMORY | ORM hidrata entidade inteira quando só 1–2 campos são usados | `.values()`, `.only()`, projeção explícita |
| `query.all()` sem filtro ou limite | 🔴 | DB/MEMORY | Carrega tabela inteira em memória | Filtrar, paginar, usar `yield_per` ou `stream_results` |
| Operação de banco dentro de loop de aplicação | 🔴 | DB | Query executada por item processado | Buscar em lote antes do loop, usar bulk insert/update |

---

## Concorrência

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `threading` para CPU-bound | 🟠 | CONCURRENCY | GIL impede paralelismo real em Python para código CPU-bound | `multiprocessing`, `concurrent.futures.ProcessPoolExecutor` ou extensão nativa |
| `asyncio` misturado com I/O bloqueante | 🔴 | CONCURRENCY | Chamada bloqueante dentro de coroutine trava o event loop inteiro | Usar equivalente async (`aiohttp`, `asyncpg`, `aiofiles`) ou `run_in_executor` |
| `asyncio.gather` sem limite de concorrência | 🟠 | CONCURRENCY | Dispara N tasks simultâneas podendo sobrecarregar banco ou serviço externo | `asyncio.Semaphore`, `anyio.CapacityLimiter` ou batch manual |

---

## Validação recomendada

- `cProfile`, `py-spy`, `scalene`, `line_profiler` para CPU;
- `memory_profiler`, `tracemalloc` para memória;
- `pytest-benchmark` para comparação antes/depois;
- Medir com volume de dados representativo do cenário real.
