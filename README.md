# Code Performance Analyzer — V3

Skill para análise de performance de código e projetos. Reúne a análise pontual
enxuta da V1 com investigação por fluxo, inventário e referências da V2.

## Capacidades

- `code-scan`: análise pontual, com resposta no chat e sem criar arquivos por padrão.
- `project-scan`: inventário de candidatos → priorização → análise por fluxo.
- Evidências separadas em **medição**, **inferência estática** e **hipótese**.
- Sugestões com localização, custo/risco, testes de regressão e validação antes/depois.
- Inventário estático e geração opcional de pastas de relatórios; não altera o projeto.
- Política de invocação explícita em `agents/openai.yaml` quando suportada.

## Instalação (Codex)

Clone este repositório, coloque a pasta `code-performance-analyzer` no diretório
local de skills do Codex e reinicie a sessão, conforme o ambiente instalado.
Se o repositório contiver `SKILL.md` na raiz, essa própria raiz é a skill.

## Execução dos scripts (opcional)

```bash
python3 scripts/project_inventory.py --project-root /projeto --output-root /tmp/perf-inventario
python3 scripts/generate_report.py --mode project-scan --filename nome-do-projeto --output-root .
python3 -m unittest discover -s tests -v
```

`project_inventory.py` produz **sinais de triagem**, não comprova gargalos.
A skill exige confirmação por leitura do fluxo e/ou medição. Não rode comandos
potencialmente perigosos em produção sem autorização.

## Estrutura

- `SKILL.md`: instruções curtas e roteamento por modo.
- `references/`: fluxos, critérios, templates e checklists por linguagem.
- `scripts/`: inventário e scaffolding de relatório em Python sem dependências.
- `tests/`: cenários regressivos contra falsos positivos, sobrescrita etc.

## Publicação e privacidade

A skill é independente de qualquer projeto analisado. Não publique código-fonte,
logs, métricas, credenciais nem conteúdo de repositórios privados junto dela.
A publicação deste material em um repositório público **não muda a visibilidade**
de nenhum outro repositório. Nenhuma licença de terceiros é presumida.
