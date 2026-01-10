"""Telegram bot for managing the PolyMarket Whale Watcher."""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters,
)
from typing import Optional
import asyncio

from .config import config


class TelegramBot:
    """Telegram bot for whale watcher notifications and commands."""
    
    def __init__(self, token: str, allowed_chat_id: str):
        """Initialize the Telegram bot.
        
        Args:
            token: Telegram bot token
            allowed_chat_id: Chat ID that is allowed to use the bot
        """
        self.token = token
        self.allowed_chat_id = allowed_chat_id
        self.application: Optional[Application] = None
        self.notification_callback = None
    
    def set_notification_callback(self, callback):
        """Set the callback function for sending notifications.
        
        Args:
            callback: Async function to call for sending notifications
        """
        self.notification_callback = callback
    
    def _check_authorization(self, update: Update) -> bool:
        """Check if the user is authorized to use the bot.
        
        Args:
            update: Telegram update object
            
        Returns:
            True if authorized, False otherwise
        """
        if update.effective_chat:
            return str(update.effective_chat.id) == self.allowed_chat_id
        return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        help_text = (
            "🐋 PolyMarket Whale Watcher Bot\n\n"
            "Available commands:\n"
            "/help - Show this help message\n"
            "/status - Show current configuration\n"
            "/addwhale <address> - Add whale address\n"
            "/removewhale <address> - Remove whale address\n"
            "/listwhales - List tracked whale addresses\n"
            "/addmarket <id> - Add market ID filter\n"
            "/removemarket <id> - Remove market ID filter\n"
            "/listmarkets - List market filters\n"
            "/addtext <keyword> - Add text filter\n"
            "/removetext <keyword> - Remove text filter\n"
            "/listtexts - List text filters\n"
            "/setminvalue <value> - Set minimum trade value\n"
            "/setinterval <seconds> - Set poll interval\n"
        )
        await update.message.reply_text(help_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await self.start_command(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        status_text = (
            f"📊 Current Configuration\n\n"
            f"Poll Interval: {config.poll_interval}s\n"
            f"Min Trade Value: ${config.min_trade_value}\n"
            f"Tracked Whales: {len(config.whale_addresses)}\n"
            f"Market Filters: {len(config.market_ids)}\n"
            f"Text Filters: {len(config.market_text_filters)}\n"
        )
        await update.message.reply_text(status_text)
    
    async def addwhale_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addwhale command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /addwhale <address>")
            return
        
        address = context.args[0]
        if config.add_whale_address(address):
            await update.message.reply_text(f"✅ Added whale address: {address}")
        else:
            await update.message.reply_text(f"⚠️ Address already tracked or invalid: {address}")
    
    async def removewhale_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removewhale command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /removewhale <address>")
            return
        
        address = context.args[0]
        if config.remove_whale_address(address):
            await update.message.reply_text(f"✅ Removed whale address: {address}")
        else:
            await update.message.reply_text(f"⚠️ Address not found: {address}")
    
    async def listwhales_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listwhales command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if config.whale_addresses:
            whales_text = "🐋 Tracked Whale Addresses:\n\n" + "\n".join(
                f"{i+1}. {addr}" for i, addr in enumerate(config.whale_addresses)
            )
        else:
            whales_text = "No whale addresses tracked."
        
        await update.message.reply_text(whales_text)
    
    async def addmarket_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addmarket command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /addmarket <market_id>")
            return
        
        market_id = context.args[0]
        if config.add_market_filter(market_id):
            await update.message.reply_text(f"✅ Added market filter: {market_id}")
        else:
            await update.message.reply_text(f"⚠️ Market filter already exists: {market_id}")
    
    async def removemarket_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removemarket command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /removemarket <market_id>")
            return
        
        market_id = context.args[0]
        if config.remove_market_filter(market_id):
            await update.message.reply_text(f"✅ Removed market filter: {market_id}")
        else:
            await update.message.reply_text(f"⚠️ Market filter not found: {market_id}")
    
    async def listmarkets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listmarkets command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if config.market_ids:
            markets_text = "📊 Market ID Filters:\n\n" + "\n".join(
                f"{i+1}. {mid}" for i, mid in enumerate(config.market_ids)
            )
        else:
            markets_text = "No market filters configured."
        
        await update.message.reply_text(markets_text)
    
    async def addtext_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addtext command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /addtext <keyword>")
            return
        
        text = " ".join(context.args)
        if config.add_text_filter(text):
            await update.message.reply_text(f"✅ Added text filter: {text}")
        else:
            await update.message.reply_text(f"⚠️ Text filter already exists: {text}")
    
    async def removetext_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removetext command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /removetext <keyword>")
            return
        
        text = " ".join(context.args)
        if config.remove_text_filter(text):
            await update.message.reply_text(f"✅ Removed text filter: {text}")
        else:
            await update.message.reply_text(f"⚠️ Text filter not found: {text}")
    
    async def listtexts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listtexts command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if config.market_text_filters:
            texts_text = "🔍 Text Filters:\n\n" + "\n".join(
                f"{i+1}. {text}" for i, text in enumerate(config.market_text_filters)
            )
        else:
            texts_text = "No text filters configured."
        
        await update.message.reply_text(texts_text)
    
    async def setminvalue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setminvalue command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /setminvalue <value>")
            return
        
        try:
            value = float(context.args[0])
            config.set_min_trade_value(value)
            await update.message.reply_text(f"✅ Set minimum trade value to: ${value}")
        except ValueError:
            await update.message.reply_text("⚠️ Invalid value. Please provide a number.")
    
    async def setinterval_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setinterval command."""
        if not self._check_authorization(update):
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /setinterval <seconds>")
            return
        
        try:
            interval = int(context.args[0])
            config.set_poll_interval(interval)
            await update.message.reply_text(f"✅ Set poll interval to: {config.poll_interval}s")
        except ValueError:
            await update.message.reply_text("⚠️ Invalid interval. Please provide a number.")
    
    async def send_notification(self, message: str):
        """Send a notification message to the allowed chat.
        
        Args:
            message: Message to send
        """
        if self.application:
            try:
                await self.application.bot.send_message(
                    chat_id=self.allowed_chat_id,
                    text=message
                )
            except Exception as e:
                print(f"Error sending notification: {e}")
    
    async def start(self):
        """Start the Telegram bot."""
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("addwhale", self.addwhale_command))
        self.application.add_handler(CommandHandler("removewhale", self.removewhale_command))
        self.application.add_handler(CommandHandler("listwhales", self.listwhales_command))
        self.application.add_handler(CommandHandler("addmarket", self.addmarket_command))
        self.application.add_handler(CommandHandler("removemarket", self.removemarket_command))
        self.application.add_handler(CommandHandler("listmarkets", self.listmarkets_command))
        self.application.add_handler(CommandHandler("addtext", self.addtext_command))
        self.application.add_handler(CommandHandler("removetext", self.removetext_command))
        self.application.add_handler(CommandHandler("listtexts", self.listtexts_command))
        self.application.add_handler(CommandHandler("setminvalue", self.setminvalue_command))
        self.application.add_handler(CommandHandler("setinterval", self.setinterval_command))
        
        # Initialize and start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
    
    async def stop(self):
        """Stop the Telegram bot."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
