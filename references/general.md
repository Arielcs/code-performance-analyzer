# Anti-padrões Gerais de Performance

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Use este arquivo para qualquer linguagem quando o problema envolver arquitetura, banco, I/O, rede, cache, concorrência, configuração ou observabilidade. Também consulte este arquivo junto à referência da linguagem quando a análise atravessar essas camadas.

---

## I/O e Arquivo

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Leitura de arquivo dentro de loop | 🔴 | IO | Arquivo aberto/lido repetidamente por item processado | Ler uma vez, usar buffer ou streaming controlado |
| Escrita síncrona por item | 🟠 | IO | Cada item dispara uma escrita em disco/banco/rede | Agrupar em lote, bufferizar ou usar fila |
| Carregar arquivo inteiro em memória | 🟠 | IO/MEMORY | `read()` em arquivo grande quando só parte é necessária | Streaming, iteração linha a linha, leitura parcial |
| Flush excessivo | 🟡 | IO | Força flush a cada escrita em vez de agrupar | Bufferizar e controlar flush manualmente |
| Abertura de conexão/arquivo por operação | 🔴 | IO | Cria e fecha recurso a cada chamada dentro de loop | Reutilizar conexão/stream fora do loop |

---

## Banco de Dados e Consultas

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Sem paginação em listagens | 🔴 | DB | Consultas retornam registros ilimitados | Paginação, limite, cursor ou streaming |
| Transação longa com lógica externa | 🟠 | DB | Mantém locks enquanto executa I/O, rede ou processamento pesado | Reduzir escopo da transação, separar fases |
| Contagem total sem índice | 🟡 | DB | `COUNT(*)` sem índice em tabela grande força full scan | Índice, cache do total ou paginação sem total exato |
| Processamento em app que deveria estar no banco | 🟡 | ALGORITHM | Filtros, agregações ou ordenações feitos em memória desnecessariamente | Empurrar para o banco, usar índice adequado |
| Múltiplas queries que poderiam ser uma | 🟠 | DB | Dados relacionados buscados em queries separadas quando um JOIN/batch resolveria | JOIN, CTE, subquery, batch |

---

## Memória e Alocação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Processar dataset grande inteiro em memória | 🔴 | MEMORY | Carrega tudo em lista/map antes de processar | Paginar, streamar, processar em chunks |
| Cópias desnecessárias de estruturas grandes | 🟠 | MEMORY | Passa/retorna coleção por valor onde referência bastaria | Referência, iterador, view imutável |
| Cache sem limite de tamanho | 🟠 | MEMORY | Cache que cresce indefinidamente pode causar OOM | Limite de entradas, TTL, política de evição (LRU/LFU) |
| Objetos pesados criados e descartados em loop | 🟠 | MEMORY | Pressiona o GC desnecessariamente | Reusar, pré-alocar, mover criação para fora do loop |

---

## Rede e Comunicação

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Operações de rede sequenciais sem dependência | 🟠 | NETWORK | Chamadas independentes aguardadas uma a uma | Paralelizar com limite de concorrência e timeout |
| Sem timeout configurado | 🟠 | NETWORK | HTTP, banco, fila ou I/O pode bloquear indefinidamente | Configurar timeout, retry controlado e circuit breaker |
| Retry sem backoff | 🟠 | NETWORK | Retentativas imediatas amplificam falha downstream | Exponential backoff, jitter e limite de tentativas |
| Payload excessivo | 🟡 | NETWORK | Endpoint trafega campos maiores que o necessário | Projeção de campos, compressão, paginação |
| Pooling de conexões ausente ou mal configurado | 🟠 | NETWORK/CONFIG | Abre/fecha conexão por operação ou pool muito pequeno | Pool configurado com base em carga real |

---

## Cache

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Operação custosa repetida sem cache | 🟠 | CACHE | Mesmo cálculo, consulta ou parsing executado com os mesmos parâmetros | Cache local, memoização, cache distribuído ou pré-processamento |
| Cache sem TTL ou invalidação | 🟠 | CACHE | Dados obsoletos servidos indefinidamente | TTL adequado, invalidação por evento ou version key |
| Cache com chave ruim gerando falsos misses | 🟡 | CACHE | Chave inclui campos variáveis desnecessários | Revisar composição da chave |
| Parsing de configuração a cada request | 🟠 | CACHE | Arquivo/variáveis carregadas e parseadas por chamada | Parsear no startup, cachear resultado |

---

## Concorrência

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Lock amplo cobrindo I/O ou rede | 🔴 | CONCURRENCY | Região crítica inclui operações lentas, bloqueando outras threads | Reduzir escopo: adquirir lock só para a seção crítica mínima |
| Paralelismo sem limite de concorrência | 🟠 | CONCURRENCY | Cria N goroutines/threads/tasks sem controle, podendo saturar recursos | Semáforo, pool de workers, batch size configurável |
| Polling ocupado | 🔴 | CONCURRENCY | Loop de espera ativa consome CPU desnecessariamente | Canal/event/condition variable/sleep controlado |
| Acesso compartilhado sem sincronização | 🔴 | CONCURRENCY | Race condition silenciosa que pode causar corrupção ou travamento | Sincronização adequada, estruturas imutáveis ou thread-local |

---

## Jobs, Workers e Processamento em Lote

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Job sem chunk/paginação | 🔴 | MEMORY/DB | Processa todos os registros de uma vez em memória | Dividir em chunks, paginar, usar cursor |
| Job sem checkpoint | 🟠 | CONFIG | Falha no meio refaz tudo do início | Salvar progresso e permitir retomada |
| Paralelismo de job sem backpressure | 🟠 | CONCURRENCY | Muitas tarefas simultâneas sobrecarregam banco ou serviços downstream | Limitar concorrência, controlar fila |
| Log síncrono e verboso dentro de job massivo | 🟡 | CONFIG | Cada item gera I/O de log síncrono | Async logging, batch flush, reduzir verbosidade |

---

## Configuração e Infraestrutura

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Logging verbose em caminho crítico | 🟡 | CONFIG | Logs de debug/trace em loops, endpoints acessados ou processamento em lote | Reduzir nível, amostragem ou logs assíncronos |
| Pool de thread/conexão subdimensionado | 🟠 | CONFIG | Pool pequeno para a demanda, criando fila ou rejeição | Ajustar com base em métricas reais de carga |
| Timeout muito alto ou ausente | 🟠 | CONFIG | Operações lentas acumulam e esgotam recursos | Timeout proporcional ao SLA, com fallback |
| Batch size fixo sem base em medição | 🟡 | CONFIG | Tamanho de lote arbitrário — muito pequeno gera overhead; muito grande pressiona memória | Calibrar com métricas de tempo, memória e throughput |

---

## Observabilidade

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Gargalo crítico sem instrumentação | ⚪ | OBSERVABILITY | Operação provavelmente lenta, mas sem dado de runtime para confirmar | Adicionar métricas, trace ou log de tempo antes de otimizar |
| Otimização sem baseline medido | 🟡 | OBSERVABILITY | Refatoração feita sem medir antes, impossibilitando validar ganho | Medir p50/p95/p99 e volume antes de mudar |

---

## Ajuste de Severidade

- Aumente para 🔴 quando o trecho estiver em endpoint crítico, loop massivo, job com SLA, produção ou risco de timeout/OOM.
- Reduza para 🟡/🟢 quando o código for raramente executado, operar poucos dados ou for ferramenta interna.
- Use ⚪ Observação quando depender de plano de execução, volume real, profiling ou APM.
