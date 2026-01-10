"""Main entry point for the PolyMarket Whale Watcher bot."""

import asyncio
import logging
import sys
from typing import Dict, Any

from .config import config
from .store import trade_store
from .polymarket import PolyMarketAPI
from .telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhaleWatcher:
    """Main whale watcher class that coordinates polling and notifications."""
    
    def __init__(self):
        """Initialize the whale watcher."""
        self.running = False
        self.bot = TelegramBot(config.telegram_bot_token, config.telegram_chat_id)
        self.api = PolyMarketAPI()
    
    def should_notify_trade(self, trade: Dict[str, Any]) -> bool:
        """Check if a trade should trigger a notification.
        
        Args:
            trade: Trade dictionary from the API
            
        Returns:
            True if the trade should trigger a notification
        """
        # Check trade value
        value = PolyMarketAPI.calculate_trade_value(trade)
        
        if value < config.min_trade_value:
            return False
        
        # Check market ID filter
        if config.market_ids:
            market_id = trade.get("market_id", "")
            if market_id not in config.market_ids:
                return False
        
        # Check text filters
        if config.market_text_filters:
            # Check in market title, description, or asset ID
            market_text = " ".join([
                str(trade.get("market", "")),
                str(trade.get("asset_id", "")),
                str(trade.get("market_id", ""))
            ]).lower()
            
            # If filters exist, at least one must match
            if not any(text_filter in market_text for text_filter in config.market_text_filters):
                return False
        
        return True
    
    async def poll_trades(self):
        """Poll for new trades and send notifications."""
        logger.info("Starting trade polling...")
        
        while self.running:
            try:
                # Fetch trades for all whale addresses
                if not config.whale_addresses:
                    logger.warning("No whale addresses configured. Waiting...")
                    await asyncio.sleep(config.poll_interval)
                    continue
                
                logger.debug(f"Fetching trades for {len(config.whale_addresses)} whale addresses...")
                trades = await self.api.get_all_whale_trades(config.whale_addresses)
                
                logger.debug(f"Fetched {len(trades)} trades")
                
                # Process trades
                new_trades_count = 0
                for trade in trades:
                    trade_id = trade.get("id")
                    if not trade_id:
                        continue
                    
                    # Check if trade is new
                    if not trade_store.is_new_trade(trade_id):
                        continue
                    
                    # Check if trade should trigger notification
                    if not self.should_notify_trade(trade):
                        trade_store.mark_trade_seen(trade_id)
                        continue
                    
                    # Send notification
                    message = PolyMarketAPI.format_trade(trade)
                    await self.bot.send_notification(message)
                    
                    # Mark as seen
                    trade_store.mark_trade_seen(trade_id)
                    new_trades_count += 1
                    
                    # Small delay between notifications
                    await asyncio.sleep(1)
                
                if new_trades_count > 0:
                    logger.info(f"Sent {new_trades_count} notifications")
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                # Continue on error with retry delay
                await asyncio.sleep(10)
            
            # Wait for next poll interval
            await asyncio.sleep(config.poll_interval)
    
    async def start(self):
        """Start the whale watcher."""
        logger.info("Starting PolyMarket Whale Watcher...")
        logger.info(f"Tracking {len(config.whale_addresses)} whale addresses")
        logger.info(f"Poll interval: {config.poll_interval}s")
        logger.info(f"Min trade value: ${config.min_trade_value}")
        
        self.running = True
        
        # Start the Telegram bot
        await self.bot.start()
        logger.info("Telegram bot started")
        
        # Start polling for trades
        poll_task = asyncio.create_task(self.poll_trades())
        
        try:
            # Run until interrupted
            await poll_task
        except asyncio.CancelledError:
            logger.info("Shutting down...")
        finally:
            self.running = False
            await self.stop()
    
    async def stop(self):
        """Stop the whale watcher."""
        logger.info("Stopping PolyMarket Whale Watcher...")
        await self.bot.stop()
        await self.api.__aexit__(None, None, None)
        logger.info("Stopped")


async def main():
    """Main entry point."""
    try:
        watcher = WhaleWatcher()
        await watcher.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
        sys.exit(0)
