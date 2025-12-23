from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from ukkie_trader.domain.strategy.definition import Order, Position, OrderSide, OrderType

class ExchangeAdapter(ABC):
    """
    Abstract interface for exchange interactions.
    Referenced from concept/06-deployment-testing.md.
    """
    
    @abstractmethod
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        since: Optional[int] = None, 
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch historical candlestick data."""
        pass

    @abstractmethod
    async def create_order(self, order: Order) -> Dict[str, Any]:
        """Place a new order on the exchange."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an existing order."""
        pass

    @abstractmethod
    async def fetch_balance(self) -> Dict[str, float]:
        """Fetch account balance."""
        pass

    @abstractmethod
    async def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Position]:
        """Fetch current open positions."""
        pass
        
    @abstractmethod
    async def get_market_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch symbol details (min size, precision, etc.)."""
        pass
