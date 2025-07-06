import re
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.config import config

class BotDetectionService:
    """Service untuk deteksi bot Twitter"""
    
    def __init__(self):
        self.bot_indicators = {
            'username_pattern': 0.3,
            'display_name_pattern': 0.2,
            'follower_ratio': 0.25,
            'account_age': 0.15,
            'tweet_frequency': 0.1,
            'profile_completeness': 0.15,
            'bio_pattern': 0.2
        }
    
    def detect_bot(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deteksi apakah akun merupakan bot"""
        
        # Hitung skor untuk setiap indikator
        scores = {}
        
        # 1. Analisis username pattern
        scores['username_pattern'] = self._analyze_username_pattern(user_data.get('username', ''))
        
        # 2. Analisis display name pattern
        scores['display_name_pattern'] = self._analyze_display_name_pattern(user_data.get('display_name', ''))
        
        # 3. Analisis rasio follower/following
        scores['follower_ratio'] = self._analyze_follower_ratio(
            user_data.get('followers_count', 0),
            user_data.get('following_count', 0)
        )
        
        # 4. Analisis umur akun
        scores['account_age'] = self._analyze_account_age(user_data.get('account_creation_date'))
        
        # 5. Analisis frekuensi tweet
        scores['tweet_frequency'] = self._analyze_tweet_frequency(
            user_data.get('tweet_count', 0),
            user_data.get('account_creation_date')
        )
        
        # 6. Analisis kelengkapan profil
        scores['profile_completeness'] = self._analyze_profile_completeness(user_data)
        
        # 7. Analisis bio pattern
        scores['bio_pattern'] = self._analyze_bio_pattern(user_data.get('bio', ''))
        
        # Hitung skor total
        total_score = sum(scores[key] * self.bot_indicators[key] for key in scores)
        
        # Tentukan apakah bot
        is_bot = total_score > config.BOT_DETECTION_THRESHOLD
        
        # Generate explanation
        explanation = self._generate_explanation(scores, total_score)
        
        return {
            'bot_probability': round(total_score, 3),
            'is_bot': is_bot,
            'confidence_level': self._get_confidence_level(total_score),
            'scores': scores,
            'explanation': explanation,
            'risk_factors': self._identify_risk_factors(scores),
            'recommendations': self._get_recommendations(scores, is_bot)
        }
    
    def _analyze_username_pattern(self, username: str) -> float:
        """Analisis pattern username yang mencurigakan"""
        if not username:
            return 0.5
        
        suspicious_patterns = [
            r'^[a-zA-Z]+\d{4,}$',  # nama + angka panjang
            r'^[a-zA-Z]+_\d{4,}$',  # nama_angka
            r'^\d+[a-zA-Z]+\d+$',  # angka-huruf-angka
            r'^(user|bot|account)\d+$',  # user/bot/account + angka
            r'^[a-zA-Z]{1,3}\d{6,}$',  # huruf pendek + angka panjang
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, username, re.IGNORECASE):
                return 0.8
        
        # Cek karakter berulang
        if len(set(username)) < len(username) * 0.5:
            return 0.6
        
        # Cek panjang username
        if len(username) > 15:
            return 0.4
        
        return 0.1
    
    def _analyze_display_name_pattern(self, display_name: str) -> float:
        """Analisis pattern display name"""
        if not display_name:
            return 0.3
        
        # Cek karakter aneh atau emoji berlebihan
        emoji_count = len(re.findall(r'[^\w\s]', display_name))
        if emoji_count > len(display_name) * 0.3:
            return 0.6
        
        # Cek nama yang terlalu umum
        generic_names = ['user', 'account', 'info', 'news', 'update', 'official']
        if any(name in display_name.lower() for name in generic_names):
            return 0.5
        
        return 0.1
    
    def _analyze_follower_ratio(self, followers: int, following: int) -> float:
        """Analisis rasio follower/following"""
        if followers == 0 and following == 0:
            return 0.7  # Akun kosong
        
        if followers == 0:
            return 0.8  # Tidak ada follower
        
        ratio = following / followers
        
        if ratio > 10:  # Following jauh lebih banyak
            return 0.9
        elif ratio > 5:
            return 0.7
        elif ratio > 2:
            return 0.5
        elif ratio < 0.1:  # Follower jauh lebih banyak (bisa jadi bot yang di-follow banyak orang)
            return 0.3
        else:
            return 0.1
    
    def _analyze_account_age(self, creation_date) -> float:
        """Analisis umur akun"""
        if not creation_date:
            return 0.5
        
        if isinstance(creation_date, str):
            try:
                creation_date = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
            except:
                return 0.5
        
        age = datetime.now() - creation_date.replace(tzinfo=None)
        age_days = age.days
        
        if age_days < 30:  # Kurang dari 1 bulan
            return 0.8
        elif age_days < 90:  # Kurang dari 3 bulan
            return 0.6
        elif age_days < 365:  # Kurang dari 1 tahun
            return 0.3
        else:
            return 0.1
    
    def _analyze_tweet_frequency(self, tweet_count: int, creation_date) -> float:
        """Analisis frekuensi tweet"""
        if not creation_date or tweet_count == 0:
            return 0.5
        
        if isinstance(creation_date, str):
            try:
                creation_date = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
            except:
                return 0.5
        
        age = datetime.now() - creation_date.replace(tzinfo=None)
        age_days = max(age.days, 1)  # Minimal 1 hari
        
        tweets_per_day = tweet_count / age_days
        
        if tweets_per_day > 50:  # Lebih dari 50 tweet per hari
            return 0.9
        elif tweets_per_day > 20:  # Lebih dari 20 tweet per hari
            return 0.7
        elif tweets_per_day > 10:  # Lebih dari 10 tweet per hari
            return 0.5
        elif tweets_per_day < 0.1:  # Kurang dari 1 tweet per 10 hari
            return 0.3
        else:
            return 0.1
    
    def _analyze_profile_completeness(self, user_data: Dict[str, Any]) -> float:
        """Analisis kelengkapan profil"""
        completeness_score = 0
        total_fields = 5
        
        if user_data.get('bio'):
            completeness_score += 1
        if user_data.get('profile_image_url'):
            completeness_score += 1
        if user_data.get('verified'):
            completeness_score += 1
        if user_data.get('display_name'):
            completeness_score += 1
        if user_data.get('followers_count', 0) > 0:
            completeness_score += 1
        
        incompleteness_ratio = 1 - (completeness_score / total_fields)
        
        # Profil yang tidak lengkap lebih mencurigakan
        return incompleteness_ratio * 0.8
    
    def _analyze_bio_pattern(self, bio: str) -> float:
        """Analisis pattern bio"""
        if not bio:
            return 0.4
        
        # Cek bio yang terlalu pendek
        if len(bio) < 10:
            return 0.6
        
        # Cek kata kunci bot
        bot_keywords = ['bot', 'automated', 'auto', 'script', 'program']
        if any(keyword in bio.lower() for keyword in bot_keywords):
            return 0.9
        
        # Cek link spam
        link_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', bio))
        if link_count > 2:
            return 0.7
        
        # Cek karakter berulang
        if len(set(bio)) < len(bio) * 0.3:
            return 0.5
        
        return 0.1
    
    def _generate_explanation(self, scores: Dict[str, float], total_score: float) -> str:
        """Generate penjelasan hasil deteksi"""
        high_risk_factors = []
        
        for factor, score in scores.items():
            if score > 0.6:
                high_risk_factors.append(self._get_factor_name(factor))
        
        if total_score > 0.8:
            explanation = f"Akun ini memiliki probabilitas tinggi ({total_score:.1%}) sebagai bot. "
        elif total_score > 0.6:
            explanation = f"Akun ini memiliki probabilitas sedang ({total_score:.1%}) sebagai bot. "
        else:
            explanation = f"Akun ini memiliki probabilitas rendah ({total_score:.1%}) sebagai bot. "
        
        if high_risk_factors:
            explanation += f"Faktor risiko utama: {', '.join(high_risk_factors)}."
        
        return explanation
    
    def _get_factor_name(self, factor: str) -> str:
        """Dapatkan nama faktor dalam bahasa Indonesia"""
        factor_names = {
            'username_pattern': 'pola username mencurigakan',
            'display_name_pattern': 'pola nama tampilan mencurigakan',
            'follower_ratio': 'rasio follower/following tidak normal',
            'account_age': 'akun terlalu baru',
            'tweet_frequency': 'frekuensi tweet tidak normal',
            'profile_completeness': 'profil tidak lengkap',
            'bio_pattern': 'pola bio mencurigakan'
        }
        return factor_names.get(factor, factor)
    
    def _get_confidence_level(self, score: float) -> str:
        """Dapatkan tingkat kepercayaan"""
        if score > 0.8:
            return 'tinggi'
        elif score > 0.6:
            return 'sedang'
        else:
            return 'rendah'
    
    def _identify_risk_factors(self, scores: Dict[str, float]) -> List[str]:
        """Identifikasi faktor risiko"""
        risk_factors = []
        
        for factor, score in scores.items():
            if score > 0.6:
                risk_factors.append(self._get_factor_name(factor))
        
        return risk_factors
    
    def _get_recommendations(self, scores: Dict[str, float], is_bot: bool) -> List[str]:
        """Dapatkan rekomendasi"""
        recommendations = []
        
        if is_bot:
            recommendations.append("Berhati-hati dengan informasi dari akun ini")
            recommendations.append("Verifikasi informasi dari sumber lain")
            recommendations.append("Pertimbangkan untuk melaporkan akun jika mencurigakan")
        else:
            recommendations.append("Akun tampak normal, namun tetap verifikasi informasi")
            recommendations.append("Periksa kredibilitas berdasarkan konten yang dibagikan")
        
        # Rekomendasi spesifik berdasarkan faktor risiko
        if scores.get('follower_ratio', 0) > 0.6:
            recommendations.append("Periksa kualitas follower dan following")
        
        if scores.get('account_age', 0) > 0.6:
            recommendations.append("Akun masih baru, tunggu track record lebih lama")
        
        if scores.get('tweet_frequency', 0) > 0.6:
            recommendations.append("Frekuensi posting tidak normal, periksa pola aktivitas")
        
        return recommendations[:5]  # Batasi maksimal 5 rekomendasi
    
    def batch_detect_bots(self, users_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deteksi bot untuk multiple users"""
        results = []
        
        for user_data in users_data:
            result = self.detect_bot(user_data)
            result['user_id'] = user_data.get('user_id')
            result['username'] = user_data.get('username')
            results.append(result)
        
        return results
    
    def get_bot_statistics(self, detection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dapatkan statistik deteksi bot"""
        total_accounts = len(detection_results)
        bot_accounts = sum(1 for result in detection_results if result.get('is_bot', False))
        
        if total_accounts == 0:
            return {
                'total_accounts': 0,
                'bot_accounts': 0,
                'bot_percentage': 0,
                'average_bot_probability': 0
            }
        
        average_probability = sum(result.get('bot_probability', 0) for result in detection_results) / total_accounts
        
        return {
            'total_accounts': total_accounts,
            'bot_accounts': bot_accounts,
            'human_accounts': total_accounts - bot_accounts,
            'bot_percentage': round((bot_accounts / total_accounts) * 100, 1),
            'average_bot_probability': round(average_probability, 3)
        } 