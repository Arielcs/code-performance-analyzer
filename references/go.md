# Anti-padrões de Performance — Go

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Goroutines e Concorrência

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Goroutine leak | 🔴 | CONCURRENCY | Goroutine fica bloqueada sem caminho de saída ou cancelamento | `context.Context` com cancelamento/timeout; fechar canal no produtor |
| Canal nunca fechado quando consumidor aguarda | 🟠 | CONCURRENCY | Consumidor em `range chan` bloqueia indefinidamente | Fechar o canal no produtor responsável quando produção terminar |
| Goroutines ilimitadas para processamento em lote | 🟠 | CONCURRENCY | Criar N goroutines simultâneas sem controle satura recursos | Worker pool com semáforo (`chan struct{}`), `errgroup` com `SetLimit` |
| Mutex com escopo mais amplo do que necessário | 🟠 | CONCURRENCY | Bloqueia trabalho independente dentro da região crítica | Reduzir região crítica; `sync.RWMutex` para cargas leitura-intensiva |
| `sync.Mutex` onde `sync/atomic` bastaria | 🟡 | CONCURRENCY | Lock completo para operação atômica simples | `atomic.Int64`, `atomic.Pointer` (Go 1.19+) |
| `time.Sleep` em goroutine de polling | 🟠 | CONCURRENCY | Polling ocupado ou com granularidade errada | `time.Ticker`, canal de sinal ou event-driven |

---

## Memória e Alocação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Slice sem capacidade estimada | 🟡 | MEMORY | `make([]T, 0)` sem capacidade realoca e copia ao crescer | `make([]T, 0, n)` quando n é estimável |
| Map sem capacidade inicial | 🟡 | MEMORY | `make(map[K]V)` sem hint realoca ao crescer | `make(map[K]V, n)` |
| `defer` dentro de loop com recurso por iteração | 🟠 | MEMORY/IO | Defers acumulam e são executados só no retorno da função, não do loop | Encapsular corpo do loop em função interna ou fechar explicitamente |
| String → `[]byte` → String sem necessidade | 🟡 | MEMORY | Conversão cria cópia | Usar `strings.Builder`, `bytes.Buffer` ou `unsafe` com cuidado se crítico |
| Alocação no heap de estrutura pequena por escape analysis | 🟡 | MEMORY | Struct escapa para heap quando poderia ficar na stack | Passar por valor quando pequena; verificar com `go build -gcflags="-m"` |

---

## Strings e Formatação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `fmt.Sprintf` para concatenação simples em caminho quente | 🟡 | MEMORY | Formatação genérica é mais lenta e aloca | `strings.Builder`, `+` para duas strings, `strconv` para conversão |
| `strings.Contains` repetido com substring constante | 🟢 | ALGORITHM | Para N strings, pode compilar regex ou usar `bytes.Index` | Compilar `regexp.MustCompile` fora do loop para múltiplas verificações |
| Conversão entre `string` e `[]byte` em loop quente | 🟠 | MEMORY | Aloca a cada conversão | Trabalhar em um único tipo ao longo do fluxo; usar `io.Writer` quando possível |

---

## Banco e Rede

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Query por item em loop (N+1) | 🔴 | DB | Uma query por elemento processado | Buscar em lote com `IN (...)` ou JOIN antes do loop |
| `http.Client` sem timeout | 🟠 | NETWORK | `http.DefaultClient` não tem timeout; pode bloquear indefinidamente | `http.Client{Timeout: tempo}` e passar `context` com deadline |
| `http.DefaultTransport` para serviço com alto volume | 🟠 | NETWORK | Limites de conexão por host podem ser insuficientes | Configurar `MaxIdleConnsPerHost`, `MaxConnsPerHost` e `IdleConnTimeout` |
| Abrir `*sql.DB` por request em vez de reutilizar | 🔴 | DB/CONFIG | `sql.Open` é caro e não reutiliza pool | Uma instância `*sql.DB` por DSN, compartilhada via injeção de dependência |

---

## Reflexão e Interfaces

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `reflect` em loop quente | 🟠 | ALGORITHM | Reflexão é ordens de magnitude mais lenta que acesso tipado | Código tipado, `interface{}` com type switch, ou generics (Go 1.18+) |
| Interface de granularidade muito fina causando boxing/unboxing frequente | 🟡 | MEMORY | Converter tipos concretos em `interface{}` em hot path aloca | Manter tipo concreto em hot path; usar interface só em fronteiras de abstração |

---

## Validação recomendada

- `go test -bench=. -benchmem` para benchmarks com alocações;
- `pprof` (CPU, heap, goroutine, mutex, block profiles);
- `go tool trace` para análise de concorrência;
- `go build -gcflags="-m"` para escape analysis;
- `goleak` para detectar goroutine leaks em testes.
