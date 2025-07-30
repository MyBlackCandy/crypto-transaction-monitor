#!/usr/bin/env python3
"""Generate address configuration for Railway environment variables"""

import json
import csv
import sys

def load_addresses_from_csv(csv_file):
    """Load addresses from CSV file"""
    addresses = {'btc': [], 'eth': []}
    labels = {'btc': {}, 'eth': {}}
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            crypto_type = row['type'].lower()
            address = row['address'].strip()
            label = row.get('label', '').strip()
            
            if crypto_type in addresses and address:
                addresses[crypto_type].append(address)
                if label:
                    labels[crypto_type][address] = label
    
    return addresses, labels

def generate_env_format(addresses, labels):
    """Generate environment variable format"""
    
    # Generate address lists
    btc_addresses = ','.join(addresses['btc'])
    eth_addresses = ','.join(addresses['eth'])
    
    # Generate label lists
    btc_labels = ','.join([f"{addr}:{label}" for addr, label in labels['btc'].items()])
    eth_labels = ','.join([f"{addr}:{label}" for addr, label in labels['eth'].items()])
    
    env_content = f"""# Generated Address Configuration
# Total: {len(addresses['btc'])} BTC, {len(addresses['eth'])} ETH addresses

# BTC Addresses
BTC_ADDRESSES={btc_addresses}

# ETH Addresses  
ETH_ADDRESSES={eth_addresses}

# Address Labels
BTC_LABELS={btc_labels}
ETH_LABELS={eth_labels}

# Alert Filtering
MINIMUM_USD_VALUE=2.0
IGNORE_DUST_TRANSACTIONS=true
"""
    
    return env_content

def create_sample_csv():
    """Create sample CSV file"""
    sample_data = [
        ['type', 'address', 'label'],
        ['btc', '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'Genesis Block'],
        ['btc', '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', 'Exchange Wallet'],
        ['btc', 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', 'Segwit Address'],
        ['eth', '0x742dDA7632C3d39f88c93c1271eB20B49C6C97b8', 'Main Wallet'],
        ['eth', '0xA0b86991c420AcB6EdDc9E4d30D4f1B2F1C8B62', 'USDC Contract'],
        ['eth', '0xdAC17F958D2ee523a2206206994597C13D831ec7', 'USDT Contract'],
    ]
    
    with open('addresses_sample.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)
    
    print("✅ Sample CSV created: addresses_sample.csv")

def main():
    if len(sys.argv) < 2:
        print("📋 Address Configuration Generator")
        print("=" * 40)
        print("Usage:")
        print("  python generate_addresses.py sample         # Create sample CSV")
        print("  python generate_addresses.py <csv_file>     # Generate from CSV")
        print("")
        print("CSV Format: type,address,label")
        print("Types: btc, eth")
        return
    
    if sys.argv[1] == 'sample':
        create_sample_csv()
        return
    
    csv_file = sys.argv[1]
    
    try:
        addresses, labels = load_addresses_from_csv(csv_file)
        env_content = generate_env_format(addresses, labels)
        
        # Write to file
        output_file = 'addresses.env'
        with open(output_file, 'w') as f:
            f.write(env_content)
        
        # Display summary
        print("📊 Address Configuration Generated")
        print("=" * 40)
        print(f"₿ BTC Addresses: {len(addresses['btc'])}")
        print(f"⟠ ETH Addresses: {len(addresses['eth'])}")
        print(f"🏷️ BTC Labels: {len(labels['btc'])}")
        print(f"🏷️ ETH Labels: {len(labels['eth'])}")
        print(f"📁 Output file: {output_file}")
        print("")
        print("Copy the content to Railway environment variables:")
        print(env_content[:200] + "..." if len(env_content) > 200 else env_content)
        
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
