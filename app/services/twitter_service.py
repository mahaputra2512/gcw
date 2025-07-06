import tweepy
import re
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.config import config

class TwitterService:
    """Service untuk mengekstrak data dari Twitter"""
    
    def __init__(self, use_real_api: bool = False):
        self.use_real_api = use_real_api
        if use_real_api:
            self._init_real_api()
        
    def _init_real_api(self):
        """Inisialisasi Twitter API asli"""
        try:
            # Setup Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=config.TWITTER_BEARER_TOKEN,
                consumer_key=config.TWITTER_API_KEY,
                consumer_secret=config.TWITTER_API_SECRET,
                wait_on_rate_limit=True
            )
            print("Twitter API initialized successfully")
        except Exception as e:
            print(f"Error initializing Twitter API: {e}")
            self.use_real_api = False
    
    def extract_tweet_id(self, url: str) -> Optional[str]:
        """Ekstrak tweet ID dari URL"""
        # Pattern untuk URL Twitter
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)',
            r'mobile\.twitter\.com/\w+/status/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_tweet_data(self, tweet_url: str) -> Dict[str, Any]:
        """Ambil data tweet dari URL"""
        tweet_id = self.extract_tweet_id(tweet_url)
        if not tweet_id:
            raise ValueError("Invalid Twitter URL")
        
        if self.use_real_api:
            return self._get_real_tweet_data(tweet_id)
        else:
            return self._get_dummy_tweet_data(tweet_id, tweet_url)
    
    def _get_real_tweet_data(self, tweet_id: str) -> Dict[str, Any]:
        """Ambil data tweet dari API asli"""
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'conversation_id'],
                user_fields=['username', 'name', 'description', 'public_metrics', 'verified', 'created_at', 'profile_image_url'],
                expansions=['author_id']
            )
            
            if not tweet.data:
                raise ValueError("Tweet not found")
            
            # Ekstrak data tweet
            tweet_data = tweet.data
            user_data = tweet.includes['users'][0] if tweet.includes and 'users' in tweet.includes else None
            
            return {
                'tweet_id': tweet_data.id,
                'text': tweet_data.text,
                'created_at': tweet_data.created_at,
                'retweet_count': tweet_data.public_metrics.get('retweet_count', 0),
                'like_count': tweet_data.public_metrics.get('like_count', 0),
                'reply_count': tweet_data.public_metrics.get('reply_count', 0),
                'quote_count': tweet_data.public_metrics.get('quote_count', 0),
                'user': {
                    'user_id': user_data.id if user_data else None,
                    'username': user_data.username if user_data else None,
                    'display_name': user_data.name if user_data else None,
                    'bio': user_data.description if user_data else None,
                    'followers_count': user_data.public_metrics.get('followers_count', 0) if user_data else 0,
                    'following_count': user_data.public_metrics.get('following_count', 0) if user_data else 0,
                    'tweet_count': user_data.public_metrics.get('tweet_count', 0) if user_data else 0,
                    'verified': user_data.verified if user_data else False,
                    'profile_image_url': user_data.profile_image_url if user_data else None,
                    'account_creation_date': user_data.created_at if user_data else None
                }
            }
        except Exception as e:
            print(f"Error fetching real tweet data: {e}")
            raise
    
    def _get_dummy_tweet_data(self, tweet_id: str, tweet_url: str) -> Dict[str, Any]:
        """Generate dummy tweet data yang realistis"""
        
        # Dummy tweets dengan berbagai kategori (diperbanyak)
        dummy_tweets = [
            # Hoax Politics
            {
                'text': "BREAKING: Pemerintah akan menaikkan harga BBM hingga 50% minggu depan! Siap-siap ya guys. #BBM #Kenaikan",
                'category': 'hoax_politics',
                'is_controversial': True
            },
            {
                'text': "URGENT: Pajak motor naik 200% mulai bulan depan! Buruan bayar sebelum terlambat! #PajakMotor #Urgent",
                'category': 'hoax_politics',
                'is_controversial': True
            },
            {
                'text': "HOAX ALERT: Menteri Keuangan mengumumkan uang Rp 1000 akan dihapus dari peredaran! Tukar sekarang juga!",
                'category': 'hoax_politics',
                'is_controversial': True
            },
            {
                'text': "BERITA PALSU: Presiden mundur karena skandal korupsi! Media mainstream tidak memberitakan ini! #BeritaPalsu",
                'category': 'hoax_politics',
                'is_controversial': True
            },
            
            # Hoax Health
            {
                'text': "Vaksin COVID-19 ternyata mengandung chip 5G yang bisa mengontrol pikiran manusia. Jangan percaya pemerintah!",
                'category': 'hoax_health',
                'is_controversial': True
            },
            {
                'text': "BAHAYA: Masker menyebabkan keracunan CO2 dan merusak otak! Dokter di seluruh dunia menyembunyikan ini!",
                'category': 'hoax_health',
                'is_controversial': True
            },
            {
                'text': "VIRAL: Air putih hangat dengan lemon bisa menyembuhkan kanker dalam 3 hari! Dokter tidak mau kasih tahu!",
                'category': 'hoax_health',
                'is_controversial': True
            },
            {
                'text': "KONSPIRASI: Obat herbal tradisional dilarang pemerintah karena bisa menyembuhkan semua penyakit! #KonspirasiFarma",
                'category': 'hoax_health',
                'is_controversial': True
            },
            
            # Hoax Disaster
            {
                'text': "Gempa bumi dahsyat akan terjadi besok di Jakarta berdasarkan prediksi paranormal terkenal. Segera evakuasi!",
                'category': 'hoax_disaster',
                'is_controversial': True
            },
            {
                'text': "PERINGATAN: Tsunami setinggi 50 meter akan menerjang Bali minggu depan! Ahli spiritual sudah memperingatkan!",
                'category': 'hoax_disaster',
                'is_controversial': True
            },
            {
                'text': "BREAKING: Gunung Merapi akan meletus hari ini! Evacuation zone 100km! Pemerintah tutup-tutupi!",
                'category': 'hoax_disaster',
                'is_controversial': True
            },
            {
                'text': "URGENT: Banjir bandang akan terjadi di Jakarta dalam 2 jam! Semua warga segera mengungsi ke tempat tinggi!",
                'category': 'hoax_disaster',
                'is_controversial': True
            },
            
            # Hoax Celebrity
            {
                'text': "VIRAL: Video artis terkenal sedang berantem di mall! Lihat videonya di link ini: [link palsu]",
                'category': 'hoax_celebrity',
                'is_controversial': True
            },
            {
                'text': "SHOCKING: Artis A meninggal dunia karena overdosis! Keluarga masih merahasiakan! #RIPArtisA",
                'category': 'hoax_celebrity',
                'is_controversial': True
            },
            {
                'text': "SCANDAL: Video messum artis B tersebar! Link download ada di bio! Jangan sampai dihapus!",
                'category': 'hoax_celebrity',
                'is_controversial': True
            },
            {
                'text': "BREAKING: Selebriti C ditangkap polisi karena narkoba! Media mainstream tidak berani memberitakan!",
                'category': 'hoax_celebrity',
                'is_controversial': True
            },
            
            # Normal Content
            {
                'text': "Selamat pagi! Hari ini cuaca sangat cerah. Semoga hari kalian menyenangkan 🌞",
                'category': 'normal',
                'is_controversial': False
            },
            {
                'text': "Terimakasih kepada semua yang sudah support channel YouTube saya! Subscriber sudah mencapai 10K! 🎉",
                'category': 'normal',
                'is_controversial': False
            },
            {
                'text': "Lagi nyoba resep nasi goreng baru nih, hasilnya enak banget! Mau coba juga? 🍚✨",
                'category': 'normal',
                'is_controversial': False
            },
            {
                'text': "Weekend ini mau kemana guys? Saya planning mau ke pantai, cuaca lagi bagus nih! 🏖️",
                'category': 'normal',
                'is_controversial': False
            },
            {
                'text': "Baru selesai baca buku bagus tentang produktivitas. Highly recommended! 📚",
                'category': 'normal',
                'is_controversial': False
            },
            
            # Information/Educational
            {
                'text': "Penelitian terbaru menunjukkan bahwa minum kopi secara teratur dapat mengurangi risiko penyakit jantung hingga 20%. Sumber: Journal of Medical Research 2024",
                'category': 'information',
                'is_controversial': False
            },
            {
                'text': "Tips hemat listrik: Matikan peralatan elektronik yang tidak digunakan, gunakan lampu LED, dan atur suhu AC di 25°C. #TipsHemat",
                'category': 'information',
                'is_controversial': False
            },
            {
                'text': "Menurut data BPS, inflasi bulan ini turun 0.2% dibanding bulan lalu. Harga sembako mulai stabil. #EkonomiIndonesia",
                'category': 'information',
                'is_controversial': False
            },
            {
                'text': "Cara mudah belajar bahasa asing: 1) Dengarkan musik, 2) Tonton film tanpa subtitle, 3) Praktek setiap hari 15 menit #BelajarBahasa",
                'category': 'information',
                'is_controversial': False
            },
            {
                'text': "Fakta menarik: Pohon bambu bisa tumbuh hingga 1 meter per hari dan menyerap CO2 35% lebih banyak dari pohon biasa! 🌱",
                'category': 'information',
                'is_controversial': False
            },
            
            # Technology
            {
                'text': "Apple baru saja merilis iPhone 15 Pro dengan fitur AI yang canggih. Harga mulai dari $999. #iPhone15Pro #Apple",
                'category': 'technology',
                'is_controversial': False
            },
            {
                'text': "Tesla mengumumkan mobil listrik baru dengan jarak tempuh 800km sekali charge. Revolusi transportasi! #Tesla #MobilListrik",
                'category': 'technology',
                'is_controversial': False
            },
            {
                'text': "Google meluncurkan AI Bard yang bisa menulis kode program. Programmer masa depan akan seperti apa ya? #GoogleBard #AI",
                'category': 'technology',
                'is_controversial': False
            },
            
            # Sports
            {
                'text': "Indonesia menang 3-1 lawan Thailand di SEA Games 2024! Timnas kita makin keren! ⚽🇮🇩 #TimnasIndonesia",
                'category': 'sports',
                'is_controversial': False
            },
            {
                'text': "Lionel Messi mencetak gol ke-800 dalam karirnya! GOAT sejati! 🐐⚽ #Messi #Football",
                'category': 'sports',
                'is_controversial': False
            },
            {
                'text': "Pertandingan badminton Indonesia vs China seru banget! Kevin/Marcus juara lagi! 🏸 #BadmintonIndonesia",
                'category': 'sports',
                'is_controversial': False
            }
        ]
        
        # Pilih tweet secara random
        selected_tweet = random.choice(dummy_tweets)
        
        # Generate dummy user data (diperbanyak)
        dummy_users = [
            # Suspicious accounts (potential bots/hoax spreaders)
            {
                'username': 'berita_update',
                'display_name': 'Berita Update',
                'bio': 'Akun berita terpercaya Indonesia',
                'followers_count': random.randint(50000, 500000),
                'following_count': random.randint(100, 1000),
                'tweet_count': random.randint(1000, 10000),
                'verified': False,
                'suspicious_ratio': 0.8
            },
            {
                'username': 'info_viral',
                'display_name': 'Info Viral',
                'bio': 'Berbagi informasi viral terkini',
                'followers_count': random.randint(10000, 100000),
                'following_count': random.randint(10000, 50000),
                'tweet_count': random.randint(500, 5000),
                'verified': False,
                'suspicious_ratio': 0.7
            },
            {
                'username': 'breaking_news24',
                'display_name': 'Breaking News 24',
                'bio': 'Breaking news dari seluruh dunia',
                'followers_count': random.randint(80000, 200000),
                'following_count': random.randint(50000, 100000),
                'tweet_count': random.randint(2000, 8000),
                'verified': False,
                'suspicious_ratio': 0.9
            },
            {
                'username': 'hoax_hunter',
                'display_name': 'Hoax Hunter',
                'bio': 'Memburu hoax dan berita palsu',
                'followers_count': random.randint(5000, 20000),
                'following_count': random.randint(10000, 30000),
                'tweet_count': random.randint(1000, 5000),
                'verified': False,
                'suspicious_ratio': 0.8
            },
            {
                'username': 'viral_content',
                'display_name': 'Viral Content',
                'bio': 'Konten viral terbaru dan terupdate',
                'followers_count': random.randint(30000, 150000),
                'following_count': random.randint(20000, 80000),
                'tweet_count': random.randint(800, 3000),
                'verified': False,
                'suspicious_ratio': 0.75
            },
            
            # Normal users
            {
                'username': 'john_doe',
                'display_name': 'John Doe',
                'bio': 'Just a regular person sharing thoughts',
                'followers_count': random.randint(100, 1000),
                'following_count': random.randint(200, 800),
                'tweet_count': random.randint(50, 500),
                'verified': False,
                'suspicious_ratio': 0.2
            },
            {
                'username': 'sarah_jakarta',
                'display_name': 'Sarah from Jakarta',
                'bio': 'Ibu rumah tangga, pecinta kuliner, Jakarta',
                'followers_count': random.randint(200, 2000),
                'following_count': random.randint(300, 1500),
                'tweet_count': random.randint(100, 800),
                'verified': False,
                'suspicious_ratio': 0.3
            },
            {
                'username': 'budi_programmer',
                'display_name': 'Budi Santoso',
                'bio': 'Software Engineer | Tech Enthusiast | Coffee Lover ☕',
                'followers_count': random.randint(500, 5000),
                'following_count': random.randint(400, 2000),
                'tweet_count': random.randint(300, 1200),
                'verified': False,
                'suspicious_ratio': 0.25
            },
            {
                'username': 'maya_travel',
                'display_name': 'Maya Explorer',
                'bio': 'Travel blogger | Indonesia 🇮🇩 | Sharing beautiful places',
                'followers_count': random.randint(1000, 10000),
                'following_count': random.randint(500, 3000),
                'tweet_count': random.randint(400, 2000),
                'verified': False,
                'suspicious_ratio': 0.35
            },
            {
                'username': 'andi_student',
                'display_name': 'Andi Mahasiswa',
                'bio': 'Mahasiswa UI | Pecinta musik | Jakarta',
                'followers_count': random.randint(150, 1500),
                'following_count': random.randint(800, 2500),
                'tweet_count': random.randint(200, 1000),
                'verified': False,
                'suspicious_ratio': 0.4
            },
            
            # Verified accounts (trusted)
            {
                'username': 'dr_health',
                'display_name': 'Dr. Health',
                'bio': 'Dokter spesialis penyakit dalam. Berbagi tips kesehatan.',
                'followers_count': random.randint(5000, 50000),
                'following_count': random.randint(500, 2000),
                'tweet_count': random.randint(200, 2000),
                'verified': True,
                'suspicious_ratio': 0.1
            },
            {
                'username': 'prof_ekonomi',
                'display_name': 'Prof. Ekonomi Indonesia',
                'bio': 'Profesor Ekonomi UI | Ekonom | Penulis buku ekonomi',
                'followers_count': random.randint(10000, 80000),
                'following_count': random.randint(200, 1000),
                'tweet_count': random.randint(500, 3000),
                'verified': True,
                'suspicious_ratio': 0.05
            },
            {
                'username': 'journalist_indo',
                'display_name': 'Jurnalis Indonesia',
                'bio': 'Jurnalis senior | 15 tahun pengalaman | Kompas',
                'followers_count': random.randint(20000, 100000),
                'following_count': random.randint(1000, 5000),
                'tweet_count': random.randint(1000, 8000),
                'verified': True,
                'suspicious_ratio': 0.08
            },
            {
                'username': 'bmkg_official',
                'display_name': 'BMKG Official',
                'bio': 'Akun resmi Badan Meteorologi Klimatologi dan Geofisika',
                'followers_count': random.randint(100000, 500000),
                'following_count': random.randint(50, 200),
                'tweet_count': random.randint(2000, 10000),
                'verified': True,
                'suspicious_ratio': 0.02
            },
            {
                'username': 'kemkes_ri',
                'display_name': 'Kementerian Kesehatan RI',
                'bio': 'Akun resmi Kementerian Kesehatan Republik Indonesia',
                'followers_count': random.randint(200000, 1000000),
                'following_count': random.randint(100, 500),
                'tweet_count': random.randint(3000, 15000),
                'verified': True,
                'suspicious_ratio': 0.01
            },
            
            # Influencers
            {
                'username': 'influencer_lifestyle',
                'display_name': 'Lifestyle Influencer',
                'bio': 'Lifestyle & Beauty Influencer | 500K+ followers | Collabs: DM',
                'followers_count': random.randint(100000, 800000),
                'following_count': random.randint(2000, 10000),
                'tweet_count': random.randint(5000, 20000),
                'verified': True,
                'suspicious_ratio': 0.15
            },
            {
                'username': 'tech_reviewer',
                'display_name': 'Tech Reviewer Indonesia',
                'bio': 'Tech reviewer | YouTube 1M+ | Gadget enthusiast',
                'followers_count': random.randint(200000, 1000000),
                'following_count': random.randint(1000, 5000),
                'tweet_count': random.randint(3000, 12000),
                'verified': True,
                'suspicious_ratio': 0.12
            },
            {
                'username': 'food_blogger',
                'display_name': 'Food Blogger Jakarta',
                'bio': 'Food blogger | Kuliner Indonesia | Jakarta foodie',
                'followers_count': random.randint(50000, 300000),
                'following_count': random.randint(3000, 15000),
                'tweet_count': random.randint(2000, 8000),
                'verified': False,
                'suspicious_ratio': 0.2
            },
            
            # Suspicious bot-like accounts
            {
                'username': f'user_{random.randint(100000, 999999)}',
                'display_name': f'User {random.randint(1000, 9999)}',
                'bio': 'Following back | DM for collab',
                'followers_count': random.randint(10, 100),
                'following_count': random.randint(5000, 20000),
                'tweet_count': random.randint(1, 50),
                'verified': False,
                'suspicious_ratio': 0.95
            },
            {
                'username': f'bot_{random.randint(1000, 9999)}',
                'display_name': f'Bot Account {random.randint(100, 999)}',
                'bio': '',
                'followers_count': random.randint(1, 50),
                'following_count': random.randint(10000, 50000),
                'tweet_count': random.randint(0, 20),
                'verified': False,
                'suspicious_ratio': 0.98
            }
        ]
        
        selected_user = random.choice(dummy_users)
        
        return {
            'tweet_id': tweet_id,
            'url': tweet_url,
            'text': selected_tweet['text'],
            'created_at': datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            'retweet_count': random.randint(0, 1000) if selected_tweet['is_controversial'] else random.randint(0, 100),
            'like_count': random.randint(0, 5000) if selected_tweet['is_controversial'] else random.randint(0, 500),
            'reply_count': random.randint(0, 500) if selected_tweet['is_controversial'] else random.randint(0, 50),
            'quote_count': random.randint(0, 200) if selected_tweet['is_controversial'] else random.randint(0, 20),
            'user': {
                'user_id': f"user_{random.randint(100000, 999999)}",
                'username': selected_user['username'],
                'display_name': selected_user['display_name'],
                'bio': selected_user['bio'],
                'followers_count': selected_user['followers_count'],
                'following_count': selected_user['following_count'],
                'tweet_count': selected_user['tweet_count'],
                'verified': selected_user['verified'],
                'profile_image_url': f"https://pbs.twimg.com/profile_images/{random.randint(1000000000, 9999999999)}/image.jpg",
                'account_creation_date': datetime.now() - timedelta(
                    days=random.randint(30, 3650)  # 1 bulan - 10 tahun
                )
            },
            'category': selected_tweet['category'],
            'is_controversial': selected_tweet['is_controversial']
        }
    
    def get_tweet_network_data(self, tweet_id: str) -> Dict[str, Any]:
        """Ambil data jaringan penyebaran tweet (retweets, replies, mentions)"""
        if self.use_real_api:
            return self._get_real_network_data(tweet_id)
        else:
            return self._get_dummy_network_data(tweet_id)
    
    def _get_real_network_data(self, tweet_id: str) -> Dict[str, Any]:
        """Ambil data jaringan dari API asli"""
        # Implementasi untuk API asli
        # Karena Twitter API v2 memiliki batasan untuk network data,
        # kita akan menggunakan pendekatan yang lebih sederhana
        pass
    
    def _get_dummy_network_data(self, tweet_id: str) -> Dict[str, Any]:
        """Generate dummy network data"""
        # Generate nodes (users yang berinteraksi)
        nodes = []
        edges = []
        
        # Original poster
        original_user = f"user_{random.randint(100000, 999999)}"
        nodes.append({
            'id': original_user,
            'label': f"@{original_user}",
            'type': 'original',
            'followers': random.randint(1000, 50000),
            'influence_score': random.uniform(0.5, 1.0)
        })
        
        # Generate retweets
        retweet_count = random.randint(5, 50)
        for i in range(retweet_count):
            user_id = f"retweeter_{i}"
            nodes.append({
                'id': user_id,
                'label': f"@{user_id}",
                'type': 'retweet',
                'followers': random.randint(100, 10000),
                'influence_score': random.uniform(0.1, 0.7)
            })
            edges.append({
                'from': original_user,
                'to': user_id,
                'type': 'retweet',
                'weight': random.uniform(0.5, 1.0)
            })
        
        # Generate replies
        reply_count = random.randint(3, 20)
        for i in range(reply_count):
            user_id = f"replier_{i}"
            nodes.append({
                'id': user_id,
                'label': f"@{user_id}",
                'type': 'reply',
                'followers': random.randint(50, 5000),
                'influence_score': random.uniform(0.1, 0.5)
            })
            edges.append({
                'from': original_user,
                'to': user_id,
                'type': 'reply',
                'weight': random.uniform(0.3, 0.8)
            })
        
        # Generate mentions
        mention_count = random.randint(1, 10)
        for i in range(mention_count):
            user_id = f"mentioner_{i}"
            nodes.append({
                'id': user_id,
                'label': f"@{user_id}",
                'type': 'mention',
                'followers': random.randint(200, 8000),
                'influence_score': random.uniform(0.2, 0.6)
            })
            edges.append({
                'from': user_id,
                'to': original_user,
                'type': 'mention',
                'weight': random.uniform(0.2, 0.6)
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_interactions': len(edges),
            'reach_estimate': sum(node['followers'] for node in nodes),
            'influence_score': sum(node['influence_score'] for node in nodes) / len(nodes)
        } 