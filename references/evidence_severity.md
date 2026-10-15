# Evidência, impacto, confiança e regressão

## Natureza da evidência

- **Medido:** reproduzido com profiler, trace, métricas, plano de execução,
  benchmark válido ou logs suficientes; descreva workload, ambiente e comparação.
- **Evidência estática:** custo demonstrável pela estrutura do código, sem
  quantificação de impacto real em produção. Exemplo: chamada externa por item
  de uma lista sem controle de concorrência.
- **Hipótese:** depende de dados ainda não disponíveis (cardinalidade, tráfego,
  plano, configuração runtime, frequência de execução ou tamanho do payload).
  Descreva a coleta que permite confirmar/refutar.

**Heurística de inventário é sempre um indício para triagem, nunca evidência medida.**
Ausência de alerta heurístico não implica ausência de gargalo.

## Severidade contextual

| Nível | Critério |
|---|---|
| Crítica | Falha de SLO, indisponibilidade, exaustão ou impacto grave comprovado no fluxo crítico. |
| Alta | Degradação substancial demonstrada ou risco concreto sustentado por carga e caminho de execução. |
| Média | Ineficiência relevante e localizada, com condições de acionamento plausíveis. |
| Baixa | Oportunidade com impacto pequeno ou residual, confirmada ou suficientemente motivada. |
| Observação | Hipótese ainda não verificável; **não rotular como defeito confirmado**. |

A criticidade não vem diretamente do nome de API, SQL ou antipadrão. Sempre
explicite confiança (`alta/média/baixa`) **separadamente** da severidade.

## Validação da correção

- Defina cenário reproduzível, baseline, warm-up, amostragem, percentis, variação
  e limites de CPU/memória/I/O quando couber.
- Cubra contratos, ordenação, cardinalidade, duplicidade, transações, locking,
  cache, fallback, retries, timeouts, concorrência e semântica de erros.
- SQL: compare resultados e plano; `EXPLAIN ANALYZE` **executa** consultas e
  pode gerar efeito colateral para operações de escrita: não rode em produção
  sem salvaguardas/autorização.
- Otimização de `OR` para `UNION ALL` pode introduzir duplicatas; trocas de
  joins, paginação ou índices exigem análise de semântica/custo de escrita.
- Considere regressões nos chamadores e integrações, e faça rollback se necessário.
- Sem executar testes ou medir, declare a validação **não realizada**.
