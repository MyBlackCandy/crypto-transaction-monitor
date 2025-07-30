import websocket
import json
import telebot
import requests
import threading
import time
import logging
import os
import schedule
from datetime import datetime
from flask import Flask, jsonify
from config import *

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Global variables
crypto_prices = {'btc': 0, 'eth': 0}
processed_transactions = set()
filtered_transactions = set()  # Track transactions filtered by value
start_time = time.time()
address_stats = {
    'btc': {addr: {'alerts': 0, 'total_value': 0, 'filtered_count': 0} for addr in MONITORED_ADDRESSES['btc']},
    'eth': {addr: {'alerts': 0, 'total_value': 0, 'filtered_count': 0} for addr in MONITORED_ADDRESSES['eth']}
}
health_status = {
    'status': 'starting',
    'last_price_update': None,
    'websocket_btc': 'disconnected',
    'websocket_eth': 'disconnected',
    'total_alerts': 0,
    'total_filtered': 0,
    'errors_count': 0
}

# Flask health endpoints
@app.route('/health')
def health_check():
    uptime = time.time() - start_time
    
    # Calculate total alerts and values
    total_btc_alerts = sum(stats['alerts'] for stats in address_stats['btc'].values())
    total_eth_alerts = sum(stats['alerts'] for stats in address_stats['eth'].values())
    total_btc_value = sum(stats['total_value'] for stats in address_stats['btc'].values())
    total_eth_value = sum(stats['total_value'] for stats in address_stats['eth'].values())
    total_btc_filtered = sum(stats['filtered_count'] for stats in address_stats['btc'].values())
    total_eth_filtered = sum(stats['filtered_count'] for stats in address_stats['eth'].values())
    
    return jsonify({
        'status': health_status['status'],
        'uptime_hours': round(uptime / 3600, 2),
        'total_alerts': total_btc_alerts + total_eth_alerts,
        'total_filtered': total_btc_filtered + total_eth_filtered,
        'minimum_usd_value': MINIMUM_USD_VALUE,
        'btc_price': crypto_prices['btc'],
        'eth_price': crypto_prices['eth'],
        'websocket_status': {
            'btc': health_status['websocket_btc'],
            'eth': health_status['websocket_eth']
        },
        'monitored_addresses': {
            'btc_count': len(MONITORED_ADDRESSES['btc']),
            'eth_count': len(MONITORED_ADDRESSES['eth']),
            'btc_addresses': MONITORED_ADDRESSES['btc'][:5],  # Show first 5
            'eth_addresses': MONITORED_ADDRESSES['eth'][:5]   # Show first 5
        },
        'statistics': {
            'btc_alerts': total_btc_alerts,
            'eth_alerts': total_eth_alerts,
            'btc_filtered': total_btc_filtered,
            'eth_filtered': total_eth_filtered,
            'total_btc_value_usd': round(total_btc_value, 2),
            'total_eth_value_usd': round(total_eth_value, 2)
        },
        'filtering': {
            'minimum_usd_value': MINIMUM_USD_VALUE,
            'ignore_dust': IGNORE_DUST_TRANSACTIONS,
            'alert_type': 'incoming_only'
        },
        'last_price_update': health_status['last_price_update'],
        'errors_count': health_status['errors_count']
    })

@app.route('/addresses')
def list_addresses():
    """List all monitored addresses with labels"""
    btc_list = []
    for addr in MONITORED_ADDRESSES['btc']:
        btc_list.append({
            'address': addr,
            'label': get_address_label(addr, 'btc'),
            'alerts': address_stats['btc'][addr]['alerts'],
            'filtered_count': address_stats['btc'][addr]['filtered_count'],
            'total_value_usd': address_stats['btc'][addr]['total_value']
        })
    
    eth_list = []
    for addr in MONITORED_ADDRESSES['eth']:
        eth_list.append({
            'address': addr,
            'label': get_address_label(addr, 'eth'),
            'alerts': address_stats['eth'][addr]['alerts'],
            'filtered_count': address_stats['eth'][addr]['filtered_count'],
            'total_value_usd': address_stats['eth'][addr]['total_value']
        })
    
    return jsonify({
        'btc_addresses': btc_list,
        'eth_addresses': eth_list,
        'totals': {
            'btc_count': len(btc_list),
            'eth_count': len(eth_list)
        },
        'filtering': {
            'minimum_usd_value': MINIMUM_USD_VALUE,
            'alert_type': 'incoming_only'
        }
    })

@app.route('/stats')
def get_stats():
    """Get detailed statistics"""
    # Top performing addresses
    top_btc = sorted(address_stats['btc'].items(), key=lambda x: x[1]['total_value'], reverse=True)[:5]
    top_eth = sorted(address_stats['eth'].items(), key=lambda x: x[1]['total_value'], reverse=True)[:5]
    
    return jsonify({
        'top_btc_addresses': [
            {
                'address': addr,
                'label': get_address_label(addr, 'btc'),
                'alerts': stats['alerts'],
                'filtered_count': stats['filtered_count'],
                'total_value_usd': round(stats['total_value'], 2)
            } for addr, stats in top_btc
        ],
        'top_eth_addresses': [
            {
                'address': addr,
                'label': get_address_label(addr, 'eth'),
                'alerts': stats['alerts'],
                'filtered_count': stats['filtered_count'],
                'total_value_usd': round(stats['total_value'], 2)
            } for addr, stats in top_eth
        ],
        'filtering': {
            'minimum_usd_value': MINIMUM_USD_VALUE,
            'ignore_dust': IGNORE_DUST_TRANSACTIONS
        }
    })

@app.route('/ping')
def ping():
    return "pong"

@app.route('/')
def index():
    return jsonify({
        'service': 'Enhanced Crypto Transaction Monitor',
        'version': '3.0',
        'status': health_status['status'],
        'monitoring': {
            'btc_addresses': len(MONITORED_ADDRESSES['btc']),
            'eth_addresses': len(MONITORED_ADDRESSES['eth'])
        },
        'filtering': {
            'minimum_usd_value': MINIMUM_USD_VALUE,
            'alert_type': 'incoming_only'
        },
        'endpoints': {
            'health': '/health',
            'addresses': '/addresses',
            'stats': '/stats',
            'ping': '/ping'
        }
    })

def get_crypto_prices():
    """ดึงราคาเหรียญ"""
    global crypto_prices, health_status
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd'}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        crypto_prices['btc'] = data.get('bitcoin', {}).get('usd', 0)
        crypto_prices['eth'] = data.get('ethereum', {}).get('usd', 0)
        health_status['last_price_update'] = datetime.now().isoformat()
        
        logging.info(f"Updated prices - BTC: ${crypto_prices['btc']:,.2f}, ETH: ${crypto_prices['eth']:,.2f}")
    except Exception as e:
        logging.error(f"Error getting prices: {e}")
        health_status['errors_count'] += 1

def send_startup_summary():
    """ส่งสรุปการตั้งค่าเมื่อเริ่มต้น"""
    btc_count = len(MONITORED_ADDRESSES['btc'])
    eth_count = len(MONITORED_ADDRESSES['eth'])
    
    # Create address list with labels
    btc_list = []
    for addr in MONITORED_ADDRESSES['btc'][:MAX_ADDRESSES_PER_MESSAGE]:
        label = get_address_label(addr, 'btc')
        btc_list.append(f"• <code>{label}</code>")
    
    eth_list = []
    for addr in MONITORED_ADDRESSES['eth'][:MAX_ADDRESSES_PER_MESSAGE]:
        label = get_address_label(addr, 'eth')
        eth_list.append(f"• <code>{label}</code>")
    
    message = f"""
🚀 <b>Enhanced Crypto Monitor Started</b>
🌐 <b>Platform:</b> Railway.app

📊 <b>Monitoring Summary:</b>
₿ <b>BTC:</b> {btc_count} addresses
⟠ <b>ETH:</b> {eth_count} addresses

⚡ <b>Alert Settings:</b>
📥 Type: Incoming Transfers Only
💰 Minimum: ${MINIMUM_USD_VALUE} USD
🗑️ Dust Filter: {'Enabled' if IGNORE_DUST_TRANSACTIONS else 'Disabled'}

"""
    
    if btc_list:
        message += f"₿ <b>BTC Addresses:</b>\n"
        message += "\n".join(btc_list)
        if btc_count > MAX_ADDRESSES_PER_MESSAGE:
            message += f"\n<i>... and {btc_count - MAX_ADDRESSES_PER_MESSAGE} more</i>"
        message += "\n\n"
    
    if eth_list:
        message += f"⟠ <b>ETH Addresses:</b>\n"
        message += "\n".join(eth_list)
        if eth_count > MAX_ADDRESSES_PER_MESSAGE:
            message += f"\n<i>... and {eth_count - MAX_ADDRESSES_PER_MESSAGE} more</i>"
        message += "\n\n"
    
    message += f"""
🔌 <b>WebSocket:</b> Connecting...
💰 <b>Current Prices:</b>
₿ BTC: ${crypto_prices['btc']:,.2f}
⟠ ETH: ${crypto_prices['eth']:,.2f}

🌐 <b>Endpoints:</b>
• Health: {RAILWAY_PUBLIC_DOMAIN}/health
• Addresses: {RAILWAY_PUBLIC_DOMAIN}/addresses
• Stats: {RAILWAY_PUBLIC_DOMAIN}/stats

⚡ <b>Status:</b> All systems starting...
📥 <b>Ready to monitor incoming transfers ≥ ${MINIMUM_USD_VALUE} USD!</b>
"""
    
    try:
        bot.send_message(CHAT_ID, message, parse_mode='HTML')
        logging.info("Startup summary sent successfully")
    except Exception as e:
        logging.error(f"Error sending startup summary: {e}")

def send_daily_report():
    """ส่งรายงานประจำวัน"""
    uptime_hours = (time.time() - start_time) / 3600
    
    # Calculate totals
    total_btc_alerts = sum(stats['alerts'] for stats in address_stats['btc'].values())
    total_eth_alerts = sum(stats['alerts'] for stats in address_stats['eth'].values())
    total_btc_value = sum(stats['total_value'] for stats in address_stats['btc'].values())
    total_eth_value = sum(stats['total_value'] for stats in address_stats['eth'].values())
    total_btc_filtered = sum(stats['filtered_count'] for stats in address_stats['btc'].values())
    total_eth_filtered = sum(stats['filtered_count'] for stats in address_stats['eth'].values())
    
    # Find most active addresses
    top_btc_addr = max(address_stats['btc'].items(), key=lambda x: x[1]['alerts'], default=(None, {'alerts': 0}))
    top_eth_addr = max(address_stats['eth'].items(), key=lambda x: x[1]['alerts'], default=(None, {'alerts': 0}))
    
    message = f"""
📊 <b>Daily Report - Incoming Transfers</b>
📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

⏱️ <b>Uptime:</b> {uptime_hours:.1f} hours
🔔 <b>Total Alerts:</b> {total_btc_alerts + total_eth_alerts}
🔇 <b>Filtered (< ${MINIMUM_USD_VALUE}):</b> {total_btc_filtered + total_eth_filtered}

₿ <b>BTC Summary:</b>
• Transfers ≥ ${MINIMUM_USD_VALUE}: {total_btc_alerts}
• Filtered: {total_btc_filtered}
• Total Value: ${total_btc_value:,.2f}
• Monitoring: {len(MONITORED_ADDRESSES['btc'])} addresses

⟠ <b>ETH Summary:</b>
• Transfers ≥ ${MINIMUM_USD_VALUE}: {total_eth_alerts}
• Filtered: {total_eth_filtered}
• Total Value: ${total_eth_value:,.2f}
• Monitoring: {len(MONITORED_ADDRESSES['eth'])} addresses

🏆 <b>Most Active (Incoming ≥ ${MINIMUM_USD_VALUE}):</b>"""
    
    if top_btc_addr[0] and top_btc_addr[1]['alerts'] > 0:
        btc_label = get_address_label(top_btc_addr[0], 'btc')
        message += f"\n₿ {btc_label}: {top_btc_addr[1]['alerts']} transfers"
    
    if top_eth_addr[0] and top_eth_addr[1]['alerts'] > 0:
        eth_label = get_address_label(top_eth_addr[0], 'eth')
        message += f"\n⟠ {eth_label}: {top_eth_addr[1]['alerts']} transfers"
    
    message += f"""

💰 <b>Current Prices:</b>
₿ BTC: ${crypto_prices['btc']:,.2f}
⟠ ETH: ${crypto_prices['eth']:,.2f}

⚙️ <b>Filter Settings:</b>
💰 Minimum: ${MINIMUM_USD_VALUE} USD
📥 Type: Incoming Only
🗑️ Dust Filter: {'Enabled' if IGNORE_DUST_TRANSACTIONS else 'Disabled'}

🟢 <b>Status:</b> All systems operational
"""
    
    try:
        bot.send_message(CHAT_ID, message, parse_mode='HTML')
        logging.info("Daily report sent successfully")
    except Exception as e:
        logging.error(f"Error sending daily report: {e}")

def format_btc_message(tx_data, matched_address, received_amount_satoshi):
    """จัดรูปแบบข้อความ BTC (เฉพาะการโอนเข้า)"""
    global address_stats
    
    tx = tx_data.get('x', {})
    value_btc = received_amount_satoshi / 10**8
    usd_value = value_btc * crypto_prices['btc']
    tx_hash = tx.get('hash', 'Unknown')
    
    # Update statistics
    address_stats['btc'][matched_address]['alerts'] += 1
    address_stats['btc'][matched_address]['total_value'] += usd_value
    health_status['total_alerts'] += 1
    
    # Get address label
    address_label = get_address_label(matched_address, 'btc')
    
    # หา addresses ที่ส่งมา
    input_addrs = []
    for inp in tx.get('inputs', []):
        if 'prev_out' in inp and 'addr' in inp['prev_out']:
            input_addrs.append(inp['prev_out']['addr'])
    
    from_addr = input_addrs[0] if input_addrs else 'Unknown'
    
    message = f"""
🔔 <b>BTC Incoming Transaction</b>

📥 <b>To:</b> {address_label}
💰 <b>Amount:</b> {value_btc:.8f} BTC
💵 <b>USD Value:</b> ${usd_value:,.2f}

📤 <b>From:</b> <code>{from_addr[:15] if from_addr != 'Unknown' else 'Unknown'}...</code>
📍 <b>Address:</b> <code>{matched_address[:15]}...{matched_address[-8:]}</code>

🔗 <b>Hash:</b> <code>{tx_hash[:20]}...</code>
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
📊 <b>Alert #:</b> {address_stats['btc'][matched_address]['alerts']}
📈 <b>Type:</b> Incoming Transfer

<a href="https://blockchain.info/tx/{tx_hash}">View Transaction</a>
"""
    return message

# WebSocket handlers
def on_btc_message(ws, message):
    try:
        data = json.loads(message)
        if data.get('op') == 'utx':
            tx = data.get('x', {})
            tx_hash = tx.get('hash')
            
            if tx_hash and tx_hash not in processed_transactions:
                # ตรวจสอบเฉพาะการโอนเข้า (outputs) ไปยัง monitored addresses
                for out in tx.get('out', []):
                    output_addr = out.get('addr')
                    if output_addr in MONITORED_ADDRESSES['btc']:
                        # ตรวจสอบว่าเป็นการโอนเข้าจริงๆ (ไม่ใช่การโอนออก)
                        is_incoming = True
                        
                        # ตรวจสอบว่า address นี้ไม่ได้เป็น input (ผู้ส่ง) ในธุรกรรมเดียวกัน
                        for inp in tx.get('inputs', []):
                            if 'prev_out' in inp and inp['prev_out'].get('addr') == output_addr:
                                is_incoming = False
                                break
                        
                        if is_incoming:
                            received_amount = out.get('value', 0)
                            received_btc = received_amount / 100000000
                            usd_value = received_btc * crypto_prices['btc']
                            
                            # ตรวจสอบมูลค่าขั้นต่ำ
                            if usd_value >= MINIMUM_USD_VALUE:
                                # ส่งแจ้งเตือนเฉพาะเมื่อเป็นการโอนเข้าและมูลค่าเพียงพอ
                                if received_amount > 0:
                                    message_text = format_btc_message(data, output_addr, received_amount)
                                    
                                    try:
                                        bot.send_message(CHAT_ID, message_text, parse_mode='HTML', disable_web_page_preview=True)
                                        processed_transactions.add(tx_hash)
                                        
                                        addr_label = get_address_label(output_addr, 'btc')
                                        logging.info(f"✅ BTC incoming alert sent: {addr_label} - {received_btc:.8f} BTC (${usd_value:.2f}) - {tx_hash[:10]}...")
                                    except Exception as e:
                                        logging.error(f"Error sending BTC message: {e}")
                                        health_status['errors_count'] += 1
                                    break  # ส่งแจ้งเตือนเพียงครั้งเดียวต่อ transaction
                            else:
                                # บันทึกธุรกรรมที่ถูกกรองออก
                                address_stats['btc'][output_addr]['filtered_count'] += 1
                                health_status['total_filtered'] += 1
                                processed_transactions.add(tx_hash)
                                filtered_transactions.add(tx_hash)
                                
                                addr_label = get_address_label(output_addr, 'btc')
                                logging.info(f"🔇 BTC transaction filtered (below ${MINIMUM_USD_VALUE}): {addr_label} - {received_btc:.8f} BTC (${usd_value:.2f}) - {tx_hash[:10]}...")
                                break
                        
    except Exception as e:
        logging.error(f"Error processing BTC message: {e}")
        health_status['errors_count'] += 1

def on_btc_error(ws, error):
    logging.error(f"BTC WebSocket error: {error}")
    health_status['websocket_btc'] = 'error'
    health_status['errors_count'] += 1

def on_btc_close(ws, close_status_code, close_msg):
    logging.warning("BTC WebSocket connection closed")
    health_status['websocket_btc'] = 'disconnected'

def on_btc_open(ws):
    logging.info("🔗 BTC WebSocket connected")
    health_status['websocket_btc'] = 'connected'
    subscribe_message = {"op": "unconfirmed_sub"}
    ws.send(json.dumps(subscribe_message))

def start_btc_websocket():
    def run_btc_ws():
        while True:
            try:
                health_status['websocket_btc'] = 'connecting'
                ws = websocket.WebSocketApp(
                    "wss://ws.blockchain.info/inv",
                    on_open=on_btc_open,
                    on_message=on_btc_message,
                    on_error=on_btc_error,
                    on_close=on_btc_close
                )
                ws.run_forever()
            except Exception as e:
                logging.error(f"BTC WebSocket crashed: {e}")
                health_status['websocket_btc'] = 'error'
                health_status['errors_count'] += 1
                time.sleep(10)
    
    thread = threading.Thread(target=run_btc_ws)
    thread.daemon = True
    thread.start()
    return thread

def update_prices_periodically():
    """อัพเดทราคาตามกำหนด"""
    while True:
        get_crypto_prices()
        time.sleep(PRICE_UPDATE_INTERVAL)

def send_health_periodically():
    """ส่ง health check ตามกำหนด"""
    while True:
        time.sleep(HEALTH_CHECK_INTERVAL)
        send_daily_report()

def cleanup_processed_transactions():
    """ล้าง processed transactions ทุก 24 ชั่วโมง"""
    global processed_transactions
    while True:
        time.sleep(86400)  # 24 ชั่วโมง
        processed_transactions.clear()
        logging.info("Cleared processed transactions cache")

def reset_daily_stats():
    """รีเซ็ตสถิติประจำวัน"""
    global address_stats
    while True:
        time.sleep(86400)  # 24 ชั่วโมง
        # Reset daily counters but keep total_value
        for crypto_type in address_stats:
            for addr in address_stats[crypto_type]:
                address_stats[crypto_type][addr]['alerts'] = 0
                address_stats[crypto_type][addr]['filtered_count'] = 0
        
        # Reset global counters
        health_status['total_alerts'] = 0
        health_status['total_filtered'] = 0
        
        logging.info("Reset daily statistics (alerts and filtered counts)")
        
        # Send summary before reset
        try:
            summary_msg = f"""
🔄 <b>Daily Reset Complete</b>

📊 <b>New day started!</b>
⚙️ Alert counters reset to 0
🔇 Filter counters reset to 0
💰 Value tracking continues

📥 <b>Ready for incoming transfers ≥ ${MINIMUM_USD_VALUE} USD</b>
"""
            bot.send_message(CHAT_ID, summary_msg, parse_mode='HTML')
        except Exception as e:
            logging.error(f"Error sending reset message: {e}")

def run_flask():
    """รัน Flask server สำหรับ Railway"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

def handle_telegram_commands():
    """Handle Telegram bot commands"""
    
    @bot.message_handler(commands=['start', 'help'])
    def send_help(message):
        help_text = f"""
🤖 <b>Enhanced Crypto Monitor Bot</b>

📊 <b>Currently Monitoring:</b>
₿ {len(MONITORED_ADDRESSES['btc'])} BTC addresses
⟠ {len(MONITORED_ADDRESSES['eth'])} ETH addresses

⚙️ <b>Alert Settings:</b>
📥 Type: Incoming Transfers Only
💰 Minimum: ${MINIMUM_USD_VALUE} USD
🗑️ Dust Filter: {'Enabled' if IGNORE_DUST_TRANSACTIONS else 'Disabled'}
🚫 Note: Outgoing transfers are not monitored
🔇 Note: Transfers < ${MINIMUM_USD_VALUE} USD are filtered out

🔧 <b>Commands:</b>
/status - Current status & filter stats
/addresses - List all addresses with counts
/stats - Show incoming transfer statistics
/prices - Current crypto prices

🌐 <b>Web Interface:</b>
{RAILWAY_PUBLIC_DOMAIN}/health - Bot health status
{RAILWAY_PUBLIC_DOMAIN}/addresses - Address list with filter stats
{RAILWAY_PUBLIC_DOMAIN}/stats - Detailed statistics
"""
        bot.reply_to(message, help_text, parse_mode='HTML')
    
    @bot.message_handler(commands=['status'])
    def send_status(message):
        uptime_hours = (time.time() - start_time) / 3600
        total_alerts = sum(stats['alerts'] for stats in address_stats['btc'].values()) + \
                      sum(stats['alerts'] for stats in address_stats['eth'].values())
        total_filtered = sum(stats['filtered_count'] for stats in address_stats['btc'].values()) + \
                        sum(stats['filtered_count'] for stats in address_stats['eth'].values())
        
        status_text = f"""
📊 <b>Bot Status</b>

⏱️ <b>Uptime:</b> {uptime_hours:.1f} hours
🔔 <b>Alerts Today:</b> {total_alerts}
🔇 <b>Filtered (< ${MINIMUM_USD_VALUE}):</b> {total_filtered}
🔌 <b>WebSocket BTC:</b> {health_status['websocket_btc']}
💰 <b>BTC Price:</b> ${crypto_prices['btc']:,.2f}
⟠ <b>ETH Price:</b> ${crypto_prices['eth']:,.2f}
❌ <b>Errors:</b> {health_status['errors_count']}

⚙️ <b>Filter Settings:</b>
💰 Minimum: ${MINIMUM_USD_VALUE} USD
📥 Type: Incoming Only
🗑️ Dust Filter: {'Enabled' if IGNORE_DUST_TRANSACTIONS else 'Disabled'}

🎯 <b>Monitoring:</b>
₿ {len(MONITORED_ADDRESSES['btc'])} BTC addresses
⟠ {len(MONITORED_ADDRESSES['eth'])} ETH addresses
"""
        bot.reply_to(message, status_text, parse_mode='HTML')
    
    @bot.message_handler(commands=['addresses'])
    def send_addresses(message):
        addr_text = f"📍 <b>Monitored Addresses</b>\n"
        addr_text += f"💰 <b>Filter:</b> Incoming ≥ ${MINIMUM_USD_VALUE} USD\n\n"
        
        if MONITORED_ADDRESSES['btc']:
            addr_text += "₿ <b>BTC Addresses:</b>\n"
            for i, addr in enumerate(MONITORED_ADDRESSES['btc'][:10], 1):
                label = get_address_label(addr, 'btc')
                alerts = address_stats['btc'][addr]['alerts']
                filtered =
