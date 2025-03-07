import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def create_map(charging_stations, selected_city=None):
    """Şarj istasyonlarını gösteren bir harita oluşturur."""
    
    # Eğer bir şehir seçilmişse, o şehirin istasyonlarını filtrele
    if selected_city and selected_city != "Tüm Şehirler":
        df = charging_stations[charging_stations["city"] == selected_city]
    else:
        df = charging_stations
    
    # Harita merkezini belirle
    if len(df) > 0:
        center_lat = df["latitude"].mean()
        center_lon = df["longitude"].mean()
    else:
        # Varsayılan merkez (Türkiye)
        center_lat = 39.0
        center_lon = 35.0
    
    # Haritayı oluştur
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    
    # Operatörlere göre renk belirle
    operators = df["operator"].unique()
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
    color_map = {op: colors[i % len(colors)] for i, op in enumerate(operators)}
    
    # İstasyon grupları oluştur
    operator_groups = {}
    for op in operators:
        operator_groups[op] = folium.FeatureGroup(name=op)
    
    # İstasyonları haritaya ekle
    for idx, row in df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4>{row['name']}</h4>
            <b>Operatör:</b> {row['operator']}<br>
            <b>Şarj Noktası Sayısı:</b> {row['charger_count']}<br>
            <b>Güç:</b> {row['power_kw']} kW<br>
            <b>Günlük Ortalama Kullanım:</b> {row['avg_daily_usage']}<br>
            <b>Müşteri Puanı:</b> {row['customer_rating']}/5.0<br>
        </div>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['name'],
            icon=folium.Icon(color=color_map[row['operator']], icon='bolt', prefix='fa')
        ).add_to(operator_groups[row['operator']])
    
    # Operatör gruplarını haritaya ekle
    for op in operators:
        operator_groups[op].add_to(m)
    
    # Katman kontrolü ekle
    folium.LayerControl().add_to(m)
    
    return m

def plot_operator_distribution(charging_stations):
    """Operatör dağılımını gösteren bir grafik oluşturur."""
    operator_counts = charging_stations["operator"].value_counts().reset_index()
    operator_counts.columns = ["Operatör", "İstasyon Sayısı"]
    
    fig = px.bar(
        operator_counts, 
        x="Operatör", 
        y="İstasyon Sayısı",
        color="Operatör",
        title="Operatörlere Göre Şarj İstasyonu Dağılımı"
    )
    
    return fig

def plot_power_distribution(charging_stations):
    """Güç dağılımını gösteren bir grafik oluşturur."""
    power_counts = charging_stations["power_kw"].value_counts().reset_index()
    power_counts.columns = ["Güç (kW)", "İstasyon Sayısı"]
    power_counts = power_counts.sort_values("Güç (kW)")
    
    fig = px.pie(
        power_counts, 
        values="İstasyon Sayısı", 
        names="Güç (kW)",
        title="Şarj İstasyonlarının Güç Dağılımı",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    return fig

def plot_city_comparison(charging_stations):
    """Şehirlere göre istasyon sayılarını gösteren bir grafik oluşturur."""
    city_counts = charging_stations["city"].value_counts().reset_index()
    city_counts.columns = ["Şehir", "İstasyon Sayısı"]
    
    fig = px.bar(
        city_counts, 
        x="Şehir", 
        y="İstasyon Sayısı",
        color="İstasyon Sayısı",
        title="Şehirlere Göre Şarj İstasyonu Sayıları",
        color_continuous_scale="Viridis"
    )
    
    return fig

def plot_demographic_data(demographic_data, traffic_data):
    """Demografik verileri gösteren bir ısı haritası oluşturur."""
    # Verileri birleştir
    merged_data = pd.merge(demographic_data, traffic_data, on="city")
    
    # Analiz için önemli sütunları seç
    columns_to_plot = [
        "population", "ev_adoption_rate", "avg_income", 
        "urbanization_rate", "tourism_score", "growth_potential",
        "avg_daily_traffic", "peak_hour_factor", "congestion_index"
    ]
    
    # Seçilen sütunlar için verileri normalize et
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(merged_data[columns_to_plot])
    normalized_df = pd.DataFrame(normalized_data, columns=columns_to_plot)
    normalized_df["city"] = merged_data["city"]
    
    # Isı haritası için verileri yeniden düzenle
    heatmap_data = normalized_df.melt(
        id_vars=["city"],
        value_vars=columns_to_plot,
        var_name="Metric",
        value_name="Normalized Value"
    )
    
    # Isı haritası oluştur
    fig = px.density_heatmap(
        heatmap_data, 
        x="Metric", 
        y="city", 
        z="Normalized Value",
        title="Şehirlere Göre Demografik ve Trafik Verileri",
        color_continuous_scale="Viridis"
    )
    
    return fig

def calculate_location_score(selected_lat, selected_lon, charging_stations, demographic_data, traffic_data):
    """Seçilen konum için uygunluk puanı hesaplar."""
    
    # En yakın 5 istasyonu bul
    charging_stations["distance"] = charging_stations.apply(
        lambda row: np.sqrt((row["latitude"] - selected_lat)**2 + (row["longitude"] - selected_lon)**2),
        axis=1
    )
    nearby_stations = charging_stations.sort_values("distance").head(5)
    
    # Konum puanlama faktörleri
    avg_distance = nearby_stations["distance"].mean() * 111  # km cinsinden yaklaşık mesafe (1 derece ~ 111 km)
    competition_factor = len(nearby_stations)
    
    # En yakın şehri bul
    city_distances = []
    for city, data in demographic_data.set_index("city").to_dict(orient="index").items():
        city_distance = np.sqrt((data.get("lat", 0) - selected_lat)**2 + (data.get("lon", 0) - selected_lon)**2)
        city_distances.append((city, city_distance))
    
    nearest_city = min(city_distances, key=lambda x: x[1])[0]
    
    # Demografik faktörler
    city_demo = demographic_data[demographic_data["city"] == nearest_city].iloc[0]
    city_traffic = traffic_data[traffic_data["city"] == nearest_city].iloc[0]
    
    # Parametreleri ağırlıklandır
    weights = {
        "competition": 0.3,  # Rekabet faktörü (daha az yakın istasyon daha iyi)
        "population": 0.15,  # Nüfus yoğunluğu
        "ev_adoption": 0.15,  # Elektrikli araç benimseme oranı
        "income": 0.1,  # Ortalama gelir
        "traffic": 0.15,  # Trafik yoğunluğu
        "growth": 0.15  # Büyüme potansiyeli
    }
    
    # Normalize edilmiş değerler
    normalized_values = {
        "competition": 1 - min(competition_factor / 5, 1) if competition_factor > 0 else 0.8,
        "population": min(city_demo["population"] / 10000000, 1),
        "ev_adoption": min(city_demo["ev_adoption_rate"] / 0.15, 1),
        "income": min(city_demo["avg_income"] / 20000, 1),
        "traffic": min(city_traffic["avg_daily_traffic"] / 2000000, 1),
        "growth": min(city_demo["growth_potential"] / 0.08, 1)
    }
    
    # Toplam puan hesapla (0-100 arası)
    total_score = sum(normalized_values[key] * weights[key] for key in weights.keys()) * 100
    
    # Sonuçları sözlük olarak döndür
    return {
        "score": round(total_score, 1),
        "nearest_city": nearest_city,
        "nearest_stations": len(nearby_stations),
        "avg_distance_km": round(avg_distance, 2),
        "population": city_demo["population"],
        "ev_adoption_rate": city_demo["ev_adoption_rate"],
        "avg_income": city_demo["avg_income"],
        "traffic": city_traffic["avg_daily_traffic"],
        "growth_potential": city_demo["growth_potential"]
    }

def create_roi_analysis(location_score, investment_amount=100000):
    """Yatırımın geri dönüş analizini oluşturur."""
    
    # Basit ROI modeli
    score_factor = location_score["score"] / 100
    
    # Günlük kullanım tahmini
    estimated_daily_usage = 10 + 30 * score_factor
    
    # Şarj başına ortalama gelir (TL)
    avg_revenue_per_charge = 75
    
    # Aylık tahmini gelir
    monthly_revenue = estimated_daily_usage * 30 * avg_revenue_per_charge
    
    # Aylık işletme giderleri
    monthly_expenses = investment_amount * 0.02 + 5000
    
    # Aylık net kar
    monthly_profit = monthly_revenue - monthly_expenses
    
    # Yatırımın geri dönüş süresi (ay)
    roi_months = investment_amount / monthly_profit if monthly_profit > 0 else float('inf')
    
    # 5 yıllık kümülatif kar projeksiyon verileri
    years = list(range(1, 6))
    cumulative_profit = [0]
    
    for year in years:
        # Yıllık kar artışı (her yıl %5 büyüme)
        yearly_profit = monthly_profit * 12 * (1 + 0.05) ** (year - 1)
        
        # İlk yıl, yatırım tutarını çıkar
        if year == 1:
            yearly_profit -= investment_amount
            
        # Kümülatif kara ekle
        cumulative_profit.append(cumulative_profit[-1] + yearly_profit)
    
    # Kümülatif karı grafiğe çevir
    cumulative_profit = cumulative_profit[1:]  # İlk 0 değerini kaldır
    
    # Sonuçları sözlük olarak döndür
    return {
        "estimated_daily_usage": round(estimated_daily_usage, 1),
        "monthly_revenue": round(monthly_revenue, 0),
        "monthly_expenses": round(monthly_expenses, 0),
        "monthly_profit": round(monthly_profit, 0),
        "roi_months": round(roi_months, 1),
        "years": years,
        "cumulative_profit": cumulative_profit
    }

def plot_roi_chart(roi_data):
    """ROI analizini gösteren bir grafik oluşturur."""
    fig = go.Figure()
    
    # Kümülatif kar çizgisi
    fig.add_trace(go.Scatter(
        x=roi_data["years"], 
        y=roi_data["cumulative_profit"],
        mode='lines+markers',
        name='Kümülatif Kar',
        line=dict(color='green', width=3),
        marker=dict(size=10, color='green')
    ))
    
    # Sıfır çizgisi
    fig.add_shape(
        type="line", 
        x0=0, 
        y0=0, 
        x1=5, 
        y1=0,
        line=dict(color="red", width=2, dash="dash")
    )
    
    # Breakeven noktasını bul
    breakeven_year = None
    for i, profit in enumerate(roi_data["cumulative_profit"]):
        if profit > 0:
            if i > 0 and roi_data["cumulative_profit"][i-1] <= 0:
                # Doğrusal interpolasyon ile breakeven yılını bul
                prev_year = roi_data["years"][i-1]
                current_year = roi_data["years"][i]
                prev_profit = roi_data["cumulative_profit"][i-1]
                current_profit = profit
                
                breakeven_year = prev_year + (0 - prev_profit) * (current_year - prev_year) / (current_profit - prev_profit)
                break
    
    # Breakeven noktasını işaretle
    if breakeven_year:
        fig.add_trace(go.Scatter(
            x=[breakeven_year],
            y=[0],
            mode='markers',
            name=f'Başabaş Noktası ({breakeven_year:.1f} yıl)',
            marker=dict(size=15, color='red', symbol='diamond')
        ))
    
    # Düzenleme
    fig.update_layout(
        title='5 Yıllık Yatırım Getirisi Projeksiyonu',
        xaxis_title='Yıllar',
        yaxis_title='Kümülatif Kar (TL)',
        legend=dict(y=0.7, x=0.1),
        hovermode='x unified'
    )
    
    # Y ekseni biçimlendirme (TL formatı)
    fig.update_yaxes(tickprefix='₺')
    
    return fig 
