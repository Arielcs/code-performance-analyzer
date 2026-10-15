# Anti-padrões de Performance — JavaScript / TypeScript

> **V3 — orientação de leitura:** as severidades desta tabela são exemplos históricos de triagem, **não classificações automáticas**. Aplique `evidence_severity.md` a cada achado com contexto e evidência; não presuma ganhos nem correções universalmente seguras.


Consulte também `general.md` quando o problema envolver banco, rede, I/O, cache, concorrência ou configuração.

---

## Renderização e DOM

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| DOM query (`querySelector`, `getElementById`) em loop | 🟠 | RENDER/LOOP | Consulta DOM repetida é custosa | Cachear referência fora do loop |
| Layout thrashing (read + write alternados) | 🔴 | RENDER | Misturar leitura (`offsetWidth`) com escrita CSS força recálculo de layout a cada iteração | Agrupar leituras e depois escritas; usar `requestAnimationFrame` |
| Listas grandes sem virtualização | 🔴 | RENDER | Renderizar milhares de itens no DOM ao mesmo tempo | Virtual scroll, paginação ou renderização incremental |
| Imagens sem dimensões explícitas | 🟡 | RENDER | Causa layout shift e reflow durante carregamento | `width`/`height` no elemento ou CSS aspect-ratio |
| `innerHTML` em loop para construir DOM | 🟠 | RENDER | Parsing e serialização HTML repetidos | `DocumentFragment`, `createElement` + `appendChild` em lote |

---

## React

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Re-render desnecessário por referência instável | 🟠 | RENDER | Objeto/array/função recriado a cada render sem necessidade | `useMemo`, `useCallback`, `React.memo` quando mensurado |
| Vários `setState` sequenciais | 🟡 | RENDER | Pode gerar renderizações extras antes do batching automático | Agrupar em objeto único ou usar `useReducer` |
| `useEffect` com dependências erradas | 🟠 | RENDER | Array de dependências incompleto ou ausente causa execuções excessivas | Revisar dependências; separar efeitos por responsabilidade |
| Componente enorme sem splitting | 🟡 | RENDER | Rerender propaga para subárvore grande desnecessariamente | Dividir componentes, isolar partes estáticas |
| `key` instável ou baseada em índice em lista mutável | 🟠 | RENDER | Causa desmonte e remonte desnecessário de elementos | Usar identificador estável e único como key |

---

## Angular

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Change detection `Default` em component pesado | 🟠 | RENDER | Verifica toda a árvore a cada ciclo | `ChangeDetectionStrategy.OnPush` onde aplicável |
| Pipe impuro em template com dados grandes | 🟠 | RENDER | Pipe impuro é chamado a cada ciclo de detecção | Usar pipe puro ou calcular fora do template |
| Função chamada diretamente no template | 🟠 | RENDER | Executada em todo ciclo de detecção | Calcular no componente, expor como propriedade ou usar pipe puro |
| `*ngFor` sem `trackBy` em lista mutável | 🟡 | RENDER | Re-renderiza todos os itens ao mudar a referência da lista | Implementar `trackBy` com identificador estável |
| Subscriptions sem `takeUntil`/`async pipe` | 🟠 | MEMORY | Vazamento de subscription ao destruir componente | `async pipe`, `takeUntil(destroy$)` ou `takeUntilDestroyed()` |

---

## Assincronismo e Rede

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `await` sequencial sem dependência | 🟠 | NETWORK | Chamadas independentes aguardadas uma a uma | `Promise.all` ou `Promise.allSettled` com limite de concorrência |
| Sem debounce/throttle em evento frequente | 🟠 | RENDER/NETWORK | `scroll`, `resize`, `input`, `keydown` disparam muitas execuções | `debounce`, `throttle`, `requestAnimationFrame` |
| Requisição repetida sem cache no cliente | 🟠 | NETWORK | Mesmos dados buscados a cada interação | Cache em memória, SWR/React Query, ou HTTP cache headers |
| `JSON.parse/stringify` em loop ou hot path | 🟠 | MEMORY/LOOP | Serialização repetida é custosa | Parsear uma vez, cachear resultado ou evitar conversão |
| `new AbortController` nunca acionado | 🟡 | NETWORK | Requisição em andamento não é cancelada ao trocar filtros/rota | Abortar no cleanup do efeito ou ao nova requisição iniciar |

---

## Memória e Vazamentos

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Event listener sem remoção | 🟠 | MEMORY | Acumula em SPAs ao navegar ou destruir componente | `removeEventListener` no cleanup, ou `AbortSignal` |
| Closure retendo referência a objeto grande | 🟡 | MEMORY | Objeto não pode ser coletado pelo GC por estar na closure | Limpar referência quando desnecessária (`ref = null`) |
| `setInterval` não cancelado | 🟠 | MEMORY | Continua executando e retém referências mesmo após componente destruído | `clearInterval` no cleanup |
| `WeakRef`/`WeakMap` ignorados onde cache evitável | 🟢 | MEMORY | Cache forte impedindo GC desnecessariamente | `WeakMap`/`WeakRef` para associações por objeto |

---

## Node.js (backend)

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| Operação CPU-bound no event loop principal | 🔴 | CONCURRENCY | Bloqueia todas as requisições durante processamento pesado | `worker_threads`, `child_process` ou job externo |
| Stream não consumido ou com backpressure ignorado | 🟠 | IO | `readable` acumulando dados porque `writable` não drena | Respeitar `drain`, usar `pipeline()` com tratamento de erro |
| `fs.readFileSync` / `execSync` em handler de request | 🔴 | IO | Operação bloqueante no event loop trava todas as requisições | Equivalente async (`fs.promises`, `exec`) |
| Sem pool de conexão para banco | 🔴 | DB/CONFIG | Abre/fecha conexão por query | Pool via Prisma, pg-pool, mongoose etc. |

---

## Geral JS/TS

| Anti-padrão | Severidade base | Categoria | Descrição | Melhoria comum |
|-------------|-----------------|-----------|-----------|----------------|
| `console.log` em loop ou produção | 🟢 | CONFIG | Overhead e poluição de logs | Remover ou condicionar por ambiente |
| Encadeamento de array methods em dados grandes | 🟡 | ALGORITHM | `.filter().map().reduce()` percorre várias vezes | Um único `reduce` quando volume justificar; medir antes |
| Uso de `arguments` em função quente | 🟢 | ALGORITHM | Menos eficiente que parâmetros nomeados em alguns engines | Parâmetros explícitos |

---

## Validação recomendada

- Chrome DevTools → Performance tab, Memory tab, Network;
- React Profiler, Angular DevTools, Vue Devtools;
- Lighthouse para carregamento inicial e Core Web Vitals;
- `clinic.js`, `0x`, `autocannon` para Node.js;
- WebPageTest para análise de rede real.
