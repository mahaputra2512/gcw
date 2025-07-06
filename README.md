# 🔍 Twitter Hoax Detector

Sistem deteksi hoax otomatis berbasis AI untuk platform Twitter dengan fitur analisis jaringan, bot detection, dan reporting yang komprehensif.

## 📋 Fitur Utama

### 🧠 Analisis Hoax dengan AI
- **OpenAI GPT Integration**: Analisis konten menggunakan model AI terdepan
- **Multi-kategori Detection**: Politik, kesehatan, bencana, celebrity, finansial, konspirasi
- **Confidence Scoring**: Probabilitas dan tingkat kepercayaan hasil analisis
- **Contextual Analysis**: Mempertimbangkan metadata tweet dan user

### 🤖 Bot Detection
- **User Behavior Analysis**: Analisis pola posting, rasio follower/following
- **Account Metrics**: Umur akun, kelengkapan profil, verifikasi status
- **Pattern Recognition**: Deteksi username dan bio patterns yang mencurigakan
- **Risk Assessment**: Skor risiko dan penjelasan faktor-faktor

### 🔍 Fact-Checking
- **Brave Search Integration**: Pencarian web otomatis untuk verifikasi
- **Source Credibility**: Evaluasi kredibilitas sumber informasi
- **Cross-referencing**: Membandingkan dengan sumber-sumber terpercaya
- **Supporting vs Contradicting**: Analisis sumber yang mendukung vs bertentangan

### 📊 Network Analysis
- **Graph Visualization**: Visualisasi jaringan penyebaran tweet
- **Influence Scoring**: Skor pengaruh dan jangkauan
- **Community Detection**: Identifikasi cluster dan echo chamber
- **Spread Pattern Analysis**: Analisis pola viral dan bot-driven spread

### 📄 Comprehensive Reporting
- **PDF Reports**: Laporan lengkap dalam format PDF
- **Interactive Dashboard**: Web interface dengan charts dan visualisasi
- **Export Options**: CSV, Excel, PDF formats
- **Historical Analytics**: Trend dan statistik dari waktu ke waktu

### 💬 Telegram Bot Integration
- **Mobile Access**: Akses mudah melalui Telegram
- **Real-time Notifications**: Update status analisis
- **File Sharing**: Download laporan PDF langsung
- **Personal Statistics**: Tracking usage personal

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### ⚡ Automatic Installation (Recommended)

#### Linux/macOS:
```bash
git clone https://github.com/your-repo/twitter-hoax-detector.git
cd twitter-hoax-detector
chmod +x setup.sh
./setup.sh
```

#### Windows:
```cmd
git clone https://github.com/your-repo/twitter-hoax-detector.git
cd twitter-hoax-detector
setup.bat
```

#### Python Script (All platforms):
```bash
git clone https://github.com/your-repo/twitter-hoax-detector.git
cd twitter-hoax-detector
python install.py
```

### 🛠️ Manual Installation

1. **Clone Repository**
```bash
git clone https://github.com/your-repo/twitter-hoax-detector.git
cd twitter-hoax-detector
```

2. **Create Virtual Environment (Recommended)**
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate.bat
```

3. **Install Dependencies**

**Option A: Minimal Installation (If having issues)**
```bash
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

**Option B: Full Installation**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you get error "sqlite3 not found", ignore it - SQLite3 is built into Python.

4. **Create Configuration**
```bash
# Copy and edit configuration
cp .env.example .env
# Edit .env with your API keys
```

5. **Run Application**
```bash
# Jalankan web server dan telegram bot
python run.py both

# Atau jalankan salah satu saja
python run.py web        # Web server only
python run.py telegram   # Telegram bot only
```

6. **Access Dashboard**
- Web Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 🔧 Troubleshooting Installation

#### Common Issues:

**1. SQLite3 Error:**
```
ERROR: Could not find a version that satisfies the requirement sqlite3
```
**Solution:** SQLite3 is built into Python. Remove it from requirements.txt or ignore the error.

**2. Matplotlib/Plotly Issues:**
```bash
# Install system dependencies first (Linux)
sudo apt-get install python3-dev python3-tk

# macOS
brew install python-tk

# Then install minimal version
pip install matplotlib --no-deps
```

**3. ReportLab Issues:**
```bash
# Alternative lightweight PDF
pip install fpdf2
# App will automatically fallback
```

**4. Kaleido Issues (Plotly export):**
```bash
# Skip kaleido for now
pip install plotly --no-deps
# Visualizations will still work in browser
```

**5. Python Version Issues:**
Check your Python version:
```bash
python --version  # Should be 3.8+
python3 --version # Try python3 if python fails
```

#### Minimal Working Setup:
If you just want to test the core functionality:
```bash
pip install fastapi uvicorn sqlalchemy pydantic requests openai
python run.py web
```

## 🔧 Konfigurasi

### 🔐 Security Configuration (PENTING!)

**⚠️ JANGAN PERNAH commit kredensial API ke GitHub!**

1. **Salin file template:**
```bash
cp env.example .env
```

2. **Edit file .env dengan kredensial Anda:**
```env
# OpenAI API
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Twitter API (opsional untuk production)
TWITTER_API_KEY=your-twitter-api-key-here
TWITTER_API_SECRET=your-twitter-api-secret-here
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here

# Brave Search API
BRAVE_SEARCH_API_KEY=your-brave-search-api-key-here

# Telegram Bot (opsional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
```

3. **Baca panduan lengkap:** [SECURITY.md](SECURITY.md)

### 🧹 Membersihkan Repository

Sebelum commit ke GitHub, jalankan:
```bash
python clean_repository.py
```

Script ini akan menghapus:
- File database (*.db)
- File .env
- Log files
- __pycache__ directories
- File-file sensitif lainnya

### Environment Variables
```bash
export OPENAI_API_KEY="your-key"
export TELEGRAM_BOT_TOKEN="your-token"
# ... other keys
```

## 📱 Telegram Bot

### Setup
1. Buat bot baru dengan @BotFather di Telegram
2. Dapatkan bot token
3. Set token di `config.py`
4. Jalankan: `python run.py telegram`

### Commands
- `/start` - Mulai menggunakan bot
- `/analyze` - Analisis tweet baru
- `/status` - Cek status analisis
- `/history` - Lihat riwayat analisis
- `/stats` - Statistik personal
- `/help` - Bantuan

### Usage
1. Kirim URL tweet ke bot
2. Bot akan memproses dan memberikan hasil
3. Download laporan PDF
4. Lihat visualisasi jaringan

## 🌐 Web Dashboard

### Main Features
- **Dashboard**: Statistik dan quick analysis
- **Analysis Page**: Form analisis lengkap dengan progress tracking
- **History**: Riwayat analisis dengan filtering dan search
- **API Docs**: Dokumentasi API interaktif

### API Endpoints

#### Analysis
```http
POST /api/analyze
Content-Type: application/form-data

{
  "tweet_url": "https://twitter.com/user/status/123456789"
}
```

#### Get Status
```http
GET /api/status/{session_id}
```

#### Get Results
```http
GET /api/result/{session_id}
```

#### Download PDF
```http
GET /api/download/pdf/{session_id}
```

#### Statistics
```http
GET /api/statistics
```

## 🏗️ Architecture

### Directory Structure
```
twitter-hoax-detector/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Database models
│   ├── database.py          # Database setup
│   ├── telegram_bot.py      # Telegram bot
│   └── services/
│       ├── twitter_service.py      # Twitter API integration
│       ├── openai_service.py       # OpenAI integration
│       ├── brave_search_service.py # Brave Search integration
│       ├── bot_detection_service.py # Bot detection logic
│       ├── network_analysis_service.py # Network analysis
│       └── pdf_service.py          # PDF generation
├── templates/               # HTML templates
├── static/                 # Static files
├── reports/                # Generated PDF reports
├── visualizations/         # Network visualizations
├── requirements.txt        # Dependencies
├── run.py                 # Main runner
└── README.md              # This file
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI/ML**: OpenAI GPT, NetworkX, scikit-learn
- **Visualization**: Plotly, Matplotlib, PyVis
- **PDF**: ReportLab
- **Bot**: python-telegram-bot
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite (production: PostgreSQL/MySQL)

## 📊 Data Flow

1. **Input**: User submits Twitter URL
2. **Extraction**: Tweet and user data extraction
3. **AI Analysis**: OpenAI analyzes content for hoax probability
4. **Bot Detection**: Analyze user metrics and patterns
5. **Fact-Checking**: Search web for supporting/contradicting sources
6. **Network Analysis**: Build and analyze spread network
7. **Visualization**: Generate network graphs
8. **Reporting**: Create comprehensive PDF report
9. **Storage**: Save results to database
10. **Delivery**: Present results via web/telegram

## 🔬 Analysis Methods

### Hoax Detection
- **Content Analysis**: Keyword matching, sentiment analysis
- **Source Verification**: Cross-reference with fact-checking sites
- **Linguistic Patterns**: Detection of misleading language
- **Temporal Analysis**: Posting time patterns

### Bot Detection
- **Account Metrics**: Age, followers, following ratios
- **Posting Patterns**: Frequency, timing, content similarity
- **Profile Analysis**: Bio patterns, profile completeness
- **Network Behavior**: Interaction patterns

### Network Analysis
- **Graph Construction**: Build interaction network
- **Centrality Measures**: Identify influential nodes
- **Community Detection**: Find clusters and echo chambers
- **Spread Modeling**: Analyze information propagation

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Coverage
```bash
pytest --cov=app tests/
```

### Manual Testing
1. Test dengan berbagai URL Twitter
2. Verifikasi hasil analisis
3. Check PDF generation
4. Test Telegram bot commands

## 📈 Performance

### Optimization Tips
- Use Redis for caching (production)
- Enable database connection pooling
- Implement async processing for heavy tasks
- Use CDN for static files

### Monitoring
- Check logs in `logs/` directory
- Monitor API response times
- Track analysis success rates
- Database performance metrics

## 🚨 Limitations

### Current Limitations
- **Dummy Data**: Menggunakan data simulasi untuk demo
- **Rate Limits**: API rate limiting belum diimplementasi
- **Scale**: Designed untuk volume menengah
- **Languages**: Optimized untuk Bahasa Indonesia

### Future Improvements
- Real-time streaming analysis
- Multi-language support
- Advanced ML models
- Blockchain verification
- Mobile apps

## 🔒 Security

### Best Practices
- Store API keys securely
- Implement rate limiting
- Validate all inputs
- Use HTTPS in production
- Regular security updates

### Privacy
- No personal data storage
- Anonymous analytics only
- Optional data retention policies
- GDPR compliance ready

## 🤝 Contributing

### Development Setup
1. Fork repository
2. Create feature branch
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Make changes
5. Run tests
6. Submit pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Team

Developed for Hackathon 2024
- AI/ML Integration
- Backend Development  
- Frontend Development
- Bot Development
- Documentation

## 📞 Support

### Issues
Report bugs and feature requests on GitHub Issues.

### Contact
- Email: support@hoaxdetector.com
- Telegram: @hoaxdetector_support
- Website: https://hoaxdetector.com

### Documentation
- API Docs: `/docs` endpoint
- User Guide: `/help` page
- Developer Guide: `docs/` directory

---

## 🎯 Demo Data

Aplikasi ini menggunakan dummy data untuk demonstrasi:

### Sample URLs
- `https://twitter.com/example/status/123456789` - Sample hoax content
- `https://twitter.com/sample/status/987654321` - Sample normal content

### Demo Features
- ✅ Full analysis pipeline
- ✅ PDF report generation
- ✅ Network visualization
- ✅ Bot detection
- ✅ Dashboard analytics
- ✅ Telegram integration

### Production Ready
Untuk production, enable API asli dengan mengubah:
```python
# Di services
use_real_api=True
```

---

**Happy Detecting! 🔍** #   s e l e k s i - g c w 
 
 #   g c w  
 