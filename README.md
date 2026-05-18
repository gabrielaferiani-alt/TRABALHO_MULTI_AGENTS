# 💰 Quantum Finance — Consultor Financeiro Inteligente

> **FIAP MBA — Data Science & Artificial Intelligence**
> Disciplina: Intelligent Multi Agents | Professor: Alexandre Alves
> Trabalho em Grupo — 8,0 pontos

Sistema de IA Agêntica multiagente para consultoria financeira do mercado brasileiro.
O sistema executa pesquisas em tempo real, consome dados oficiais da B3 e do Banco Central
do Brasil, e gera recomendações personalizadas por perfil de investidor.

---

## 🏗️ Arquitetura do Sistema

```
┌────────────────────────────────────────────────────────────────┐
│                     USUÁRIO / CLIENTE                          │
│              (Pergunta sobre investimentos)                     │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│              🧠 LEAD ADVISOR (Agente Estrategista)              │
│                   Model: Gemini 2.5 Flash lite                     │
│                                                                │
│  • Recebe o perfil do cliente                                  │
│  • Orquestra os subagentes especializados                      │
│  • Consolida informações e gera recomendação final             │
└──────────────────┬─────────────────────────┬───────────────────┘
                   │                         │
       Delega para │                         │ Delega para
                   ▼                         ▼
┌─────────────────────────┐   ┌──────────────────────────────────┐
│  📰 MARKET ANALYST       │   │  📊 B3 DATA AGENT                │
│  (Agente Pesquisador)   │   │  (Especialista de Dados B3)      │
│                         │   │                                  │
│  Ferramentas:           │   │  Ferramentas:                    │
│  • search_financial_    │   │  • get_stock_quote()             │
│    concepts()           │   │  • get_stock_fundamentals()      │
│  • get_tesouro_direto_  │   │  • get_historical_performance()  │
│    rates()              │   │  • get_fii_data()                │
│  • get_fixed_income_    │   │  • get_market_indicators()       │
│    reference()          │   │                                  │
│                         │   │  Fontes de dados:                │
│  Explica: CDB, Tesouro  │   │  • yfinance (B3 em tempo real)  │
│  Direto, FIIs, ações    │   │  • API pública do BCB            │
└────────────┬────────────┘   └──────────────┬───────────────────┘
             │                               │
             ▼                               ▼
    Base de conhecimento         Dados reais B3 + BCB
    financeiro BR + SerpAPI      (cotações, SELIC, IPCA)
```

### Padrão de Orquestração
O sistema usa o padrão **Hierarquia Estrita (Command & Control)** ensinado em aula:
o Lead Advisor é o orquestrador central que delega tarefas aos subagentes especializados
via `sub_agents` do Google ADK. Os subagentes não se comunicam entre si — toda coordenação
passa pelo Lead Advisor, garantindo coerência na recomendação final.

---

## 🤖 Agentes

### 1. Lead Advisor (Agente Estrategista)
**Arquivo:** `quantum_finance/agents/lead_advisor.py`

| Atributo | Valor |
|---|---|
| **Modelo** | `gemini-2.5-flash-lite` |
| **Papel** | Orquestrador principal |
| **Sub-agentes** | `market_analyst`, `b3_data_agent` |

**Responsabilidades:**
- Analisar o perfil do investidor (risco, horizonte, objetivos)
- Delegar pesquisas ao Market Analyst e dados ao B3 Data Agent
- Consolidar as informações e montar a recomendação final
- Garantir que nenhuma cotação seja "alucinada" — todos os dados vêm das ferramentas

**Fluxo de decisão:**
```
Consulta do usuário
       │
       ▼
Identificar perfil (conservador / moderado / arrojado)
       │
       ├─► Delegar ao market_analyst: explicar produtos adequados
       │
       ├─► Delegar ao b3_data_agent: buscar SELIC, IPCA, CDI
       │
       ├─► [Se ações/FIIs forem relevantes] → b3_data_agent: cotações + fundamentals
       │
       └─► Consolidar tudo → Recomendação final estruturada
```

---

### 2. Market Analyst (Agente Pesquisador)
**Arquivo:** `quantum_finance/agents/market_analyst.py`

| Atributo | Valor |
|---|---|
| **Modelo** | `gemini-2.5-flash-lite` |
| **Papel** | Especialista em produtos financeiros |
| **Ferramentas** | 3 ferramentas |

**Ferramentas e Prompts Internos:**

| Ferramenta | Quando é chamada | O que retorna |
|---|---|---|
| `search_financial_concepts(query)` | Sempre que precisar explicar um produto ou conceito | Descrição detalhada do produto, riscos, perfil indicado |
| `get_tesouro_direto_rates()` | Quando o cliente pergunta sobre Tesouro Direto | Taxas de referência dos principais títulos públicos |
| `get_fixed_income_reference()` | Quando o cliente pergunta sobre CDB, LCI, LCA | Rentabilidades típicas baseadas no CDI atual |

---

### 3. B3 Data Agent (Especialista de Dados)
**Arquivo:** `quantum_finance/agents/b3_data_agent.py`

| Atributo | Valor |
|---|---|
| **Modelo** | `gemini-2.5-flash-lite` |
| **Papel** | Especialista em dados reais de mercado |
| **Ferramentas** | 5 ferramentas |

**Ferramentas e Prompts Internos:**

| Ferramenta | Quando é chamada | O que retorna |
|---|---|---|
| `get_stock_quote(ticker)` | Para qualquer consulta sobre cotação atual | Preço, variação %, volume, data |
| `get_stock_fundamentals(ticker)` | Para análise fundamentalista de ação | P/L, P/VP, DY, ROE, margem líquida, beta |
| `get_historical_performance(ticker, periodo)` | Para comparação de performance | Retorno %, volatilidade anual, máxima/mínima do período |
| `get_fii_data(ticker)` | Para consultas sobre Fundos Imobiliários | Preço cota, DY, P/VP específico de FIIs |
| `get_market_indicators()` | No início de qualquer recomendação | SELIC, IPCA, CDI — fonte: API pública BCB |

---

## 🛠️ Ferramentas (Tools)

### b3_tools.py — Dados da B3 via yfinance

```python
get_stock_quote(ticker: str) -> dict
```
Busca cotação atual de ação da B3. Tickers com sufixo `.SA` adicionado automaticamente.
Fonte: Yahoo Finance (dados B3 em tempo real, atraso ~15min para conta gratuita).

```python
get_stock_fundamentals(ticker: str) -> dict
```
Retorna P/L, P/VP, Dividend Yield (%), ROE, margem líquida, market cap, beta,
máximas/mínimas 52 semanas, média 50 dias, recomendação de analistas.

```python
get_historical_performance(ticker: str, periodo: str = "1y") -> dict
```
Calcula retorno no período, volatilidade anualizada (base 252 dias), máximo e mínimo.

```python
get_fii_data(ticker: str) -> dict
```
Dados específicos de FIIs: preço da cota, DY anual, P/VP.

---

### market_tools.py — Indicadores Macroeconômicos via BCB

```python
get_market_indicators() -> dict
```
Consulta a API pública do Banco Central do Brasil (sem chave de API).
Retorna: SELIC meta, IPCA acumulado 12 meses, CDI.
Série BCB usadas: #432 (SELIC meta), #433 (IPCA), #12 (CDI diário).

```python
get_tesouro_direto_rates() -> dict
```
Taxas de referência estimadas do Tesouro Direto baseadas na SELIC/IPCA.
Cobertura: Tesouro Selic, IPCA+, Prefixado.

```python
get_fixed_income_reference() -> dict
```
Rentabilidades típicas de CDB, LCI, LCA e Poupança baseadas no CDI atual.

---

### search_tools.py — Pesquisa de Conteúdo Financeiro

```python
search_financial_concepts(query: str) -> dict
```
Pesquisa informações sobre produtos e conceitos financeiros.
- **Com SERPAPI_KEY**: Busca no Google (resultados em tempo real)
- **Sem SERPAPI_KEY**: Usa base de conhecimento embutida (CDB, Tesouro, FIIs, ações, perfis, diversificação)

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Conta Google AI Studio (para GOOGLE_API_KEY gratuita)

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-grupo/quantum-finance.git
cd quantum-finance
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env e adicione sua GOOGLE_API_KEY
```

Obtenha a chave gratuita em: https://aistudio.google.com/apikey

### 4. Executar

**Modo terminal interativo:**
```bash
python main.py
```

**Interface Web (ADK):**
```bash
adk web
```
Acesse: http://localhost:8000 — selecione `lead_advisor`

**Run via ADK CLI:**
```bash
adk run quantum_finance
```

---

## 💬 Exemplos de Uso

### Consulta de perfil e recomendação completa
```
Você: Tenho 35 anos, R$ 50.000 para investir, perfil moderado e quero 
      construir renda passiva nos próximos 10 anos. O que você recomenda?
```

### Análise de ação específica
```
Você: Como está a PETR4 hoje? Vale a pena comprar?
```

### Comparação de produtos
```
Você: Melhor investir em CDB ou Tesouro Direto agora com a SELIC atual?
```

### Consulta de FII
```
Você: Me dê os dados do HGLG11 e me diga se é um bom FII para renda passiva.
```

---

## 📁 Estrutura do Projeto

```
quantum-finance/
├── main.py                          # Ponto de entrada + modo interativo
├── requirements.txt                 # Dependências Python
├── .env.example                     # Template de variáveis de ambiente
├── README.md                        # Este documento
└── quantum_finance/
    ├── __init__.py
    ├── agents/
    │   ├── __init__.py
    │   ├── lead_advisor.py          # Agente Estrategista (orquestrador)
    │   ├── market_analyst.py        # Agente Pesquisador
    │   └── b3_data_agent.py         # Agente de Dados B3
    └── tools/
        ├── __init__.py
        ├── b3_tools.py              # Cotações e fundamentals (yfinance)
        ├── market_tools.py          # SELIC, IPCA, CDI (API BCB)
        └── search_tools.py          # Pesquisa de conceitos financeiros
```

---

## 🔒 Decisões de Design

### Anti-Alucinação
O principal risco num consultor financeiro de IA é inventar cotações ou taxas.
Nossa solução:
1. O B3 Data Agent tem regra explícita no prompt: **NUNCA forneça cotações sem chamar a ferramenta**
2. O Lead Advisor tem regra idêntica: delegar ao B3 Data Agent antes de qualquer dado de mercado
3. As ferramentas retornam dicionários com campo `"erro"` explícito quando dados não estão disponíveis
4. O sistema prefere dizer "dado indisponível" a inventar um número

### Confiabilidade das Fontes
- **Cotações B3**: Yahoo Finance via yfinance (dados com ~15 min de atraso para gratuito)
- **Indicadores macro**: API pública do Banco Central do Brasil (sem autenticação)
- **Conceitos**: Base de conhecimento curada + Google Search via SerpAPI (opcional)

### Framework
Usamos o **Google ADK** (Agent Development Kit) conforme recomendado pelo professor.
O padrão `sub_agents` do ADK permite ao Lead Advisor delegar chamadas para agentes
especializados de forma nativa, sem precisar implementar orquestração manual.

---

## 👥 Grupo

| Nome | RM |
|---|---|
| GABRIELA FERIANI LEONI | 365336 | 
| RAPHAEL ALBERTO SUPPI | 365245 | 
| Lucas Caspirro Gitti Alcaraz | 364789 | 

---

## 📋 Disclaimer 

> Este sistema é desenvolvido para fins **educacionais** no contexto do MBA FIAP.
> As análises geradas pela IA não constituem recomendação formal de investimento.
> Sempre consulte um assessor de investimentos certificado (CFP/CEA) antes de
> tomar decisões financeiras. Dados de mercado podem ter defasagem de até 15 minutos.

---

## Link vídeo Youtube - execução agente    

LINK VIDEO EXECUÇÃO AGENTE :  https://www.youtube.com/watch?v=gezE8GGNtbk
