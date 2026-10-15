# Guia de execução — V3

Os comandos são opcionais: para code-scan pequeno a análise é feita no chat,
sem scripts. Execute sempre a partir do diretório de seu projeto (ou use caminhos absolutos).

## Inventário opcional para project-scan

```bash
python3 /CAMINHO/DA/SKILL/scripts/project_inventory.py \
  --project-root /CAMINHO/DO/PROJETO \
  --output-root /CAMINHO/DE/SAIDA \
  --top-n 30
```

Resultados: `project_inventory.json` e `project_inventory.md`.
Scores indicam **ordem de inspeção**, não a existência/severidade de um gargalo.
Leia controladores, serviços, repositórios, jobs, integrações e configs conforme
os fluxos de execução relevantes. O script não executa, modifica ou instrumenta o projeto.

## Relatório opcional

```bash
python3 /CAMINHO/DA/SKILL/scripts/generate_report.py \
  --mode project-scan --filename meu_projeto --output-root .
```

Para análise pontual, use `--mode code-scan`. O script cria um relatório inicial
**apenas se solicitado**; cabe ao agente preencher os achados reais e os limites.
Cada execução gera pasta nova e não sobrescreve análises anteriores.

## Em agentes

1. Descubra a localização de `SKILL.md` com as ferramentas de skills disponíveis.
2. Resolva `scripts/` relativamente à pasta desse arquivo; não faça `find` amplo
   no home ou sistema de arquivos para descobrir a instalação.
3. Carregue apenas a referência do modo, as linguagens envolvidas e as
   evidências pertinentes.
4. Não leia todo o código em profundidade: priorize fluxos e hot paths.
5. Não envie código proprietário, segredos, outputs e relatórios para serviços
   externos sem autorização expressa.

## Compatibilidade

Python 3.9+ (stdlib); sem dependências externas. Inclui testes unittest:

```bash
python3 -m unittest discover -s tests -v
```
