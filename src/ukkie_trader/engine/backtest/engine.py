from enum import Enum
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from ukkie_trader.domain.strategy.definition import FrozenStrategy, MarketRegime

class TradingState(str, Enum):
    IDLE = "IDLE"
    ENTERING = "ENTERING"
    IN_POSITION = "IN_POSITION"
    EXITING = "EXITING"
    STOPPED = "STOPPED"

class BacktestEngine:
    """
    State-machine based backtest engine.
    Referenced from concept/04-algorithms.md.
    """
    
    def __init__(self, strategy: FrozenStrategy, initial_capital: float = 10000.0):
        self.strategy = strategy
        self.capital = initial_capital
        self.state = TradingState.IDLE
        self.position = 0.0
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = []

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Main loop for the backtest.
        """
        for timestamp, bar in df.iterrows():
            self._process_bar(timestamp, bar)
            self.equity_curve.append(self._calculate_total_equity(bar['close']))
            
        return self._calculate_metrics()

    def _process_bar(self, timestamp: Any, bar: pd.Series):
        if self.state == TradingState.IDLE:
            if self._check_entry_condition(bar):
                self.state = TradingState.ENTERING
                self._execute_entry(timestamp, bar)
        
        elif self.state == TradingState.IN_POSITION:
            if self._check_exit_condition(bar) or self._check_stop_loss(bar):
                self.state = TradingState.EXITING
                self._execute_exit(timestamp, bar)

    def _check_entry_condition(self, bar: pd.Series) -> bool:
        # Simplistic: price > ema_20 (placeholder)
        # In real: evaluate self.strategy.frozen_definition.signal_logic
        return bar['close'] > bar.get('ema', bar['close'] * 0.99)

    def _execute_entry(self, timestamp: Any, bar: pd.Series):
        self.entry_price = bar['close']
        # Sizing logic
        sizing = self.strategy.frozen_definition.position_sizing
        size_pct = sizing.fraction if sizing.fraction else 0.1
        self.position = (self.capital * size_pct) / self.entry_price
        self.capital -= self.position * self.entry_price
        
        self.trades.append({
            "timestamp": timestamp,
            "type": "ENTRY",
            "price": self.entry_price,
            "size": self.position
        })
        self.state = TradingState.IN_POSITION

    def _check_exit_condition(self, bar: pd.Series) -> bool:
        return bar['close'] < bar.get('ema', bar['close'] * 1.01)

    def _check_stop_loss(self, bar: pd.Series) -> bool:
        sl_pct = self.strategy.frozen_definition.risk_params.stop_loss_pct or 5.0
        if self.entry_price == 0: return False
        
        pnl_pct = (bar['close'] - self.entry_price) / self.entry_price * 100
        return pnl_pct < -sl_pct

    def _execute_exit(self, timestamp: Any, bar: pd.Series):
        exit_price = bar['close']
        self.capital += self.position * exit_price
        self.position = 0.0
        
        self.trades.append({
            "timestamp": timestamp,
            "type": "EXIT",
            "price": exit_price,
            "pnl": (exit_price - self.entry_price) * self.position
        })
        self.state = TradingState.IDLE

    def _calculate_total_equity(self, current_price: float) -> float:
        return self.capital + (self.position * current_price)

    def _calculate_metrics(self) -> Dict[str, Any]:
        equity_series = pd.Series(self.equity_curve)
        total_return = (equity_series.iloc[-1] - equity_series.iloc[0]) / equity_series.iloc[0] * 100
        
        # Drawdown
        rolling_max = equity_series.cummax()
        drawdowns = (equity_series - rolling_max) / rolling_max * 100
        max_dd = drawdowns.min()
        
        return {
            "total_return": float(total_return),
            "max_drawdown": float(max_dd),
            "total_trades": len(self.trades) // 2,
            "final_equity": float(equity_series.iloc[-1])
        }
