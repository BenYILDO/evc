import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import time
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt

# Yerel modülleri içe aktar
from data_generator import generate_all_data
from utils import (
    create_map, plot_operator_distribution, plot_power_distribution, 
    plot_city_comparison, plot_demographic_data, calculate_location_score,
    create_roi_analysis, plot_roi_chart
)

# Sayfanın yapısını ayarla
st.set_page_config(
    page_title="Elektrikli Şarj İstasyonu Lokasyon Analizi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile bazı stilleri ayarla
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0277BD;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .score-box {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-box {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
        width: 48%;
    }
    .roi-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .step-box {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .step-number {
        background-color: #9C27B0;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
        float: left;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 class='main-header'>⚡ Elektrikli Şarj İstasyonu Lokasyon Analizi</h1>", unsafe_allow_html=True)

# Kenar çubuğu - Kullanıcı Tipi Seçimi
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    
    # Kullanıcı tipi seçimi
    user_type = st.radio(
        "Kullanıcı Tipi",
        ("Yatırımcı", "Genel Kullanıcı"),
        index=0
    )
    
    st.divider()
    
    # Şehir seçimi
    data = generate_all_data()
    cities = ["Tüm Şehirler"] + sorted(list(data["demographic_data"]["city"].unique()))
    selected_city = st.selectbox("Şehir Seçin", cities)
    
    # Yatırımcı ise, daha fazla seçenek göster
    if user_type == "Yatırımcı":
        st.divider()
        st.subheader("Yatırım Parametreleri")
        
        investment_amount = st.slider(
            "Yatırım Miktarı (TL)",
            min_value=50000,
            max_value=500000,
            value=150000,
            step=10000,
            format="%d TL"
        )
        
        charger_count = st.slider(
            "Şarj Noktası Sayısı",
            min_value=2,
            max_value=20,
            value=4
        )
        
        charger_power = st.select_slider(
            "Şarj Gücü (kW)",
            options=[50, 100, 150, 250, 350],
            value=150
        )
    
    st.divider()
    st.caption("© 2023 Elektrikli Şarj İstasyonu Analizi")
    st.caption("Endüstri Mühendisliği Bitirme Projesi")

# Ana sayfayı kullanıcı tipine göre yapılandır
if user_type == "Genel Kullanıcı":
    # Genel kullanıcı arayüzü
    tabs = st.tabs(["Şarj İstasyonu Haritası", "İstatistikler", "Demografik Analiz"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Türkiye Şarj İstasyonu Haritası</h2>", unsafe_allow_html=True)
        
        # Şarj istasyonu haritası
        charging_map = create_map(data["charging_stations"], selected_city)
        folium_static(charging_map, width=1000, height=500)
        
        # Bilgi kutusu
        st.markdown(
            "<div class='info-box'>"
            "Bu harita Türkiye'deki elektrikli araç şarj istasyonlarının dağılımını göstermektedir. "
            "Her bir marker bir şarj istasyonunu temsil eder. Üzerine tıklayarak detayları görebilirsiniz. "
            "Haritanın sağ üst köşesindeki katman kontrolü ile istasyonları operatöre göre filtreleyebilirsiniz."
            "</div>",
            unsafe_allow_html=True
        )
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Şarj İstasyonu İstatistikleri</h2>", unsafe_allow_html=True)
        
        # İstatistik grafikleri
        col1, col2 = st.columns(2)
        
        with col1:
            # Operatör dağılımı
            operator_fig = plot_operator_distribution(data["charging_stations"])
            st.plotly_chart(operator_fig, use_container_width=True)
            
            # Şehir karşılaştırması
            city_fig = plot_city_comparison(data["charging_stations"])
            st.plotly_chart(city_fig, use_container_width=True)
        
        with col2:
            # Güç dağılımı
            power_fig = plot_power_distribution(data["charging_stations"])
            st.plotly_chart(power_fig, use_container_width=True)
            
            # İstasyon yaş dağılımı
            year_counts = data["charging_stations"]["installation_year"].value_counts().sort_index()
            year_df = pd.DataFrame({
                "Yıl": year_counts.index,
                "İstasyon Sayısı": year_counts.values
            })
            year_fig = px.line(
                year_df,
                x="Yıl",
                y="İstasyon Sayısı",
                markers=True,
                title="Yıllara Göre Şarj İstasyonu Kurulum Sayıları",
                color_discrete_sequence=["#1E88E5"]
            )
            st.plotly_chart(year_fig, use_container_width=True)
    
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Demografik ve Trafik Analizi</h2>", unsafe_allow_html=True)
        
        # Demografik ısı haritası
        demo_fig = plot_demographic_data(data["demographic_data"], data["traffic_data"])
        st.plotly_chart(demo_fig, use_container_width=True)
        
        # Açıklama
        st.markdown(
            "<div class='info-box'>"
            "Bu ısı haritası, şehirlerin demografik ve trafik verilerini normalize edilmiş şekilde göstermektedir. "
            "Koyu renkler daha yüksek değerleri, açık renkler daha düşük değerleri temsil eder. "
            "Bu veriler, şarj istasyonu lokasyon seçiminde önemli faktörlerdir."
            "</div>",
            unsafe_allow_html=True
        )

else:  # Yatırımcı kullanıcı arayüzü
    tabs = st.tabs(["Bölge Analizi", "Rakip Analizi", "Yatırım Getirisi", "Rapor Oluştur"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Bölge Analizi ve Konum Seçimi</h2>", unsafe_allow_html=True)
        
        # Harita üzerinde konum seçimi
        st.markdown("Harita üzerinde analiz etmek istediğiniz konumu seçin:")
        
        # Başlangıç merkezi
        if selected_city != "Tüm Şehirler":
            city_data = data["demographic_data"][data["demographic_data"]["city"] == selected_city].iloc[0]
            center_lat = data["cities"][selected_city]["lat"]
            center_lon = data["cities"][selected_city]["lon"]
        else:
            center_lat = 39.0
            center_lon = 35.0
        
        # Harita
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Folium haritası oluştur (mevcut istasyonları göster)
            m = create_map(data["charging_stations"], selected_city)
            
            # Kullanıcının tıklama yapabilmesi için haritaya marker ekle
            m.add_child(folium.LatLngPopup())
            
            # Haritayı görüntüle
            map_data = folium_static(m, width=800, height=500, returned_objects=True)
            
            # Konum girişi (manuel)
            lat_lon_container = st.container()
            
            with lat_lon_container:
                col_lat, col_lon = st.columns(2)
                with col_lat:
                    latitude = st.number_input("Enlem", value=center_lat, format="%.6f")
                with col_lon:
                    longitude = st.number_input("Boylam", value=center_lon, format="%.6f")
        
        # Bölge analizi butonuna tıklayınca
        analyze_button = st.button("Bölgeyi Analiz Et", type="primary")
        
        if analyze_button:
            with st.spinner("Bölge analizi yapılıyor..."):
                # Konum puanı hesapla
                location_score = calculate_location_score(
                    latitude, longitude, 
                    data["charging_stations"], 
                    data["demographic_data"], 
                    data["traffic_data"]
                )
                
                # Sonuçları göster
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("<h3 class='sub-header'>Lokasyon Analiz Sonuçları</h3>", unsafe_allow_html=True)
                    
                    # Konum puanı
                    st.markdown(
                        f"<div class='score-box'>"
                        f"<div>Konum Uygunluk Puanı</div>"
                        f"<div class='score-value'>{location_score['score']}/100</div>"
                        f"<div>En yakın şehir: {location_score['nearest_city']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Demografik metrikler
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    
                    metrics = [
                        {"label": "Nüfus", "value": f"{location_score['population']:,}"},
                        {"label": "Elektrikli Araç Benimseme Oranı", "value": f"%{location_score['ev_adoption_rate']*100:.1f}"},
                        {"label": "Ortalama Gelir", "value": f"₺{location_score['avg_income']:,}"},
                        {"label": "Günlük Trafik", "value": f"{location_score['traffic']:,}"},
                        {"label": "Yakındaki İstasyon Sayısı", "value": f"{location_score['nearest_stations']}"},
                        {"label": "Ortalama Mesafe", "value": f"{location_score['avg_distance_km']} km"}
                    ]
                    
                    for metric in metrics:
                        st.markdown(
                            f"<div class='metric-box'>"
                            f"<div>{metric['label']}</div>"
                            f"<div style='font-size: 1.5rem; font-weight: bold;'>{metric['value']}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h3 class='sub-header'>Konum Değerlendirmesi</h3>", unsafe_allow_html=True)
                    
                    # Konum puanına göre değerlendirme
                    recommendation = ""
                    if location_score["score"] >= 80:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **mükemmel** bir seçimdir. Yüksek potansiyel ve düşük rekabet barındırıyor."
                    elif location_score["score"] >= 60:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **iyi** bir seçimdir. Yatırım için uygun koşullar mevcut."
                    elif location_score["score"] >= 40:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **orta** düzeyde uygundur. Bazı risk faktörleri mevcut olabilir."
                    else:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **düşük** uygunluktadır. Alternatif lokasyonlar değerlendirilmelidir."
                    
                    st.markdown(f"<div class='info-box'>{recommendation}</div>", unsafe_allow_html=True)
                    
                    # Öneriler
                    st.markdown("<h4>Öneriler</h4>", unsafe_allow_html=True)
                    suggestions = []
                    
                    if location_score["nearest_stations"] > 3:
                        suggestions.append("Bu bölgede rekabet yüksek olabilir. Farklılaşmak için daha yüksek güçlü şarj cihazları düşünebilirsiniz.")
                    
                    if location_score["ev_adoption_rate"] < 0.05:
                        suggestions.append("Bölgedeki elektrikli araç benimseme oranı düşük. Uzun vadeli bir yatırım stratejisi düşünülmelidir.")
                    
                    if location_score["avg_distance_km"] > 5:
                        suggestions.append("En yakın rakiplere mesafe yeterli. Bu, müşteri çekmek için bir avantaj olabilir.")
                    
                    if location_score["traffic"] > 500000:
                        suggestions.append("Bölgedeki trafik yoğunluğu yüksek. Bu, potansiyel müşteri hacmi için olumludur.")
                    
                    if not suggestions:
                        suggestions.append("Lokasyon genel olarak uygun görünüyor. Standart kurulum planınızla ilerleyebilirsiniz.")
                    
                    for suggestion in suggestions:
                        st.markdown(f"- {suggestion}")
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Rakip Analizi</h2>", unsafe_allow_html=True)
        
        # Rakip analizi grafikleri
        competitor_data = data["competitor_data"]
        
        # Market payı pasta grafiği
        fig1 = px.pie(
            competitor_data,
            values="market_share",
            names="operator",
            title="Operatörlerin Pazar Payı",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig1.update_traces(textinfo='percent+label')
        
        # Operatör karşılaştırma metrikler
        fig2 = px.scatter(
            competitor_data,
            x="total_stations",
            y="avg_customer_rating",
            size="avg_charger_count",
            color="operator",
            hover_name="operator",
            size_max=50,
            title="Operatör Karşılaştırması"
        )
        fig2.update_layout(
            xaxis_title="Toplam İstasyon Sayısı",
            yaxis_title="Ortalama Müşteri Puanı"
        )
        
        # Operatör özellikleri radar grafiği
        categories = ['total_stations', 'avg_charger_count', 'avg_power', 'avg_customer_rating', 'brand_recognition']
        display_names = {
            'total_stations': 'İstasyon Sayısı', 
            'avg_charger_count': 'Ort. Şarj Noktası', 
            'avg_power': 'Ort. Güç (kW)', 
            'avg_customer_rating': 'Müşteri Puanı',
            'brand_recognition': 'Marka Tanınırlığı'
        }
        
        # Verileri normalize et
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(competitor_data[categories])
        
        fig3 = go.Figure()
        
        for i, operator in enumerate(competitor_data['operator']):
            # İlk ve son noktaları birleştirmek için verileri kopyala
            values = list(normalized_data[i])
            values.append(values[0])
            
            # Kategorileri etiketlerle değiştir
            category_labels = [display_names[cat] for cat in categories]
            category_labels.append(category_labels[0])
            
            fig3.add_trace(go.Scatterpolar(
                r=values,
                theta=category_labels,
                fill='toself',
                name=operator
            ))
        
        fig3.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Operatör Özellikleri Karşılaştırması",
            showlegend=True
        )
        
        # Grafikleri göster
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
            
            # Rakip bilgileri tablosu
            st.markdown("<h3 class='sub-header'>Operatör Detayları</h3>", unsafe_allow_html=True)
            
            display_df = competitor_data[['operator', 'total_stations', 'avg_charger_count', 
                                         'avg_power', 'avg_customer_rating', 'market_share',
                                         'pricing_tier', 'expansion_rate']]
            
            display_df.columns = [
                'Operatör', 'Toplam İstasyon', 'Ort. Şarj Noktası', 
                'Ort. Güç (kW)', 'Müşteri Puanı', 'Pazar Payı',
                'Fiyatlandırma', 'Büyüme Oranı'
            ]
            
            # Pazar payını yüzde olarak biçimlendir
            display_df['Pazar Payı'] = (display_df['Pazar Payı'] * 100).round(1).astype(str) + '%'
            
            # Büyüme oranını yüzde olarak biçimlendir
            display_df['Büyüme Oranı'] = (display_df['Büyüme Oranı'] * 100).round(1).astype(str) + '%'
            
            st.dataframe(display_df, use_container_width=True)
    
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Yatırım Getirisi Analizi</h2>", unsafe_allow_html=True)
        
        # Konum seçili değilse uyarı göster
        if not analyze_button:
            st.warning("Lütfen önce 'Bölge Analizi' sekmesinde bir konum seçin ve analiz edin.")
        else:
            # Yatırım parametrelerini göster
            st.markdown(
                f"<div class='info-box'>"
                f"<b>Yatırım Tutarı:</b> ₺{investment_amount:,}<br>"
                f"<b>Şarj Noktası Sayısı:</b> {charger_count}<br>"
                f"<b>Şarj Gücü:</b> {charger_power} kW<br>"
                f"<b>Konum Puanı:</b> {location_score['score']}/100"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # ROI analizi yap
            roi_data = create_roi_analysis(location_score, investment_amount)
            
            # ROI grafiği
            roi_fig = plot_roi_chart(roi_data)
            st.plotly_chart(roi_fig, use_container_width=True)
            
            # ROI metrikleri
            col1, col2, col3 = st.columns(3)
            
            metrics = [
                {"label": "Tahmini Günlük Kullanım", "value": f"{roi_data['estimated_daily_usage']} şarj/gün", "delta": ""},
                {"label": "Aylık Gelir", "value": f"₺{roi_data['monthly_revenue']:,.0f}", "delta": ""},
                {"label": "Aylık Gider", "value": f"₺{roi_data['monthly_expenses']:,.0f}", "delta": ""},
                {"label": "Aylık Net Kar", "value": f"₺{roi_data['monthly_profit']:,.0f}", "delta": ""},
                {"label": "Geri Dönüş Süresi", "value": f"{roi_data['roi_months']:.1f} ay", "delta": f"{roi_data['roi_months']/12:.1f} yıl"},
                {"label": "5 Yıllık Toplam Kar", "value": f"₺{sum(roi_data['cumulative_profit']):,.0f}", "delta": ""}
            ]
            
            col_map = {"col1": col1, "col2": col2, "col3": col3}
            
            for i, metric in enumerate(metrics):
                col_name = f"col{i % 3 + 1}"
                col_map[col_name].metric(
                    metric["label"],
                    metric["value"],
                    metric["delta"]
                )
            
            # Finansal tavsiyeler
            st.markdown("<h3 class='sub-header'>Finansal Değerlendirme</h3>", unsafe_allow_html=True)
            
            # ROI verilerine göre tavsiyeler
            roi_advice = ""
            if roi_data["roi_months"] < 24:
                roi_advice = "Bu lokasyon **çok iyi bir yatırım fırsatı** sunmaktadır. 2 yıldan kısa sürede yatırımınızı geri alabilirsiniz."
            elif roi_data["roi_months"] < 36:
                roi_advice = "Bu lokasyon **iyi bir yatırım fırsatı** sunmaktadır. 3 yıldan kısa sürede yatırımınızı geri alabilirsiniz."
            elif roi_data["roi_months"] < 48:
                roi_advice = "Bu lokasyon **makul bir yatırım fırsatı** sunmaktadır. 4 yıldan kısa sürede yatırımınızı geri alabilirsiniz."
            else:
                roi_advice = "Bu lokasyon **uzun vadeli bir yatırım** gerektirmektedir. Yatırımınızı geri almak 4 yıldan fazla sürebilir."
            
            st.markdown(f"<div class='roi-box'>{roi_advice}</div>", unsafe_allow_html=True)
            
            # Ek öneriler
            st.markdown("<h4>Finansal Öneriler</h4>")
            st.markdown("""
            - Elektrikli araç piyasasının büyüme hızını göz önünde bulundurun
            - Farklı şarj fiyatlandırma modelleri üzerinde çalışın (abonelik, kullanım başına ödeme)
            - Ek gelir kaynakları düşünün (reklam, ek hizmetler)
            - İlk yatırım maliyetini düşürmek için teşvik programlarını araştırın
            - Bakım ve işletme maliyetlerini optimize edin
            """)
    
    with tabs[3]:
        st.markdown("<h2 class='sub-header'>Rapor Oluştur</h2>", unsafe_allow_html=True)
        
        # Konum seçili değilse uyarı göster
        if not analyze_button:
            st.warning("Lütfen önce 'Bölge Analizi' sekmesinde bir konum seçin ve analiz edin.")
        else:
            # Rapor detayları
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-number'>1</div>"
                "<div style='margin-left: 40px;'>"
                "<h4>Konum Bilgileri</h4>"
                f"<p>Enlem: {latitude}, Boylam: {longitude}<br>"
                f"En Yakın Şehir: {location_score['nearest_city']}<br>"
                f"Lokasyon Puanı: {location_score['score']}/100</p>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-number'>2</div>"
                "<div style='margin-left: 40px;'>"
                "<h4>Yatırım Detayları</h4>"
                f"<p>Yatırım Tutarı: ₺{investment_amount:,}<br>"
                f"Şarj Noktası Sayısı: {charger_count}<br>"
                f"Şarj Gücü: {charger_power} kW</p>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            
            if 'roi_data' in locals():
                st.markdown(
                    "<div class='step-box'>"
                    "<div class='step-number'>3</div>"
                    "<div style='margin-left: 40px;'>"
                    "<h4>Finansal Projeksiyon</h4>"
                    f"<p>Aylık Gelir: ₺{roi_data['monthly_revenue']:,.0f}<br>"
                    f"Aylık Gider: ₺{roi_data['monthly_expenses']:,.0f}<br>"
                    f"Aylık Net Kar: ₺{roi_data['monthly_profit']:,.0f}<br>"
                    f"Geri Dönüş Süresi: {roi_data['roi_months']:.1f} ay ({roi_data['roi_months']/12:.1f} yıl)<br>"
                    f"5 Yıllık Toplam Kar: ₺{sum(roi_data['cumulative_profit']):,.0f}</p>"
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-number'>4</div>"
                "<div style='margin-left: 40px;'>"
                "<h4>Sonuç</h4>"
                f"<p>Bu lokasyon şarj istasyonu kurulumu için"
                f"{' <b>mükemmel</b>' if location_score['score'] >= 80 else ' <b>iyi</b>' if location_score['score'] >= 60 else ' <b>orta</b>' if location_score['score'] >= 40 else ' <b>düşük</b>'}"
                " bir seçimdir.</p>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            
            # Rapor indirme butonu
            if st.button("Detaylı Rapor Oluştur", type="primary"):
                with st.spinner("Rapor oluşturuluyor..."):
                    time.sleep(2)  # Rapor oluşturma simülasyonu
                    st.success("Rapor başarıyla oluşturuldu!")
                    
                    # PDF indirme butonu (simülasyon)
                    st.download_button(
                        label="Raporu İndir (PDF)",
                        data=b"Simulated PDF content",
                        file_name=f"elektrikli_sarj_istasyonu_raporu_{location_score['nearest_city'].lower().replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    pass 
