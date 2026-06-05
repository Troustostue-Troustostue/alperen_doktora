import streamlit as st
import pandas as pd
import numpy as np

# --- Algoritma ---
def hesapla_hadde_serisi(baslangic, hedef, hadde_sayisi, strateji, df_envanter):
    # 1. Sütun isimlerini güvenli bul
    cap_col = [col for col in df_envanter.columns if 'çap' in str(col).lower() or 'cap' in str(col).lower()][0]
    adet_col = [col for col in df_envanter.columns if 'adet' in str(col).lower()][0]
    
    # 2. Excel'deki virgülleri (2,50) noktaya çevirip garanti şekilde sayıya dönüştür
    df_envanter[cap_col] = pd.to_numeric(df_envanter[cap_col].astype(str).str.replace(',', '.'), errors='coerce')
    df_envanter[adet_col] = pd.to_numeric(df_envanter[adet_col], errors='coerce')
    df_envanter = df_envanter.dropna(subset=[cap_col]) # Boş satırları temizle
    
    # 3. Stok Sözlüğünü Oluştur
    envanter_gruplu = df_envanter.groupby(cap_col)[adet_col].sum().to_dict()
    
    # 4. Teorik Daralma Dağılımını Hesapla
    total_strain = 2 * np.log(baslangic / hedef)
    
    # Güvenlik subabı: Seçilen stratejiyi küçük harfe çevirip kelime arıyoruz
    str_isim = str(strateji).lower()
    if "sabit" in str_isim:
        weights = np.ones(hadde_sayisi)
    elif "artan" in str_isim:
        weights = np.linspace(1, hadde_sayisi, hadde_sayisi)
    else:
        # "azalan" kelimesi geçerse veya hiçbir şey bulunamazsa varsayılan olarak azalan yap
        weights = np.linspace(hadde_sayisi, 1, hadde_sayisi)
        
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
            kalan_stok = envanter_gruplu[chosen_die]
            durum = f"Stoktan ({int(kalan_stok)} adet kaldı)"
            
            envanter_gruplu[chosen_die] -= 1 # Kullanılanı stoktan düş
            
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
st.title("Tel Çekme: Envanter Odaklı Hadde Dizilimi Simülatörü")
st.markdown("Doktora tezi proses optimizasyon aracı. Stok miktarını (Adet) dikkate alır.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Envanteri Yükle")
    yuklenen_dosya = st.file_uploader("Envanter Dosyasını Seç (.xlsx veya .csv)", type=["xlsx", "csv"])
    
    st.header("2. Parametreler")
    baslangic = st.number_input("Başlangıç Çapı (mm)", value=8.00, step=0.1)
    hedef = st.selectbox("Hedef Nihai Çap (mm)", [2.80, 2.50, 2.10], index=1)
    sayi = st.slider("Ara Hadde Sayısı", min_value=4, max_value=14, value=9)
    strateji = st.selectbox("Daralma Stratejisi", ["Azalan Daralma", "Sabit Daralma", "Artan Daralma"])

with col2:
    if yuklenen_dosya is not None:
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                df_envanter = pd.read_csv(yuklenen_dosya)
            else:
                df_envanter = pd.read_excel(yuklenen_dosya)
                
            df_sonuc = hesapla_hadde_serisi(baslangic, hedef, sayi, strateji, df_envanter)
            
            st.header("Sonuç ve Kesit Daralma Grafiği")
            st.line_chart(df_sonuc.set_index("Hadde No")["Seçilen Çap (mm)"])
            
            st.header("Hadde Dizilim Tablosu")
            st.dataframe(df_sonuc, use_container_width=True)
            
        except Exception as e:
            st.error(f"Uygulamada bir hata oluştu. Hata detayı: {e}")
    else:
        st.info("👈 Lütfen sol taraftan 'PCD Hadde Envanter' Excel dosyanızı yükleyin.")