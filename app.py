import streamlit as st
import pandas as pd
import numpy as np

# --- Algoritma ---
def hesapla_hadde_serisi(baslangic, hedef, hadde_sayisi, strateji, df_envanter):
    # 1. Excel'den Çap ve Adet sütunlarını otomatik bul
    cap_col = [col for col in df_envanter.columns if 'Çap' in col or 'cap' in col.lower()][0]
    adet_col = [col for col in df_envanter.columns if 'Adet' in col or 'adet' in col.lower()][0]
    
    # 2. Aynı çapları grupla ve toplam adetlerini bir sözlüğe (dictionary) çevir
    envanter_gruplu = df_envanter.groupby(cap_col)[adet_col].sum().to_dict()
    
    # 3. Teorik Daralma Dağılımını Hesapla
    total_strain = 2 * np.log(baslangic / hedef)
    
    if strateji == "sabit":
        weights = np.ones(hadde_sayisi)
    elif strateji == "azalan":
        weights = np.linspace(hadde_sayisi, 1, hadde_sayisi)
    elif strateji == "artan":
        weights = np.linspace(1, hadde_sayisi, hadde_sayisi)
        
    strains = (weights / weights.sum()) * total_strain
    
    theoretical = []
    current = baslangic
    for e in strains:
        current = current / np.exp(e/2)
        theoretical.append(current)
    theoretical[-1] = hedef
    
    actual_schedule = []
    current_D = baslangic
    
    # 4. Stok Miktarına (Adet) Göre Seçim Yap
    for i in range(hadde_sayisi - 1):
        target = theoretical[i]
        
        # Filtre: Çapı uygun olan VE Stokta (Adet > 0) olan kalıplar
        valid_dies = [cap for cap, adet in envanter_gruplu.items() if adet > 0 and cap < current_D and cap > hedef]
        
        if len(valid_dies) == 0:
            chosen_die = target
            durum = "YOK - İşlenecek"
        else:
            valid_pool = np.array(valid_dies)
            idx = (np.abs(valid_pool - target)).argmin()
            chosen_die = valid_pool[idx]
            kalan_stok = envanter_gruplu[chosen_die]
            durum = f"Stoktan ({kalan_stok} adet kaldı)"
            
            # Seçilen kalıptan 1 adet düş
            envanter_gruplu[chosen_die] -= 1
            
        actual_schedule.append((chosen_die, durum, target))
        current_D = chosen_die
        
    # Final Hedef Kalıbı
    actual_schedule.append((hedef, "Final Hedef Kalıbı", hedef))
    
    # 5. Tabloyu Oluştur
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
st.set_page_config(page_title="Hadde Serisi Oluşturma", layout="wide")
st.title("Envantere Göre Hadde Serisi Belirleme")
st.markdown("Stok durumunu ve miktarını dikkate alarak hat dizayn edilir.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Envanter Yükleme")
    yuklenen_dosya = st.file_uploader("Envanter Dosyasını Seç (.xlsx)", type=["xlsx", "csv"])
    st.header("2. Parametreler")
    baslangic = st.number_input("Başlangıç Çapı (mm)", value=8.00, step=0.1)
    hedef = st.selectbox("Nihai Çap (mm)", [2.80, 2.50, 2.10], index=1)
    sayi = st.slider("Hadde Sayısı", min_value=4, max_value=14, value=9)
    strateji = st.selectbox("Redüksiyon Stratejisi", ["Azalan", "Sabit", "Artan"])

with col2:
    if yuklenen_dosya is not None:
        # Dosyayı oku (CSV veya Excel)
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                df_envanter = pd.read_csv(yuklenen_dosya)
            else:
                df_envanter = pd.read_excel(yuklenen_dosya)
                
            # Hesaplamayı tetikle
            df_sonuc = hesapla_hadde_serisi(baslangic, hedef, sayi, strateji, df_envanter)
            
            st.header("Sonuç ve Kesit Daralma Grafiği")
            st.line_chart(df_sonuc.set_index("Hadde No")["Seçilen Çap (mm)"])
            
            st.header("Hadde Dizilim Tablosu")
            st.dataframe(df_sonuc, use_container_width=True)
            
        except Exception as e:
            st.error(f"Dosya okunurken bir hata oluştu: Lütfen Çap ve Adet sütunlarının olduğundan emin olun. Hata detayı: {e}")
    else:
        st.info("Envantere ait Excel dosyasını yükle.")