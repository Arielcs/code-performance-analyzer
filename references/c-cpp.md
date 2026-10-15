# Anti-padrões de Performance — C / C++

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Memória e Alocação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Alocação dinâmica (`new`/`malloc`) em loop quente | 🟠 | MEMORY | Overhead de alocação e fragmentação de heap | Pré-alocar, object pool, arena allocator, stack se tamanho fixo |
| Passagem por valor de objetos pesados | 🟠 | MEMORY | Cópia completa de `std::vector`, `std::string`, structs grandes | `const&`, `std::move` quando transferência de propriedade; `std::string_view`, `std::span` |
| `std::vector` sem `reserve` antes de `push_back` em loop | 🟡 | MEMORY | Realocações e cópias ao crescer | `vector.reserve(n)` quando n é estimável |
| `std::string` construída por concatenação com `+` em loop | 🟠 | MEMORY | Cria temporários a cada `+` | `std::string::append`, `reserve` + append, ou `std::ostringstream` |
| `std::shared_ptr` quando `unique_ptr` bastaria | 🟡 | MEMORY | Contador de referência atômico tem custo desnecessário | `std::unique_ptr` para propriedade exclusiva |
| Objeto não trivial retornado por valor sem NRVO/move | 🟡 | MEMORY | Cópia não eliminada pelo compilador | Verificar se NRVO se aplica; `std::move` explícito na última linha se necessário |

---

## Localidade de Cache e Layout de Dados

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Array de ponteiros (AoP) para dados acessados sequencialmente | 🟠 | ALGORITHM | Ponteiros espalhados causam cache misses | Array de objetos (AoS) ou Structure of Arrays (SoA) conforme padrão de acesso |
| Iteração por coluna em array 2D row-major | 🟠 | ALGORITHM | Acesso não contíguo em memória — cache miss por linha | Trocar loops para iteração por linha (row-major order) |
| Struct com padding excessivo por ordem de campos | 🟢 | MEMORY | Campos pequenos intercalados com grandes desperdiçam memória | Ordenar campos do maior para o menor alinhamento |
| Branch imprevisível em loop apertado | 🟡 | ALGORITHM | Preditor de branch falha aumentando stalls de pipeline | `[[likely]]`/`[[unlikely]]`, lookup table, branchless com operações bitwise |

---

## Algoritmos e Estruturas de Dados

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Algoritmo O(n²) onde O(n log n) ou O(n) existe | 🔴 | ALGORITHM | Busca linear aninhada, insertion sort em volume grande | `std::sort`, `std::unordered_map`/`set`, algoritmos de biblioteca padrão |
| `std::list` para acesso por índice ou percurso sequencial | 🟠 | ALGORITHM | Cache-unfriendly por natureza linked-list | `std::vector` ou `std::deque`; `std::list` só quando inserção/remoção no meio é dominante |
| `std::map` (árvore) quando `std::unordered_map` bastaria | 🟡 | ALGORITHM | Lookup O(log n) desnecessário | `std::unordered_map` para O(1) médio; `std::map` só quando ordem é necessária |
| Cálculo invariante dentro de loop | 🟠 | LOOP | Expressão constante recalculada a cada iteração | Extrair para variável antes do loop (loop-invariant code motion manual) |

---

## Concorrência e Threads

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `std::mutex` cobrindo I/O ou lógica não crítica | 🟠 | CONCURRENCY | Bloqueia threads independentes desnecessariamente | Reduzir região crítica; `std::shared_mutex` para cargas leitura-intensiva |
| False sharing em estruturas compartilhadas entre threads | 🟠 | CONCURRENCY | Variáveis de threads diferentes na mesma linha de cache causam invalidação constante | Alinhar com `alignas(64)` ou separar variáveis em cache lines distintas |
| `volatile` como substituto de sincronização | 🔴 | CONCURRENCY | `volatile` não garante atomicidade nem ordenação de memória | `std::atomic`, `std::mutex`, ou barreiras de memória corretas |
| `new Thread` + join por tarefa sem pool | 🟠 | CONCURRENCY | Custo de criação de thread por operação | Thread pool (C++11+: `std::async` com policy, ou biblioteca de terceiros) |

---

## I/O

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `std::endl` em vez de `'\n'` em saída intensiva | 🟡 | IO | `std::endl` faz flush a cada chamada | Usar `'\n'`; flush manual quando necessário |
| `printf`/`cout` em loop apertado sem buffer | 🟡 | IO | Syscall por linha | `setvbuf`, `printf` em buffer intermediário, ou I/O assíncrono |
| Fread/fwrite byte a byte sem buffer | 🟠 | IO | N syscalls para N bytes | Ler em chunks; usar `fread(buf, size, count, fp)` |

---

## Validação recomendada

- `perf stat`, `perf record` + `perf report` / `flamegraph` para CPU;
- `Valgrind --tool=callgrind` para call graph e cache simulation;
- `heaptrack`, `massif` para alocações de heap;
- `AddressSanitizer`, `MemorySanitizer` para bugs de memória que impactam performance;
- Google Benchmark para microbenchmarks;
- Compilar com `-O2`/`-O3` e `-march=native` para avaliação realista.
