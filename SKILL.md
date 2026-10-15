---
name: code-performance-analyzer
description: >-
  Analisa performance de funções, arquivos e projetos, investigando gargalos em algoritmos,
  banco de dados, I/O, rede, memória, concorrência e renderização. Possui code-scan
  (análise pontual) e project-scan (inventário e investigação por fluxo). Distingue
  evidências medidas, evidências estáticas e hipóteses, priorizando correções verificáveis.
---

# Code Performance Analyzer — V3

## Ativação e princípios

- Use quando o usuário solicitar explicitamente esta skill ou uma análise de performance.
- Somente leitura por padrão: **não altere código, banco, infra ou configurações** sem autorização.
- Nunca afirme que uma heurística, regex ou nome de arquivo comprova gargalo.
- Não infira ganho percentual, severidade crítica, custo ou regressão sem evidência.
- Leia só o que o escopo exige; evite ferramentas e artefatos desnecessários.
- Não publique, envie ou registre dados do projeto em serviços externos sem autorização.

## Escolha do modo

1. **`code-scan`** — trecho, função, arquivo ou módulo pequeno. Siga `references/code_scan.md`.
   Responda no chat. **Não crie pastas, inventários ou relatórios** a menos que solicitados.
2. **`project-scan`** — repositório, pasta ampla, aplicação ou projeto inteiro. Siga
   `references/project_scan.md`: inventário → priorização → investigação dos fluxos
   críticos → validação → cobertura e limites. Salve relatórios só quando solicitados
   ou quando o pedido incluir um entregável documental.

## Rotina obrigatória de investigação

1. Delimite escopo, hot path, volume, frequência, ambiente e sinais observáveis.
   Na ausência desses dados, avance com hipóteses explícitas e conservadoras.
2. Leia arquivos relevantes e, quando necessário, os chamadores, dependências, SQLs,
   configurações e limites de concorrência para entender o fluxo ponta a ponta.
3. Para cada achado, cite `arquivo:linha` ou o trecho efetivamente lido.
   Diferencie **medido**, **evidência estática** e **hipótese** (`references/evidence_severity.md`).
4. Classifique por impacto provável, confiança, alcance e custo/risco da correção.
5. Proponha mudança concreta + teste de equivalência funcional + medição antes/depois.
   Se não puder confirmar, explique exatamente qual dado/execução falta.
6. Registre escopo, cobertura e pontos examinados sem problema *apenas quando lidos*.

## Referências sob demanda

- Sempre que necessário: `references/evidence_severity.md`; padrões transversais:
  `references/general.md`.
- Carregue apenas as linguagens presentes: `java.md`, `sql.md`, `python.md`,
  `javascript-typescript.md`, `go.md`, `c-cpp.md`, `php.md`, `ruby.md`, `rust.md`.
  Para outra linguagem, use `general.md` e documentação relevante.
- Para varredura ampla: `references/project_scan.md` e
  `scripts/project_inventory.py`. **Scores apenas ordenam candidatos.**
- Para relatórios solicitados: `references/report_template.md` (code-scan),
  `references/project_report_template.md` (project-scan), `scripts/generate_report.py`.
- Guia operacional e exemplos: `references/execution_guide.md` (sob demanda).

## Saída

Entregue primeiro os achados de maior impacto, evidência, local exato, consequência,
correção e método de validação. Separe "Não verificáveis" de problemas confirmados.
Se não encontrar problemas demonstráveis, diga isso e identifique os limites da análise.
Não confunda melhoria de estilo com melhoria de desempenho.
