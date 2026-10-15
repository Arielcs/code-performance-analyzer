# 📊 Relatório de Análise de Performance — Código/Módulo

> **V3:** para cada achado, distinguir `medido / evidência estática / hipótese`, confiança, contexto e validação funcional+benchmark. Indicar expressamente quando não houve teste nem medição. Não preencha placeholders com invenções.

> **Nome da análise:** `{NOME_ANALISE}`  
> **Modo:** `code-scan`  
> **Data/Hora:** `{DATA_HORA}`  
> **Linguagem(ns):** `{LINGUAGENS}`  
> **Escopo:** `{ESCOPO}`  
> **Total de problemas encontrados:** `{TOTAL}`

---

## 1. Contexto Informado

| Item | Informação |
|------|------------|
| Volume de dados esperado | `{VOLUME_DADOS}` |
| Frequência de execução | `{FREQUENCIA}` |
| Ambiente | `{AMBIENTE}` |
| Evidência de lentidão/profiling | `{EVIDENCIA}` |
| Código completo ou fragmento | `{COMPLETUDE}` |

---

## 2. Premissas e Limitações

{PREMISSAS_LIMITACOES}

---

## 3. Escopo Analisado

| Arquivo/Trecho | Linguagem | Observação |
|----------------|-----------|------------|
| `{ARQUIVO_1}` | `{LINGUAGEM_1}` | `{OBS_1}` |

---

## 4. Resumo Executivo

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

## 5. Top 3 Prioridades

1. **{PRIORIDADE_1}** — {MOTIVO_1}
2. **{PRIORIDADE_2}** — {MOTIVO_2}
3. **{PRIORIDADE_3}** — {MOTIVO_3}

---

## 6. Problemas Encontrados

> Ordenar por severidade e impacto provável: 🔴 → 🟠 → 🟡 → 🟢 → ⚪.

### [{SEVERIDADE}] {TITULO_PROBLEMA}

**Categoria:** `{CATEGORIA}`  
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

## 7. Itens Avaliados Sem Problema Encontrado

| Arquivo/Trecho | O que foi avaliado | Por que não foi classificado como problema |
|----------------|--------------------|--------------------------------------------|
| `{TRECHO_OK_1}` | `{AVALIACAO_1}` | `{JUSTIFICATIVA_OK_1}` |

---

## 8. Pontos que Dependem de Profiling ou Métricas Reais

| Ponto | Por que depende de medição | Ferramenta/ação recomendada |
|-------|-----------------------------|-----------------------------|
| `{PONTO_1}` | `{MOTIVO_MEDICAO_1}` | `{ACAO_1}` |

---

## 9. Plano de Validação das Melhorias

1. {PASSO_VALIDACAO_1}
2. {PASSO_VALIDACAO_2}
3. {PASSO_VALIDACAO_3}

---

## 10. Ferramentas Recomendadas

{FERRAMENTAS_RECOMENDADAS}

---

## 11. Conclusão

{CONCLUSAO}

---

*Relatório gerado pela skill `code-performance-analyzer` em modo `code-scan`.*
