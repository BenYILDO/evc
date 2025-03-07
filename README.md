# Elektrikli Şarj İstasyonu Lokasyon Analiz Sistemi

Elektrikli araç şarj istasyonlarının lokasyon analizini yapan bir web uygulaması. Bu proje, yatırımcıların ve genel kullanıcıların elektrikli şarj istasyonlarının konumlarını analiz etmesine, yeni istasyonlar için uygun lokasyonları belirlemesine ve yatırım getirisi hesaplamalarını yapmasına olanak tanır.

## Özellikler

- **Harita Tabanlı Görselleştirme**: Türkiye'deki mevcut şarj istasyonlarını interaktif harita üzerinde görüntüleme
- **Lokasyon Analizi**: Seçilen konumun şarj istasyonu kurulumu için uygunluğunu değerlendirme
- **Demografik Analiz**: Bölgelerin demografik verilerine ve trafik yoğunluğuna dayalı analiz
- **Rakip Analizi**: Mevcut operatörlerin pazar paylarını ve performanslarını karşılaştırma
- **Yatırım Getirisi Hesaplama**: Seçilen konum ve yatırım parametrelerine göre ROI tahmini
- **Rapor Oluşturma**: Analiz sonuçlarını detaylı rapor halinde alma

## Kurulum

```bash
# Depoyu klonlayın
git clone https://github.com/kullanici/elektrikli-sarj-istasyonu-analizi.git
cd elektrikli-sarj-istasyonu-analizi

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
streamlit run app.py
```

## Kullanım

1. Uygulama başlatıldığında, sol taraftaki kenar çubuğundan "Yatırımcı" veya "Genel Kullanıcı" modunu seçin.
2. Yatırımcı modunda:
   - "Bölge Analizi" sekmesinde harita üzerinde bir konum seçin ve "Bölgeyi Analiz Et" butonuna tıklayın.
   - Konum analiz sonuçlarını, demografik verileri ve önerileri görüntüleyin.
   - "Rakip Analizi" sekmesinde operatörlerin karşılaştırmalı analizlerini inceleyin.
   - "Yatırım Getirisi" sekmesinde finansal projeksiyonları ve tahmini geri dönüş süresini görüntüleyin.
   - "Rapor Oluştur" sekmesinde tüm analiz sonuçlarını içeren detaylı bir rapor oluşturun.
3. Genel Kullanıcı modunda:
   - "Şarj İstasyonu Haritası" sekmesinde Türkiye'deki mevcut şarj istasyonlarını görüntüleyin.
   - "İstatistikler" sekmesinde operatör dağılımı, güç dağılımı ve şehir karşılaştırması gibi istatistikleri inceleyin.
   - "Demografik Analiz" sekmesinde şehirlerin demografik ve trafik verilerini görüntüleyin.

## Veri Kaynakları

Uygulama şu anda suni veriler kullanmaktadır. Gerçek verilerle çalışması için aşağıdaki kaynaklar entegre edilebilir:

- Elektrikli araç şarj istasyonu verileri (resmi operatör verileri)
- TÜİK demografik verileri
- Trafik yoğunluğu verileri
- Elektrikli araç kullanım oranları
- Gelir ve sosyoekonomik veriler

## Teknik Detaylar

- **Programlama Dili**: Python
- **Web Çatısı**: Streamlit
- **Görselleştirme Kütüphaneleri**: Folium, Plotly, Matplotlib
- **Veri İşleme**: Pandas, NumPy
- **Analitik Modeller**: Scikit-learn

## Gelecek Geliştirmeler

- Gerçek verilerin entegrasyonu
- Daha gelişmiş tahmin modelleri
- Elektrik şebekesi verilerinin entegrasyonu
- Mobil uygulama versiyonu
- API hizmeti

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## İletişim

Proje sahibi: [Ad Soyad](mailto:email@example.com)

Elektrikli Şarj İstasyonu Lokasyon Analiz Sistemi, Endüstri Mühendisliği Bitirme Projesi kapsamında geliştirilmiştir. 
