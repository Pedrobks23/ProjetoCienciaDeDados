# 📊 Projeto 1 — Análise Exploratória e Dashboard de Dados do ReclameAqui

**Empresa analisada:** BigLojas (rede de hipermercados)  
**Disciplina:** Ciência de Dados  
**Instituição:** UNIFOR — Universidade de Fortaleza  
**Integrantes:** Pedro · Victor Rios  

---

## 📝 Descrição

Este projeto realiza uma análise exploratória completa dos dados de reclamações da empresa **BigLojas** extraídos do portal **ReclameAqui**. O objetivo é transformar reclamações brutas em inteligência de negócio, identificando padrões, gargalos operacionais e tendências que possam orientar decisões estratégicas da empresa.

O entregável principal é um **dashboard interativo** publicado em nuvem com Streamlit, acompanhado de um notebook Jupyter com toda a análise exploratória documentada.

---

## 🎯 Objetivos de Análise

- Identificar os principais motivos de reclamação
- Mapear a taxa de resolução por tipo de STATUS
- Identificar os estados com maior concentração de reclamações
- Detectar padrões sazonais (meses com pico de reclamações)
- Analisar o comportamento textual das descrições por status
- Entregar recomendações estratégicas baseadas nos dados

---

## 📁 Estrutura do Repositório

```
📦 ProjetoBigLojas
├── 📓 ProjetoBigLojas.ipynb       # Notebook com EDA completa
├── 🖥️  app.py                      # Código do dashboard Streamlit
├── 📄 requirements.txt            # Dependências do projeto
├── 📊 RECLAMEAQUI_BIGLOJAS.csv    # Base de dados
└── 📖 README.md                   # Este arquivo
```

---

## 📦 Dataset

A base de dados contém **1.000 reclamações** da BigLojas coletadas do ReclameAqui, com as seguintes variáveis:

| Coluna | Descrição |
|---|---|
| `ID` | Identificador único da reclamação |
| `TEMA` | Título/motivo da reclamação |
| `LOCAL` | Cidade e estado da ocorrência |
| `TEMPO` | Data da reclamação |
| `CATEGORIA` | Classificação original do portal |
| `STATUS` | Situação atual (Respondida, Resolvido, Não resolvido, Em réplica, Não respondida) |
| `DESCRICAO` | Texto completo da reclamação |
| `URL` | Link original da queixa |
| `ANO`, `MES`, `DIA` | Variáveis temporais extraídas |
| `CASOS` | Variável quantitativa de contagem |

### Colunas criadas no pré-processamento

| Coluna | Descrição |
|---|---|
| `TEMA_CATEGORIA` | Categorização automática por palavras-chave (10 categorias) |
| `ESTADO` | UF extraída da coluna LOCAL via regex |
| `TAMANHO_TEXTO` | Comprimento em caracteres da DESCRICAO |
| `FAIXA_TAMANHO_TEXTO` | Classificação: Curto / Médio / Longo / Muito longo |

---

## 🔍 Análises Realizadas

### No Notebook (EDA)
1. Verificação de nulos e padronização da base
2. Categorização automática dos 930 temas distintos em 10 categorias
3. Extração de estado (UF) a partir da coluna LOCAL
4. Análise de tamanho e faixa dos textos das descrições
5. Série temporal de reclamações por mês
6. Top 10 motivos de reclamação
7. Cruzamento Status × Categoria
8. Proporção por status (gráfico de pizza)
9. Distribuição espacial por estado (Pareto)
10. Histograma e Boxplot do tamanho do texto por status
11. Faixas de tamanho do texto
12. WordCloud com remoção de stopwords em português

### No Dashboard (Streamlit)
- **KPIs** no topo: total de reclamações, total de casos, status mais frequente, estado líder
- **Filtros globais** interativos: Estado, Status, Faixa de tamanho do texto, Categoria
- **Série temporal** com média móvel de 3 períodos
- **Mapa cloroplético** do Brasil com seletor de ano
- **Gráfico de Pareto** por estado
- **Proporção por status** (pizza)
- **Status × Categoria** (barras agrupadas)
- **Histograma** e **Boxplot** do tamanho do texto
- **WordCloud** das descrições
- **Faixas de tamanho** do texto
- **Top 10 motivos** e **Reclamações por categoria**
- Exportação da base filtrada em CSV

---

## 🚀 Como Executar

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Rodar o Dashboard localmente

```bash
streamlit run app.py
```

### Rodar o Notebook

Abra o arquivo `ProjetoBigLojas.ipynb` no Google Colab ou Jupyter e execute as células em ordem. Certifique-se de que o arquivo `RECLAMEAQUI_BIGLOJAS.csv` esteja no mesmo diretório (ou no `/content/` no Colab).

---

## 📊 Principais Resultados

- **Status mais comum:** Respondida (401 registros — 40% do total)
- **Mês com mais reclamações:** Março de 2021 (125 registros)
- **Estado líder:** São Paulo, seguido de Rio Grande do Sul e Paraná
- **Categoria com mais reclamações:** Produto alimentar com problema (143)
- **Categoria com mais "Não resolvido":** Problema financeiro/cobrança

---

## 💡 Recomendações Estratégicas

1. **Processo para reclamações financeiras** — são as mais difíceis de resolver e exigem um fluxo dedicado de atendimento
2. **Controle de qualidade de alimentos** — especialmente em SP e RS, onde a concentração de casos é maior
3. **Treinamento de atendimento ao cliente** — mau atendimento é uma das maiores categorias, indicando falha no relacionamento com o consumidor

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Pandas** — manipulação de dados
- **Matplotlib** — visualizações no notebook
- **Plotly** — visualizações interativas no dashboard
- **Streamlit** — deploy do dashboard
- **WordCloud** — nuvem de palavras
- **Google Colab** — ambiente de desenvolvimento do notebook

---

## 🔗 Links

- 🖥️ [Dashboard publicado](https://biglojas.streamlit.app) <!-- substitua pelo link real -->
- 📓 [Notebook no Google Colab](https://colab.research.google.com) <!-- substitua pelo link real -->
- 🎥 [Vídeo explicativo](https://youtube.com) <!-- substitua pelo link real -->
