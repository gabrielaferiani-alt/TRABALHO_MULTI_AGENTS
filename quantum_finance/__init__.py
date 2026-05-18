"""
Quantum Finance — Sistema Multiagente de Consultoria Financeira
FIAP MBA Data Science & Artificial Intelligence — Intelligent Multi Agents
"""

from dotenv import load_dotenv
import os

# Carrega o .env da raiz do projeto (um nível acima deste pacote)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from quantum_finance.agents.lead_advisor import lead_advisor_agent

# root_agent é obrigatório para o ADK web descobrir o agente
root_agent = lead_advisor_agent

__version__ = "1.0.0"
__author__ = "Grupo Quantum Finance"