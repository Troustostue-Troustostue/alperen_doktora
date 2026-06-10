import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# --- Animasyon Motoru (SVG / HTML) ---
def ciz_animasyon(df_schedule, baslangic_cap):
    svg_width = len(df_schedule) * 200 + 150
    
    html_kodu = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .wire {{ fill: #b87333; }} 
        .die-body {{ fill: #e0e0e0; stroke: #757575; stroke-width: 2; }} 
        .die-hole {{ fill: #ffffff; }} 
        .text-title {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 13px; fill: #1e1e1e; font-weight: bold; }}
        .text-info {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 12px; fill: #424242; font-weight: bold; }}
        .text-wire {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 13px; fill: #b87333; font-weight: bold; }}
        
        .flow-line {{ stroke: rgba(255,255,255,0.6); stroke-width: 2; stroke-dasharray: 10, 10; animation: flow 0.5s linear infinite; }}
        @keyframes flow {{ 0% {{ stroke-dashoffset: 20; }} 100% {{ stroke-dashoffset: 0; }} }}
        
        /* Scrollbar'ı daha zarif yapmak için küçük bir dokunuş */
        ::-webkit-scrollbar {{ height: 10px; }}
        ::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 5px; }}
        ::-webkit-scrollbar-thumb {{ background: #c1c1c1; border-radius: 5px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #a8a8a8; }}

        .container {{ overflow-x: auto; overflow-y: hidden; white-space: nowrap; border: 2px solid #e0e0e0; border-radius: 10px; padding: 20px; background-color: #fafafa; box-shadow: inset 0px 0px 10px rgba(0,0,0,0.05); }}
    </style>
    </head>
    <body>
    <div class="container">
        <svg width="{svg_width}" height="350">
    """
    
    current_x = 10
    prev_D = baslangic_cap
    merkez_y = 130 
    
    h_giris = prev_D * 10 
    html_kodu += f'<text x="{current_x}" y="{merkez_y - h_giris/2 - 15}" class="text-wire">Giriş: {prev_D:.2f} mm</text>'
    
    for idx, row in df_schedule.iterrows():
        d_out = row['Seçilen Çap (mm)']
        red_oran = row['Kesit Daralması (%)']
        hadde_no = row['Hadde No']
        
        h_in = prev_D * 10
        h_out = d_out * 10
        
        y_in_top = merkez_y - h_in/2
        y_in_bot = merkez_y + h_in/2
        y_out_top = merkez_y - h_out/2
        y_out_bot = merkez_y + h_out/2
        
        html_kodu += f'<rect x="{current_x}" y="{y_in_top}" width="100" height="{h_in}" class="wire" />'
        html_kodu += f'<polygon points="{current_x+100},{y_in_top} {current_x+140},{y_out_top} {current_x+140},{y_out_bot} {current_x+100},{y_in_bot}" class="wire" />'
        html_kodu += f'<rect x="{current_x+100}" y="40" width="40" height="180" rx="5" class="die-body" />'
        html_kodu += f'<polygon points="{current_x+100},{y_in_top} {current_x+140},{y_out_top} {current_x+140},{y_out_bot} {current_x+100},{y_in_bot}" fill="none" stroke="#616161" stroke-width="1" />'
        
        html_kodu += f'<text x="{current_x+120}" y="28" class="text-title" text-anchor="middle">Hadde {int(hadde_no)}</text>'
        
        # Yazıların Y koordinatları aşağıya taşındı ve araları açıldı
        html_kodu += f'<text x="{current_x+120}" y="250" class="text-title" text-anchor="middle" fill="#d32f2f">-% {red_oran}</text>'
        html_kodu += f'<text x="{current_x+120}" y="270" class="text-info" text-anchor="middle">PCD Elmas</text>'
        
        html_kodu += f'<text x="{current_x+170}" y="{y_out_top - 15}" class="text-wire" text-anchor="middle">Ø {d_out:.2f}</text>'
        html_kodu += f'<line x1="{current_x}" y1="{merkez_y}" x2="{current_x+140}" y2="{merkez_y}" class="flow-line" />'
        
        current_x += 200
        prev_D = d_out
        
    h_final = prev_D * 10
    y_final_top = merkez_y - h_final/2
    html_kodu += f'<rect x="{current_x}" y="{y_final_top}" width="100" height="{h_final}" class="wire" />'
    html_kodu += f'<text x="{current_x+50}" y="{y_final_top - 15}" class="text-wire" text-anchor="middle">Nihai: {prev_D:.2f} mm</text>'
    html_kodu += f'<line x1="{current_x}" y1="{merkez_y}" x2="{current_x+100}" y2="{merkez_y}" class="flow-line" />'
    
    html_kodu += """
        </svg>
    </div>
    </body>
    </html>
    """
    return html_kodu

# --- Optimizasyon Algoritması ---
def hesapla_hadde_serisi(baslangic, hedef, hadde_sayisi, strateji, df_envanter):
    cap_col = [col for col in df_envanter.columns if 'çap' in str(col).lower() or 'cap' in str(col).lower()][0]
    adet_col = [col for col in df_envanter.columns if 'adet' in str(col).lower()][0]
    
    df_envanter[cap_col] = pd.to_numeric(df_envanter[cap_col].astype(str).str.replace(',', '.'), errors='coerce')
    df_envanter[adet_col] = pd.to_numeric(df_envanter[adet_col], errors='coerce')
    df_envanter = df_envanter.dropna(subset=[cap_col]) 
    
    envanter_gruplu = df_envanter.groupby(cap_col)[adet_col].sum().to_dict()
    total_strain = 2 * np.log(baslangic / hedef)
    
    str_isim = str(strateji).lower()
    if "sabit" in str_isim: weights = np.ones(hadde_sayisi)
    elif "artan" in str_isim: weights = np.linspace(1, hadde_sayisi, hadde_sayisi)
    else: weights = np.linspace(hadde_sayisi, 1, hadde_sayisi)
        
    strains = (weights / weights.sum()) * total_strain
    theoretical = []
    current = baslangic
    for e in strains:
        current = current / np.exp(e/2)
        theoretical.append(current)
    theoretical[-1] = hedef
    
    actual_schedule = []
    current_D = baslangic
    
    for i in range(hadde_sayisi - 1):
        target = theoretical[i]
        valid_dies = [cap for cap, adet in envanter_gruplu.items() if adet > 0 and cap < current_D and cap > hedef]
        
        if len(valid_dies) == 0:
            chosen_die = target
            durum = "YOK - İşlenecek"
        else:
            valid_pool = np.array(valid_dies)
            idx = (np.abs(valid_pool - target)).argmin()
            chosen_die = valid_pool[idx]
            envanter_gruplu[chosen_die] -= 1 
            durum = "Stoktan Kullanıldı"
            
        actual_schedule.append((chosen_die, durum, target))
        current_D = chosen_die
        
    actual_schedule.append((hedef, "Final Hedef Kalıbı", hedef))
    
    results = []
    prev_D = baslangic
    for i, data in enumerate(actual_schedule):
        D, durum, teorik = data
        red_ratio = (1 - (D**2 / prev_D**2)) * 100 
        results.append({
            "Hadde No": i + 1,
            "Seçilen Çap (mm)": D,
            "Kesit Daralması (%)": round(red_ratio, 2),
            "Durum / Stok": durum,
            "Teorik Çap (mm)": round(teorik, 4)
        })
        prev_D = D
        
    return pd.DataFrame(results)

# --- Arayüz (UI) ---
st.set_page_config(page_title="Hadde Tasarım Simülatörü", layout="wide")
st.title("Envanter Bazlı Tel Çekme Hat Tasarım Simülatörü")
st.markdown("Simülasyon Programı")

col1, col2 = st.columns([1, 3])

with col1:
    st.header("1. Envanteri Yükle")
    yuklenen_dosya = st.file_uploader("Envanter Dosyası (.xlsx)", type=["xlsx", "csv"])
    
    st.header("2. Parametreler")
    baslangic = st.number_input("Başlangıç Çapı (mm)", value=8.00, step=0.1)
    hedef = st.selectbox("Nihai Çap (mm)", [2.80, 2.50, 2.10], index=1)
    sayi = st.slider("Hadde Sayısı", min_value=4, max_value=14, value=9)
    strateji = st.selectbox("Alan Azaltma Stratejisi", ["Azalan Daralma", "Sabit Daralma", "Artan Daralma"])

with col2:
    if yuklenen_dosya is not None:
        try:
            if yuklenen_dosya.name.endswith('.csv'): df_envanter = pd.read_csv(yuklenen_dosya)
            else: df_envanter = pd.read_excel(yuklenen_dosya)
                
            df_sonuc = hesapla_hadde_serisi(baslangic, hedef, sayi, strateji, df_envanter)
            
            st.subheader("⚙️ Proses Animasyonu")
            animasyon_html = ciz_animasyon(df_sonuc, baslangic)
            
            # Streamlit çerçeve yüksekliği 300'den 400'e çıkarıldı!
            components.html(animasyon_html, height=400, scrolling=True)
            
            st.subheader("📊 Hadde Dizilim Tablosu")
            st.dataframe(df_sonuc, use_container_width=True)
            
        except Exception as e:
            st.error(f"Uygulamada bir hata oluştu: {e}")
    else:
        st.info("👈 Lütfen sol taraftan 'PCD Hadde Envanter' dosyanızı yükleyin.")