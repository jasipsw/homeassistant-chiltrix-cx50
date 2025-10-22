#!/usr/bin/env python3
"""
Chiltrix CX50 Register Scanner
This diagnostic tool scans Modbus registers to find which addresses work.
Run this from the command line to identify working registers for your device.

Usage:
    python3 register_scanner.py <IP_ADDRESS>
    
Example:
    python3 register_scanner.py 192.168.1.100
"""

import sys
import asyncio
from pymodbus.client import ModbusTcpClient

async def scan_registers(host, port=502, slave_id=1):
    """Scan common register ranges to find working addresses."""
    
    print(f"Connecting to {host}:{port} (slave_id={slave_id})...")
    client = ModbusTcpClient(host=host, port=port, timeout=5)
    
    if not client.connect():
        print("ERROR: Failed to connect!")
        return
    
    print("Connected successfully!\n")
    print("Scanning registers...\n")
    print("-" * 80)
    
    # Define ranges to scan based on typical heat pump implementations
    scan_ranges = [
        (0x00, 0x10, "Control registers"),
        (0xCA, 0xD8, "Temperature registers"),
        (0xF0, 0xF8, "Status registers"),
        (0x100, 0x120, "Performance registers"),
    ]
    
    working_registers = []
    
    for start, end, description in scan_ranges:
        print(f"\nScanning {description} (0x{start:X}-0x{end:X}):")
        print("-" * 80)
        
        for address in range(start, end + 1):
            try:
                result = client.read_holding_registers(address, 1, slave_id)
                
                if not result.isError():
                    value = result.registers[0]
                    print(f"✓ 0x{address:03X} ({address:3d}): {value:5d} (0x{value:04X})")
                    working_registers.append((address, value))
                else:
                    error_code = getattr(result, 'exception_code', '?')
                    print(f"✗ 0x{address:03X} ({address:3d}): Error (exception code: {error_code})")
                    
            except Exception as e:
                print(f"✗ 0x{address:03X} ({address:3d}): Exception - {e}")
            
            # Small delay to avoid overwhelming the device
            await asyncio.sleep(0.1)
    
    client.close()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - Working Registers:")
    print("=" * 80)
    
    if working_registers:
        print(f"\nFound {len(working_registers)} working registers:\n")
        for addr, value in working_registers:
            print(f"  Register 0x{addr:03X} ({addr:3d}): {value}")
        
        print("\n" + "-" * 80)
        print("Copy these addresses into your const.py file:")
        print("-" * 80)
        for addr, _ in working_registers:
            print(f"REGISTER_UNKNOWN_0x{addr:03X} = 0x{addr:X}  # {addr}")
    else:
        print("\nNo working registers found!")
        print("Possible issues:")
        print("  - Wrong slave ID (try 0, 1, or 2)")
        print("  - Device not responding")
        print("  - Incorrect IP address")
        print("  - RS485 wiring issue")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 register_scanner.py <IP_ADDRESS> [PORT] [SLAVE_ID]")
        print("Example: python3 register_scanner.py 192.168.1.100")
        print("Example: python3 register_scanner.py 192.168.1.100 502 1")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    slave_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    asyncio.run(scan_registers(host, port, slave_id))

if __name__ == "__main__":
    main()
