"""Trade storage and deduplication for the PolyMarket Whale Watcher bot."""

import json
import logging
import os
from typing import Set, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class TradeStore:
    """Store for tracking seen trades and preventing duplicates."""
    
    def __init__(self, filepath: str = "trades.json"):
        """Initialize the trade store.
        
        Args:
            filepath: Path to the JSON file for persisting trade IDs
        """
        self.filepath = filepath
        self.seen_trades: Set[str] = set()
        self.trade_timestamps: Dict[str, float] = {}
        self._load()
    
    def _load(self):
        """Load seen trades from disk."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.seen_trades = set(data.get("trades", []))
                    self.trade_timestamps = data.get("timestamps", {})
                    # Clean old entries (older than 7 days)
                    self._clean_old_entries()
            except Exception as e:
                logger.error(f"Error loading trade store from {self.filepath}: {e}", exc_info=True)
                self.seen_trades = set()
                self.trade_timestamps = {}
    
    def _save(self):
        """Save seen trades to disk."""
        try:
            data = {
                "trades": list(self.seen_trades),
                "timestamps": self.trade_timestamps
            }
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving trade store to {self.filepath}: {e}", exc_info=True)
    
    def _clean_old_entries(self):
        """Remove entries older than 7 days."""
        cutoff = (datetime.now() - timedelta(days=7)).timestamp()
        old_trades = [
            trade_id for trade_id, ts in self.trade_timestamps.items()
            if ts < cutoff
        ]
        for trade_id in old_trades:
            self.seen_trades.discard(trade_id)
            self.trade_timestamps.pop(trade_id, None)
    
    def is_new_trade(self, trade_id: str) -> bool:
        """Check if a trade is new (not seen before).
        
        Args:
            trade_id: Unique identifier for the trade
            
        Returns:
            True if the trade is new, False if it's a duplicate
        """
        return trade_id not in self.seen_trades
    
    def mark_trade_seen(self, trade_id: str):
        """Mark a trade as seen.
        
        Args:
            trade_id: Unique identifier for the trade
        """
        self.seen_trades.add(trade_id)
        self.trade_timestamps[trade_id] = datetime.now().timestamp()
        self._save()
    
    def clear(self):
        """Clear all stored trades."""
        self.seen_trades.clear()
        self.trade_timestamps.clear()
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored trades.
        
        Returns:
            Dictionary with trade statistics
        """
        return {
            "total_trades": len(self.seen_trades),
            "oldest_trade": min(self.trade_timestamps.values()) if self.trade_timestamps else None,
            "newest_trade": max(self.trade_timestamps.values()) if self.trade_timestamps else None
        }


# Global store instance
trade_store = TradeStore()
