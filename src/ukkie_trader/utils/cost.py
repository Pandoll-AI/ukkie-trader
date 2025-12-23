import math
from typing import Dict, Any
from ukkie_trader.domain.strategy.definition import MarketRegime

class CostModel:
    """
    Estimates realistic trade costs.
    Referenced from concept/04-algorithms.md.
    """
    
    def __init__(self):
        # Default parameters for Binance Spot as a baseline
        self.maker_fee_bps = 10.0
        self.taker_fee_bps = 10.0
        
        # Base slippage in bps by regime
        self.base_slippage = {
            MarketRegime.NORMAL: 1.0,
            MarketRegime.VOLATILE: 3.0,
            MarketRegime.ILLIQUID: 10.0,
            MarketRegime.EVENT: 20.0
        }
        
        # Multipliers
        self.regime_multiplier = {
            MarketRegime.NORMAL: 1.0,
            MarketRegime.VOLATILE: 2.5,
            MarketRegime.ILLIQUID: 4.0,
            MarketRegime.EVENT: 10.0
        }

    def estimate_cost(
        self, 
        trade_size_usd: float, 
        regime: MarketRegime, 
        adv_usd: float = 1_000_000.0, 
        is_maker: bool = False
    ) -> Dict[str, float]:
        """
        Calculates Estimated Cost of Trade (ECT).
        ECT = (Fixed Fee) + (Slippage)
        Slippage = BaseSlip * Multiplier * sqrt(TradeSize / ADV)
        """
        # 1. Fixed Fee
        fee_bps = self.maker_fee_bps if is_maker else self.taker_fee_bps
        fixed_fee_usd = trade_size_usd * (fee_bps / 10000.0)
        
        # 2. Slippage calculation
        base_slip = self.base_slippage[regime]
        multiplier = self.regime_multiplier[regime]
        
        # Sqrt impact model
        size_factor = math.sqrt(trade_size_usd / adv_usd) if adv_usd > 0 else 1.0
        
        slippage_bps = base_slip * multiplier * size_factor
        slippage_usd = trade_size_usd * (slippage_bps / 10000.0)
        
        return {
            "fixed_fee_usd": fixed_fee_usd,
            "slippage_usd": slippage_usd,
            "total_cost_usd": fixed_fee_usd + slippage_usd,
            "slippage_bps": slippage_bps
        }
