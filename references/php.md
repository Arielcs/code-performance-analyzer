# Anti-padrões de Performance — PHP

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Banco de Dados e ORM

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Query dentro de loop (N+1) | 🔴 | DB | Uma query por item iterado | Eager loading, JOIN, batch com `whereIn()` |
| Carregar coleção inteira sem paginação | 🔴 | MEMORY/DB | `Model::all()` ou `->get()` sem filtro ou limite | `->paginate()`, `->chunk()`, `->cursor()` |
| `SELECT *` desnecessário | 🟡 | DB | Trafega colunas não usadas | `->select(['col1', 'col2'])` |
| Contagem manual de coleção já carregada | 🟡 | DB | `count(Model::all())` faz `COUNT(*)` no banco | `Model::count()` direto |
| Update por item em vez de update em lote | 🟠 | DB | Um `UPDATE` SQL por iteração | `Model::whereIn('id', $ids)->update([...])` |
| Conexão nova por operação em script de longa duração | 🔴 | DB/CONFIG | Abre/fecha PDO por iteração | Reutilizar conexão; usar pool via FPM ou Swoole |

---

## Laravel / Eloquent

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `with()` esquecido em relacionamento acessado em loop | 🔴 | DB | Lazy loading dispara N queries adicionais | `with('relacao')` ou `load('relacao')` antes do loop |
| `chunk()` sem `chunkById()` para grandes updates | 🟠 | DB | `chunk` com ordem pode repetir ou pular registros durante update | `chunkById()` para consistência em operações destrutivas |
| Accessor pesado sem cache em modelo | 🟠 | ALGORITHM | Accessor computado a cada acesso ao atributo | `protected $appends` com getter cacheado ou `@once` (PHP 8+) |
| `dd()`, `dump()`, `Log::debug()` em produção | 🟢 | CONFIG | Overhead de saída e I/O de log | Remover; usar níveis de log condicionados ao ambiente |

---

## Arrays e Strings

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `array_merge` dentro de loop | 🟠 | MEMORY | Cria novo array a cada iteração — O(n²) | Acumular em variável e `array_merge` uma vez; ou usar spread `[...$a, ...$b]` |
| Concatenação de string com `.` em loop | 🟡 | MEMORY | Fragmentação e realocação | Acumular em array + `implode()` ao final |
| `in_array` em array grande sem chave | 🟠 | ALGORITHM | O(n) por verificação | `isset($haystack[$needle])` com array de chaves ou `array_flip` antes do loop |
| `preg_match` recompilado por chamada com padrão constante | 🟡 | LOOP | PCRE compila o padrão; PHP pode cachear, mas depende da configuração | Verificar se `opcache.pcre.jit` está ativo; padrão constante geralmente é cacheado |
| `json_decode`/`json_encode` dentro de loop | 🟠 | MEMORY/LOOP | Serialização repetida desnecessária | Decodificar uma vez fora do loop |

---

## Concorrência e Sessões

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `session_start()` bloqueando requests concorrentes do mesmo usuário | 🟠 | CONCURRENCY | PHP mantém lock no arquivo de sessão até `session_write_close()` | Chamar `session_write_close()` o mais cedo possível; usar store baseado em Redis |
| Chamada externa bloqueante em FPM sem async | 🟠 | NETWORK | Worker FPM ocioso esperando resposta HTTP/serviço externo | Filas (Horizon/Redis), ReactPHP para I/O não-bloqueante, ou cache da resposta |

---

## Configuração e OPcache

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| OPcache desabilitado em produção | 🔴 | CONFIG | PHP recompila arquivos a cada request | Habilitar e configurar `opcache.enable=1`, `opcache.revalidate_freq=60` |
| Autoload não otimizado para produção | 🟠 | CONFIG | Composer autoload padrão verifica arquivos em cada require | `composer dump-autoload --optimize --classmap-authoritative` para produção |
| `file_get_contents` remoto sem timeout | 🟠 | NETWORK | Pode bloquear worker PHP indefinidamente | `stream_context_create` com timeout ou biblioteca HTTP com timeout |

---

## Validação recomendada

- Blackfire Profiler para CPU, memória e queries por request;
- Xdebug Profiler com kcachegrind para análise offline;
- `EXPLAIN ANALYZE` para queries SQL;
- Laravel Telescope, Debugbar para desenvolvimento;
- `ab`, `wrk`, ou `k6` para teste de carga em endpoint.
