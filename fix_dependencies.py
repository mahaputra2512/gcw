#!/usr/bin/env python3
"""
Script untuk memperbaiki konflik dependencies
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error: {description}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🔧 Memperbaiki dependency conflicts...")
    
    # Commands untuk memperbaiki dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip uninstall -y crawl4ai litellm", "Uninstalling conflicting packages"),
        ("pip install --upgrade aiofiles>=24.1.0", "Upgrading aiofiles"),
        ("pip install --upgrade httpx>=0.27.2", "Upgrading httpx"),
        ("pip install --upgrade pillow~=10.4", "Upgrading pillow"),
        ("pip install --upgrade pydantic>=2.10", "Upgrading pydantic"),
        ("pip install --upgrade openai>=1.66.1", "Upgrading openai"),
        ("pip install -r requirements.txt", "Installing all requirements"),
    ]
    
    print("📋 Akan menjalankan perintah berikut:")
    for cmd, desc in commands:
        print(f"  - {desc}: {cmd}")
    
    response = input("\n⚠️  Lanjutkan? (y/n): ")
    if response.lower() != 'y':
        print("❌ Dibatalkan oleh pengguna")
        return
    
    # Execute commands
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"❌ Gagal pada: {desc}")
            print("💡 Coba jalankan perintah secara manual:")
            print(f"   {cmd}")
            break
    else:
        print("\n🎉 Semua dependencies berhasil diperbaiki!")
        print("\n📋 Langkah selanjutnya:")
        print("1. Jalankan: python run.py --mode web")
        print("2. Buka browser: http://localhost:8000")
        print("3. Atau jalankan telegram bot: python run.py --mode telegram")

if __name__ == "__main__":
    main() 