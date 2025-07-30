#!/usr/bin/env python3
"""Bulk operations for managing large numbers of addresses"""

import requests
import time
import os
import sys
from datetime import datetime

class BulkAddressOperations:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoMonitor/1.0'
        })
    
    def check_btc_balances(self, addresses, batch_size=10):
        """Check BTC balances for multiple addresses"""
        results = {}
        
        print(f"🔍 Checking {len(addresses)} BTC addresses...")
        
        # Process in batches to avoid rate limiting
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i+batch_size]
            batch_results = self._check_btc_batch(batch)
            results.update(batch_results)
            
            print(f"⏳ Progress: {min(i+batch_size, len(addresses))}/{len(addresses)}")
            time.sleep(1)  # Rate limiting
        
        return results
    
    def _check_btc_batch(self, addresses):
        """Check BTC balances for a batch of addresses"""
        results = {}
        
        for address in addresses:
            try:
                url = f"https://blockchain.info/rawaddr/{address}?limit=0"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results[address] = {
                        'balance': data.get('final_balance', 0) / 100000000,  # Convert to BTC
                        'tx_count': data.get('n_tx', 0),
                        'total_received': data.get('total_received', 0) / 100000000,
                        'total_sent': data.get('total_sent', 0) / 100000000,
                        'status': 'success'
                    }
                else:
                    results[address] = {'status': 'error', 'message': f"HTTP {response.status_code}"}
                    
            except Exception as e:
                results[address] = {'status': 'error', 'message': str(e)}
        
        return results
    
    def generate_balance_report(self, addresses, crypto_type='btc'):
        """Generate balance report for addresses"""
        print(f"📊 Generating {crypto_type.upper()} balance report...")
        
        if crypto_type == 'btc':
            results = self.check_btc_balances(addresses)
        else:
            print("⚠️ ETH balance checking not implemented yet")
            return []
        
        # Calculate totals
        total_balance = 0
        total_tx_count = 0
        active_addresses = 0
        
        report_data = []
        
        for address, data in results.items():
            if data.get('status') == 'success':
                balance = data.get('balance', 0)
                tx_count = data.get('tx_count', 0)
                
                if balance > 0:
                    active_addresses += 1
                
                total_balance += balance
                total_tx_count += tx_count
                
                report_data.append({
                    'address': address,
                    'balance': balance,
                    'tx_count': tx_count,
                    'status': 'active' if balance > 0 else 'empty'
                })
            else:
                report_data.append({
                    'address': address,
                    'balance': 0,
                    'tx_count': 0,
                    'status': 'error',
                    'error': data.get('message', 'Unknown error')
                })
        
        # Sort by balance (highest first)
        report_data.sort(key=lambda x: x.get('balance', 0), reverse=True)
        
        # Print report
        print(f"\n📈 {crypto_type.upper()} Balance Report")
        print("=" * 60)
        print(f"Total Addresses: {len(addresses)}")
        print(f"Active Addresses: {active_addresses}")
        print(f"Total Balance: {total_balance:.8f} {crypto_type.upper()}")
        print(f"Total Transactions: {total_tx_count}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📋 Top 10 Addresses by Balance:")
        print("-" * 60)
        
        for i, addr_data in enumerate(report_data[:10]):
            address = addr_data['address']
            balance = addr_data['balance']
            status = addr_data['status']
            
            short_addr = f"{address[:8]}...{address[-6:]}"
            
            if status == 'error':
                print(f"{i+1:2d}. {short_addr} - ERROR: {addr_data.get('error', 'Unknown')}")
            else:
                print(f"{i+1:2d}. {short_addr} - {balance:.8f} {crypto_type.upper()} ({status})")
        
        return report_data
    
    def find_zero_balance_addresses(self, addresses, crypto_type='btc'):
        """Find addresses with zero balance"""
        print(f"🔍 Finding zero balance {crypto_type.upper()} addresses...")
        
        if crypto_type == 'btc':
            results = self.check_btc_balances(addresses)
        else:
            print("⚠️ ETH balance checking not implemented yet")
            return []
        
        zero_balance = []
        
        for address, data in results.items():
            if data.get('status') == 'success' and data.get('balance', 0) == 0:
                zero_balance.append(address)
        
        print(f"Found {len(zero_balance)} addresses with zero balance:")
        for addr in zero_balance[:20]:  # Show first 20
            short_addr = f"{addr[:8]}...{addr[-6:]}"
            print(f"  • {short_addr}")
        
        if len(zero_balance) > 20:
            print(f"  ... and {len(zero_balance) - 20} more")
        
        return zero_balance

def main():
    if len(sys.argv) < 2:
        print("🔧 Bulk Address Operations")
        print("=" * 40)
        print("Commands:")
        print("  python bulk_operations.py balance btc    # Check BTC balances")
        print("  python bulk_operations.py balance eth    # Check ETH balances")
        print("  python bulk_operations.py zero btc       # Find zero balance BTC")
        print("  python bulk_operations.py zero eth       # Find zero balance ETH")
        print("  python bulk_operations.py report         # Generate full report")
        return
    
    ops = BulkAddressOperations()
    
    # Load addresses from environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file")
    except ImportError:
        print("💡 Install python-dotenv: pip install python-dotenv")
    except:
        print("⚠️ No .env file found, using system environment")
    
    btc_addresses = os.getenv('BTC_ADDRESSES', '').split(',')
    btc_addresses = [addr.strip() for addr in btc_addresses if addr.strip()]
    
    eth_addresses = os.getenv('ETH_ADDRESSES', '').split(',')
    eth_addresses = [addr.strip() for addr in eth_addresses if addr.strip()]
    
    if sys.argv[1] == 'balance':
        if len(sys.argv) < 3:
            print("❌ Please specify crypto type (btc/eth)")
            return
        
        crypto_type = sys.argv[2].lower()
        addresses = btc_addresses if crypto_type == 'btc' else eth_addresses
        
        if not addresses:
            print(f"❌ No {crypto_type.upper()} addresses found in environment")
            return
        
        ops.generate_balance_report(addresses, crypto_type)
    
    elif sys.argv[1] == 'zero':
        if len(sys.argv) < 3:
            print("❌ Please specify crypto type (btc/eth)")
            return
        
        crypto_type = sys.argv[2].lower()
        addresses = btc_addresses if crypto_type == 'btc' else eth_addresses
        
        if not addresses:
            print(f"❌ No {crypto_type.upper()} addresses found in environment")
            return
        
        ops.find_zero_balance_addresses(addresses, crypto_type)
    
    elif sys.argv[1] == 'report':
        print("📊 Generating Complete Balance Report")
        print("=" * 50)
        
        if btc_addresses:
            ops.generate_balance_report(btc_addresses, 'btc')
        
        if eth_addresses:
            print("\n⚠️ ETH balance checking not implemented yet")
    
    else:
        print(f"❌ Unknown command: {sys.argv[1]}")

if __name__ == "__main__":
    main()
