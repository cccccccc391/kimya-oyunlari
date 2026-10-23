# Kimya Oyunları

Akıllı tahtada bütün sınıfla oynanan kimya oyunlarının toplu sayfası (Türkiye Yüzyılı Maarif Modeli, 2024). Oyunlar şu an **şifresiz** yayındadır.

| Sınıf | Oyun | Öğrenme çıktıları |
|---|---|---|
| 9 | Görünmeyeni Görmek | KİM.9.1.3–9.1.8 |
| 9 | Kimya Hayattır | KİM.9.1.1–9.1.2 |
| 9 | Çeşitliliğin Sırrı | KİM.9.2.1–9.2.13 |
| 9 | Atıktan Nanoya | KİM.9.3.1–9.3.2 |
| 10 | Tepkimenin İzinde | KİM.10.1.1–10.1.3 |
| 10 | Mol Atölyesi | KİM.10.1.4–10.1.7 |

## Kilit (şu an kapalı)

Kilit `arac/yayin.json` dosyasındaki `"kilit"` değeriyle açılıp kapatılır (24 Ekim 2026'dan beri `false`: oyunlar şifresiz). Şifresiz sürüm, tahtaların daha önce hatırladığı kilit anahtarını kendiliğinden siler. Kilit açıkken:

- Her oyun sayfası, öğretmen şifresiyle **şifrelenmiş** olarak yayınlanır. Şifre girilmeden oyunun içeriği tarayıcıya hiç gelmez; sayfanın kaynağına bakmak da işe yaramaz.
- Şifre doğruysa oyunu tarayıcının kendisi çözer ve açar. Arada bir sunucu yoktur.
- “Bu tahtada hatırla” işaretliyse tarayıcı, şifreden türetilen anahtarı o tahtanın tarayıcı belleğine yazar (şifrenin kendisini değil). Bütün oyunlar aynı adreste olduğu için bir kez açılan kilit o tahtadaki bütün oyunları açar.
- Tahtanın şifreyi unutması için: bu sayfadaki ya da bir oyunun Öğretmen sayfasındaki **🔒 Bu tahtada kilitle** düğmesi.
- Tarayıcı belleği silinirse tahta şifreyi de unutur; yeniden girmek yeterlidir.

## Tahtaya indirmek

Ana sayfadaki **⬇ Paketi indir (ZIP)** bütün oyunların internetsiz sürümünü içerir. ZIP açılınca çıkan `Kimya-Oyunlari` klasöründeki `Kimya-Oyunlari.html` dosyası oyun listesini açar. Kilit açıksa internetsiz sürüm de aynı şifreyle açılır.

## İlerleme ve yedek

İlerleme ve sınıf oyları tahtanın tarayıcısında saklanır. Her oyunun Öğretmen sayfasında **💾 Yedeği indir** ve **📂 Yedekten yükle** düğmeleri vardır; yedek dosyası başka bir tahtaya da yüklenebilir.

## Yeniden üretmek (teknik)

1. Her oyunun kendi klasöründe tek dosyalık sürümü üretin: `python arac/tek-dosya.py`
2. Kilit açık olacaksa (`arac/yayin.json` içinde `"kilit": true`) bu klasörde `.kilit` dosyasının ilk satırına şifreyi yazın (bu dosya git'e eklenmez).
3. `python arac/kilitle.py` çalıştırın. `index.html`, her oyunun `index.html` dosyası ve `indir/kimya-oyunlari.zip` yeniden üretilir.

Kilit açıkken şifreleme: PBKDF2-SHA256 (250 000 tur) ile türetilen anahtar ve AES-256-GCM (tarayıcıda Web Crypto). Python için `cryptography` paketi gerekir.

## Hazırlanışı

Oyunların fikri, konusu ve pedagojik yönü bir BİLSEM kimya öğretmenine aittir. Kodu, benzetimleri ve metinleri öğretmenin isteği üzerine Claude (Anthropic) yapay zekâ modeli tarafından yazılmıştır.
