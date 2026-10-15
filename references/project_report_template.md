# 📊 Relatório de Análise de Performance — Projeto Inteiro

> **V3:** para cada achado, distinguir `medido / evidência estática / hipótese`, confiança, contexto e validação funcional+benchmark. Indicar expressamente quando não houve teste nem medição. Não preencha placeholders com invenções.

> **Nome da análise:** `{NOME_ANALISE}`  
> **Modo:** `project-scan`  
> **Data/Hora:** `{DATA_HORA}`  
> **Projeto/Repositório:** `{PROJETO}`  
> **Stack identificada:** `{STACK}`  
> **Tipo de projeto:** `{TIPO_PROJETO}`  
> **Total de problemas encontrados:** `{TOTAL}`

---

## 1. Resumo Executivo

{RESUMO_EXECUTIVO}

### Distribuição por Severidade

| Severidade | Qtd | Observação |
|------------|-----|------------|
| 🔴 Crítico | `{QTD_CRITICO}` | `{OBS_CRITICO}` |
| 🟠 Alto | `{QTD_ALTO}` | `{OBS_ALTO}` |
| 🟡 Médio | `{QTD_MEDIO}` | `{OBS_MEDIO}` |
| 🟢 Baixo | `{QTD_BAIXO}` | `{OBS_BAIXO}` |
| ⚪ Observação | `{QTD_OBSERVACAO}` | `{OBS_OBSERVACAO}` |

---

## 2. Contexto Informado

| Item | Informação |
|------|------------|
| Volume de dados esperado | `{VOLUME_DADOS}` |
| Frequência de execução | `{FREQUENCIA}` |
| Ambiente | `{AMBIENTE}` |
| Evidência de lentidão/profiling | `{EVIDENCIA}` |
| Restrições conhecidas | `{RESTRICOES}` |
| Escopo solicitado | `{ESCOPO_SOLICITADO}` |

---

## 3. Premissas e Limitações

{PREMISSAS_LIMITACOES}

---

## 4. Inventário do Projeto

| Item | Resultado |
|------|-----------|
| Linguagem principal | `{LINGUAGEM_PRINCIPAL}` |
| Linguagens secundárias | `{LINGUAGENS_SECUNDARIAS}` |
| Frameworks/bibliotecas relevantes | `{FRAMEWORKS}` |
| Arquivos de configuração relevantes | `{CONFIGS}` |
| Pontos de entrada identificados | `{PONTOS_ENTRADA}` |
| Camadas identificadas | `{CAMADAS}` |

---

## 5. Cobertura da Análise

| Tipo | Qtd | Critério/observação |
|------|-----|---------------------|
| Arquivos encontrados | `{QTD_ARQUIVOS}` | `{OBS_ARQUIVOS}` |
| Arquivos ignorados | `{QTD_IGNORADOS}` | `{CRITERIO_IGNORADOS}` |
| Arquivos apenas mapeados | `{QTD_MAPEADOS}` | `{OBS_MAPEADOS}` |
| Arquivos analisados superficialmente | `{QTD_SUPERFICIAL}` | `{OBS_SUPERFICIAL}` |
| Arquivos analisados profundamente | `{QTD_PROFUNDO}` | `{OBS_PROFUNDO}` |

### 5.1 Pastas/Arquivos Ignorados

| Caminho/Padrão | Motivo |
|----------------|--------|
| `{IGNORADO_1}` | `{MOTIVO_IGNORADO_1}` |

### 5.2 Arquivos Analisados Profundamente

| Arquivo | Papel arquitetural | Motivo da priorização |
|---------|--------------------|-----------------------|
| `{ARQUIVO_PROFUNDO_1}` | `{PAPEL_1}` | `{MOTIVO_PRIORIZACAO_1}` |

### 5.3 Arquivos Analisados Superficialmente ou Apenas Mapeados

| Arquivo | Classificação | Observação |
|---------|---------------|------------|
| `{ARQUIVO_MAPEADO_1}` | `{CLASSIFICACAO_1}` | `{OBS_MAPEADO_1}` |

---

## 6. Mapa de Riscos por Camada

| Camada | Risco identificado | Impacto provável | Evidência no código |
|--------|--------------------|------------------|---------------------|
| `{CAMADA_1}` | `{RISCO_1}` | `{IMPACTO_1}` | `{EVIDENCIA_1}` |

---

## 7. Top 3 Prioridades

1. **{PRIORIDADE_1}** — {MOTIVO_1}
2. **{PRIORIDADE_2}** — {MOTIVO_2}
3. **{PRIORIDADE_3}** — {MOTIVO_3}

---

## 8. Problemas Encontrados

> Ordenar por severidade e impacto provável: 🔴 → 🟠 → 🟡 → 🟢 → ⚪.

### [{SEVERIDADE}] {TITULO_PROBLEMA}

**Categoria:** `{CATEGORIA}`  
**Fluxo/Camada:** `{FLUXO_CAMADA}`  
**Arquivo:** `{ARQUIVO}`  
**Linha(s):** `{LINHAS}`  
**Confiança:** `{CONFIANCA}`  
**Cenário de impacto:** `{CENARIO_IMPACTO}`

#### ❌ Código problemático

```{LINGUAGEM}
{CODIGO_PROBLEMATICO}
```

#### ⚠️ Por que pode causar lentidão

{EXPLICACAO}

#### ✅ Melhoria recomendada

```{LINGUAGEM}
{CODIGO_CORRIGIDO}
```

#### 💡 Justificativa da melhoria

{JUSTIFICATIVA}

#### 🧪 Como validar

{COMO_VALIDAR}

---

<!-- Repetir o bloco acima para cada problema encontrado -->

---

## 9. Itens Avaliados Sem Problema Encontrado

| Arquivo/Trecho | O que foi avaliado | Por que não foi classificado como problema |
|----------------|--------------------|--------------------------------------------|
| `{TRECHO_OK_1}` | `{AVALIACAO_1}` | `{JUSTIFICATIVA_OK_1}` |

---

## 10. Pontos que Dependem de Profiling ou Métricas Reais

| Ponto | Por que depende de medição | Ferramenta/ação recomendada |
|-------|-----------------------------|-----------------------------|
| `{PONTO_1}` | `{MOTIVO_MEDICAO_1}` | `{ACAO_1}` |

---

## 11. Melhorias Rápidas

| Melhoria | Esforço | Impacto esperado | Arquivo/fluxo relacionado |
|----------|---------|------------------|---------------------------|
| `{MELHORIA_RAPIDA_1}` | `{ESFORCO_1}` | `{IMPACTO_RAPIDO_1}` | `{RELACIONADO_1}` |

---

## 12. Melhorias Estruturais

| Melhoria | Esforço | Impacto esperado | Risco/observação |
|----------|---------|------------------|------------------|
| `{MELHORIA_ESTRUTURAL_1}` | `{ESFORCO_ESTRUTURAL_1}` | `{IMPACTO_ESTRUTURAL_1}` | `{RISCO_ESTRUTURAL_1}` |

---

## 13. Plano de Validação

1. {PASSO_VALIDACAO_1}
2. {PASSO_VALIDACAO_2}
3. {PASSO_VALIDACAO_3}

---

## 14. Ferramentas Recomendadas

{FERRAMENTAS_RECOMENDADAS}

---

## 15. Conclusão

{CONCLUSAO}

---

*Relatório gerado pela skill `code-performance-analyzer` em modo `project-scan`.*
