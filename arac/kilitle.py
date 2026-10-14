"""Kimya Oyunları: oyunların tek dosyalık sürümlerini öğretmen şifresiyle
şifreler, toplu sayfayı ve tahtaya indirilecek ZIP paketini üretir.

Kullanım (bu klasörden):  python arac/kilitle.py
Gerekenler:
  - .kilit dosyası (ilk satır: şifre; git'e eklenmez)
  - her oyunun ../<oyun>/dagitim/<oyun>.html dosyası (oyun klasöründe
    python arac/tek-dosya.py ile üretilir)
Çıktı: index.html, <oyun>/index.html, indir/kimya-oyunlari.zip

Şifreleme: PBKDF2-SHA256 (250 000 tur) ile türetilen anahtar, AES-256-GCM.
Bütün oyunlar aynı tuzu kullanır; böylece bir tahtada bir kez açılan kilit,
aynı adresteki bütün oyunları açar.
"""
import base64
import hashlib
import html
import io
import json
import os
import pathlib
import sys
import zipfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KOK = pathlib.Path(__file__).resolve().parent.parent
DEV = KOK.parent
TUR = 250000

OYUNLAR = [
    {'id': 'gorunmeyeni-gormek', 'ad': 'Görünmeyeni Görmek', 'alt': 'Atomun 2500 yıllık keşif yolculuğu: Thales’ten orbitallere', 'sinif': 9, 'kazanim': 'KİM.9.1.3–9.1.8'},
    {'id': 'kimya-hayattir', 'ad': 'Kimya Hayattır', 'alt': 'Ürün laboratuvarı ve kaza dosyaları', 'sinif': 9, 'kazanim': 'KİM.9.1.1–9.1.2'},
    {'id': 'cesitliligin-sirri', 'ad': 'Çeşitliliğin Sırrı', 'alt': 'Bağlardan sıvılara: Maddeler neden bu kadar farklı?', 'sinif': 9, 'kazanim': 'KİM.9.2.1–9.2.13'},
    {'id': 'atiktan-nanoya', 'ad': 'Atıktan Nanoya', 'alt': 'Metallerin ve nanoparçacıkların sürdürülebilir kimyası', 'sinif': 9, 'kazanim': 'KİM.9.3.1–9.3.2'},
    {'id': 'tepkimenin-izinde', 'ad': 'Tepkimenin İzinde', 'alt': 'Kanıtlar, tepkime modeli, çökelme, redoks ve asit-baz', 'sinif': 10, 'kazanim': 'KİM.10.1.1–10.1.3'},
    {'id': 'mol-atolyesi', 'ad': 'Mol Atölyesi', 'alt': 'Mol kavramı, denkleştirme ve stokiyometri', 'sinif': 10, 'kazanim': 'KİM.10.1.4–10.1.7'},
]


# Toplu sayfada listelenmeyen, kendi adresinde kilitli yayınlanan oyunlar.
# cikti klasörü ayrı bir yayın reposudur; içine kilitli index.html ve eski
# çevrim dışı önbelleği temizleyen sw.js yazılır.
OZEL = [
    {'id': 'element-oyunu', 'ad': 'Element Dosyaları', 'alt': 'Atomun Peşinde: kanıtlardan elementin kimliğini çıkar', 'cikti': DEV / 'element-oyunu-yayin', 'geri': '../kimya-oyunlari/'},
]

# Eski sürümün service worker'ı telefonlarda oyunu önbellekte tutuyordu. Bu sürüm
# önbelleği siler ve kendini kaldırır; böylece önbellekteki kilitsiz kopya da gider.
SW_TEMIZLE = """// Önbellek temizleyici: eski çevrim dışı kopyayı siler ve kendini kaldırır.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', olay => olay.waitUntil((async () => {
  for (const ad of await caches.keys()) await caches.delete(ad);
  await self.registration.unregister();
  for (const istemci of await self.clients.matchAll({ type: 'window' })) istemci.navigate(istemci.url);
})()));
"""

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode('ascii')


def sifre_oku() -> str:
    p = KOK / '.kilit'
    if not p.exists():
        raise SystemExit('.kilit dosyası yok: ilk satıra şifreyi yazın.')
    s = p.read_text(encoding='utf-8').splitlines()[0].strip().lower()
    if len(s) < 8:
        raise SystemExit('Şifre en az 8 karakter olmalı.')
    return s


def tuz_oku() -> bytes:
    p = KOK / 'arac' / 'tuz.txt'
    if not p.exists():
        p.write_text(b64(os.urandom(16)) + '\n', encoding='ascii')
    return base64.b64decode(p.read_text(encoding='ascii').strip())


KILIT_SABLON = (KOK / 'arac' / 'kilit-sablon.html').read_text(encoding='utf-8')
SAYFA_SABLON = (KOK / 'arac' / 'sayfa-sablon.html').read_text(encoding='utf-8')


def kilitli_sayfa(o: dict, anahtar: bytes, tuz: bytes, geri: str) -> str:
    kaynak = DEV / o['id'] / 'dagitim' / (o['id'] + '.html')
    duz = kaynak.read_bytes()
    iv = os.urandom(12)
    sifreli = AESGCM(anahtar).encrypt(iv, duz, None)  # şifreli metin + 16 baytlık etiket (WebCrypto biçimi)
    veri = {'tuz': b64(tuz), 'iv': b64(iv), 'veri': b64(sifreli), 'tur': TUR, 'ad': o['ad']}
    return (KILIT_SABLON
            .replace('__BASLIK__', html.escape(o['ad']))
            .replace('__ALT__', html.escape(o['alt']))
            .replace('__GERI__', geri)
            .replace('__VERI__', json.dumps(veri, ensure_ascii=False)))


def kartlar(baglanti) -> str:
    parca = []
    for sinif in (9, 10):
        parca.append('<h2>' + str(sinif) + '. sınıf</h2><div class="izgara">')
        for o in OYUNLAR:
            if o['sinif'] != sinif:
                continue
            parca.append('<a class="kart" href="' + baglanti(o) + '"><b>' + html.escape(o['ad']) + '</b><span>' + html.escape(o['alt']) + '</span><small>' + o['kazanim'] + '</small><em>🔒 Aç ▶</em></a>')
        parca.append('</div>')
    return '\n'.join(parca)


def main() -> int:
    sifre = sifre_oku()
    tuz = tuz_oku()
    anahtar = hashlib.pbkdf2_hmac('sha256', sifre.encode('utf-8'), tuz, TUR, 32)

    # çevrim içi site
    for o in OYUNLAR:
        d = KOK / o['id']
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(kilitli_sayfa(o, anahtar, tuz, '../'), encoding='utf-8')
    site = (SAYFA_SABLON
            .replace('__KARTLAR__', kartlar(lambda o: o['id'] + '/'))
            .replace('__CEVRIMICI__', '1'))
    (KOK / 'index.html').write_text(site, encoding='utf-8')

    # kendi adresinde yayınlanan kilitli oyunlar
    for o in OZEL:
        o['cikti'].mkdir(exist_ok=True)
        (o['cikti'] / 'index.html').write_text(kilitli_sayfa(o, anahtar, tuz, o['geri']), encoding='utf-8')
        (o['cikti'] / 'sw.js').write_text(SW_TEMIZLE, encoding='utf-8')
        (o['cikti'] / '.nojekyll').write_text('', encoding='utf-8')

    # tahtaya indirilecek paket (internetsiz)
    menu = (SAYFA_SABLON
            .replace('__KARTLAR__', kartlar(lambda o: o['id'] + '.html'))
            .replace('__CEVRIMICI__', '0'))
    (KOK / 'indir').mkdir(exist_ok=True)
    zp = KOK / 'indir' / 'kimya-oyunlari.zip'
    bellek = io.BytesIO()
    with zipfile.ZipFile(bellek, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('Kimya-Oyunlari/Kimya-Oyunlari.html', menu)
        for o in OYUNLAR:
            z.writestr('Kimya-Oyunlari/' + o['id'] + '.html', kilitli_sayfa(o, anahtar, tuz, 'Kimya-Oyunlari.html'))
        z.writestr('Kimya-Oyunlari/OKU-BENI.txt', (KOK / 'arac' / 'okubeni.txt').read_text(encoding='utf-8'))
    zp.write_bytes(bellek.getvalue())
    print(f'{len(OYUNLAR)} + {len(OZEL)} oyun kilitlendi; paket: {zp.relative_to(KOK)} ({zp.stat().st_size // 1024} KB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
