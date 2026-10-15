# Anti-padrões de Performance — Ruby

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## ActiveRecord e Banco de Dados

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| N+1 com ActiveRecord | 🔴 | DB | Associação carregada em loop dispara N queries adicionais | `includes`, `preload`, `eager_load` conforme tipo de join necessário |
| `.all` / `.where` sem limite ou paginação | 🔴 | DB/MEMORY | Carrega toda a tabela em memória | `find_each`, `in_batches`, `kaminari`, `pagy` |
| Carregar objetos completos para poucos atributos | 🟠 | DB/MEMORY | ActiveRecord hidrata objeto inteiro para 1–2 colunas | `.pluck(:col1, :col2)`, `.select(:col)` |
| Operação de banco dentro de loop | 🔴 | DB | Query por item iterado | Buscar em lote com `where(id: ids)` antes do loop |
| `update` individual por item em vez de `update_all` | 🟠 | DB | Um SQL UPDATE por registro | `update_all`, `upsert_all` (Rails 6+) para updates em massa |
| Contador calculado em runtime sem `counter_cache` | 🟡 | DB | `user.posts.count` executa COUNT a cada chamada quando precisa ser frequente | `counter_cache: true` no `belongs_to` |
| `destroy_all` sem `delete_all` quando callbacks não importam | 🟡 | DB | `destroy_all` carrega cada objeto e executa callbacks | `delete_all` para remoção sem callbacks |

---

## Ruby Puro

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Concatenação de string em loop | 🟠 | MEMORY | `str += parte` cria nova string a cada iteração | `<<` (mutação) ou `Array#join` ao final |
| `map` + `select` encadeados em coleção grande | 🟡 | ALGORITHM | Percorre a coleção duas vezes | `each_with_object` ou `filter_map` (Ruby 2.7+) em uma passagem |
| `Array#flatten` recursivo desnecessário | 🟡 | MEMORY | `flatten` sem profundidade percorre tudo | `flatten(1)` para profundidade controlada |
| Regex ou parsing recriado por chamada | 🟡 | LOOP | `Regexp.new(pattern)` em método quente | Constante `REGEX = /pattern/` fora do método |
| `Hash#merge` em loop para acumular | 🟠 | MEMORY | Cria novo Hash a cada iteração | `merge!` (mutação) ou `each_with_object({})` |
| `include?` em Array quando Set resolveria | 🟠 | ALGORITHM | `array.include?(x)` é O(n) por chamada | Converter para `Set` quando pesquisado repetidamente |

---

## Concorrência e Workers

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Chamada externa sem timeout em worker Sidekiq/Resque | 🟠 | NETWORK | Request bloqueante pode travar worker indefinidamente | Timeout explícito, `Timeout::timeout` ou opção do cliente HTTP |
| Job Sidekiq processando dataset inteiro em memória | 🔴 | MEMORY/DB | `Model.all.each` em job massivo | `find_each`, `in_batches`, paginação por cursor |
| GVL (GIL) ignorado para CPU-bound em threads MRI | 🟠 | CONCURRENCY | Threads Ruby MRI não ganham paralelismo real em CPU-bound | `Ractors` (experimental), processos separados ou extensão nativa |

---

## Rails

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `before_action` pesado em toda a controller | 🟡 | DB/CACHE | Carrega dados desnecessários para actions que não os usam | Limitar com `only:` / `except:` |
| Serialização de objetos grandes sem cache | 🟠 | CACHE | Serializar JSON de resposta complexa sem cache | Rails cache com `cache_key_with_version`, Jbuilder cache |
| Template com lógica N+1 (objetos aninhados) | 🔴 | DB | Loop em view que acessa associação lazy | Eager load antes de renderizar |
| `session` com objetos grandes | 🟠 | MEMORY | Sessão cookie serializada a cada request | Armazenar só IDs; usar store server-side para dados grandes |

---

## Validação recomendada

- `rack-mini-profiler` para tempo por request e queries;
- `bullet` gem para detecção automática de N+1 e eager loading desnecessário;
- `stackprof` para CPU profiling;
- `memory_profiler` para alocações de memória;
- `derailed_benchmarks` para memória em boot e requests Rails.
