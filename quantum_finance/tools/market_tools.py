"""
Ferramentas para buscar indicadores macroeconômicos do mercado brasileiro.
Utiliza a API pública do Banco Central do Brasil (BCB) — sem necessidade de chave.
"""

import requests
from datetime import datetime, timedelta


BCB_API_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# Códigos das séries do BCB
SERIES_BCB = {
    "selic_meta": 432,       # Taxa SELIC meta (% a.a.)
    "selic_diaria": 11,      # Taxa SELIC efetiva diária
    "ipca": 433,             # IPCA acumulado 12 meses (% a.a.)
    "cdi": 12,               # CDI diário
    "dolar_compra": 10813,   # USD/BRL - compra
    "dolar_venda": 10814,    # USD/BRL - venda
    "ibovespa": 7,           # Ibovespa pontos (série histórica)
}


def _buscar_serie_bcb(codigo: int, ultimos: int = 5) -> list:
    """Busca os últimos N registros de uma série no BCB."""
    url = BCB_API_BASE.format(codigo=codigo)
    try:
        resp = requests.get(
            url,
            params={"formato": "json", "dataInicial": "", "dataFinal": ""},
            timeout=10
        )
        if resp.status_code == 200:
            dados = resp.json()
            return dados[-ultimos:] if len(dados) >= ultimos else dados
    except Exception:
        pass
    return []


def get_market_indicators() -> dict:
    """
    Busca os principais indicadores macroeconômicos do mercado brasileiro.
    Fonte: API pública do Banco Central do Brasil (BCB).

    Returns:
        Dicionário com SELIC, IPCA, CDI e câmbio USD/BRL.
    """
    resultado = {
        "fonte": "Banco Central do Brasil (BCB)",
        "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    # SELIC meta
    selic = _buscar_serie_bcb(SERIES_BCB["selic_meta"], 1)
    if selic:
        resultado["selic_meta_aa_pct"] = float(selic[-1]["valor"])
        resultado["selic_data"] = selic[-1]["data"]

    # IPCA
    ipca = _buscar_serie_bcb(SERIES_BCB["ipca"], 1)
    if ipca:
        resultado["ipca_acumulado_12m_pct"] = float(ipca[-1]["valor"])
        resultado["ipca_data"] = ipca[-1]["data"]

    # CDI
    cdi = _buscar_serie_bcb(SERIES_BCB["cdi"], 1)
    if cdi:
        resultado["cdi_diario_pct"] = float(cdi[-1]["valor"])
        resultado["cdi_data"] = cdi[-1]["data"]

    # Estimativa CDI anual (base 252 dias úteis)
    if resultado.get("selic_meta_aa_pct"):
        resultado["cdi_estimado_aa_pct"] = round(resultado["selic_meta_aa_pct"] - 0.10, 2)

    if not resultado.get("selic_meta_aa_pct"):
        resultado["aviso"] = "API do BCB pode estar temporariamente indisponível. Dados podem estar desatualizados."

    return resultado


def get_tesouro_direto_rates() -> dict:
    """
    Retorna as taxas de referência do Tesouro Direto baseadas na SELIC atual.
    Para taxas exatas em tempo real, consultar: https://www.tesourodireto.com.br

    Returns:
        Dicionário com taxas estimadas dos principais títulos do Tesouro Direto.
    """
    indicadores = get_market_indicators()
    selic = indicadores.get("selic_meta_aa_pct", 13.75)
    ipca = indicadores.get("ipca_acumulado_12m_pct", 4.5)

    return {
        "fonte": "Estimativa baseada na SELIC/IPCA do BCB",
        "aviso": "Taxas exatas: www.tesourodireto.com.br",
        "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "selic_referencia_pct": selic,
        "ipca_referencia_pct": ipca,
        "titulos": {
            "Tesouro Selic 2027": {
                "tipo": "Pós-fixado",
                "taxa_referencia": f"SELIC + ~0.10% a.a. (aprox. {selic + 0.10:.2f}% a.a.)",
                "risco": "Muito Baixo",
                "perfil_indicado": "Conservador / Reserva de Emergência",
                "liquidez": "Diária (D+1)",
                "investimento_minimo": "R$ 30,00",
            },
            "Tesouro IPCA+ 2029": {
                "tipo": "Híbrido (IPCA + taxa prefixada)",
                "taxa_referencia": f"IPCA ({ipca:.2f}%) + ~5.5% a.a.",
                "risco": "Baixo",
                "perfil_indicado": "Conservador / Moderado",
                "liquidez": "Diária (com marcação a mercado)",
                "investimento_minimo": "R$ 30,00",
            },
            "Tesouro Prefixado 2027": {
                "tipo": "Prefixado",
                "taxa_referencia": f"Aprox. {selic - 1.5:.2f}% a.a. (taxa fixa)",
                "risco": "Baixo-Médio",
                "perfil_indicado": "Moderado",
                "liquidez": "Diária (com marcação a mercado)",
                "investimento_minimo": "R$ 30,00",
            },
        },
    }


def get_fixed_income_reference() -> dict:
    """
    Retorna taxas de referência para renda fixa (CDB, LCI, LCA) baseadas no CDI.

    Returns:
        Dicionário com referências de rentabilidade para produtos de renda fixa.
    """
    indicadores = get_market_indicators()
    selic = indicadores.get("selic_meta_aa_pct", 13.75)
    cdi_estimado = indicadores.get("cdi_estimado_aa_pct", selic - 0.10)

    return {
        "fonte": "Taxas de mercado estimadas com base no CDI/BCB",
        "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cdi_referencia_aa_pct": cdi_estimado,
        "selic_referencia_aa_pct": selic,
        "produtos": {
            "CDB (Certificado de Depósito Bancário)": {
                "tipo": "Renda Fixa Bancária",
                "rentabilidade_tipica": f"90% a 130% do CDI ({cdi_estimado * 0.90:.2f}% a {cdi_estimado * 1.30:.2f}% a.a.)",
                "cobertura": "FGC até R$ 250.000 por CPF/instituição",
                "liquidez": "Depende do produto (D+0 a vencimento)",
                "ir": "Tabela regressiva: 22.5% (até 180d) a 15% (acima de 720d)",
                "perfil_indicado": "Conservador / Moderado",
            },
            "LCI/LCA (Letras de Crédito Imobiliário/Agronegócio)": {
                "tipo": "Renda Fixa Bancária - Isenção IR",
                "rentabilidade_tipica": f"80% a 95% do CDI ({cdi_estimado * 0.80:.2f}% a {cdi_estimado * 0.95:.2f}% a.a.) — ISENTO IR",
                "cobertura": "FGC até R$ 250.000 por CPF/instituição",
                "liquidez": "Geralmente sem liquidez antes do vencimento",
                "ir": "ISENTO para pessoa física",
                "perfil_indicado": "Conservador / Moderado",
            },
            "Poupança": {
                "tipo": "Renda Fixa Tradicional",
                "rentabilidade_tipica": f"{min(selic * 0.70, 0.5 * 12):.2f}% a.a. (70% SELIC quando SELIC > 8.5%)",
                "cobertura": "FGC até R$ 250.000",
                "liquidez": "Mensal (aniversário da aplicação)",
                "ir": "ISENTO para pessoa física",
                "perfil_indicado": "Conservador (mas geralmente supera menos o CDB)",
            },
        },
    }
