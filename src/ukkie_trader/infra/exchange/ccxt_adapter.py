import ccxt.async_support as ccxt
import pandas as pd
from typing import List, Dict, Any, Optional
from ukkie_trader.infra.exchange.base import ExchangeAdapter
from ukkie_trader.domain.strategy.definition import Order, Position, OrderSide, OrderType

class CCXTAdapter(ExchangeAdapter):
    """
    Concrete implementation of ExchangeAdapter using the CCXT library.
    """
    
    def __init__(self, exchange_id: str, api_key: str = "", secret: str = "", options: Dict[str, Any] = None):
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        self.client = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': options or {}
        })

    async def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        since: Optional[int] = None, 
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch OHLCV data and return as a formatted pandas DataFrame."""
        ohlcv = await self.client.fetch_ohlcv(symbol, timeframe, since, limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    async def create_order(self, order: Order) -> Dict[str, Any]:
        """Map Ukkie Order to CCXT create_order."""
        # Note: This is a simplified mapping for MVP
        side = order.side.value.lower()
        order_type = order.order_type.value.lower()
        params = {}
        
        response = await self.client.create_order(
            order.asset, 
            order_type, 
            side, 
            order.quantity, 
            order.price, 
            params
        )
        return response

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            await self.client.cancel_order(order_id, symbol)
            return True
        except Exception:
            return False

    async def fetch_balance(self) -> Dict[str, float]:
        balance = await self.client.fetch_balance()
        return balance['total']

    async def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Position]:
        # CCXT position handling varies significantly by exchange (Futures/Spot)
        # This is a stub for future implementation
        return []

    async def get_market_info(self, symbol: str) -> Dict[str, Any]:
        markets = await self.client.load_markets()
        return markets.get(symbol, {})

    async def close(self):
        await self.client.close()
