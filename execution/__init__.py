"""
Risk Management & Paper Trading Execution Package.
"""
from .risk_manager import BovineRiskManager
from .paper_trader import BovinePaperTrader

__all__ = [
    "BovineRiskManager",
    "BovinePaperTrader"
]
