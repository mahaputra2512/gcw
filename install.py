#!/usr/bin/env python3
"""
Twitter Hoax Detector - Smart Installer
=======================================

Script instalasi yang handle dependencies secara bertahap
dengan error handling untuk menghindari masalah kompatibilitas.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description=""):
    """Run command dengan error handling"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - Berhasil")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Gagal: {e.stderr}")
        return False

def install_package(package, description=""):
    """Install single package dengan error handling"""
    return run_command(f"pip install {package}", description or f"Installing {package}")

def check_python_version():
    """Cek versi Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ diperlukan!")
        print(f"   Versi saat ini: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def create_directories():
    """Buat direktori yang diperlukan"""
    directories = [
        "reports",
        "visualizations",
        "static", 
        "templates",
        "logs",
        "app/services"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Direktori dibuat")

def install_core_dependencies():
    """Install dependencies inti"""
    core_packages = [
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("requests", "HTTP client"),
        ("python-dotenv", "Environment variables")
    ]
    
    print("\n📦 Installing Core Dependencies...")
    success_count = 0
    
    for package, desc in core_packages:
        if install_package(package, desc):
            success_count += 1
    
    return success_count == len(core_packages)

def install_ai_dependencies():
    """Install AI/ML dependencies"""
    ai_packages = [
        ("openai", "OpenAI API client"),
        ("networkx", "Network analysis"),
        ("pandas", "Data processing")
    ]
    
    print("\n🧠 Installing AI Dependencies...")
    success_count = 0
    
    for package, desc in ai_packages:
        if install_package(package, desc):
            success_count += 1
    
    return success_count >= 2  # Minimal 2 dari 3

def install_optional_dependencies():
    """Install dependencies opsional dengan fallback"""
    optional_packages = [
        ("matplotlib", "Plotting library"),
        ("plotly", "Interactive plots"),
        ("seaborn", "Statistical visualization"),
        ("reportlab", "PDF generation"),
        ("python-telegram-bot", "Telegram bot"),
        ("tweepy", "Twitter API"),
        ("pyvis", "Network visualization"),
        ("python-louvain", "Community detection")
    ]
    
    print("\n🎨 Installing Optional Dependencies...")
    installed = []
    failed = []
    
    for package, desc in optional_packages:
        if install_package(package, desc):
            installed.append(package)
        else:
            failed.append(package)
            print(f"⚠️  {package} gagal diinstall - akan menggunakan fallback")
    
    print(f"\n✅ Berhasil: {len(installed)}/{len(optional_packages)} optional packages")
    if failed:
        print(f"⚠️  Gagal: {', '.join(failed)}")
    
    return len(installed) >= len(optional_packages) // 2

def install_system_dependencies():
    """Install system dependencies jika perlu"""
    system = platform.system().lower()
    
    if system == "linux":
        print("\n🐧 Mendeteksi Linux - install system packages...")
        system_packages = [
            "sudo apt-get update",
            "sudo apt-get install -y python3-dev",
            "sudo apt-get install -y build-essential"
        ]
        
        for cmd in system_packages:
            run_command(cmd, f"System package: {cmd.split()[-1]}")
    
    elif system == "darwin":  # macOS
        print("\n🍎 Mendeteksi macOS - checking Xcode tools...")
        run_command("xcode-select --install", "Xcode command line tools")
    
    else:
        print(f"\n💻 Mendeteksi {system} - manual system setup mungkin diperlukan")

def create_config_files():
    """Buat file konfigurasi jika belum ada"""
    
    # .env file
    if not os.path.exists(".env"):
        env_content = """# Twitter Hoax Detector Configuration
DEBUG=true
OPENAI_API_KEY=your-openai-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ File .env dibuat")
    
    # app/__init__.py
    os.makedirs("app", exist_ok=True)
    if not os.path.exists("app/__init__.py"):
        with open("app/__init__.py", "w") as f:
            f.write("")
    
    if not os.path.exists("app/services/__init__.py"):
        with open("app/services/__init__.py", "w") as f:
            f.write("")
    
    print("✅ File konfigurasi dibuat")

def test_installation():
    """Test instalasi dengan import basic modules"""
    print("\n🧪 Testing Installation...")
    
    test_imports = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("requests", "HTTP client")
    ]
    
    success = True
    for module, desc in test_imports:
        try:
            __import__(module)
            print(f"✅ {desc} - OK")
        except ImportError:
            print(f"❌ {desc} - GAGAL")
            success = False
    
    return success

def main():
    """Main installer function"""
    print("🚀 Twitter Hoax Detector - Smart Installer")
    print("=" * 50)
    
    # 1. Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # 2. Upgrade pip
    print("\n📦 Upgrading pip...")
    run_command("pip install --upgrade pip", "Pip upgrade")
    
    # 3. Create directories
    create_directories()
    
    # 4. Install core dependencies
    if not install_core_dependencies():
        print("❌ Core dependencies installation failed!")
        sys.exit(1)
    
    # 5. Install AI dependencies
    if not install_ai_dependencies():
        print("⚠️  Some AI dependencies failed - continuing with available packages")
    
    # 6. Install optional dependencies
    install_optional_dependencies()
    
    # 7. Create config files
    create_config_files()
    
    # 8. Test installation
    if test_installation():
        print("\n🎉 Installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file dengan API keys Anda")
        print("2. Jalankan: python run.py both")
        print("3. Akses: http://localhost:8000")
    else:
        print("\n⚠️  Installation completed with some issues")
        print("   Aplikasi mungkin tetap bisa jalan dengan fitur terbatas")
    
    print("\n📚 Dokumentasi: README.md")
    print("🐛 Issues: https://github.com/your-repo/issues")

if __name__ == "__main__":
    main() 