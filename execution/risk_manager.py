"""
Institutional Risk Management Engine for Bovine Commodity Trading.
Implements Volatility Targeting, ATR Dynamic Stops, Trailing Profits,
and Portfolio Drawdown Circuit Breakers.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from config import RISK_CONFIG, COMMODITY_SPECS, CommoditySpec, ENSO_CONFIG


@dataclass
class PositionRiskState:
    symbol: str
    entry_price: float
    current_price: float
    position_units: int
    stop_loss_price: float
    take_profit_price: float
    trailing_high_water: float
    atr_at_entry: float
    unrealized_pnl: float


class BovineRiskManager:
    """Manages risk limits, position sizing, stop exits, and circuit breakers."""

    def __init__(self, config: Optional[Dict] = None, enso_regime: Optional[str] = "super_elnino"):
        self.cfg = config if config is not None else RISK_CONFIG.copy()
        self.enso_regime = enso_regime
        self.target_vol = self.cfg.get("target_annual_volatility", 0.15)
        self.max_leverage = self.cfg.get("max_portfolio_leverage", 2.5)
        self.max_pos_weight = self.cfg.get("max_position_weight", 0.60)
        
        # In Super El Niño, expand ATR stop buffer slightly to tolerate weather headline volatility
        if self.enso_regime == "super_elnino":
            self.atr_stop_mult = ENSO_CONFIG.get("atr_stop_loss_mult_elnino", 2.8)
        else:
            self.atr_stop_mult = self.cfg.get("atr_stop_loss_mult", 2.5)

        self.atr_tp_mult = self.cfg.get("atr_take_profit_mult", 4.5)
        self.trailing_act = self.cfg.get("trailing_stop_activation", 2.0)
        self.soft_dd_limit = self.cfg.get("max_drawdown_soft_limit", 0.08)
        self.hard_dd_circuit = self.cfg.get("max_drawdown_hard_circuit", 0.15)

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        asset_volatility: float,
        portfolio_equity: float,
        current_drawdown: float = 0.0,
        target_weight: float = 1.0
    ) -> int:
        """
        Calculates number of futures contracts to trade using Volatility Targeting & Drawdown Scaling.
        """
        if abs(target_weight) < 1e-4 or price <= 0 or portfolio_equity <= 0:
            return 0

        # Check Hard Circuit Breaker
        if current_drawdown >= self.hard_dd_circuit:
            return 0 # Circuit breaker triggered: Flat

        # Soft Drawdown Scaling
        dd_multiplier = 0.5 if current_drawdown >= self.soft_dd_limit else 1.0

        spec: CommoditySpec = COMMODITY_SPECS.get(symbol, COMMODITY_SPECS["LE=F"])
        multiplier = spec.point_value

        # Annualized asset dollar volatility per contract
        vol = max(asset_volatility, 0.08)
        dollar_vol_per_contract = price * multiplier * vol

        # Portfolio target dollar volatility allocation
        target_dollar_vol = (portfolio_equity * self.target_vol) * abs(target_weight) * dd_multiplier

        # Volatility-targeted number of contracts
        raw_contracts = target_dollar_vol / (dollar_vol_per_contract + 1e-6)

        # Apply Leverage and Max Position Weight constraints
        notional_per_contract = price * multiplier
        max_contracts_by_leverage = (portfolio_equity * self.max_leverage * self.max_pos_weight) / notional_per_contract

        final_contracts = int(np.clip(np.floor(raw_contracts), 0, np.floor(max_contracts_by_leverage)))
        
        # Ensure at least 1 contract if signal is strong and equity permits
        if final_contracts == 0 and abs(target_weight) >= 0.5 and portfolio_equity >= spec.margin_initial * 2:
            final_contracts = 1

        sign = 1 if target_weight > 0 else -1
        return sign * final_contracts

    def update_trailing_stops(
        self,
        pos: PositionRiskState,
        current_price: float,
        current_atr: float
    ) -> Tuple[bool, str, float]:
        """
        Evaluates stop-loss, take-profit, and trailing chandelier stops.
        Returns: (should_exit, reason, new_stop_price)
        """
        is_long = pos.position_units > 0

        if is_long:
            # Check Stop Loss
            if current_price <= pos.stop_loss_price:
                return True, "STOP_LOSS", pos.stop_loss_price

            # Check Take Profit
            if current_price >= pos.take_profit_price:
                return True, "TAKE_PROFIT", pos.take_profit_price

            # Update High Water Mark & Trailing Stop
            if current_price > pos.trailing_high_water:
                pos.trailing_high_water = current_price

            # If profit is past activation threshold (e.g. 2.0 * ATR), trail stop
            profit_in_atr = (current_price - pos.entry_price) / (pos.atr_at_entry + 1e-6)
            if profit_in_atr >= self.trailing_act:
                trail_stop = pos.trailing_high_water - (1.5 * current_atr)
                pos.stop_loss_price = max(pos.stop_loss_price, trail_stop)

            if current_price <= pos.stop_loss_price:
                return True, "TRAILING_STOP", pos.stop_loss_price

        else: # Short position
            # Check Stop Loss
            if current_price >= pos.stop_loss_price:
                return True, "STOP_LOSS", pos.stop_loss_price

            # Check Take Profit
            if current_price <= pos.take_profit_price:
                return True, "TAKE_PROFIT", pos.take_profit_price

            # Update Low Water Mark & Trailing Stop
            if current_price < pos.trailing_high_water:
                pos.trailing_high_water = current_price

            profit_in_atr = (pos.entry_price - current_price) / (pos.atr_at_entry + 1e-6)
            if profit_in_atr >= self.trailing_act:
                trail_stop = pos.trailing_high_water + (1.5 * current_atr)
                pos.stop_loss_price = min(pos.stop_loss_price, trail_stop)

            if current_price >= pos.stop_loss_price:
                return True, "TRAILING_STOP", pos.stop_loss_price

        return False, "HOLD", pos.stop_loss_price
