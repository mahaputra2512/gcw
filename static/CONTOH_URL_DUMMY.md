# 📋 Contoh URL Dummy untuk Testing

Aplikasi ini menggunakan data dummy untuk demonstrasi. Anda bisa menggunakan URL Twitter/X apa saja untuk testing, sistem akan secara otomatis menggunakan data dummy yang telah disiapkan.

## 🔗 **Contoh URL yang Bisa Digunakan**

### **URL Twitter Klasik:**
```
https://twitter.com/user/status/1234567890
https://twitter.com/anyone/status/9876543210
https://twitter.com/test/status/1111111111
https://twitter.com/dummy/status/2222222222
https://twitter.com/sample/status/3333333333
https://twitter.com/demo/status/4444444444
https://twitter.com/hoax/status/5555555555
https://twitter.com/viral/status/6666666666
https://twitter.com/news/status/7777777777
https://twitter.com/breaking/status/8888888888
```

### **URL X.com (format baru):**
```
https://x.com/user/status/1234567890
https://x.com/anyone/status/9876543210
https://x.com/test/status/1111111111
https://x.com/dummy/status/2222222222
https://x.com/sample/status/3333333333
https://x.com/demo/status/4444444444
https://x.com/hoax/status/5555555555
https://x.com/viral/status/6666666666
https://x.com/news/status/7777777777
https://x.com/breaking/status/8888888888
```

### **URL dengan Mobile:**
```
https://mobile.twitter.com/user/status/1234567890
https://mobile.twitter.com/test/status/9876543210
https://mobile.twitter.com/demo/status/1111111111
```

## 📊 **Kategori Data Dummy**

Sistem akan secara random memilih dari berbagai kategori:

### **1. Hoax Politics (🚨 Hoax)**
- Kenaikan BBM palsu
- Pajak motor naik 200%
- Uang Rp 1000 dihapus
- Presiden mundur (hoax)

### **2. Hoax Health (🚨 Hoax)**
- Vaksin mengandung chip 5G
- Masker menyebabkan keracunan CO2
- Air lemon menyembuhkan kanker
- Konspirasi obat herbal

### **3. Hoax Disaster (🚨 Hoax)**
- Gempa berdasarkan paranormal
- Tsunami 50 meter
- Gunung Merapi meletus
- Banjir bandang palsu

### **4. Hoax Celebrity (🚨 Hoax)**
- Video artis berantem
- Artis meninggal hoax
- Scandal palsu
- Penangkapan palsu

### **5. Normal Content (✅ Normal)**
- Cuaca cerah
- Terima kasih subscriber
- Resep masakan
- Rencana weekend
- Rekomendasi buku

### **6. Information/Educational (✅ Normal)**
- Tips kesehatan
- Tips hemat listrik
- Data ekonomi
- Tips belajar bahasa
- Fakta ilmiah

### **7. Technology (✅ Normal)**
- iPhone 15 Pro
- Tesla mobil listrik
- Google AI Bard

### **8. Sports (✅ Normal)**
- Timnas Indonesia
- Lionel Messi
- Badminton Indonesia

## 👥 **Tipe User Dummy**

### **Suspicious Accounts (🤖 Potential Bots)**
- `@berita_update` - High following ratio
- `@info_viral` - Viral content spreader
- `@breaking_news24` - Breaking news spreader
- `@hoax_hunter` - Hoax hunter account
- `@viral_content` - Viral content account

### **Normal Users (👤 Human)**
- `@john_doe` - Regular person
- `@sarah_jakarta` - Housewife from Jakarta
- `@budi_programmer` - Software engineer
- `@maya_travel` - Travel blogger
- `@andi_student` - University student

### **Verified Accounts (✅ Trusted)**
- `@dr_health` - Medical doctor
- `@prof_ekonomi` - Economics professor
- `@journalist_indo` - Senior journalist
- `@bmkg_official` - BMKG official
- `@kemkes_ri` - Ministry of Health

### **Influencers (📱 Influencer)**
- `@influencer_lifestyle` - Lifestyle influencer
- `@tech_reviewer` - Tech reviewer
- `@food_blogger` - Food blogger

### **Bot-like Accounts (🤖 Suspicious)**
- `@user_123456` - Random user numbers
- `@bot_1234` - Bot accounts

## 🎯 **Cara Testing**

### **1. Quick Test:**
```
URL: https://twitter.com/test/status/123456
Hasil: Random tweet + user dari database dummy
```

### **2. Multiple Tests:**
Coba beberapa URL berbeda untuk melihat variasi data:
```
https://twitter.com/hoax/status/111111
https://twitter.com/normal/status/222222
https://twitter.com/viral/status/333333
```

### **3. Analyze Different Categories:**
Setiap URL akan menghasilkan kombinasi random dari:
- Tweet content (35+ variasi)
- User profile (20+ variasi)
- Metrics (followers, likes, retweets)
- Bot detection score
- Hoax probability

## 📈 **Contoh Hasil Analysis**

### **URL Hoax:**
- **Hoax Probability:** 80-95%
- **Bot Detection:** 60-90%
- **Fact Check:** Contradicting sources
- **Network:** High spread pattern

### **URL Normal:**
- **Hoax Probability:** 5-30%
- **Bot Detection:** 10-40%
- **Fact Check:** Supporting/neutral sources
- **Network:** Normal spread pattern

## 🔄 **Refresh Data**

Untuk mendapatkan data dummy baru:
1. Reload halaman
2. Gunakan URL berbeda
3. Restart aplikasi (data akan ter-randomize ulang)

## 🎨 **Kustomisasi Data Dummy**

Untuk menambah/edit data dummy:
1. **Tweet Content:** Edit `app/services/twitter_service.py` line 103
2. **User Profiles:** Edit `app/services/twitter_service.py` line 180
3. **Search Results:** Edit `app/services/brave_search_service.py` line 88

## 🚀 **Production Mode**

Untuk menggunakan API asli (bukan dummy):
1. Edit `app/main.py`
2. Ganti `use_real_api=False` menjadi `use_real_api=True`
3. Pastikan semua API key valid

---

**Happy Testing!** 🎉

Gunakan URL apa saja dari daftar di atas untuk melihat berbagai variasi hasil analisis dummy. 