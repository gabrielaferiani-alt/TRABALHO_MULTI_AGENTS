"""
Ferramentas para buscar dados reais da B3 via yfinance.
Tickers brasileiros usam o sufixo '.SA' (ex: PETR4 -> PETR4.SA).
"""

import yfinance as yf
from datetime import datetime, timedelta


def get_stock_quote(ticker: str) -> dict:
    """
    Busca a cotação atual de uma ação da B3.

    Args:
        ticker: Código da ação (ex: 'PETR4', 'VALE3', 'ITUB4').
                O sufixo '.SA' é adicionado automaticamente se ausente.

    Returns:
        Dicionário com preço atual, variação, volume e informações básicas.
    """
    if not ticker.endswith(".SA"):
        ticker = ticker.upper() + ".SA"

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        preco_atual = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        preco_anterior = info.get("previousClose", 0)
        variacao = 0.0
        if preco_atual and preco_anterior:
            variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

        return {
            "ticker": ticker.replace(".SA", ""),
            "nome": info.get("longName", info.get("shortName", ticker)),
            "preco_atual": round(preco_atual, 2) if preco_atual else None,
            "variacao_percentual": round(variacao, 2),
            "volume": info.get("volume", info.get("regularMarketVolume")),
            "mercado": "B3 - Bolsa de Valores do Brasil",
            "moeda": "BRL",
            "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except Exception as e:
        return {
            "erro": f"Não foi possível obter cotação para {ticker}: {str(e)}",
            "ticker": ticker.replace(".SA", ""),
        }


def get_stock_fundamentals(ticker: str) -> dict:
    """
    Busca indicadores fundamentalistas de uma ação da B3.

    Args:
        ticker: Código da ação (ex: 'PETR4', 'VALE3', 'ITUB4').

    Returns:
        Dicionário com P/L, P/VP, DY, ROE, margem líquida e outros indicadores.
    """
    if not ticker.endswith(".SA"):
        ticker = ticker.upper() + ".SA"

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        dividend_yield = info.get("dividendYield")
        if dividend_yield:
            dividend_yield = round(dividend_yield * 100, 2)

        return {
            "ticker": ticker.replace(".SA", ""),
            "nome": info.get("longName", ticker),
            "setor": info.get("sector", "N/D"),
            "industria": info.get("industry", "N/D"),
            "p_l": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
            "p_vp": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else None,
            "dividend_yield_pct": dividend_yield,
            "roe_pct": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
            "margem_liquida_pct": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
            "divida_liquida": info.get("totalDebt"),
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
            "52_semanas_max": info.get("fiftyTwoWeekHigh"),
            "52_semanas_min": info.get("fiftyTwoWeekLow"),
            "media_50_dias": info.get("fiftyDayAverage"),
            "recomendacao_analistas": info.get("recommendationKey", "N/D"),
            "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except Exception as e:
        return {
            "erro": f"Não foi possível obter fundamentals para {ticker}: {str(e)}",
            "ticker": ticker.replace(".SA", ""),
        }


def get_historical_performance(ticker: str, periodo: str = "1y") -> dict:
    """
    Busca a performance histórica de uma ação.

    Args:
        ticker: Código da ação.
        periodo: Período de análise ('1mo', '3mo', '6mo', '1y', '2y', '5y').

    Returns:
        Dicionário com retorno no período, volatilidade e dados históricos.
    """
    if not ticker.endswith(".SA"):
        ticker = ticker.upper() + ".SA"

    periodos_validos = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if periodo not in periodos_validos:
        periodo = "1y"

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)

        if hist.empty:
            return {"erro": f"Sem dados históricos para {ticker}", "ticker": ticker.replace(".SA", "")}

        preco_inicial = hist["Close"].iloc[0]
        preco_final = hist["Close"].iloc[-1]
        retorno = ((preco_final - preco_inicial) / preco_inicial) * 100
        volatilidade = hist["Close"].pct_change().std() * (252 ** 0.5) * 100

        return {
            "ticker": ticker.replace(".SA", ""),
            "periodo": periodo,
            "preco_inicial": round(float(preco_inicial), 2),
            "preco_final": round(float(preco_final), 2),
            "retorno_percentual": round(float(retorno), 2),
            "volatilidade_anual_pct": round(float(volatilidade), 2),
            "maximo_periodo": round(float(hist["Close"].max()), 2),
            "minimo_periodo": round(float(hist["Close"].min()), 2),
            "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except Exception as e:
        return {
            "erro": f"Não foi possível obter histórico para {ticker}: {str(e)}",
            "ticker": ticker.replace(".SA", ""),
        }


def get_fii_data(ticker: str) -> dict:
    """
    Busca dados específicos de Fundos de Investimento Imobiliário (FIIs).

    Args:
        ticker: Código do FII (ex: 'HGLG11', 'KNRI11', 'XPML11').

    Returns:
        Dicionário com P/VP, DY, rendimento mensal e informações do fundo.
    """
    if not ticker.endswith(".SA"):
        ticker = ticker.upper() + ".SA"

    try:
        fii = yf.Ticker(ticker)
        info = fii.info

        dividend_yield = info.get("dividendYield")
        if dividend_yield:
            dividend_yield = round(dividend_yield * 100, 2)

        preco = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")

        return {
            "ticker": ticker.replace(".SA", ""),
            "nome": info.get("longName", ticker),
            "tipo": "Fundo de Investimento Imobiliário (FII)",
            "preco_cota": round(preco, 2) if preco else None,
            "dividend_yield_anual_pct": dividend_yield,
            "p_vp": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else None,
            "volume_medio": info.get("averageVolume"),
            "52_semanas_max": info.get("fiftyTwoWeekHigh"),
            "52_semanas_min": info.get("fiftyTwoWeekLow"),
            "mercado": "B3 - Bolsa de Valores do Brasil",
            "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except Exception as e:
        return {
            "erro": f"Não foi possível obter dados do FII {ticker}: {str(e)}",
            "ticker": ticker.replace(".SA", ""),
        }
