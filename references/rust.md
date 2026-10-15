# Anti-padrões de Performance — Rust

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Propriedade, Borrowing e Clones

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `.clone()` desnecessário de dados grandes | 🟠 | MEMORY | Cópia profunda por conveniência sem necessidade real | Borrowing (`&` ou `&mut`), `Rc`/`Arc` quando compartilhado, mover propriedade |
| `.to_string()` / `.to_owned()` em hot path sem necessidade | 🟡 | MEMORY | Aloca nova String quando `&str` bastaria | Aceitar `&str` em funções; converter só quando necessário armazenar |
| Clonar `Vec` para passar a função que aceita slice | 🟠 | MEMORY | Cópia desnecessária | Passar `&[T]` (slice) |
| `collect()` intermediário desnecessário | 🟡 | MEMORY | Materializa iterador em `Vec` quando iteração direta bastaria | Encadear iteradores lazy; `collect()` só quando estrutura de dados final é necessária |

---

## Alocação e Memória

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `Vec` sem capacidade estimada em loop | 🟡 | MEMORY | Realoca ao crescer: O(log n) realocações | `Vec::with_capacity(n)` quando n é estimável |
| `String` construída com `+` em loop | 🟠 | MEMORY | Cada `+` pode alocar | `String::with_capacity(n)` + `push_str` ou `format!` uma vez |
| Alocação em hot path que poderia ser stack | 🟠 | MEMORY | Boxed values (`Box<T>`) desnecessários para dados pequenos | Tipo de tamanho fixo na stack; box só para polimorfismo/tamanho dinâmico |
| Buffer reutilizável não aproveitado | 🟡 | MEMORY | Aloca novo buffer a cada chamada em loop de I/O | Reutilizar `Vec<u8>` ou `BufWriter`/`BufReader` como buffer |

---

## Iteradores e Algoritmos

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Algoritmo O(n²) em coleção grande | 🔴 | ALGORITHM | Busca linear aninhada, comparações de pares | `HashMap`/`HashSet`, ordenação + two-pointers, índice |
| `contains` em `Vec` repetido | 🟠 | ALGORITHM | O(n) por chamada em loop | `HashSet` para lookup O(1) |
| Iterador não short-circuitado | 🟡 | ALGORITHM | `.filter().map().collect()` quando `.find()` ou `.any()` era suficiente | Usar operações de short-circuit: `any`, `all`, `find`, `position` |
| `.sort()` quando `sort_unstable()` bastaria | 🟢 | ALGORITHM | `sort` preserva ordem de iguais com custo extra | `sort_unstable()` quando ordem de iguais não importa |

---

## Concorrência Async (Tokio / async-std)

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `Mutex` segurado durante `.await` | 🔴 | CONCURRENCY | Bloqueia outras tasks enquanto aguarda I/O | Soltar o lock antes do await; usar `tokio::sync::Mutex` se necessário manter entre awaits |
| Futures independentes com `await` sequencial | 🟠 | NETWORK | Execução serializada sem necessidade | `tokio::join!`, `futures::join_all`, `FuturesUnordered` com limite |
| Spawnar task por item sem limite de concorrência | 🟠 | CONCURRENCY | Pode saturar I/O ou CPU | `Semaphore`, `FuturesUnordered` com `buffer_unordered(n)` |
| Operação CPU-bound em runtime async | 🔴 | CONCURRENCY | Bloqueia thread do runtime, travando tasks async | `tokio::task::spawn_blocking` para código bloqueante |
| Channel com `send` não aguardado em runtime finalizado | 🟠 | CONCURRENCY | Mensagens perdidas silenciosamente | Awaitar `send`, usar `try_send` com tratamento ou garantir que receiver viva |

---

## Serialização e I/O

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `serde_json::from_str` / `to_string` sem `simd-json` em hot path | 🟢 | ALGORITHM | Para volumes muito altos, `serde_json` pode ser o gargalo | Avaliar `simd-json` ou `sonic-rs` para parsing massivo com benchmark |
| I/O sem buffer (`File::write` por pequeno chunk) | 🟠 | IO | Muitas syscalls pequenas | `BufWriter`, `BufReader` para envolver o handle |
| Desserialização de campos não usados | 🟢 | MEMORY | `#[derive(Deserialize)]` materializando campos descartados | `#[serde(skip)]`, `serde_with` ou desserialização manual parcial |

---

## Validação recomendada

- `cargo bench` + Criterion para microbenchmarks com análise estatística;
- `cargo flamegraph` ou `perf record` + `flamegraph` para CPU profiling;
- `heaptrack`, `dhat` (Valgrind) para análise de alocações de heap;
- `tokio-console` para diagnóstico de runtime async;
- `cargo build -gcflags="-m"` — inexistente em Rust; usar `cargo asm` para inlining;
- `RUSTFLAGS="-C target-cpu=native"` para habilitar otimizações de CPU no benchmark.
