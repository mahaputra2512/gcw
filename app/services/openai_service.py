import openai
import json
import re
from typing import Dict, Any, List
from app.config import config

class OpenAIService:
    """Service untuk analisis hoax menggunakan OpenAI"""
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
    
    def analyze_hoax(self, tweet_text: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisis apakah tweet mengandung hoax atau tidak"""
        
        # Buat prompt untuk analisis hoax
        prompt = self._create_hoax_analysis_prompt(tweet_text, user_data)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Anda adalah ahli fact-checker dan analisis hoax di media sosial. Analisis dengan objektif dan berdasarkan bukti."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse hasil analisis
            analysis_result = self._parse_analysis_result(analysis_text)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in OpenAI analysis: {e}")
            # Fallback ke analisis rule-based sederhana
            return self._fallback_analysis(tweet_text, user_data)
    
    def _create_hoax_analysis_prompt(self, tweet_text: str, user_data: Dict[str, Any]) -> str:
        """Buat prompt untuk analisis hoax"""
        
        prompt = f"""
        Analisis tweet berikut untuk mendeteksi apakah berpotensi hoax atau misinformasi:

        TWEET: "{tweet_text}"

        INFORMASI PENGGUNA:
        - Username: @{user_data.get('username', 'unknown')}
        - Display Name: {user_data.get('display_name', 'unknown')}
        - Bio: {user_data.get('bio', 'tidak ada')}
        - Followers: {user_data.get('followers_count', 0):,}
        - Following: {user_data.get('following_count', 0):,}
        - Total Tweet: {user_data.get('tweet_count', 0):,}
        - Verified: {'Ya' if user_data.get('verified', False) else 'Tidak'}

        KRITERIA ANALISIS:
        1. Klaim yang tidak didukung bukti
        2. Bahasa sensasional atau clickbait
        3. Informasi medis/kesehatan tanpa sumber
        4. Klaim politik yang tidak terverifikasi
        5. Informasi bencana atau darurat yang tidak resmi
        6. Konspirasi atau teori tidak berdasar
        7. Informasi keuangan/ekonomi yang mencurigakan

        BERIKAN ANALISIS DALAM FORMAT JSON:
        {{
            "hoax_probability": [0.0-1.0],
            "is_hoax": [true/false],
            "confidence_level": ["rendah"/"sedang"/"tinggi"],
            "analysis_summary": "ringkasan analisis dalam bahasa Indonesia",
            "red_flags": ["daftar", "tanda", "bahaya"],
            "reasons": ["alasan 1", "alasan 2", "dst"],
            "category": "kategori hoax (political/health/disaster/celebrity/financial/conspiracy/normal)",
            "recommendations": ["saran untuk pembaca"]
        }}

        Berikan respons dalam format JSON yang valid.
        """
        
        return prompt
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """Parse hasil analisis dari OpenAI"""
        try:
            # Coba extract JSON dari respons
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validasi dan normalisasi hasil
                return {
                    'hoax_probability': float(result.get('hoax_probability', 0.0)),
                    'is_hoax': bool(result.get('is_hoax', False)),
                    'confidence_level': result.get('confidence_level', 'sedang'),
                    'analysis_summary': result.get('analysis_summary', ''),
                    'red_flags': result.get('red_flags', []),
                    'reasons': result.get('reasons', []),
                    'category': result.get('category', 'normal'),
                    'recommendations': result.get('recommendations', []),
                    'raw_analysis': analysis_text
                }
            else:
                # Jika tidak ada JSON, gunakan fallback
                return self._fallback_analysis_from_text(analysis_text)
                
        except Exception as e:
            print(f"Error parsing OpenAI result: {e}")
            return self._fallback_analysis_from_text(analysis_text)
    
    def _fallback_analysis(self, tweet_text: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisis fallback berbasis rule jika OpenAI gagal"""
        
        # Keywords yang mencurigakan
        hoax_keywords = [
            'breaking', 'urgent', 'viral', 'rahasia', 'tersembunyi', 'konspirasi',
            'jangan percaya', 'pemerintah menyembunyikan', 'fakta tersembunyi',
            'akan terjadi', 'prediksi', 'ramalan', 'paranormal', 'chip 5g',
            'vaksin berbahaya', 'obat ajaib', 'sembuh total', 'tanpa efek samping'
        ]
        
        # Hitung skor hoax berdasarkan keywords
        text_lower = tweet_text.lower()
        keyword_matches = sum(1 for keyword in hoax_keywords if keyword in text_lower)
        
        # Analisis user metrics
        user_suspicious_score = 0
        followers = user_data.get('followers_count', 0)
        following = user_data.get('following_count', 0)
        
        # Rasio following/followers yang mencurigakan
        if followers > 0:
            ratio = following / followers
            if ratio > 2:  # Following jauh lebih banyak dari followers
                user_suspicious_score += 0.3
        
        # Akun baru dengan followers sedikit
        if followers < 100:
            user_suspicious_score += 0.2
        
        # Hitung probabilitas hoax
        content_score = min(keyword_matches * 0.2, 0.7)
        total_score = min(content_score + user_suspicious_score, 1.0)
        
        return {
            'hoax_probability': total_score,
            'is_hoax': total_score > config.HOAX_THRESHOLD,
            'confidence_level': 'sedang',
            'analysis_summary': f'Analisis berdasarkan {keyword_matches} kata kunci mencurigakan dan metrik akun pengguna.',
            'red_flags': [keyword for keyword in hoax_keywords if keyword in text_lower],
            'reasons': self._generate_fallback_reasons(keyword_matches, user_suspicious_score),
            'category': self._classify_category(text_lower),
            'recommendations': [
                'Verifikasi informasi dari sumber terpercaya',
                'Periksa tanggal dan konteks informasi',
                'Cari konfirmasi dari media massa resmi'
            ],
            'raw_analysis': 'Analisis menggunakan sistem rule-based (fallback)'
        }
    
    def _fallback_analysis_from_text(self, analysis_text: str) -> Dict[str, Any]:
        """Buat analisis fallback dari teks yang tidak bisa diparsing"""
        
        # Coba deteksi indikator hoax dari teks
        hoax_indicators = ['hoax', 'palsu', 'tidak benar', 'misinformasi', 'mencurigakan']
        is_hoax = any(indicator in analysis_text.lower() for indicator in hoax_indicators)
        
        return {
            'hoax_probability': 0.6 if is_hoax else 0.3,
            'is_hoax': is_hoax,
            'confidence_level': 'rendah',
            'analysis_summary': analysis_text[:200] + '...' if len(analysis_text) > 200 else analysis_text,
            'red_flags': [],
            'reasons': ['Analisis berdasarkan respons teks OpenAI'],
            'category': 'normal',
            'recommendations': [
                'Verifikasi lebih lanjut diperlukan',
                'Konsultasi dengan ahli terkait'
            ],
            'raw_analysis': analysis_text
        }
    
    def _generate_fallback_reasons(self, keyword_matches: int, user_score: float) -> List[str]:
        """Generate alasan untuk analisis fallback"""
        reasons = []
        
        if keyword_matches > 0:
            reasons.append(f"Mengandung {keyword_matches} kata kunci yang sering digunakan dalam hoax")
        
        if user_score > 0.2:
            reasons.append("Metrik akun pengguna menunjukkan karakteristik yang mencurigakan")
        
        if keyword_matches == 0 and user_score <= 0.2:
            reasons.append("Tidak ada indikator hoax yang jelas terdeteksi")
        
        return reasons
    
    def _classify_category(self, text_lower: str) -> str:
        """Klasifikasi kategori berdasarkan konten"""
        
        categories = {
            'health': ['vaksin', 'obat', 'virus', 'covid', 'kesehatan', 'penyakit', 'dokter'],
            'political': ['pemerintah', 'presiden', 'politik', 'pemilu', 'partai', 'menteri'],
            'disaster': ['gempa', 'banjir', 'tsunami', 'bencana', 'darurat', 'evakuasi'],
            'celebrity': ['artis', 'selebriti', 'aktor', 'penyanyi', 'viral'],
            'financial': ['investasi', 'saham', 'crypto', 'bitcoin', 'uang', 'bisnis'],
            'conspiracy': ['konspirasi', 'rahasia', 'tersembunyi', 'illuminati', 'freemason']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'normal'
    
    def get_fact_check_suggestions(self, tweet_text: str) -> List[str]:
        """Berikan saran untuk fact-checking"""
        
        suggestions = [
            "Cari sumber asli dari klaim yang dibuat",
            "Periksa tanggal dan konteks informasi",
            "Verifikasi dengan situs fact-checking terpercaya",
            "Cari konfirmasi dari media massa resmi",
            "Periksa kredibilitas penulis/sumber"
        ]
        
        # Tambahkan saran spesifik berdasarkan konten
        text_lower = tweet_text.lower()
        
        if any(word in text_lower for word in ['kesehatan', 'obat', 'vaksin']):
            suggestions.append("Konsultasi dengan tenaga medis profesional")
            suggestions.append("Periksa situs resmi Kementerian Kesehatan")
        
        if any(word in text_lower for word in ['politik', 'pemerintah', 'pemilu']):
            suggestions.append("Cek situs resmi instansi pemerintah terkait")
            suggestions.append("Verifikasi dengan komisi pemilihan umum")
        
        if any(word in text_lower for word in ['bencana', 'darurat', 'gempa']):
            suggestions.append("Periksa situs BMKG atau BNPB")
            suggestions.append("Verifikasi dengan media lokal terpercaya")
        
        return suggestions[:6]  # Batasi maksimal 6 saran 