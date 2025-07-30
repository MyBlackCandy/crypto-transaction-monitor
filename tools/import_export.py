#!/usr/bin/env python3
"""Import/Export addresses between different formats"""

import json
import csv
import time
import sys
from typing import Dict, List

class AddressManager:
    def __init__(self):
        self.addresses = {'btc': [], 'eth': []}
        self.labels = {'btc': {}, 'eth': {}}
    
    def import_from_csv(self, csv_file: str):
        """Import addresses from CSV file"""
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                crypto_type = row['type'].lower()
                address = row['address'].strip()
                label = row.get('label', '').strip()
                
                if crypto_type in self.addresses and address:
                    self.addresses[crypto_type].append(address)
                    if label:
                        self.labels[crypto_type][address] = label
    
    def import_from_json(self, json_file: str):
        """Import addresses from JSON file"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.addresses = data.get('addresses', {'btc': [], 'eth': []})
        self.labels = data.get('labels', {'btc': {}, 'eth': {}})
    
    def import_from_env(self, env_file: str):
        """Import addresses from .env file"""
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    
                    if key == 'BTC_ADDRESSES':
                        self.addresses['btc'] = [addr.strip() for addr in value.split(',') if addr.strip()]
                    elif key == 'ETH_ADDRESSES':
                        self.addresses['eth'] = [addr.strip() for addr in value.split(',') if addr.strip()]
                    elif key == 'BTC_LABELS':
                        for pair in value.split(','):
                            if ':' in pair:
                                addr, label = pair.split(':', 1)
                                self.labels['btc'][addr.strip()] = label.strip()
                    elif key == 'ETH_LABELS':
                        for pair in value.split(','):
                            if ':' in pair:
                                addr, label = pair.split(':', 1)
                                self.labels['eth'][addr.strip()] = label.strip()
    
    def export_to_csv(self, csv_file: str):
        """Export addresses to CSV file"""
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['type', 'address', 'label'])
            
            for addr in self.addresses['btc']:
                label = self.labels['btc'].get(addr, '')
                writer.writerow(['btc', addr, label])
            
            for addr in self.addresses['eth']:
                label = self.labels['eth'].get(addr, '')
                writer.writerow(['eth', addr, label])
    
    def export_to_json(self, json_file: str):
        """Export addresses to JSON file"""
        data = {
            'addresses': self.addresses,
            'labels': self.labels,
            'metadata': {
                'total_btc': len(self.addresses['btc']),
                'total_eth': len(self.addresses['eth']),
                'export_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_to_env(self, env_file: str):
        """Export addresses to .env format"""
        btc_addresses = ','.join(self.addresses['btc'])
        eth_addresses = ','.join(self.addresses['eth'])
        
        btc_labels = ','.join([f"{addr}:{label}" for addr, label in self.labels['btc'].items()])
        eth_labels = ','.join([f"{addr}:{label}" for addr, label in self.labels['eth'].items()])
        
        content = f"""# Crypto Address Configuration
# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}

# BTC Addresses ({len(self.addresses['btc'])} total)
BTC_ADDRESSES={btc_addresses}

# ETH Addresses ({len(self.addresses['eth'])} total)
ETH_ADDRESSES={eth_addresses}

# Address Labels
BTC_LABELS={btc_labels}
ETH_LABELS={eth_labels}

# Alert Filtering
MINIMUM_USD_VALUE=2.0
IGNORE_DUST_TRANSACTIONS=true
"""
        
        with open(env_file, 'w') as f:
            f.write(content)
    
    def get_summary(self):
        """Get summary of addresses"""
        return {
            'btc_count': len(self.addresses['btc']),
            'eth_count': len(self.addresses['eth']),
            'btc_labeled': len(self.labels['btc']),
            'eth_labeled': len(self.labels['eth']),
            'total': len(self.addresses['btc']) + len(self.addresses['eth'])
        }

def main():
    if len(sys.argv) < 3:
        print("📊 Address Import/Export Tool")
        print("=" * 40)
        print("Usage:")
        print("  python import_export.py import <file>     # Import from file")
        print("  python import_export.py export <format>   # Export to format")
        print("  python import_export.py convert <in> <out> # Convert between formats")
        print("")
        print("Supported formats: csv, json, env")
        return
    
    manager = AddressManager()
    
    if sys.argv[1] == 'import':
        file_path = sys.argv[2]
        file_ext = file_path.split('.')[-1].lower()
        
        try:
            if file_ext == 'csv':
                manager.import_from_csv(file_path)
            elif file_ext == 'json':
                manager.import_from_json(file_path)
            elif file_ext == 'env':
                manager.import_from_env(file_path)
            else:
                print(f"❌ Unsupported file format: {file_ext}")
                return
            
            summary = manager.get_summary()
            print(f"✅ Imported {summary['total']} addresses")
            print(f"   ₿ BTC: {summary['btc_count']} ({summary['btc_labeled']} labeled)")
            print(f"   ⟠ ETH: {summary['eth_count']} ({summary['eth_labeled']} labeled)")
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    elif sys.argv[1] == 'export':
        if len(sys.argv) < 3:
            print("❌ Please specify export format (csv, json, env)")
            return
        
        # Load from environment first
        try:
            manager.import_from_env('.env')
        except:
            print("⚠️ No .env file found, using empty configuration")
        
        export_format = sys.argv[2].lower()
        output_file = f"addresses.{export_format}"
        
        try:
            if export_format == 'csv':
                manager.export_to_csv(output_file)
            elif export_format == 'json':
                manager.export_to_json(output_file)
            elif export_format == 'env':
                manager.export_to_env(output_file)
            else:
                print(f"❌ Unsupported export format: {export_format}")
                return
            
            summary = manager.get_summary()
            print(f"✅ Exported {summary['total']} addresses to {output_file}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    elif sys.argv[1] == 'convert':
        if len(sys.argv) < 4:
            print("❌ Please specify input and output files")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        input_ext = input_file.split('.')[-1].lower()
        output_ext = output_file.split('.')[-1].lower()
        
        try:
            # Import
            if input_ext == 'csv':
                manager.import_from_csv(input_file)
            elif input_ext == 'json':
                manager.import_from_json(input_file)
            elif input_ext == 'env':
                manager.import_from_env(input_file)
            
            # Export
            if output_ext == 'csv':
                manager.export_to_csv(output_file)
            elif output_ext == 'json':
                manager.export_to_json(output_file)
            elif output_ext == 'env':
                manager.export_to_env(output_file)
            
            summary = manager.get_summary()
            print(f"✅ Converted {summary['total']} addresses from {input_file} to {output_file}")
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
    
    else:
        print(f"❌ Unknown command: {sys.argv[1]}")

if __name__ == "__main__":
    main()
