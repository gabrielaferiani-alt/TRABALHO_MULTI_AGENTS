"""
Ferramentas de pesquisa para buscar informações públicas sobre produtos e
conceitos do mercado financeiro brasileiro.
"""

import os
import requests
from datetime import datetime


def search_financial_concepts(query: str) -> dict:
    """
    Pesquisa informações públicas sobre produtos e conceitos financeiros brasileiros.
    Utiliza a API do Google Search (via SerpAPI) se disponível; caso contrário,
    retorna base de conhecimento embutida sobre o mercado brasileiro.

    Args:
        query: Termo de pesquisa (ex: 'Como funciona CDB', 'O que são FIIs').

    Returns:
        Dicionário com resultados relevantes e fontes confiáveis.
    """
    serpapi_key = os.getenv("SERPAPI_KEY")

    if serpapi_key:
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": f"{query} mercado financeiro brasileiro 2026",
                    "hl": "pt",
                    "gl": "br",
                    "api_key": serpapi_key,
                    "num": 5,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                resultados = []
                for r in data.get("organic_results", [])[:5]:
                    resultados.append({
                        "titulo": r.get("title"),
                        "resumo": r.get("snippet"),
                        "fonte": r.get("link"),
                    })
                return {
                    "query": query,
                    "fonte": "Google Search (SerpAPI)",
                    "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "resultados": resultados,
                }
        except Exception:
            pass

    # Base de conhecimento embutida — não depende de chave de API
    return _knowledge_base_lookup(query)


def _knowledge_base_lookup(query: str) -> dict:
    """Retorna informações da base de conhecimento embutida."""
    query_lower = query.lower()

    base = {
        "cdb": {
            "titulo": "CDB - Certificado de Depósito Bancário",
            "descricao": (
                "O CDB é um título de renda fixa emitido pelos bancos para captar recursos. "
                "Ao investir em CDB, você empresta dinheiro ao banco e recebe juros em troca. "
                "A rentabilidade geralmente é expressa como percentual do CDI (ex: 110% CDI). "
                "Tem cobertura do FGC (Fundo Garantidor de Créditos) de até R$ 250.000 por CPF/instituição. "
                "O Imposto de Renda segue tabela regressiva: 22,5% (até 180 dias) a 15% (acima de 720 dias). "
                "É indicado para perfis conservadores e moderados. "
                "Fonte: CVM / Banco Central do Brasil."
            ),
            "fontes": ["https://www.bcb.gov.br", "https://www.investidor.gov.br"],
        },
        "tesouro direto": {
            "titulo": "Tesouro Direto - Títulos Públicos Federais",
            "descricao": (
                "Programa do Governo Federal para venda de títulos públicos a pessoas físicas via internet. "
                "Principais títulos: Tesouro Selic (pós-fixado, indicado para reserva de emergência), "
                "Tesouro IPCA+ (protege contra inflação + taxa real), Tesouro Prefixado (taxa fixa definida no momento). "
                "Investimento mínimo de R$ 30,00. Liquidez diária. "
                "IR segue tabela regressiva como o CDB. "
                "Considerado o investimento de menor risco do Brasil (garantia do Governo Federal). "
                "Fonte: www.tesourodireto.com.br"
            ),
            "fontes": ["https://www.tesourodireto.com.br"],
        },
        "fii": {
            "titulo": "FIIs - Fundos de Investimento Imobiliário",
            "descricao": (
                "FIIs são fundos que investem em imóveis ou ativos ligados ao setor imobiliário. "
                "São negociados na B3 como ações (código com 11 no final, ex: HGLG11). "
                "Distribuem rendimentos mensais isentos de IR para pessoas físicas (se o fundo tiver > 50 cotistas e "
                "cotas não representarem > 10% do patrimônio). "
                "Principais tipos: FIIs de tijolo (imóveis físicos), FIIs de papel (CRIs, LCIs), "
                "FIIs híbridos. "
                "Indicadores importantes: P/VP (Preço/Valor Patrimonial), Dividend Yield (DY). "
                "Fonte: B3 / CVM."
            ),
            "fontes": ["https://www.b3.com.br", "https://www.cvm.gov.br"],
        },
        "acao": {
            "titulo": "Ações - Renda Variável na B3",
            "descricao": (
                "Ações são frações do capital social de uma empresa. "
                "Ao comprar ações, o investidor se torna sócio da empresa. "
                "Ganhos vêm por valorização (ganho de capital) e distribuição de lucros (dividendos/JCP). "
                "Tipos: ON (ordinárias, direito a voto), PN (preferenciais, preferência em dividendos). "
                "Sufixo 3 = ON, 4 = PN na B3. "
                "Risco maior que renda fixa, potencial de retorno superior no longo prazo. "
                "IR sobre ganho de capital: 15% (operações comuns) e 20% (day trade). "
                "Isenção de IR para vendas abaixo de R$ 20.000/mês. "
                "Fonte: B3."
            ),
            "fontes": ["https://www.b3.com.br", "https://www.cvm.gov.br"],
        },
        "perfil investidor": {
            "titulo": "Perfil de Investidor (Suitability)",
            "descricao": (
                "O perfil de investidor classifica o apetite ao risco: "
                "1) CONSERVADOR: Prioriza segurança, prefere renda fixa (CDB, Tesouro, LCI/LCA). "
                "2) MODERADO: Aceita algum risco, combina renda fixa com FIIs e algumas ações. "
                "3) ARROJADO/AGRESSIVO: Aceita alta volatilidade, foco em ações, fundos multimercado. "
                "A regulação exige que as instituições financeiras avaliem o perfil antes de recomendar produtos (API/Suitability - ANBIMA). "
                "Fonte: ANBIMA / CVM."
            ),
            "fontes": ["https://www.anbima.com.br", "https://www.cvm.gov.br"],
        },
        "diversificação": {
            "titulo": "Diversificação de Carteira",
            "descricao": (
                "Diversificação é a estratégia de distribuir investimentos em diferentes classes de ativos "
                "para reduzir o risco sem necessariamente reduzir o retorno esperado (teoria moderna de portfólio). "
                "Uma carteira equilibrada pode combinar: renda fixa (CDB, Tesouro), FIIs, ações nacionais, "
                "fundos multimercado e até ativos internacionais. "
                "A alocação ideal depende do perfil, horizonte de tempo e objetivos do investidor."
            ),
            "fontes": ["https://www.investidor.gov.br"],
        },
    }

    # Busca na base de conhecimento
    for chave, conteudo in base.items():
        if chave in query_lower:
            return {
                "query": query,
                "fonte": "Base de conhecimento financeiro (mercado brasileiro 2026)",
                "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "resultado": conteudo,
            }

    # Resposta genérica se não encontrar
    return {
        "query": query,
        "fonte": "Base de conhecimento financeiro (mercado brasileiro 2026)",
        "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resultado": {
            "titulo": f"Pesquisa sobre: {query}",
            "descricao": (
                "Para consultas sobre o mercado financeiro brasileiro, fontes oficiais recomendadas: "
                "- Banco Central do Brasil: www.bcb.gov.br (taxas, regulação bancária) "
                "- Tesouro Nacional: www.tesourodireto.com.br (títulos públicos) "
                "- B3: www.b3.com.br (ações, FIIs, cotações) "
                "- CVM: www.cvm.gov.br (regulação do mercado de capitais) "
                "- ANBIMA: www.anbima.com.br (fundos de investimento, suitability) "
                "- Investidor.gov.br: educação financeira oficial do Brasil"
            ),
            "fontes": ["https://www.bcb.gov.br", "https://www.b3.com.br", "https://www.cvm.gov.br"],
        },
    }
