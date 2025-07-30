#!/usr/bin/env python3
"""Validate crypto addresses before deployment"""

import re
import requests
import time
import os
import sys

def validate_btc_address(address):
    """Validate BTC address format"""
    if not address:
        return False, "Empty address"
    
    # Legacy P2PKH (starts with 1)
    if address.startswith('1'):
        if len(address) < 26 or len(address) > 35:
            return False, "Invalid P2PKH length"
    
    # Script P2SH (starts with 3)
    elif address.startswith('3'):
        if len(address) < 26 or len(address) > 35:
            return False, "Invalid P2SH length"
    
    # Bech32 Segwit (starts with bc1)
    elif address.startswith('bc1'):
        if len(address) < 42 or len(address) > 62:
            return False, "Invalid Bech32 length"
    
    # Testnet addresses
    elif address.startswith(('m', 'n', '2', 'tb1')):
        return False, "Testnet address not allowed"
    
    else:
        return False, "Unknown address format"
    
    return True, "Valid format"

def validate_eth_address(address):
    """Validate ETH address format"""
    if not address:
        return False, "Empty address"
    
    if not address.startswith('0x'):
        return False, "Must start with 0x"
    
    if len(address) != 42:
        return False, "Must be 42 characters long"
    
    # Check hex format
    try:
        int(address[2:], 16)
    except ValueError:
        return False, "Contains invalid hex characters"
    
    return True, "Valid format"

def validate_from_env():
    """Validate addresses from environment variables"""
    
    btc_addresses = os.getenv('BTC_ADDRESSES', '').split(',')
    btc_addresses = [addr.strip() for addr in btc_addresses if addr.strip()]
    
    eth_addresses = os.getenv('ETH_ADDRESSES', '').split(',')
    eth_addresses = [addr.strip() for addr in eth_addresses if addr.strip()]
    
    print("🔍 Validating Addresses from Environment")
    print("=" * 50)
    
    all_valid = True
    
    # Validate BTC addresses
    if btc_addresses:
        print(f"\n₿ Validating {len(btc_addresses)} BTC addresses...")
        
        valid_count = 0
        for addr in btc_addresses:
            is_valid, message = validate_btc_address(addr)
            status = "✅" if is_valid else "❌"
            short_addr = f"{addr[:10]}...{addr[-8:]}"
            print(f"  {status} {short_addr}: {message}")
            
            if is_valid:
                valid_count += 1
            else:
                all_valid = False
        
        print(f"✅ Valid: {valid_count}/{len(btc_addresses)}")
    
    # Validate ETH addresses
    if eth_addresses:
        print(f"\n⟠ Validating {len(eth_addresses)} ETH addresses...")
        
        valid_count = 0
        for addr in eth_addresses:
            is_valid, message = validate_eth_address(addr)
            status = "✅" if is_valid else "❌"
            short_addr = f"{addr[:10]}...{addr[-8:]}"
            print(f"  {status} {short_addr}: {message}")
            
            if is_valid:
                valid_count += 1
            else:
                all_valid = False
        
        print(f"✅ Valid: {valid_count}/{len(eth_addresses)}")
    
    # Validate filtering settings
    min_usd = os.getenv('MINIMUM_USD_VALUE', '2.0')
    try:
        min_val = float(min_usd)
        print(f"\n💰 Minimum USD Value: ${min_val} ✅")
    except ValueError:
        print(f"\n💰 Minimum USD Value: Invalid ({min_usd}) ❌")
        all_valid = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All addresses and settings are valid!")
        print("✅ Ready for deployment!")
        return True
    else:
        print("⚠️ Some addresses or settings have issues.")
        print("🛑 Please fix before deployment.")
        return False

def main():
    if len(sys.argv) < 2:
        print("🔍 Address Validator")
        print("=" * 30)
        print("Usage:")
        print("  python validate_addresses.py env           # Validate from env vars")
        print("  python validate_addresses.py btc <addr>    # Validate single BTC")
        print("  python validate_addresses.py eth <addr>    # Validate single ETH")
        return
    
    if sys.argv[1] == 'env':
        # Load from .env file if exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("📄 Loaded .env file")
        except ImportError:
            print("💡 Install python-dotenv: pip install python-dotenv")
        except:
            print("⚠️ No .env file found, using system environment")
        
        validate_from_env()
        
    elif sys.argv[1] == 'btc' and len(sys.argv) > 2:
        address = sys.argv[2]
        is_valid, message = validate_btc_address(address)
        status = "✅" if is_valid else "❌"
        print(f"{status} {address}: {message}")
        
    elif sys.argv[1] == 'eth' and len(sys.argv) > 2:
        address = sys.argv[2]
        is_valid, message = validate_eth_address(address)
        status = "✅" if is_valid else "❌"
        print(f"{status} {address}: {message}")
        
    else:
        print("❌ Invalid arguments")

if __name__ == "__main__":
    main()
