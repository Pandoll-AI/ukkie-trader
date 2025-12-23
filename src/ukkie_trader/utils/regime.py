import numpy as np
from typing import Optional
from ukkie_trader.domain.strategy.definition import MarketRegime

class RegimeDetector:
    """
    Classifies market conditions based on volatility and volume.
    Referenced from concept/04-algorithms.md.
    """
    
    def __init__(self, vol_window: int = 20, liquid_window: int = 20):
        self.vol_window = vol_window
        self.liquid_window = liquid_window

    def detect(self, prices: np.ndarray, volumes: np.ndarray) -> MarketRegime:
        """
        Simplistic version for MVP:
        - VOLATILE: Current volatility > 2x average volatility.
        - ILLIQUID: Current volume < 0.5x average volume.
        - NORMAL: Otherwise.
        """
        if len(prices) < self.vol_window:
            return MarketRegime.NORMAL
            
        # 1. Calculate returns
        returns = np.diff(np.log(prices))
        
        # 2. Historical Volatility (rolling std)
        current_vol = np.std(returns[-self.vol_window:])
        avg_vol = np.std(returns) if len(returns) > self.vol_window else current_vol
        
        # 3. Volume average
        current_vol_sum = np.mean(volumes[-self.liquid_window:])
        avg_vol_sum = np.mean(volumes)
        
        if current_vol > 2 * avg_vol:
            return MarketRegime.VOLATILE
            
        if current_vol_sum < 0.5 * avg_vol_sum:
            return MarketRegime.ILLIQUID
            
        return MarketRegime.NORMAL
