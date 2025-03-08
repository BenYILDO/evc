import json
import os
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Optional

def get_districts(city: str) -> List[str]:
    """Seçilen ile ait ilçeleri döndürür."""
    # Örnek ilçe verileri (gerçek API'den alınabilir)
    district_data = {
        "İstanbul": [
            "Kadıköy", "Beşiktaş", "Şişli", "Üsküdar", "Beyoğlu", "Bakırköy",
            "Maltepe", "Ataşehir", "Kartal", "Pendik", "Ümraniye", "Sarıyer"
        ],
        "Ankara": [
            "Çankaya", "Yenimahalle", "Keçiören", "Mamak", "Etimesgut",
            "Sincan", "Altındağ", "Gölbaşı", "Pursaklar"
        ],
        "İzmir": [
            "Konak", "Karşıyaka", "Bornova", "Buca", "Çiğli", "Balçova",
            "Gaziemir", "Narlıdere", "Bayraklı", "Karabağlar"
        ]
    }
    
    return district_data.get(city, ["Merkez"])

def get_neighborhoods(city: str, district: str) -> List[str]:
    """Seçilen ilçeye ait mahalleleri döndürür."""
    # Örnek mahalle verileri (gerçek API'den alınabilir)
    if district == "Tüm İlçeler":
        return []
    
    neighborhood_data = {
        "Kadıköy": [
            "Caferağa", "Fenerbahçe", "Göztepe", "Koşuyolu", "Moda",
            "Osmanağa", "Rasimpaşa", "Suadiye", "Zühtüpaşa"
        ],
        "Çankaya": [
            "Bahçelievler", "Çukurambar", "Kızılay", "Dikmen", "Ayrancı",
            "Çayyolu", "Oran", "Yıldız", "Gaziosmanpaşa"
        ],
        "Konak": [
            "Alsancak", "Göztepe", "Güzelyalı", "Hatay", "Karabağlar",
            "Yeşilyurt", "Üçkuyular"
        ]
    }
    
    return neighborhood_data.get(district, ["Merkez"])

def analyze_area(city: str, district: str, neighborhood: Optional[str] = None) -> List[Dict]:
    """Seçilen bölgedeki potansiyel lokasyonları analiz eder."""
    # Örnek potansiyel lokasyonlar (gerçek verilerle değiştirilmeli)
    potential_locations = []
    
    # Her bölge için 3-7 arası potansiyel lokasyon oluştur
    num_locations = np.random.randint(3, 8)
    
    for i in range(num_locations):
        # Bölgeye göre koordinat aralıkları (gerçek koordinatlarla değiştirilmeli)
        if city == "İstanbul":
            lat = np.random.uniform(40.9, 41.1)
            lon = np.random.uniform(28.9, 29.3)
        else:
            lat = np.random.uniform(39.0, 40.0)
            lon = np.random.uniform(32.0, 33.0)
        
        location = {
            "lat": lat,
            "lon": lon,
            "address": f"{neighborhood or district}, {city}",
            "score": np.random.randint(60, 100),
            "daily_traffic": np.random.randint(5000, 50000),
            "nearby_businesses": np.random.randint(10, 100),
            "competition_level": np.random.choice(["Düşük", "Orta", "Yüksek"]),
            "estimated_revenue": np.random.randint(50000, 200000),
            "roi_months": np.random.randint(24, 60),
            "risk_level": np.random.choice(["Düşük", "Orta", "Yüksek"])
        }
        
        potential_locations.append(location)
    
    # Puana göre sırala
    return sorted(potential_locations, key=lambda x: x["score"], reverse=True)

def create_area_analysis_map(
    potential_locations: List[Dict],
    city: str,
    district: str,
    neighborhood: Optional[str] = None
) -> "folium.Map":
    """Potansiyel lokasyonları gösteren bir harita oluşturur."""
    import folium
    from folium import plugins
    
    # Harita merkezini belirle
    center_lat = sum(loc["lat"] for loc in potential_locations) / len(potential_locations)
    center_lon = sum(loc["lon"] for loc in potential_locations) / len(potential_locations)
    
    # Haritayı oluştur
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    # Isı haritası verilerini hazırla
    heat_data = [[loc["lat"], loc["lon"], loc["score"]/100] for loc in potential_locations]
    
    # Isı haritası ekle
    plugins.HeatMap(heat_data).add_to(m)
    
    # Her potansiyel lokasyon için marker ekle
    for loc in potential_locations:
        popup_html = f"""
        <div style='width: 200px'>
            <h4>Lokasyon Puanı: {loc['score']}/100</h4>
            <p><b>Günlük Trafik:</b> {loc['daily_traffic']:,}</p>
            <p><b>Yakın İşletmeler:</b> {loc['nearby_businesses']}</p>
            <p><b>Rekabet:</b> {loc['competition_level']}</p>
            <p><b>Tahmini Gelir:</b> ₺{loc['estimated_revenue']:,}</p>
            <p><b>Geri Dönüş:</b> {loc['roi_months']} ay</p>
            <p><b>Risk:</b> {loc['risk_level']}</p>
        </div>
        """
        
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(
                color='red' if loc["score"] >= 80 else 'orange' if loc["score"] >= 60 else 'blue',
                icon='info-sign'
            )
        ).add_to(m)
    
    return m 
