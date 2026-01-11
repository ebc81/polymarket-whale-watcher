"""PolyMarket API integration for fetching trades."""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class PolyMarketAPI:
    """Client for interacting with the PolyMarket API."""
    
    BASE_URL = "https://data-api.polymarket.com"
    TRADES_ENDPOINT = "/trades"
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """Initialize the PolyMarket API client.
        
        Args:
            session: Optional aiohttp session to use for requests
        """
        self.session = session
        self._own_session = session is None
    
    @staticmethod
    def calculate_trade_value(trade: Dict[str, Any]) -> float:
        """Calculate the trade value.
        
        Args:
            trade: Trade dictionary from the API
            
        Returns:
            Trade value in USD
        """
        side = trade.get("side", "").upper()
        price = float(trade.get("price", 0))
        size = float(trade.get("size", 0))
        
        # Calculate trade value (size * price for buy, size for sell)
        return size if side == "SELL" else size * price
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_session:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_session and self.session:
            await self.session.close()
    
    async def get_trades(
        self,
        maker_address: Optional[str] = None,
        limit: int = 100,
        retries: int = 3,
        retry_delay: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch recent trades from PolyMarket.
        
        Args:
            maker_address: Optional address to filter trades by maker
            limit: Maximum number of trades to fetch
            retries: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of trade dictionaries
        """
        params: Dict[str, Any] = {"limit": limit, "offset": 0}
        if maker_address:
            params["user"] = maker_address.lower()
        
        for attempt in range(retries):
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()
                    self._own_session = True
                
                url = f"{self.BASE_URL}{self.TRADES_ENDPOINT}"
                async with self.session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        trades = data if isinstance(data, list) else []
                        if maker_address:
                            for trade in trades:
                                trade.setdefault("maker_address", maker_address.lower())
                        return trades
                    else:
                        logger.warning(f"API returned status {response.status}")
                        if attempt < retries - 1:
                            await asyncio.sleep(retry_delay)
                        continue
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching trades (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error fetching trades (attempt {attempt + 1}/{retries}): {e}", exc_info=True)
                if attempt < retries - 1:
                    await asyncio.sleep(retry_delay)
        
        return []
    
    async def get_all_whale_trades(
        self,
        whale_addresses: List[str],
        limit_per_address: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch trades for multiple whale addresses.
        
        Args:
            whale_addresses: List of addresses to fetch trades for
            limit_per_address: Maximum trades per address
            
        Returns:
            Combined list of all trades
        """
        tasks = [
            self.get_trades(maker_address=addr, limit=limit_per_address)
            for addr in whale_addresses
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_trades = []
        for result in results:
            if isinstance(result, list):
                all_trades.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching trades for whale: {result}")
        
        # Sort by timestamp (most recent first)
        all_trades.sort(
            key=lambda x: x.get("timestamp", x.get("created_at", 0)),
            reverse=True
        )
        
        return all_trades
    
    @staticmethod
    def format_trade(trade: Dict[str, Any]) -> str:
        """Format a trade for display.
        
        Args:
            trade: Trade dictionary from the API
            
        Returns:
            Formatted string representation of the trade
        """
        trade_id = (
            trade.get("transactionHash")
            or trade.get("id")
            or trade.get("name")
            or trade.get("uuid")
            or "unknown"
        )
        maker = trade.get("maker_address") or trade.get("user") or "unknown"
        maker_display = maker[:10] + "..." if maker not in (None, "unknown") else maker
        market_info = trade.get("market") if isinstance(trade.get("market"), dict) else {}
        title = trade.get("title") or market_info.get("question") or "Unknown Market"
        outcome = trade.get("outcome", "N/A")
        side = trade.get("side", "unknown").upper()
        price = float(trade.get("price", 0))
        size = float(trade.get("size", 0))
        value = PolyMarketAPI.calculate_trade_value(trade)
        event_slug = trade.get("eventSlug") or trade.get("slug")
        timestamp = trade.get("timestamp", trade.get("created_at", 0))
        if timestamp:
            try:
                dt = datetime.fromtimestamp(int(timestamp))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                time_str = str(timestamp)
        else:
            time_str = "unknown"
        link = f"https://polymarket.com/event/{event_slug}" if event_slug else None
        side_emoji = "🟢" if side == "BUY" else "🔴"
        message = (
            "🐋 Whale Trade Alert\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"👤 Trader: {maker_display}\n"
            f"📊 Market: {title}\n"
            f"🏷️ Outcome: {outcome}\n"
            f"⚖️ Side: {side_emoji+side}\n"
            f"📈 Size: {size}\n"
            f"💵 Price: ${price:.4f}\n"
            f"💰 Value: ${value:.2f}\n"
            f"🕒 Time: {time_str}\n"
            f"🆔 ID: {trade_id[:10]}...\n"
        )
        if link:
            message += f"\n🔗 Link: {link}"
        return message
