# Security Configuration

## Environment Variables Setup

Aplikasi ini menggunakan environment variables untuk menyimpan kredensial API yang sensitif. Ikuti langkah-langkah berikut untuk setup:

### 1. Buat file .env

Salin file `env.example` ke `.env`:

```bash
cp env.example .env
```

### 2. Isi Kredensial API

Edit file `.env` dan isi dengan kredensial API yang sebenarnya:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Twitter API
TWITTER_API_KEY=your-twitter-api-key-here
TWITTER_API_SECRET=your-twitter-api-secret-here
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here

# Brave Search API
BRAVE_SEARCH_API_KEY=your-brave-search-api-key-here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
```

### 3. Cara Mendapatkan API Keys

#### OpenAI API
1. Buat akun di [OpenAI Platform](https://platform.openai.com/)
2. Buat API key baru di bagian API Keys
3. Salin API key ke variabel `OPENAI_API_KEY`

#### Twitter API
1. Buat akun developer di [Twitter Developer Portal](https://developer.twitter.com/)
2. Buat aplikasi baru
3. Dapatkan API Key, API Secret, dan Bearer Token
4. Salin ke variabel yang sesuai

#### Brave Search API
1. Buat akun di [Brave Search API](https://api.search.brave.com/)
2. Dapatkan API key
3. Salin ke variabel `BRAVE_SEARCH_API_KEY`

#### Telegram Bot
1. Chat dengan [@BotFather](https://t.me/BotFather) di Telegram
2. Buat bot baru dengan `/newbot`
3. Dapatkan token dan salin ke `TELEGRAM_BOT_TOKEN`

### 4. Keamanan

- **JANGAN PERNAH** commit file `.env` ke repository
- File `.env` sudah ditambahkan ke `.gitignore`
- Gunakan kredensial yang berbeda untuk development dan production
- Rotasi API keys secara berkala

### 5. Deployment

Untuk deployment ke VPS atau cloud provider, set environment variables melalui:

- **VPS**: Export environment variables atau gunakan file `.env`
- **Docker**: Gunakan file `.env` atau docker-compose environment
- **Cloud Provider**: Gunakan secrets manager atau environment variables

### 6. Troubleshooting

Jika aplikasi tidak bisa mengakses API:

1. Pastikan file `.env` ada di root directory
2. Pastikan semua kredensial sudah diisi dengan benar
3. Cek logs untuk error message
4. Verify API keys masih valid dan tidak expired

### 7. Testing

Untuk testing, buat file `.env.test` dengan kredensial testing atau mock values. 