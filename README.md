# 🤖 Crypto Transaction Monitor Bot

Real-time Bitcoin and Ethereum transaction monitoring bot with Telegram notifications. Tracks incoming transfers ≥ $2 USD with WebSocket connections and Railway deployment.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/crypto-monitor)

## ✨ Features

- 🔔 **Real-time Monitoring** - WebSocket connections for instant alerts
- 💰 **Value Filtering** - Only alerts for transfers ≥ $2 USD (configurable)
- 📥 **Incoming Only** - Monitors incoming transfers, ignores outgoing
- 🏷️ **Address Labels** - Custom labels for easy identification
- 📊 **Web Dashboard** - Health checks and statistics via web endpoints
- 💬 **Telegram Commands** - Interactive bot commands
- 🚀 **Railway Ready** - One-click deployment on Railway.app
- 📈 **Multi-Address** - Unlimited Bitcoin and Ethereum addresses

## 🚀 Quick Deploy on Railway

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Set environment variables (see below)
4. Deploy! 🎉

## ⚙️ Environment Variables

```env
# Required
TELEGRAM_TOKEN=your_bot_token_from_botfather
CHAT_ID=your_telegram_chat_id

# API Keys
INFURA_PROJECT_ID=your_infura_project_id

# Addresses (comma-separated)
BTC_ADDRESSES=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
ETH_ADDRESSES=0x742dDA7632C3d39f88c93c1271eB20B49C6C97b8,0xA0b86991c420AcB6EdDc9E4d30D4f1B2F1C8B62

# Optional - Address Labels
BTC_LABELS=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa:Genesis Block,3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy:Exchange Wallet
ETH_LABELS=0x742dDA7632C3d39f88c93c1271eB20B49C6C97b8:Main Wallet

# Optional - Filtering
MINIMUM_USD_VALUE=2.0
IGNORE_DUST_TRANSACTIONS=true
```

## 📱 Telegram Setup

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add bot to your group/channel and get Chat ID

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/MyBlackCandy/crypto-transaction-monitor.git
cd crypto-transaction-monitor

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Run bot
python bot.py
```

## 📊 Web Endpoints

Once deployed, access these endpoints:

- `/health` - Bot status and statistics
- `/addresses` - List of monitored addresses
- `/stats` - Detailed performance statistics
- `/ping` - Simple health check

Example: `https://your-app.railway.app/health`

## 💬 Telegram Commands

- `/status` - Current bot status
- `/addresses` - List monitored addresses
- `/stats` - Statistics with filtering info
- `/prices` - Current crypto prices
- `/help` - Command help

## 🛠️ Management Tools

### Address Management
```bash
# Generate from CSV
python tools/generate_addresses.py sample
python tools/generate_addresses.py addresses.csv

# Validate addresses
python tools/validate_addresses.py env

# Interactive management
python tools/manage_addresses.py
```

### Bulk Operations
```bash
# Check balances
python tools/bulk_operations.py balance btc
python tools/bulk_operations.py balance eth

# Find zero balance addresses
python tools/bulk_operations.py zero btc
```

## 📈 Monitoring

### Health Monitoring
- Railway dashboard for logs and metrics
- Web endpoints for health checks
- Telegram daily reports
- Error tracking and alerting

### Statistics Tracking
- Alert counts per address
- Filtered transaction counts
- USD value tracking
- Performance metrics

## 🔍 How It Works

1. **WebSocket Connection** - Connects to Blockchain.info for real-time BTC data
2. **Transaction Analysis** - Checks if transactions are incoming to monitored addresses
3. **Value Filtering** - Only processes transactions ≥ minimum USD value
4. **Telegram Alert** - Sends formatted notification with transaction details
5. **Statistics** - Tracks alerts and filtered transactions per address

## 📊 Sample Alert

```
🔔 BTC Incoming Transaction

📥 To: Main Wallet
💰 Amount: 0.00125000 BTC
💵 USD Value: $54.25

📤 From: 1A1zP1eP5QG...
📍 Address: 3J98t1WpEZ7...12345

🔗 Hash: a1b2c3d4e5f...
⏰ Time: 15:30:45
📊 Alert #: 15
📈 Type: Incoming Transfer

View Transaction
```

## 🔧 Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIMUM_USD_VALUE` | 2.0 | Minimum USD value to trigger alerts |
| `IGNORE_DUST_TRANSACTIONS` | true | Filter out dust transactions |
| `LOG_LEVEL` | INFO | Logging level |
| `HEALTH_CHECK_INTERVAL` | 21600 | Health report interval (seconds) |
| `PRICE_UPDATE_INTERVAL` | 300 | Price update interval (seconds) |

## 📦 Tech Stack

- **Python 3.11+** - Core language
- **WebSocket** - Real-time data connections
- **Flask** - Web dashboard
- **Railway.app** - Hosting platform
- **Telegram Bot API** - Notifications
- **Blockchain.info API** - Bitcoin data
- **CoinGecko API** - Price data

## 💰 Cost

- **Railway.app**: Free $5/month (sufficient for 24/7 operation)
- **APIs**: Free tiers (Blockchain.info, CoinGecko, Infura)
- **Total**: $0/month for most use cases

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for monitoring purposes only. Always verify transactions independently. Not financial advice.

## 🆘 Support

- 📚 Documentation: Check this README
- 🐛 Issues: [GitHub Issues](https://github.com/MyBlackCandy/crypto-transaction-monitor/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/MyBlackCandy/crypto-transaction-monitor/discussions)

## 🎯 Roadmap

- [ ] Ethereum WebSocket support
- [ ] Mobile app notifications
- [ ] Advanced filtering rules
- [ ] Multi-language support
- [ ] Historical data analysis
- [ ] Alert templates

---

<div align="center">
  <strong>Built with ❤️ for the crypto community</strong>
</div>
