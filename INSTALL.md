# 🚀 Panduan Instalasi - Twitter Hoax Detector

## 📋 Prasyarat
- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- Git (optional, untuk clone repository)

## 📦 Opsi Instalasi

### Opsi 1: Instalasi Otomatis (Recommended)
```bash
python install.py
```

### Opsi 2: Instalasi Manual
```bash
# Instal dependencies minimum
pip install -r requirements-minimal.txt

# Atau instal semua dependencies
pip install -r requirements.txt
```

### Opsi 3: Menggunakan Script
**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

### Opsi 4: Fix Dependency Conflicts ⚠️
Jika mengalami konflik dependencies (seperti crawl4ai, litellm):
```bash
python fix_dependencies.py
```

Script ini akan:
- Menghapus packages yang konflik
- Mengupgrade dependencies ke versi yang kompatibel
- Menginstal ulang semua requirements

## 🔧 Troubleshooting

### 1. Error "Could not find a version that satisfies the requirement sqlite3"
**Solusi:** sqlite3 adalah built-in module Python, hapus dari requirements.txt

### 2. Dependency Conflicts
**Gejala:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
crawl4ai 0.5.0.post4 requires aiofiles>=24.1.0, but you have aiofiles 23.2.1
```

**Solusi:**
```bash
python fix_dependencies.py
```

### 3. Telegram Bot Token Error
**Gejala:**
```
ERROR: TELEGRAM_BOT_TOKEN not found in config!
```

**Solusi:** Token sudah diatur di `app/config.py`

### 4. FastAPI Reload Warning
**Gejala:**
```
WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.
```

**Solusi:** Gunakan `run.py` yang sudah diperbaiki

### 5. ModuleNotFoundError
**Solusi:**
```bash
# Instal package yang hilang
pip install [package_name]

# Atau instal ulang semua requirements
pip install -r requirements.txt --force-reinstall
```

### 6. Permission Denied (Linux/macOS)
**Solusi:**
```bash
# Gunakan virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate     # Windows

# Atau instal dengan user flag
pip install --user -r requirements.txt
```

### 7. SSL Certificate Error
**Solusi:**
```bash
# Upgrade pip dan certificates
pip install --upgrade pip
pip install --upgrade certifi
```

## 🏃 Cara Menjalankan

### 1. Web Server
```bash
python run.py --mode web
```
Buka browser: http://localhost:8000

### 2. Telegram Bot
```bash
python run.py --mode telegram
```

### 3. Both (Web + Telegram)
```bash
python run.py --mode both
```

## 🔍 Verifikasi Instalasi

### Test Database
```bash
python -c "from app.database import init_db; init_db(); print('Database OK')"
```

### Test Dependencies
```bash
python -c "import fastapi, uvicorn, openai, telegram; print('Dependencies OK')"
```

### Test API Keys
```bash
python -c "from app.config import Config; print('OpenAI:', bool(Config.OPENAI_API_KEY)); print('Telegram:', bool(Config.TELEGRAM_BOT_TOKEN))"
```

## 🐳 Docker (Alternative)

### Build Image
```bash
docker build -t hoax-detector .
```

### Run Container
```bash
docker run -p 8000:8000 hoax-detector
```

## 🆘 Jika Masih Bermasalah

1. **Buat Virtual Environment Baru:**
```bash
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/macOS
# atau
fresh_env\Scripts\activate     # Windows

pip install -r requirements-minimal.txt
```

2. **Instal Satu per Satu:**
```bash
pip install fastapi uvicorn
pip install sqlalchemy
pip install openai
pip install python-telegram-bot
# dst...
```

3. **Cek Versi Python:**
```bash
python --version
# Pastikan Python 3.8+
```

4. **Reset Cache pip:**
```bash
pip cache purge
```

5. **Hubungi Developer:**
- Buat issue di GitHub repository
- Sertakan error message lengkap
- Sertakan informasi sistem (OS, Python version)

## 📚 Referensi
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Telegram Bot](https://python-telegram-bot.org/)
- [OpenAI API](https://platform.openai.com/docs/) 