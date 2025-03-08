import requests
import pandas as pd
import numpy as np
from datetime import datetime

API_KEY = "390bef26-9ab6-4f3d-ac2c-e48e7012f7ce"
BASE_URL = "https://api.openchargemap.io/v3"

# Türkiye'nin 81 ili
TURKEY_CITIES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin",
    "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale",
    "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum",
    "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Isparta", "Mersin",
    "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli",
    "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt",
    "Karaman", "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük",
    "Kilis", "Osmaniye", "Düzce"
]

def normalize_city_name(city_name):
    """Şehir ismini standart formata dönüştürür."""
    if not isinstance(city_name, str):
        return "Bilinmeyen Şehir"
    
    # Şehir ismini temizle
    city = city_name.split("/")[0].strip()
    
    # İstanbul'un özel ilçeleri için kontrol
    istanbul_districts = ["Kadıköy", "Beşiktaş", "Şişli", "Bakırköy", "Beyoğlu"]
    if city in istanbul_districts:
        return "İstanbul"
    
    # Diğer büyükşehirlerin ilçeleri için benzer kontroller eklenebilir
    
    # En yakın il ismini bul
    for valid_city in TURKEY_CITIES:
        if city.lower() in valid_city.lower() or valid_city.lower() in city.lower():
            return valid_city
    
    return "Bilinmeyen Şehir"

def fetch_charging_stations(country_code="TR"):
    """OpenChargeMap API'sinden Türkiye'deki şarj istasyonlarını çeker."""
    
    headers = {
        "X-API-Key": API_KEY,
        "User-Agent": "ElektrikliSarjIstasyonuAnalizi/1.0"
    }
    
    params = {
        "countrycode": country_code,
        "maxresults": 1000,
        "compact": True,
        "verbose": False,
        "includecomments": False
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/poi",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        stations = []
        for station in data:
            raw_city = station.get("AddressInfo", {}).get("Town", "Bilinmeyen Şehir")
            normalized_city = normalize_city_name(raw_city)
            
            if normalized_city != "Bilinmeyen Şehir":  # Sadece geçerli şehirleri ekle
                station_data = {
                    "station_id": station.get("ID"),
                    "name": station.get("AddressInfo", {}).get("Title", "Bilinmeyen İstasyon"),
                    "operator": station.get("OperatorInfo", {}).get("Title", "Bilinmeyen Operatör"),
                    "latitude": station.get("AddressInfo", {}).get("Latitude"),
                    "longitude": station.get("AddressInfo", {}).get("Longitude"),
                    "city": normalized_city,
                    "address": station.get("AddressInfo", {}).get("AddressLine1", ""),
                    "charger_count": len(station.get("Connections", [])),
                    "status": station.get("StatusType", {}).get("Title", "Bilinmeyen"),
                    "last_updated": station.get("DateLastStatusUpdate")
                }
                
                connections = station.get("Connections", [])
                if connections:
                    max_power = max([
                        conn.get("PowerKW", 0) or 0
                        for conn in connections
                    ])
                    station_data["power_kw"] = max_power if max_power > 0 else None
                    
                    connection_types = set([
                        conn.get("ConnectionType", {}).get("Title", "")
                        for conn in connections
                    ])
                    station_data["connection_types"] = ", ".join(filter(None, connection_types))
                
                stations.append(station_data)
        
        df = pd.DataFrame(stations)
        
        # Eksik değerleri doldur
        df["power_kw"] = df["power_kw"].fillna(50)
        df["charger_count"] = df["charger_count"].fillna(1)
        
        # Simüle edilmiş değerler ekle
        df["avg_daily_usage"] = np.random.randint(5, 40, size=len(df))
        df["customer_rating"] = np.random.uniform(3.0, 5.0, size=len(df)).round(1)
        df["installation_year"] = np.random.randint(2018, 2024, size=len(df))
        df["installation_cost"] = np.random.randint(20000, 150000, size=len(df))
        df["monthly_revenue"] = df["avg_daily_usage"] * 30 * 75
        df["operational_cost"] = df["installation_cost"] * 0.02 + 5000
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"API çağrısı sırasında hata oluştu: {e}")
        return None

def generate_demographic_data(cities):
    """Şehirler için demografik veri oluşturur."""
    # TÜİK verilerini kullanarak gerçeğe yakın değerler
    city_data = {
        "İstanbul": 15462000, "Ankara": 5639000, "İzmir": 4367000, "Bursa": 3056000,
        "Antalya": 2511000, "Adana": 2237000, "Konya": 2232000, "Gaziantep": 2069000,
        "Şanlıurfa": 2073000, "Mersin": 1840000, "Diyarbakır": 1756000, "Kayseri": 1400000,
        "Eskişehir": 871000, "Samsun": 1335000, "Denizli": 1033000
    }
    
    # Eksik şehirler için varsayılan değerler
    for city in TURKEY_CITIES:
        if city not in city_data:
            city_data[city] = np.random.randint(300000, 1000000)
    
    demographic_data = []
    for city in cities:
        if city in TURKEY_CITIES:  # Sadece geçerli şehirler için veri oluştur
            population = city_data.get(city, 500000)
            data = {
                "city": city,
                "population": population,
                "ev_adoption_rate": round(np.random.uniform(0.01, 0.15), 3),
                "avg_income": int(np.random.uniform(5000, 20000)),
                "urbanization_rate": round(np.random.uniform(0.65, 0.95), 2),
                "avg_age": int(np.random.uniform(32, 45)),
                "public_transport_usage": round(np.random.uniform(0.1, 0.6), 2),
                "tourism_score": int(np.random.uniform(1, 10)),
                "growth_potential": round(np.random.uniform(0.01, 0.08), 3)
            }
            demographic_data.append(data)
    
    return pd.DataFrame(demographic_data)

def generate_traffic_data(cities):
    """Şehirler için trafik verisi oluşturur."""
    traffic_data = []
    
    for city in cities:
        data = {
            "city": city,
            "avg_daily_traffic": int(np.random.uniform(50000, 2000000)),
            "peak_hour_factor": round(np.random.uniform(1.5, 3.5), 1),
            "highway_accessibility": round(np.random.uniform(0.3, 0.9), 2),
            "congestion_index": round(np.random.uniform(1.0, 10.0), 1),
            "avg_commute_time": int(np.random.uniform(15, 60)),
            "major_routes_count": int(np.random.uniform(3, 15)),
            "traffic_growth_rate": round(np.random.uniform(0.01, 0.08), 3)
        }
        traffic_data.append(data)
    
    return pd.DataFrame(traffic_data)

def generate_competitor_analysis(charging_stations):
    """Rakip analizi verileri oluşturur."""
    
    # Türkiye'deki başlıca şarj istasyonu operatörleri ve özellikleri
    major_operators = {
        "ZES": {
            "brand_recognition": 9,
            "pricing_tier": "Premium",
            "typical_power": 180,
            "expansion_rate": 0.25,
            "service_quality": 9,
            "payment_methods": ["Kredi Kartı", "ZES Kart", "Mobil Uygulama"],
            "target_segment": "Premium",
            "partnership_score": 8,
            "tech_level": 9
        },
        "Eşarj": {
            "brand_recognition": 8,
            "pricing_tier": "Premium",
            "typical_power": 150,
            "expansion_rate": 0.20,
            "service_quality": 8,
            "payment_methods": ["Kredi Kartı", "Eşarj Kart", "Mobil Uygulama"],
            "target_segment": "Premium",
            "partnership_score": 7,
            "tech_level": 8
        },
        "Voltrun": {
            "brand_recognition": 7,
            "pricing_tier": "Orta",
            "typical_power": 120,
            "expansion_rate": 0.15,
            "service_quality": 7,
            "payment_methods": ["Kredi Kartı", "Mobil Uygulama"],
            "target_segment": "Orta Segment",
            "partnership_score": 6,
            "tech_level": 7
        },
        "Sharz": {
            "brand_recognition": 6,
            "pricing_tier": "Ekonomik",
            "typical_power": 90,
            "expansion_rate": 0.18,
            "service_quality": 7,
            "payment_methods": ["Kredi Kartı", "Mobil Uygulama"],
            "target_segment": "Ekonomik",
            "partnership_score": 5,
            "tech_level": 7
        },
        "Powersarj": {
            "brand_recognition": 5,
            "pricing_tier": "Orta",
            "typical_power": 100,
            "expansion_rate": 0.12,
            "service_quality": 6,
            "payment_methods": ["Kredi Kartı", "Mobil Uygulama"],
            "target_segment": "Orta Segment",
            "partnership_score": 5,
            "tech_level": 6
        }
    }
    
    operators = charging_stations["operator"].unique()
    competitor_data = []
    total_stations = len(charging_stations)
    
    for operator in operators:
        stations = charging_stations[charging_stations["operator"] == operator]
        station_count = len(stations)
        
        # Operatör bilgilerini al veya varsayılan değerler kullan
        op_info = major_operators.get(operator, {
            "brand_recognition": np.random.randint(3, 7),
            "pricing_tier": np.random.choice(["Ekonomik", "Orta", "Premium"], p=[0.4, 0.4, 0.2]),
            "typical_power": np.random.randint(50, 150),
            "expansion_rate": round(np.random.uniform(0.05, 0.15), 2),
            "service_quality": np.random.randint(5, 8),
            "payment_methods": ["Kredi Kartı"],
            "target_segment": "Orta Segment",
            "partnership_score": np.random.randint(3, 7),
            "tech_level": np.random.randint(5, 8)
        })
        
        # Pazar payı ve büyüme potansiyeli hesapla
        market_share = round(station_count / total_stations, 3)
        growth_potential = min(1.0, (1 - market_share) * op_info["expansion_rate"])
        
        # Ortalama şarj gücü ve fiyatlandırma stratejisi
        avg_power = round(stations["power_kw"].mean(), 1)
        pricing_multiplier = {
            "Ekonomik": 0.8,
            "Orta": 1.0,
            "Premium": 1.2
        }.get(op_info["pricing_tier"], 1.0)
        
        # Müşteri memnuniyeti ve teknik performans
        customer_satisfaction = round(
            (op_info["service_quality"] * 0.4 +
             op_info["tech_level"] * 0.3 +
             len(op_info["payment_methods"]) * 0.1 +
             op_info["brand_recognition"] * 0.2) / 10, 1
        )
        
        # Rekabet gücü skoru
        competitive_score = round(
            (market_share * 0.3 +
             growth_potential * 0.2 +
             customer_satisfaction * 0.3 +
             op_info["partnership_score"] / 10 * 0.2) * 10, 1
        )
        
        data = {
            "operator": operator,
            "total_stations": station_count,
            "avg_charger_count": round(stations["charger_count"].mean(), 1),
            "avg_power": avg_power,
            "market_share": market_share,
            "growth_potential": round(growth_potential, 3),
            "pricing_tier": op_info["pricing_tier"],
            "avg_price_per_kwh": round(75 * pricing_multiplier, 2),  # Baz fiyat 75 TL
            "brand_recognition": op_info["brand_recognition"],
            "customer_satisfaction": customer_satisfaction,
            "service_quality": op_info["service_quality"],
            "tech_level": op_info["tech_level"],
            "payment_options": len(op_info["payment_methods"]),
            "target_segment": op_info["target_segment"],
            "competitive_score": competitive_score,
            "expansion_rate": op_info["expansion_rate"]
        }
        competitor_data.append(data)
    
    # Rekabet analizi DataFrame'ini oluştur ve sırala
    df = pd.DataFrame(competitor_data)
    return df.sort_values(by=["competitive_score", "market_share"], ascending=[False, False])

def fetch_all_data():
    """Tüm veri setlerini oluşturur ve sözlük olarak döndürür."""
    # Şarj istasyonlarını API'den çek
    charging_stations = fetch_charging_stations()
    
    if charging_stations is None or len(charging_stations) == 0:
        print("API'den veri çekilemedi, varsayılan veriler kullanılıyor...")
        from data_generator import generate_all_data
        return generate_all_data()
    
    # Benzersiz şehirleri al
    cities = charging_stations["city"].unique()
    
    # Diğer verileri oluştur
    demographic_data = generate_demographic_data(cities)
    traffic_data = generate_traffic_data(cities)
    competitor_data = generate_competitor_analysis(charging_stations)
    
    # Şehir koordinatlarını ekle
    cities_dict = {
        city: {
            "lat": charging_stations[charging_stations["city"] == city]["latitude"].mean(),
            "lon": charging_stations[charging_stations["city"] == city]["longitude"].mean(),
            "population": demographic_data[demographic_data["city"] == city]["population"].iloc[0]
        }
        for city in cities
    }
    
    return {
        "cities": cities_dict,
        "charging_stations": charging_stations,
        "demographic_data": demographic_data,
        "traffic_data": traffic_data,
        "competitor_data": competitor_data
    } 
