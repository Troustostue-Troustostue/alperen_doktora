import webbrowser
import os

def zihin_haritasi_olustur(markdown_metni, dosya_adi="zihin_haritasi.html"):
    # Autoloader kullanarak sıfır JavaScript koduyla garantili render yapan sistem
    html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tez Zihin Haritası</title>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #f8f9fa; font-family: sans-serif; }}
        .markmap {{ width: 100%; height: 100vh; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.16.0"></script>
</head>
<body>
    <div class="markmap">
{markdown_metni}
    </div>
</body>
</html>"""

    # HTML dosyasını oluştur ve kaydet
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(html_icerik)
    
    print(f"Zihin haritası başarıyla oluşturuldu: {dosya_adi}")
    
    # Dosyayı otomatik olarak varsayılan web tarayıcısında aç
    dosya_yolu = 'file://' + os.path.realpath(dosya_adi)
    webbrowser.open(dosya_yolu)

# ==========================================
# İÇERİĞİ BURAYA YAZIYORSUN
# ==========================================
tez_markdown = """
# CuMg0.4 Tel Çekme Prosesi
## FAZ 1: Hammadde
### 20.00 mm Filmaşin
### Tavlı ve Sünek Yapı
## FAZ 2: Kaba Kırma (Rod Breakdown)
### 20 mm ➔ 14 mm ➔ 8 mm
### Mukavemet: ~500 MPa
### Karbür (TC) Kalıplar
## FAZ 3: Optimizasyon (Niehoff MSM 85)
### 2.80 mm Nihai Çap
#### 656.9 MPa
#### Uzama: %4.15
### 2.50 mm Nihai Çap
#### 672.7 MPa
#### Uzama: %1.45
### 2.10 mm Nihai Çap
#### 710.6 MPa
#### Uzama: %2.78 (Dinamik Toparlanma)
#### <111> Lif Dokusu
"""

# Fonksiyonu çalıştır
zihin_haritasi_olustur(tez_markdown)