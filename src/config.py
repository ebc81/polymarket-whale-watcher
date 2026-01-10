"""Configuration management for the PolyMarket Whale Watcher bot."""

import json
import logging
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for the bot."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Telegram configuration
        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Persistent state file
        self.state_file: str = os.getenv("CONFIG_STATE_FILE", "config_state.json")
        
        # Polling configuration
        self.poll_interval: int = int(os.getenv("POLL_INTERVAL", "60"))
        self.min_trade_value: float = float(os.getenv("MIN_TRADE_VALUE", "0"))
        self.heartbeat_interval: int = max(60, int(os.getenv("HEARTBEAT_INTERVAL", "600")))
        
        # Whale addresses (bootstrap list)
        whale_addresses_str = os.getenv("WHALE_ADDRESSES", "")
        self.whale_addresses: List[str] = [
            addr.strip().lower() for addr in whale_addresses_str.split(",") if addr.strip()
        ]
        
        # Market filters
        market_ids_str = os.getenv("MARKET_IDS", "")
        self.market_ids: List[str] = [
            mid.strip() for mid in market_ids_str.split(",") if mid.strip()
        ]
        
        market_text_str = os.getenv("MARKET_TEXT_FILTERS", "")
        self.market_text_filters: List[str] = [
            text.strip().lower() for text in market_text_str.split(",") if text.strip()
        ]
        
        # Exclusion filters
        exclude_market_ids_str = os.getenv("EXCLUDE_MARKET_IDS", "")
        self.exclude_market_ids: List[str] = [
            mid.strip().lower() for mid in exclude_market_ids_str.split(",") if mid.strip()
        ]
        
        exclude_text_str = os.getenv("EXCLUDE_MARKET_TEXT_FILTERS", "")
        self.exclude_market_text_filters: List[str] = [
            text.strip().lower() for text in exclude_text_str.split(",") if text.strip()
        ]
        
        self._load_state()
        self._validate()
    
    def _load_state(self):
        """Load persisted state from disk if available."""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            logger.warning("Could not load config state from %s: %s", self.state_file, exc)
            return
        
        self.poll_interval = max(10, int(data.get("poll_interval", self.poll_interval)))
        self.min_trade_value = max(0.0, float(data.get("min_trade_value", self.min_trade_value)))
        self.heartbeat_interval = max(60, int(data.get("heartbeat_interval", self.heartbeat_interval)))
        persisted_whales = data.get("whale_addresses")
        if isinstance(persisted_whales, list):
            self.whale_addresses = [addr.strip().lower() for addr in persisted_whales if addr]
        persisted_market_ids = data.get("market_ids")
        if isinstance(persisted_market_ids, list):
            self.market_ids = [mid.strip() for mid in persisted_market_ids if mid]
        persisted_market_texts = data.get("market_text_filters")
        if isinstance(persisted_market_texts, list):
            self.market_text_filters = [text.strip().lower() for text in persisted_market_texts if text]
        persisted_exclude_market_ids = data.get("exclude_market_ids")
        if isinstance(persisted_exclude_market_ids, list):
            self.exclude_market_ids = [mid.strip().lower() for mid in persisted_exclude_market_ids if mid]
        persisted_exclude_texts = data.get("exclude_market_text_filters")
        if isinstance(persisted_exclude_texts, list):
            self.exclude_market_text_filters = [text.strip().lower() for text in persisted_exclude_texts if text]
    
    def _save_state(self):
        """Persist mutable settings to disk."""
        data = {
            "poll_interval": self.poll_interval,
            "min_trade_value": self.min_trade_value,
            "heartbeat_interval": self.heartbeat_interval,
            "whale_addresses": self.whale_addresses,
            "market_ids": self.market_ids,
            "market_text_filters": self.market_text_filters,
            "exclude_market_ids": self.exclude_market_ids,
            "exclude_market_text_filters": self.exclude_market_text_filters,
        }
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            logger.error("Failed to save config state to %s: %s", self.state_file, exc)
    
    def _validate(self):
        """Validate required configuration."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.telegram_chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is required")
    
    def add_whale_address(self, address: str) -> bool:
        """Add a whale address to track."""
        address = address.strip().lower()
        if address and address not in self.whale_addresses:
            self.whale_addresses.append(address)
            self._save_state()
            return True
        return False
    
    def remove_whale_address(self, address: str) -> bool:
        """Remove a whale address from tracking."""
        address = address.strip().lower()
        if address in self.whale_addresses:
            self.whale_addresses.remove(address)
            self._save_state()
            return True
        return False
    
    def add_market_filter(self, market_id: str) -> bool:
        """Add a market ID filter."""
        market_id = market_id.strip()
        if market_id and market_id not in self.market_ids:
            self.market_ids.append(market_id)
            self._save_state()
            return True
        return False
    
    def remove_market_filter(self, market_id: str) -> bool:
        """Remove a market ID filter."""
        market_id = market_id.strip()
        if market_id in self.market_ids:
            self.market_ids.remove(market_id)
            self._save_state()
            return True
        return False
    
    def add_text_filter(self, text: str) -> bool:
        """Add a market text filter."""
        text = text.strip().lower()
        if text and text not in self.market_text_filters:
            self.market_text_filters.append(text)
            self._save_state()
            return True
        return False
    
    def remove_text_filter(self, text: str) -> bool:
        """Remove a market text filter."""
        text = text.strip().lower()
        if text in self.market_text_filters:
            self.market_text_filters.remove(text)
            self._save_state()
            return True
        return False
    
    def set_min_trade_value(self, value: float) -> None:
        """Set the minimum trade value filter."""
        self.min_trade_value = max(0, value)
        self._save_state()
    
    def set_poll_interval(self, interval: int) -> None:
        """Set the poll interval in seconds."""
        self.poll_interval = max(10, interval)
        self._save_state()
    
    def set_heartbeat_interval(self, interval: int) -> None:
        """Set the heartbeat interval in seconds."""
        self.heartbeat_interval = max(60, interval)
        self._save_state()
    
    def add_exclude_market_id(self, market_id: str) -> bool:
        """Add a market ID to the exclusion list."""
        market_id = market_id.strip().lower()
        if market_id and market_id not in self.exclude_market_ids:
            self.exclude_market_ids.append(market_id)
            self._save_state()
            return True
        return False
    
    def remove_exclude_market_id(self, market_id: str) -> bool:
        """Remove a market ID from the exclusion list."""
        market_id = market_id.strip().lower()
        if market_id in self.exclude_market_ids:
            self.exclude_market_ids.remove(market_id)
            self._save_state()
            return True
        return False
    
    def add_exclude_text_filter(self, text: str) -> bool:
        """Add a text filter to the exclusion list."""
        text = text.strip().lower()
        if text and text not in self.exclude_market_text_filters:
            self.exclude_market_text_filters.append(text)
            self._save_state()
            return True
        return False
    
    def remove_exclude_text_filter(self, text: str) -> bool:
        """Remove a text filter from the exclusion list."""
        text = text.strip().lower()
        if text in self.exclude_market_text_filters:
            self.exclude_market_text_filters.remove(text)
            self._save_state()
            return True
        return False


# Global config instance
config = Config()
