import os
from typing import List, Dict

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# API Keys
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')

def parse_addresses(env_var: str) -> List[str]:
    """Parse addresses from environment variable"""
    addresses = os.getenv(env_var, '')
    if not addresses:
        return []
    
    # Split by comma and clean whitespace
    addr_list = [addr.strip() for addr in addresses.split(',') if addr.strip()]
    
    # Validate addresses format
    validated_addresses = []
    for addr in addr_list:
        if validate_address_format(addr):
            validated_addresses.append(addr)
        else:
            print(f"⚠️ Invalid address format: {addr}")
    
    return validated_addresses

def parse_labels(env_var: str) -> Dict[str, str]:
    """Parse address labels from environment variable"""
    labels = os.getenv(env_var, '')
    if not labels:
        return {}
    
    label_dict = {}
    for pair in labels.split(','):
        if ':' in pair:
            addr, label = pair.split(':', 1)
            label_dict[addr.strip()] = label.strip()
    
    return label_dict

def validate_address_format(address: str) -> bool:
    """Basic address format validation"""
    if not address:
        return False
    
    # BTC address patterns
    if (address.startswith('1') or address.startswith('3') or 
        address.startswith('bc1') or address.startswith('tb1')):
        return len(address) >= 26 and len(address) <= 62
    
    # ETH address pattern
    if address.startswith('0x'):
        return len(address) == 42 and all(c in '0123456789abcdefABCDEF' for c in address[2:])
    
    return False

def get_address_label(address: str, crypto_type: str) -> str:
    """Get human-readable label for address"""
    labels = ADDRESS_LABELS.get(crypto_type, {})
    return labels.get(address, f"{address[:8]}...{address[-6:]}")

# Parse monitored addresses
MONITORED_ADDRESSES = {
    'btc': parse_addresses('BTC_ADDRESSES'),
    'eth': parse_addresses('ETH_ADDRESSES')
}

# Parse address labels
ADDRESS_LABELS = {
    'btc': parse_labels('BTC_LABELS'),
    'eth': parse_labels('ETH_LABELS')
}

# Alert Filtering Settings
MINIMUM_USD_VALUE = float(os.getenv('MINIMUM_USD_VALUE', '2.0'))           # Default $2 USD minimum
IGNORE_DUST_TRANSACTIONS = os.getenv('IGNORE_DUST_TRANSACTIONS', 'true').lower() == 'true'

# Optional Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '21600'))  # 6 hours
PRICE_UPDATE_INTERVAL = int(os.getenv('PRICE_UPDATE_INTERVAL', '300'))    # 5 minutes
MAX_ADDRESSES_PER_MESSAGE = int(os.getenv('MAX_ADDRESSES_PER_MESSAGE', '10'))

# Railway specific settings
PORT = int(os.getenv('PORT', '8080'))
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL', '')
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')

# Validation
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")
if not CHAT_ID:
    raise ValueError("CHAT_ID environment variable is required")
if not MONITORED_ADDRESSES['btc'] and not MONITORED_ADDRESSES['eth']:
    raise ValueError("At least one BTC or ETH address must be specified")

# Display configuration summary
total_btc = len(MONITORED_ADDRESSES['btc'])
total_eth = len(MONITORED_ADDRESSES['eth'])
print(f"📊 Configuration loaded: {total_btc} BTC addresses, {total_eth} ETH addresses")
print(f"💰 Minimum alert value: ${MINIMUM_USD_VALUE}")
print(f"🗑️ Ignore dust transactions: {IGNORE_DUST_TRANSACTIONS}")

if total_btc > 0:
    print(f"₿ BTC Addresses: {', '.join([get_address_label(addr, 'btc') for addr in MONITORED_ADDRESSES['btc'][:3]])}{'...' if total_btc > 3 else ''}")

if total_eth > 0:
    print(f"⟠ ETH Addresses: {', '.join([get_address_label(addr, 'eth') for addr in MONITORED_ADDRESSES['eth'][:3]])}{'...' if total_eth > 3 else ''}")
