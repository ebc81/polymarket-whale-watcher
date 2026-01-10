# PolyMarket Whale Watcher 🐋

A Telegram bot that monitors large trades (whale activity) on PolyMarket and sends real-time notifications.

## Features

- 📊 Real-time monitoring of whale trades on PolyMarket
- 🔔 Telegram notifications for significant trades
- 🎯 Customizable filters (minimum value, market IDs, keywords)
- 👥 Track multiple whale addresses
- 🔄 Automatic retry on API errors
- 💾 Trade deduplication to prevent duplicate notifications
- 🛡️ Single chat ID restriction for security
- ⚙️ Easy configuration via Telegram bot commands

## Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))
- Your Telegram chat ID (get it from [@userinfobot](https://t.me/userinfobot))

## Installation

### Windows Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ebc81/polymarket-whale-watcher.git
   cd polymarket-whale-watcher
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your Telegram bot token and chat ID
   ```bash
   copy .env.example .env
   notepad .env
   ```

5. **Run the bot:**
   ```bash
   python -m src.main
   ```

### Raspberry Pi / Linux Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ebc81/polymarket-whale-watcher.git
   cd polymarket-whale-watcher
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your credentials
   ```bash
   cp .env.example .env
   nano .env
   ```

5. **Run the bot:**
   ```bash
   python -m src.main
   ```

### Running as a Systemd Service (Linux/Raspberry Pi)

1. **Edit the service file:**
   ```bash
   nano service/polymarket-bot.service
   ```
   Update the `User` and `WorkingDirectory` paths to match your setup.

2. **Copy the service file:**
   ```bash
   sudo cp service/polymarket-bot.service /etc/systemd/system/
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable polymarket-bot.service
   sudo systemctl start polymarket-bot.service
   ```

4. **Check the status:**
   ```bash
   sudo systemctl status polymarket-bot.service
   ```

5. **View logs:**
   ```bash
   sudo journalctl -u polymarket-bot.service -f
   ```

## Configuration

### Environment Variables

Edit the `.env` file to configure the bot:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# PolyMarket Configuration
POLL_INTERVAL=60                # How often to check for new trades (seconds)
MIN_TRADE_VALUE=0               # Minimum trade value to notify (USD)

# Bootstrap whale addresses (comma-separated)
WHALE_ADDRESSES=0x0029ec6df644c87b7ba49e9627b04b8fa0f6bc93,0x003f24b98b1b54a49e3df4bb3a07a0f5fda4a3ed

# Market filters (optional, comma-separated market IDs)
MARKET_IDS=

# Market text filters (optional, comma-separated keywords)
MARKET_TEXT_FILTERS=
```

### Getting Your Telegram Credentials

1. **Bot Token:**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token provided

2. **Chat ID:**
   - Start a chat with your bot
   - Send any message to it
   - Open [@userinfobot](https://t.me/userinfobot) and get your user ID
   - Use this ID as your `TELEGRAM_CHAT_ID`

## Bot Commands

Once the bot is running, you can manage it using these Telegram commands:

### General Commands
- `/start` or `/help` - Show help message with all commands
- `/status` - Show current configuration

### Whale Management
- `/addwhale <address>` - Add a whale address to track
- `/removewhale <address>` - Remove a whale address
- `/listwhales` - List all tracked whale addresses

### Market Filters
- `/addmarket <id>` - Add a market ID filter
- `/removemarket <id>` - Remove a market ID filter
- `/listmarkets` - List all market filters

### Text Filters
- `/addtext <keyword>` - Add a keyword filter for market names
- `/removetext <keyword>` - Remove a keyword filter
- `/listtexts` - List all text filters

### Configuration
- `/setminvalue <value>` - Set minimum trade value (USD)
- `/setinterval <seconds>` - Set poll interval (minimum 10 seconds)

### Example Usage

```
/addwhale 0x1234567890abcdef1234567890abcdef12345678
/setminvalue 1000
/setinterval 30
/addtext trump
/status
```

## How It Works

1. **Polling Loop**: The bot continuously polls the PolyMarket trades API at the configured interval
2. **Trade Fetching**: It fetches recent trades for all tracked whale addresses
3. **Filtering**: Trades are filtered based on:
   - Minimum trade value
   - Market ID (if configured)
   - Market text/keywords (if configured)
4. **Deduplication**: Each trade is checked against a local store to prevent duplicate notifications
5. **Notifications**: Qualifying trades are formatted and sent to your Telegram chat

## Project Structure

```
polymarket-whale-watcher/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── store.py              # Trade storage and deduplication
│   ├── polymarket.py         # PolyMarket API client
│   ├── telegram_bot.py       # Telegram bot implementation
│   └── main.py               # Main entry point
├── service/
│   └── polymarket-bot.service # Systemd service file
├── .env.example              # Example environment configuration
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Troubleshooting

### Bot doesn't respond to commands
- Verify your `TELEGRAM_CHAT_ID` is correct
- Make sure you've started a chat with your bot first
- Check that the bot token is valid

### No trade notifications
- Verify whale addresses are correctly configured
- Check if `MIN_TRADE_VALUE` is set too high
- Ensure the bot is running (check logs)
- Verify network connectivity to PolyMarket API

### "Unauthorized access" message
- Your Telegram chat ID doesn't match the configured `TELEGRAM_CHAT_ID`
- Only the configured chat ID can use the bot

### Service won't start on Linux
- Check file permissions: `chmod +x src/main.py`
- Verify paths in the service file are correct
- Check logs: `sudo journalctl -u polymarket-bot.service -f`

## Security Notes

- Never commit your `.env` file to version control
- Keep your bot token secret
- The bot only responds to the configured chat ID
- Store whale addresses and API keys securely

## API Rate Limiting

The PolyMarket API has rate limits. The bot includes:
- Configurable poll intervals (default: 60 seconds)
- Automatic retry on errors with exponential backoff
- Request timeouts to prevent hanging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Disclaimer

This bot is for informational purposes only. Use at your own risk. The authors are not responsible for any trading decisions made based on notifications from this bot.
