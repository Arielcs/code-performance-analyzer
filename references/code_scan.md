# Code scan — análise pontual

Use em funções, trechos, arquivos ou módulos pequenos. Não execute inventário de projeto.

1. Identifique linguagem, framework, fluxo e custo potencial das operações.
2. Examine complexidade algorítmica, iterações, I/O, acesso ao banco, rede,
   alocação, serialização, contenção e renderização **somente se relevantes**.
3. Leia dependências e chamadores **quando disponíveis e quando mudarem a conclusão**.
4. Não confunda `findAll`, `SELECT *`, `await`, `synchronized` ou loop com defeito
   automático. Teste se o volume, frequência, plano, concorrência ou estrutura sustenta risco.
5. Para cada achado, anote:
   - `arquivo:linha` (ou trecho colado sem linha), comportamento e caminho executado;
   - evidência (`medição`, `estática`, `hipótese`) e confiança;
   - impacto provável e condições necessárias;
   - solução concreta e efeitos colaterais possíveis;
   - validação funcional + benchmark/perfiling/EXPLAIN apropriado.
6. Na ausência de achados, explique o que foi efetivamente analisado e o que
   permanece desconhecido. Não invente itens auditados.

**Saída padrão:** resposta concisa no chat, agrupada por impacto, com seção de
limitações quando necessária. Sem criação de arquivos ou execução de scripts.
**Sob pedido de relatório:** use `references/report_template.md` e
`scripts/generate_report.py`. Não declare ganhos de performance sem medição.
