import logging
import asyncio
import os
import requests
from datetime import datetime
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from sqlalchemy.orm import Session

# Import services
from app.database import SessionLocal, init_db
from app.models import TelegramUser, AnalysisSession, HoaxAnalysis, Tweet, TwitterUser
from app.services.twitter_service import TwitterService
from app.services.openai_service import OpenAIService
from app.services.brave_search_service import BraveSearchService
from app.services.bot_detection_service import BotDetectionService
from app.services.network_analysis_service import NetworkAnalysisService
from app.services.pdf_service import PDFService
from app.config import config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize services
twitter_service = TwitterService(use_real_api=False)
openai_service = OpenAIService()
brave_search_service = BraveSearchService(use_real_api=False)
bot_detection_service = BotDetectionService()
network_analysis_service = NetworkAnalysisService()
pdf_service = PDFService()

class TelegramBot:
    """Telegram Bot untuk Twitter Hoax Detector"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command dan message handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Save user to database
        with self.get_db() as db:
            telegram_user = db.query(TelegramUser).filter(
                TelegramUser.telegram_user_id == user.id
            ).first()
            
            if not telegram_user:
                telegram_user = TelegramUser(
                    telegram_user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    total_requests=0
                )
                db.add(telegram_user)
                db.commit()
        
        welcome_message = f"""
🔍 **Selamat datang di Twitter Hoax Detector Bot!**

Halo {user.first_name}! Bot ini membantu Anda menganalisis tweet untuk mendeteksi hoax dan bot.

**Fitur yang tersedia:**
• 🔍 Analisis hoax dengan AI
• 🤖 Deteksi bot otomatis
• 📊 Visualisasi jaringan
• 📄 Laporan PDF
• 📈 Statistik personal

**Cara menggunakan:**
1. Kirim URL tweet yang ingin dianalisis
2. Bot akan memproses dan memberikan hasil
3. Gunakan /help untuk bantuan lebih lanjut

**Commands:**
/analyze - Mulai analisis baru
/status - Cek status analisis
/history - Lihat riwayat analisis
/stats - Statistik personal
/help - Bantuan

Kirim URL tweet sekarang untuk memulai analisis!
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        
        help_message = """
📖 **Bantuan Twitter Hoax Detector Bot**

**Commands tersedia:**
• `/start` - Mulai menggunakan bot
• `/analyze` - Memulai analisis baru
• `/status` - Cek status analisis yang sedang berjalan
• `/history` - Lihat riwayat analisis Anda
• `/stats` - Statistik personal
• `/help` - Tampilkan bantuan ini

**Cara menggunakan:**
1. **Analisis Tweet**: Kirim URL tweet langsung atau gunakan /analyze
2. **Format URL yang didukung**:
   - https://twitter.com/username/status/123456789
   - https://x.com/username/status/123456789
   - https://mobile.twitter.com/username/status/123456789

**Proses Analisis:**
• Ekstraksi data tweet dan pengguna
• Analisis konten menggunakan AI
• Deteksi karakteristik bot
• Pencarian fact-checking
• Analisis jaringan penyebaran
• Generate laporan PDF

**Waktu proses:** 30-60 detik per analisis

**Catatan:** Bot ini menggunakan dummy data untuk demonstrasi. Hasil analisis bersifat prediktif dan sebaiknya diverifikasi lebih lanjut.

Butuh bantuan? Hubungi developer: @hoaxdetector_support
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Input URL Tweet", callback_data="input_url")],
            [InlineKeyboardButton("📊 Lihat Contoh", callback_data="show_example")],
            [InlineKeyboardButton("❓ Bantuan", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
🔍 **Mulai Analisis Tweet**

Pilih salah satu opsi di bawah ini:
• Masukkan URL tweet untuk analisis
• Lihat contoh analisis
• Baca bantuan lebih lanjut

Atau langsung kirim URL tweet ke chat ini!
        """
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        
        user_id = update.effective_user.id
        
        with self.get_db() as db:
            # Cari analisis yang sedang berjalan
            sessions = db.query(AnalysisSession).filter(
                AnalysisSession.user_ip == str(user_id),
                AnalysisSession.status.in_(["pending", "processing"])
            ).order_by(AnalysisSession.created_at.desc()).all()
            
            if not sessions:
                await update.message.reply_text(
                    "📊 Tidak ada analisis yang sedang berjalan.\n\n"
                    "Kirim URL tweet untuk memulai analisis baru!"
                )
                return
            
            message = "📊 **Status Analisis:**\n\n"
            for session in sessions[:5]:  # Maksimal 5 terakhir
                progress = session.progress or 0
                status_emoji = "⏳" if session.status == "processing" else "🔄"
                
                message += f"{status_emoji} **Session {session.session_id[:8]}**\n"
                message += f"• URL: {session.tweet_url[:50]}...\n"
                message += f"• Progress: {progress}%\n"
                message += f"• Status: {session.status}\n"
                message += f"• Waktu: {session.created_at.strftime('%H:%M:%S')}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status")],
                [InlineKeyboardButton("📋 Lihat Riwayat", callback_data="show_history")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        
        user_id = update.effective_user.id
        
        with self.get_db() as db:
            # Ambil riwayat analisis user
            sessions = db.query(AnalysisSession).filter(
                AnalysisSession.user_ip == str(user_id),
                AnalysisSession.status == "completed"
            ).order_by(AnalysisSession.created_at.desc()).limit(10).all()
            
            if not sessions:
                await update.message.reply_text(
                    "📋 Belum ada riwayat analisis.\n\n"
                    "Kirim URL tweet untuk memulai analisis pertama!"
                )
                return
            
            message = "📋 **Riwayat Analisis (10 terakhir):**\n\n"
            
            for i, session in enumerate(sessions, 1):
                analysis = db.query(HoaxAnalysis).filter(
                    HoaxAnalysis.id == session.analysis_id
                ).first()
                
                if analysis:
                    hoax_emoji = "🚨" if analysis.is_hoax else "✅"
                    hoax_status = "HOAX" if analysis.is_hoax else "BUKAN HOAX"
                    
                    message += f"{i}. {hoax_emoji} **{hoax_status}**\n"
                    message += f"   📊 Probabilitas: {analysis.hoax_probability:.1%}\n"
                    message += f"   🕒 {session.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                    message += f"   🔗 {session.tweet_url[:40]}...\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_history")],
                [InlineKeyboardButton("📊 Statistik", callback_data="show_stats")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        
        user_id = update.effective_user.id
        
        with self.get_db() as db:
            # Update total requests
            telegram_user = db.query(TelegramUser).filter(
                TelegramUser.telegram_user_id == user_id
            ).first()
            
            if telegram_user:
                telegram_user.total_requests += 1
                telegram_user.last_request_at = datetime.utcnow()
                db.commit()
            
            # Hitung statistik user
            total_analyses = db.query(AnalysisSession).filter(
                AnalysisSession.user_ip == str(user_id),
                AnalysisSession.status == "completed"
            ).count()
            
            hoax_count = db.query(AnalysisSession).join(HoaxAnalysis).filter(
                AnalysisSession.user_ip == str(user_id),
                AnalysisSession.status == "completed",
                HoaxAnalysis.is_hoax == True
            ).count()
            
            # Statistik global
            global_analyses = db.query(AnalysisSession).filter(
                AnalysisSession.status == "completed"
            ).count()
            
            global_hoax = db.query(HoaxAnalysis).filter(
                HoaxAnalysis.is_hoax == True
            ).count()
            
            message = f"""
📊 **Statistik Personal**

**Aktivitas Anda:**
• Total Analisis: {total_analyses}
• Hoax Terdeteksi: {hoax_count}
• Persentase Hoax: {(hoax_count/total_analyses*100):.1f}% 
• Total Request: {telegram_user.total_requests if telegram_user else 0}
• Bergabung: {telegram_user.created_at.strftime('%d/%m/%Y') if telegram_user else 'N/A'}

**Statistik Global:**
• Total Analisis: {global_analyses}
• Hoax Terdeteksi: {global_hoax}
• Persentase Hoax: {(global_hoax/global_analyses*100):.1f}%

**Rangking Anda:**
🏆 {'Top User' if total_analyses > 10 else 'Active User' if total_analyses > 5 else 'New User'}
            """
            
            keyboard = [
                [InlineKeyboardButton("📈 Detail Statistik", callback_data="detailed_stats")],
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        
        message_text = update.message.text
        user_id = update.effective_user.id
        
        # Cek apakah pesan adalah URL Twitter
        if self.is_twitter_url(message_text):
            await self.start_analysis(update, context, message_text)
        else:
            # Berikan petunjuk
            await update.message.reply_text(
                "🤔 Sepertinya itu bukan URL Twitter.\n\n"
                "**Format yang didukung:**\n"
                "• https://twitter.com/username/status/123456789\n"
                "• https://x.com/username/status/123456789\n\n"
                "Kirim URL tweet yang valid untuk memulai analisis!"
            )
    
    def is_twitter_url(self, text: str) -> bool:
        """Cek apakah text adalah URL Twitter"""
        import re
        twitter_patterns = [
            r'https?://(?:www\.)?twitter\.com/\w+/status/\d+',
            r'https?://(?:www\.)?x\.com/\w+/status/\d+',
            r'https?://mobile\.twitter\.com/\w+/status/\d+'
        ]
        
        for pattern in twitter_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    async def start_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tweet_url: str):
        """Mulai analisis tweet"""
        
        user_id = update.effective_user.id
        
        # Kirim pesan konfirmasi
        progress_message = await update.message.reply_text(
            "🔍 **Memulai Analisis Tweet**\n\n"
            "⏳ Memproses URL tweet...\n"
            "📊 Progress: 0%\n\n"
            "Mohon tunggu, analisis akan memakan waktu 30-60 detik."
        )
        
        try:
            # Panggil API untuk memulai analisis
            response = requests.post(
                f"{self.get_api_base_url()}/api/analyze",
                data={"tweet_url": tweet_url},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                session_id = result.get('session_id')
                
                # Update database dengan user_id
                with self.get_db() as db:
                    session = db.query(AnalysisSession).filter(
                        AnalysisSession.session_id == session_id
                    ).first()
                    
                    if session:
                        session.user_ip = str(user_id)  # Store telegram user_id
                        db.commit()
                
                # Mulai tracking progress
                await self.track_analysis_progress(progress_message, session_id, user_id)
                
            else:
                await progress_message.edit_text(
                    "❌ **Error memulai analisis**\n\n"
                    "Gagal memproses tweet. Silakan coba lagi nanti."
                )
        
        except Exception as e:
            logger.error(f"Error starting analysis: {e}")
            await progress_message.edit_text(
                "❌ **Error memulai analisis**\n\n"
                f"Terjadi kesalahan: {str(e)}"
            )
    
    async def track_analysis_progress(self, message, session_id: str, user_id: int):
        """Track progress analisis"""
        
        max_attempts = 60  # 2 menit maksimal
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(
                    f"{self.get_api_base_url()}/api/status/{session_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    progress = status_data.get('progress', 0)
                    status = status_data.get('status', 'processing')
                    
                    # Update progress message
                    progress_text = self.get_progress_text(progress)
                    await message.edit_text(
                        f"🔍 **Analisis Tweet**\n\n"
                        f"📊 Progress: {progress}%\n"
                        f"⏳ Status: {progress_text}\n\n"
                        f"{'🔄 Sedang memproses...' if status == 'processing' else '✅ Selesai!' if status == 'completed' else '❌ Gagal!'}"
                    )
                    
                    if status == 'completed':
                        await self.send_analysis_result(message, session_id, user_id)
                        return
                    elif status == 'failed':
                        await message.edit_text(
                            "❌ **Analisis Gagal**\n\n"
                            "Terjadi kesalahan saat memproses tweet."
                        )
                        return
                
                await asyncio.sleep(3)
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error tracking progress: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        # Timeout
        await message.edit_text(
            "⏰ **Timeout**\n\n"
            "Analisis memakan waktu terlalu lama. Gunakan /status untuk cek status terbaru."
        )
    
    def get_progress_text(self, progress: int) -> str:
        """Get progress text berdasarkan progress"""
        if progress <= 20:
            return "Ekstraksi data tweet..."
        elif progress <= 40:
            return "Analisis hoax dengan AI..."
        elif progress <= 60:
            return "Deteksi bot..."
        elif progress <= 80:
            return "Fact-checking..."
        elif progress <= 95:
            return "Membuat laporan..."
        else:
            return "Selesai!"
    
    async def send_analysis_result(self, message, session_id: str, user_id: int):
        """Kirim hasil analisis"""
        
        try:
            response = requests.get(
                f"{self.get_api_base_url()}/api/result/{session_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                tweet_data = result.get('tweet_data', {})
                hoax_analysis = result.get('hoax_analysis', {})
                bot_detection = result.get('bot_detection', {})
                
                # Format hasil
                hoax_emoji = "🚨" if hoax_analysis.get('is_hoax') else "✅"
                hoax_status = "HOAX TERDETEKSI" if hoax_analysis.get('is_hoax') else "BUKAN HOAX"
                
                bot_emoji = "🤖" if bot_detection.get('is_bot') else "👤"
                bot_status = "BOT TERDETEKSI" if bot_detection.get('is_bot') else "BUKAN BOT"
                
                result_message = f"""
🔍 **Hasil Analisis Tweet**

{hoax_emoji} **{hoax_status}**
📊 Probabilitas: {hoax_analysis.get('hoax_probability', 0):.1%}

{bot_emoji} **{bot_status}**
📊 Probabilitas: {bot_detection.get('bot_probability', 0):.1%}

**Informasi Tweet:**
👤 Pengguna: @{tweet_data.get('user', {}).get('username', 'N/A')}
📅 Tanggal: {datetime.fromisoformat(tweet_data.get('created_at', '2024-01-01T00:00:00')).strftime('%d/%m/%Y %H:%M')}
💬 Tweet: {tweet_data.get('text', 'N/A')[:100]}...

**Metrics:**
🔄 Retweet: {tweet_data.get('retweet_count', 0)}
❤️ Like: {tweet_data.get('like_count', 0)}
💬 Reply: {tweet_data.get('reply_count', 0)}
                """
                
                # Tombol aksi
                keyboard = [
                    [InlineKeyboardButton("📄 Download PDF", callback_data=f"download_pdf_{session_id}")],
                    [InlineKeyboardButton("📊 Visualisasi", callback_data=f"view_viz_{session_id}")],
                    [InlineKeyboardButton("📋 Detail Lengkap", callback_data=f"view_detail_{session_id}")],
                    [InlineKeyboardButton("🔄 Analisis Baru", callback_data="input_url")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await message.edit_text(result_message, reply_markup=reply_markup, parse_mode='Markdown')
                
            else:
                await message.edit_text(
                    "❌ **Error mengambil hasil**\n\n"
                    "Gagal mengambil hasil analisis. Coba lagi nanti."
                )
        
        except Exception as e:
            logger.error(f"Error sending result: {e}")
            await message.edit_text(
                "❌ **Error mengambil hasil**\n\n"
                f"Terjadi kesalahan: {str(e)}"
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "input_url":
            await query.edit_message_text(
                "📝 **Masukkan URL Tweet**\n\n"
                "Kirim URL tweet yang ingin dianalisis ke chat ini.\n\n"
                "**Format yang didukung:**\n"
                "• https://twitter.com/username/status/123456789\n"
                "• https://x.com/username/status/123456789\n\n"
                "Contoh: https://twitter.com/elonmusk/status/1234567890"
            )
        
        elif data == "show_example":
            await query.edit_message_text(
                "📊 **Contoh Analisis**\n\n"
                "**Input:** https://twitter.com/example/status/123456789\n\n"
                "**Hasil:**\n"
                "🚨 **HOAX TERDETEKSI**\n"
                "📊 Probabilitas: 85%\n"
                "🤖 **BOT TERDETEKSI**\n"
                "📊 Probabilitas: 70%\n\n"
                "**Alasan:**\n"
                "• Konten mengandung klaim tanpa bukti\n"
                "• Akun memiliki pola bot\n"
                "• Rasio follower/following mencurigakan\n\n"
                "Kirim URL tweet Anda untuk analisis nyata!"
            )
        
        elif data.startswith("download_pdf_"):
            session_id = data.replace("download_pdf_", "")
            pdf_url = f"{self.get_api_base_url()}/api/download/pdf/{session_id}"
            
            await query.edit_message_text(
                f"📄 **Download Laporan PDF**\n\n"
                f"Klik link berikut untuk download:\n"
                f"[Download PDF Report]({pdf_url})\n\n"
                f"Atau akses melalui browser:\n"
                f"`{pdf_url}`",
                parse_mode='Markdown'
            )
        
        elif data.startswith("view_viz_"):
            session_id = data.replace("view_viz_", "")
            await query.edit_message_text(
                "📊 **Visualisasi Jaringan**\n\n"
                "Visualisasi jaringan penyebaran tweet sedang dipersiapkan.\n"
                "Fitur ini akan tersedia dalam update berikutnya.\n\n"
                "Saat ini Anda dapat mengakses visualisasi melalui web dashboard."
            )
        
        elif data.startswith("view_detail_"):
            session_id = data.replace("view_detail_", "")
            detail_url = f"{self.get_api_base_url()}/result/{session_id}"
            
            await query.edit_message_text(
                f"📋 **Detail Lengkap**\n\n"
                f"Klik link berikut untuk melihat detail:\n"
                f"[Lihat Detail Lengkap]({detail_url})\n\n"
                f"Atau akses melalui browser:\n"
                f"`{detail_url}`",
                parse_mode='Markdown'
            )
        
        # Handle other callbacks
        elif data == "refresh_status":
            await self.status_command(update, context)
        elif data == "refresh_history":
            await self.history_command(update, context)
        elif data == "refresh_stats":
            await self.stats_command(update, context)
        elif data == "show_help":
            await self.help_command(update, context)
    
    def get_api_base_url(self) -> str:
        """Get base URL untuk API"""
        return "http://localhost:8000"  # Sesuaikan dengan deployment
    
    def run(self):
        """Run the bot"""
        print("Starting Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    
    # Inisialisasi database
    init_db()
    
    # Cek token
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in config!")
        print("Please set TELEGRAM_BOT_TOKEN in environment variables or config.py")
        return
    
    # Jalankan bot
    bot = TelegramBot(token)
    bot.run()

if __name__ == "__main__":
    main() 