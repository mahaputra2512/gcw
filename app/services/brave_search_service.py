import requests
import json
from typing import Dict, Any, List
from app.config import config
import random

class BraveSearchService:
    """Service untuk pencarian web dan fact-checking menggunakan Brave Search"""
    
    def __init__(self, use_real_api: bool = False):
        self.use_real_api = use_real_api
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": config.BRAVE_SEARCH_API_KEY
        }
    
    def search_for_fact_check(self, query: str, tweet_text: str) -> Dict[str, Any]:
        """Cari informasi untuk fact-checking"""
        
        if self.use_real_api:
            return self._real_search(query)
        else:
            return self._dummy_search(query, tweet_text)
    
    def _real_search(self, query: str) -> Dict[str, Any]:
        """Pencarian menggunakan Brave Search API asli"""
        try:
            params = {
                "q": query,
                "count": 10,
                "offset": 0,
                "mkt": "id-ID",  # Market Indonesia
                "safesearch": "moderate"
            }
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("web", {}).get("results", [])
            
            # Process results
            processed_results = []
            for result in results:
                processed_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "source": self._extract_domain(result.get("url", "")),
                    "relevance_score": self._calculate_relevance(result, query)
                })
            
            return {
                "query": query,
                "total_results": len(processed_results),
                "results": processed_results,
                "supporting_sources": self._categorize_sources(processed_results, "supporting"),
                "contradicting_sources": self._categorize_sources(processed_results, "contradicting"),
                "neutral_sources": self._categorize_sources(processed_results, "neutral")
            }
            
        except Exception as e:
            print(f"Error in Brave Search: {e}")
            return self._dummy_search(query, "")
    
    def _dummy_search(self, query: str, tweet_text: str) -> Dict[str, Any]:
        """Generate dummy search results untuk testing"""
        
        # Dummy results berdasarkan kategori
        dummy_results = self._generate_dummy_results(query, tweet_text)
        
        return {
            "query": query,
            "total_results": len(dummy_results),
            "results": dummy_results,
            "supporting_sources": self._categorize_sources(dummy_results, "supporting"),
            "contradicting_sources": self._categorize_sources(dummy_results, "contradicting"),
            "neutral_sources": self._categorize_sources(dummy_results, "neutral")
        }
    
    def _generate_dummy_results(self, query: str, tweet_text: str) -> List[Dict[str, Any]]:
        """Generate dummy search results yang realistis"""
        
        # Tentukan kategori berdasarkan tweet
        category = self._determine_category(tweet_text)
        
        if category == "hoax_health":
            return [
                {
                    "title": "Fakta atau Hoax: Klaim Vaksin Mengandung Chip 5G",
                    "url": "https://www.kompas.com/tren/read/2023/10/15/fakta-vaksin-chip-5g",
                    "description": "Klaim bahwa vaksin COVID-19 mengandung chip 5G telah dibantah oleh berbagai ahli kesehatan dan organisasi kesehatan dunia...",
                    "source": "kompas.com",
                    "relevance_score": 0.9,
                    "credibility": "tinggi",
                    "stance": "contradicting"
                },
                {
                    "title": "WHO Bantah Rumor Vaksin Berbahaya",
                    "url": "https://www.who.int/news/item/vaccine-safety-facts",
                    "description": "World Health Organization (WHO) memberikan klarifikasi mengenai keamanan vaksin COVID-19...",
                    "source": "who.int",
                    "relevance_score": 0.85,
                    "credibility": "tinggi",
                    "stance": "contradicting"
                },
                {
                    "title": "Vaksin COVID-19: Manfaat dan Efek Samping",
                    "url": "https://www.kemkes.go.id/article/view/21060300002/vaksin-covid-19",
                    "description": "Kementerian Kesehatan RI menjelaskan manfaat dan efek samping vaksin COVID-19...",
                    "source": "kemkes.go.id",
                    "relevance_score": 0.8,
                    "credibility": "tinggi",
                    "stance": "neutral"
                }
            ]
        
        elif category == "hoax_politics":
            return [
                {
                    "title": "Kenaikan Harga BBM: Fakta dan Rumor",
                    "url": "https://www.liputan6.com/bisnis/read/4567890/kenaikan-bbm-fakta-rumor",
                    "description": "Pemerintah belum mengumumkan kenaikan harga BBM. Informasi yang beredar di media sosial belum dikonfirmasi...",
                    "source": "liputan6.com",
                    "relevance_score": 0.9,
                    "credibility": "tinggi",
                    "stance": "contradicting"
                },
                {
                    "title": "Klarifikasi Kementerian ESDM tentang Harga BBM",
                    "url": "https://www.esdm.go.id/id/media-center/arsip-berita/klarifikasi-harga-bbm",
                    "description": "Kementerian ESDM memberikan klarifikasi resmi mengenai rumor kenaikan harga BBM...",
                    "source": "esdm.go.id",
                    "relevance_score": 0.85,
                    "credibility": "tinggi",
                    "stance": "contradicting"
                }
            ]
        
        elif category == "hoax_disaster":
            return [
                {
                    "title": "BMKG Bantah Prediksi Gempa Bumi Berdasarkan Paranormal",
                    "url": "https://www.bmkg.go.id/press-release/prediksi-gempa-paranormal",
                    "description": "BMKG menegaskan bahwa prediksi gempa bumi tidak dapat dilakukan berdasarkan paranormal atau hal-hal yang tidak ilmiah...",
                    "source": "bmkg.go.id",
                    "relevance_score": 0.95,
                    "credibility": "tinggi",
                    "stance": "contradicting"
                },
                {
                    "title": "Cara Kerja Sistem Peringatan Dini Gempa",
                    "url": "https://www.bmkg.go.id/edukasi/gempa-bumi/sistem-peringatan-dini",
                    "description": "BMKG menjelaskan bagaimana sistem peringatan dini gempa bumi bekerja dan mengapa prediksi akurat sangat sulit...",
                    "source": "bmkg.go.id",
                    "relevance_score": 0.8,
                    "credibility": "tinggi",
                    "stance": "neutral"
                }
            ]
        
        else:  # normal content
            return [
                {
                    "title": "Manfaat Kopi untuk Kesehatan Jantung",
                    "url": "https://www.halodoc.com/artikel/manfaat-kopi-untuk-jantung",
                    "description": "Penelitian menunjukkan bahwa konsumsi kopi dalam jumlah sedang dapat memberikan manfaat untuk kesehatan jantung...",
                    "source": "halodoc.com",
                    "relevance_score": 0.7,
                    "credibility": "sedang",
                    "stance": "supporting"
                },
                {
                    "title": "Studi: Kopi Dapat Mengurangi Risiko Penyakit Jantung",
                    "url": "https://www.cnnindonesia.com/gaya-hidup/20231015123456-255-123456/studi-kopi-jantung",
                    "description": "Studi terbaru dari European Society of Cardiology menunjukkan hubungan positif antara konsumsi kopi dan kesehatan jantung...",
                    "source": "cnnindonesia.com",
                    "relevance_score": 0.8,
                    "credibility": "tinggi",
                    "stance": "supporting"
                }
            ]
    
    def _determine_category(self, text: str) -> str:
        """Tentukan kategori berdasarkan konten tweet"""
        text_lower = text.lower()
        
        health_keywords = ['vaksin', 'covid', 'obat', 'kesehatan', 'virus', 'chip 5g']
        politics_keywords = ['pemerintah', 'bbm', 'harga', 'politik', 'menteri']
        disaster_keywords = ['gempa', 'bencana', 'tsunami', 'banjir', 'darurat', 'paranormal']
        
        if any(keyword in text_lower for keyword in health_keywords):
            return "hoax_health"
        elif any(keyword in text_lower for keyword in politics_keywords):
            return "hoax_politics"
        elif any(keyword in text_lower for keyword in disaster_keywords):
            return "hoax_disaster"
        else:
            return "normal"
    
    def _categorize_sources(self, results: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Kategorikan sumber berdasarkan stance mereka"""
        return [result for result in results if result.get('stance') == category]
    
    def _extract_domain(self, url: str) -> str:
        """Ekstrak domain dari URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url
    
    def _calculate_relevance(self, result: Dict[str, Any], query: str) -> float:
        """Hitung skor relevansi (simplified)"""
        # Simplified relevance calculation
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        query_lower = query.lower()
        
        relevance = 0.0
        query_words = query_lower.split()
        
        for word in query_words:
            if word in title:
                relevance += 0.4
            if word in description:
                relevance += 0.2
        
        return min(relevance, 1.0)
    
    def get_source_credibility(self, domain: str) -> Dict[str, Any]:
        """Evaluasi kredibilitas sumber"""
        
        # Daftar sumber terpercaya
        trusted_sources = {
            "kemkes.go.id": {"credibility": "tinggi", "type": "pemerintah"},
            "bmkg.go.id": {"credibility": "tinggi", "type": "pemerintah"},
            "who.int": {"credibility": "tinggi", "type": "internasional"},
            "kompas.com": {"credibility": "tinggi", "type": "media"},
            "detik.com": {"credibility": "tinggi", "type": "media"},
            "cnn.com": {"credibility": "tinggi", "type": "media"},
            "bbc.com": {"credibility": "tinggi", "type": "media"},
            "reuters.com": {"credibility": "tinggi", "type": "media"},
            "liputan6.com": {"credibility": "sedang", "type": "media"},
            "okezone.com": {"credibility": "sedang", "type": "media"},
            "tribunnews.com": {"credibility": "sedang", "type": "media"}
        }
        
        # Sumber yang kurang kredibel
        suspicious_sources = {
            "blog.com": {"credibility": "rendah", "type": "blog"},
            "wordpress.com": {"credibility": "rendah", "type": "blog"},
            "blogspot.com": {"credibility": "rendah", "type": "blog"}
        }
        
        # Cek domain
        if domain in trusted_sources:
            return trusted_sources[domain]
        elif domain in suspicious_sources:
            return suspicious_sources[domain]
        elif domain.endswith(".go.id"):
            return {"credibility": "tinggi", "type": "pemerintah"}
        elif domain.endswith(".edu"):
            return {"credibility": "tinggi", "type": "akademik"}
        elif domain.endswith(".org"):
            return {"credibility": "sedang", "type": "organisasi"}
        else:
            return {"credibility": "sedang", "type": "umum"}
    
    def generate_fact_check_summary(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ringkasan fact-checking"""
        
        supporting = len(search_results.get("supporting_sources", []))
        contradicting = len(search_results.get("contradicting_sources", []))
        neutral = len(search_results.get("neutral_sources", []))
        
        total = supporting + contradicting + neutral
        
        if total == 0:
            return {
                "summary": "Tidak ditemukan informasi yang cukup untuk verifikasi.",
                "confidence": "rendah",
                "recommendation": "Perlu pencarian lebih lanjut dengan kata kunci yang berbeda."
            }
        
        # Hitung persentase
        support_pct = (supporting / total) * 100
        contradict_pct = (contradicting / total) * 100
        
        if contradict_pct > 50:
            return {
                "summary": f"Mayoritas sumber ({contradict_pct:.1f}%) tidak mendukung klaim ini.",
                "confidence": "tinggi",
                "recommendation": "Klaim kemungkinan tidak akurat atau hoax."
            }
        elif support_pct > 50:
            return {
                "summary": f"Mayoritas sumber ({support_pct:.1f}%) mendukung klaim ini.",
                "confidence": "sedang",
                "recommendation": "Klaim kemungkinan akurat, namun perlu verifikasi tambahan."
            }
        else:
            return {
                "summary": "Sumber-sumber menunjukkan hasil yang beragam.",
                "confidence": "sedang",
                "recommendation": "Diperlukan analisis lebih mendalam untuk menentukan keakuratan."
            } 