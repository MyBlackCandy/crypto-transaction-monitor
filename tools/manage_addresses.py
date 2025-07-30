#!/usr/bin/env python3
"""Interactive address management"""

import os
import json
import time

def load_addresses():
    """Load addresses from various sources"""
    addresses = {'btc': [], 'eth': []}
    labels = {'btc': {}, 'eth': {}}
    
    # Try to load from JSON
    if os.path.exists('addresses.json'):
        with open('addresses.json', 'r') as f:
            data = json.load(f)
            addresses = data.get('addresses', addresses)
            labels = data.get('labels', labels)
    
    return addresses, labels

def save_addresses(addresses, labels):
    """Save addresses to JSON"""
    data = {
        'addresses': addresses,
        'labels': labels,
        'metadata': {
            'total': len(addresses['btc']) + len(addresses['eth']),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    with open('addresses.json', 'w') as f:
        json.dump(data, f, indent=2)

def add_address_interactive():
    """Add address interactively"""
    addresses, labels = load_addresses()
    
    print("\n➕ Add New Address")
    print("-" * 20)
    
    crypto_type = input("Crypto type (btc/eth): ").lower()
    if crypto_type not in ['btc', 'eth']:
        print("❌ Invalid crypto type")
        return
    
    address = input("Address: ").strip()
    if not address:
        print("❌ Address cannot be empty")
        return
    
    if address in addresses[crypto_type]:
        print("⚠️ Address already exists")
        return
    
    label = input("Label (optional): ").strip()
    
    addresses[crypto_type].append(address)
    if label:
        labels[crypto_type][address] = label
    
    save_addresses(addresses, labels)
    
    display_name = label if label else f"{address[:8]}...{address[-6:]}"
    print(f"✅ Added {crypto_type.upper()}: {display_name}")

def list_addresses():
    """List all addresses"""
    addresses, labels = load_addresses()
    
    print("\n📋 Current Addresses")
    print("=" * 40)
    
    for crypto_type in ['btc', 'eth']:
        if addresses[crypto_type]:
            print(f"\n{crypto_type.upper()} ({len(addresses[crypto_type])} addresses):")
            for i, addr in enumerate(addresses[crypto_type], 1):
                label = labels[crypto_type].get(addr, '')
                display = f"{addr[:8]}...{addr[-6:]}"
                if label:
                    display += f" ({label})"
                print(f"  {i:2d}. {display}")

def remove_address_interactive():
    """Remove address interactively"""
    addresses, labels = load_addresses()
    
    print("\n➖ Remove Address")
    print("-" * 20)
    
    crypto_type = input("Crypto type (btc/eth): ").lower()
    if crypto_type not in ['btc', 'eth']:
        print("❌ Invalid crypto type")
        return
    
    if not addresses[crypto_type]:
        print(f"❌ No {crypto_type.upper()} addresses found")
        return
    
    print(f"\n{crypto_type.upper()} Addresses:")
    for i, addr in enumerate(addresses[crypto_type], 1):
        label = labels[crypto_type].get(addr, '')
        display = f"{addr[:8]}...{addr[-6:]}"
        if label:
            display += f" ({label})"
        print(f"  {i}. {display}")
    
    try:
        choice = int(input("\nSelect address to remove (number): ")) - 1
        if 0 <= choice < len(addresses[crypto_type]):
            addr_to_remove = addresses[crypto_type][choice]
            label = labels[crypto_type].get(addr_to_remove, '')
            
            # Confirm removal
            display_name = label if label else f"{addr_to_remove[:8]}...{addr_to_remove[-6:]}"
            confirm = input(f"Remove {display_name}? (y/N): ").lower()
            
            if confirm == 'y':
                addresses[crypto_type].remove(addr_to_remove)
                if addr_to_remove in labels[crypto_type]:
                    del labels[crypto_type][addr_to_remove]
                
                save_addresses(addresses, labels)
                print(f"✅ Removed {display_name}")
            else:
                print("❌ Cancelled")
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")

def generate_env():
    """Generate .env format"""
    addresses, labels = load_addresses()
    
    btc_addresses = ','.join(addresses['btc'])
    eth_addresses = ','.join(addresses['eth'])
    
    btc_labels = ','.join([f"{addr}:{label}" for addr, label in labels['btc'].items()])
    eth_labels = ','.join([f"{addr}:{label}" for addr, label in labels['eth'].items()])
    
    env_content = f"""# Generated Address Configuration
# Created on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Telegram Configuration
TELEGRAM_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here

# API Keys
INFURA_PROJECT_ID=your_infura_project_id

# BTC Addresses ({len(addresses['btc'])} total)
BTC_ADDRESSES={btc_addresses}

# ETH Addresses ({len(addresses['eth'])} total)
ETH_ADDRESSES={eth_addresses}

# Address Labels
BTC_LABELS={btc_labels}
ETH_LABELS={eth_labels}

# Alert Filtering
MINIMUM_USD_VALUE=2.0
IGNORE_DUST_TRANSACTIONS=true

# Optional Settings
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=21600
PRICE_UPDATE_INTERVAL=300
MAX_ADDRESSES_PER_MESSAGE=10
"""
    
    with open('addresses.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated addresses.env")
    print("\n📋 Environment Variables:")
    print("=" * 40)
    print("Copy these to Railway.app:")
    print("\n" + "="*40)
    
    # Show only the important parts
    print(f"BTC_ADDRESSES={btc_addresses}")
    print(f"ETH_ADDRESSES={eth_addresses}")
    if btc_labels:
        print(f"BTC_LABELS={btc_labels}")
    if eth_labels:
        print(f"ETH_LABELS={eth_labels}")
    print("MINIMUM_USD_VALUE=2.0")
    print("IGNORE_DUST_TRANSACTIONS=true")

def show_statistics():
    """Show address statistics"""
    addresses, labels = load_addresses()
    
    total_btc = len(addresses['btc'])
    total_eth = len(addresses['eth'])
    labeled_btc = len(labels['btc'])
    labeled_eth = len(labels['eth'])
    
    print("\n📊 Address Statistics")
    print("=" * 40)
    print(f"₿ BTC Addresses: {total_btc}")
    print(f"  └─ Labeled: {labeled_btc} ({labeled_btc/total_btc*100 if total_btc > 0 else 0:.1f}%)")
    print(f"⟠ ETH Addresses: {total_eth}")
    print(f"  └─ Labeled: {labeled_eth} ({labeled_eth/total_eth*100 if total_eth > 0 else 0:.1f}%)")
    print(f"📊 Total Addresses: {total_btc + total_eth}")
    print(f"🏷️ Total Labels: {labeled_btc + labeled_eth}")

def main():
    while True:
        print("\n🎯 Crypto Address Manager")
        print("=" * 30)
        print("1. 📋 List addresses")
        print("2. ➕ Add address")
        print("3. ➖ Remove address")
        print("4. 📊 Show statistics")
        print("5. 📄 Generate .env file")
        print("6. 🚪 Exit")
        
        choice = input("\nSelect option (1-6): ")
        
        if choice == '1':
            list_addresses()
        elif choice == '2':
            add_address_interactive()
        elif choice == '3':
            remove_address_interactive()
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            generate_env()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
