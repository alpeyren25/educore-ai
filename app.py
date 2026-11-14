# ai/knowledge_base.py
"""
EduCore-AI Bilgi Tabanı Motoru.
JSON dosyalarından konu kartlarını yükler, TF-IDF benzeri skorla
sorguya en uygun kartları getirir. Harici kütüphane yok.
"""
import json, re, os
from pathlib import Path
from collections import Counter

CONTENT_DIR = Path(__file__).parent.parent / "content"

_TR = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")

def _norm(s):
    return s.translate(_TR).lower() if isinstance(s, str) else ""

def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", _norm(s)))

class KnowledgeBase:
    def __init__(self, content_dir=None):
        self.dir = Path(content_dir) if content_dir else CONTENT_DIR
        self.cards = []
        self.by_subject = {}
        self._load()

    def _load(self):
        if not self.dir.exists():
            return
        for path in sorted(self.dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for card in data:
                        if self._validate(card):
                            self.cards.append(card)
            except Exception as e:
                print(f"Uyarı: {path} yüklenemedi: {e}")
        for c in self.cards:
            self.by_subject.setdefault(c["ders"], []).append(c)

    def _validate(self, c):
        required = ("ders", "konu", "etiketler", "icerik")
        return all(k in c for k in required) and isinstance(c["etiketler"], list)

    def score(self, query, card, subject=None):
        q = _tokens(query)
        if not q:
            return 0.0
        tags = set()
        for t in card.get("etiketler", []):
            tags |= _tokens(t)
        tags |= _tokens(card.get("konu", ""))
        if not tags:
            return 0.0
        overlap = len(q & tags)
        if overlap == 0:
            return 0.0
        precision = overlap / len(q)
        recall = overlap / len(tags)
        s = 0.6 * precision + 0.4 * recall
        if subject and card.get("ders") == subject:
            s += 0.20
        return s

    def search(self, query, subject=None, top_k=3, min_score=0.10):
        scored = [(self.score(query, c, subject), c) for c in self.cards]
        scored = [(s, c) for s, c in scored if s >= min_score]
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored[:top_k]]

    def stats(self):
        return {
            "toplam": len(self.cards),
            "dersler": {k: len(v) for k, v in self.by_subject.items()},
        }


# ─── Test ───
if __name__ == "__main__":
    kb = KnowledgeBase()
    print("Yüklenen kartlar:", kb.stats())
    for q in ["türev nasıl alınır", "fotosentez nedir", "ohm kanunu", "python döngü"]:
        print(f"\nSorgu: {q}")
        for c in kb.search(q, top_k=2):
            print(f"  → [{c['ders']}] {c['konu']}")
            // content/matematik.json
[
  {
    "ders": "Matematik",
    "konu": "Türev",
    "etiketler": ["türev", "derivative", "turev alma", "türev kuralları", "türev formülü"],
    "icerik": "Türev, bir fonksiyonun değişim hızını verir. f(x)'in türevi f'(x) ile gösterilir. Bir noktadaki türev, o noktadaki teğetin eğimidir.",
    "kurallar": [
      "Sabitin türevi 0'dır: (c)' = 0",
      "Kuvvet kuralı: (x^n)' = n·x^(n-1)",
      "Toplam kuralı: (f+g)' = f' + g'",
      "Çarpım kuralı: (f·g)' = f'·g + f·g'",
      "Bölüm kuralı: (f/g)' = (f'·g - f·g') / g²",
      "Zincir kuralı: (f(g(x)))' = f'(g(x))·g'(x)",
      "e^x türevi: (e^x)' = e^x",
      "ln(x) türevi: (ln x)' = 1/x",
      "sin(x)' = cos(x), cos(x)' = -sin(x)"
    ],
    "ornek": "f(x) = 3x² + 2x + 5 → f'(x) = 6x + 2",
    "adimlar": [
      "Her terimi ayrı ayrı türevle",
      "Sabit terimleri at (türevleri 0)",
      "Kuvvet kuralını uygula: x^n → n·x^(n-1)",
      "Sonuçları topla"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "İntegral",
    "etiketler": ["integral", "antitürev", "belirsiz integral", "belirli integral", "integral alma"],
    "icerik": "İntegral, türevin tersidir. Bir fonksiyonun altındaki alanı verir. ∫f(x)dx = F(x) + C (F, f'nin antitürevidir).",
    "kurallar": [
      "∫x^n dx = x^(n+1)/(n+1) + C (n≠-1)",
      "∫1/x dx = ln|x| + C",
      "∫e^x dx = e^x + C",
      "∫sin(x)dx = -cos(x) + C",
      "∫cos(x)dx = sin(x) + C",
      "∫(f+g)dx = ∫f dx + ∫g dx",
      "Belirli integral: ∫[a→b] f(x)dx = F(b) - F(a)"
    ],
    "ornek": "∫3x² dx = 3·(x³/3) + C = x³ + C",
    "adimlar": [
      "Kuvvet kuralını kullan: x^n → x^(n+1)/(n+1)",
      "Sabit katsayıyı dışarı al",
      "Sonuna +C ekle (belirsiz integral için)",
      "Belirli integralde üst-alt sınır değerlerini çıkar"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "İkinci Dereceden Denklem",
    "etiketler": ["ikinci derece", "diskriminant", "delta", "kökler", "quadratic"],
    "icerik": "ax² + bx + c = 0 (a≠0) formundaki denklem. Diskriminant Δ = b² - 4ac ile kök sayısı belirlenir.",
    "kurallar": [
      "Δ > 0 → iki farklı gerçek kök",
      "Δ = 0 → tek (çift) kök: x = -b/(2a)",
      "Δ < 0 → gerçek kök yok (karmaşık kökler var)",
      "Kök formülü: x = (-b ± √Δ) / (2a)",
      "Kökler toplamı: x₁ + x₂ = -b/a",
      "Kökler çarpımı: x₁ · x₂ = c/a"
    ],
    "ornek": "x² - 5x + 6 = 0 → Δ = 25-24 = 1 → x = (5±1)/2 → x₁=3, x₂=2",
    "adimlar": [
      "a, b, c katsayılarını belirle",
      "Δ = b² - 4ac hesapla",
      "Δ'nın işaretine göre kök durumunu belirle",
      "Kök formülünü uygula"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Trigonometri",
    "etiketler": ["trigonometri", "sinüs", "kosinüs", "tanjant", "sin cos tan"],
    "icerik": "Dik üçgende kenar oranları. Birim çemberde açı fonksiyonları. Temel oranlar: sin, cos, tan; tersleri: csc, sec, cot.",
    "kurallar": [
      "sin²x + cos²x = 1",
      "tan x = sin x / cos x",
      "sin(a+b) = sin a·cos b + cos a·sin b",
      "cos(a+b) = cos a·cos b - sin a·sin b",
      "sin(2a) = 2·sin a·cos a",
      "cos(2a) = cos²a - sin²a",
      "Dik üçgende: sin = karşı/hipotenüs, cos = komşu/hipotenüs, tan = karşı/komşu"
    ],
    "ornek": "30° için sin=1/2, cos=√3/2, tan=1/√3",
    "adimlar": [
      "Açıyı ve bilinen kenarları yaz",
      "Hangi oranın kullanılacağını seç",
      "Formülde yerine koy",
      "Bilinmeyen kenarı/açıyı çöz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Logaritma",
    "etiketler": ["logaritma", "log", "ln", "logaritma kuralları"],
    "icerik": "log_a(b) = c ⇔ a^c = b. Yani 'b'yi elde etmek için 'a'nın kaçıncı kuvvetini almalıyız' sorusunun cevabı. Doğal logaritma ln = log_e.",
    "kurallar": [
      "log(a·b) = log a + log b",
      "log(a/b) = log a - log b",
      "log(a^n) = n·log a",
      "log_a(1) = 0",
      "log_a(a) = 1",
      "Taban değiştirme: log_a(b) = ln b / ln a",
      "ln(e) = 1, ln(1) = 0"
    ],
    "ornek": "log₂(8) = 3 çünkü 2³ = 8",
    "adimlar": [
      "Tabanı ve sayıyı belirle",
      "Kurallarla sadeleştir",
      "Mümkünse tabanı eşitle",
      "Üs formuna çevirip çöz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Limit",
    "etiketler": ["limit", "süreklilik", "limit kuralları", "sonsuzda limit"],
    "icerik": "Bir fonksiyonun belirli bir noktaya yaklaşırken aldığı değer. lim(x→a) f(x) = L, x a'ya yaklaşırken f(x) L'ye yaklaşır.",
    "kurallar": [
      "lim(x→a) [f(x) + g(x)] = lim f + lim g",
      "lim(x→a) [f(x)·g(x)] = lim f · lim g",
      "lim(x→a) [f(x)/g(x)] = lim f / lim g (lim g ≠ 0)",
      "Belirsizlik: 0/0 veya ∞/∞ → sadeleştir veya L'Hôpital",
      "L'Hôpital: 0/0 ise f'/g' limitine bak"
    ],
    "ornek": "lim(x→2) (x²-4)/(x-2) = lim (x-2)(x+2)/(x-2) = lim(x+2) = 4",
    "adimlar": [
      "Doğrudan yerine koymayı dene",
      "Belirsizlik çıkarsa sadeleştir",
      "Gerekirse L'Hôpital uygula",
      "Sonucu yaz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Olasılık",
    "etiketler": ["olasılık", "probability", "permütasyon", "kombinasyon"],
    "icerik": "Bir olayın gerçekleşme şansı. P(A) = istenen durumlar / toplam durumlar. 0 ≤ P(A) ≤ 1.",
    "kurallar": [
      "P(A) = istenen / toplam",
      "P(A') = 1 - P(A)",
      "P(A ∪ B) = P(A) + P(B) - P(A ∩ B)",
      "Bağımsız olaylar: P(A ∩ B) = P(A) · P(B)",
      "Koşullu: P(A|B) = P(A ∩ B) / P(B)",
      "Permütasyon: P(n,r) = n! / (n-r)!",
      "Kombinasyon: C(n,r) = n! / (r!(n-r)!)"
    ],
    "ornek": "Bir zar atışında çift gelme olasılığı: 3/6 = 1/2",
    "adimlar": [
      "Toplam durum sayısını bul",
      "İstenen durum sayısını bul",
      "Oranı hesapla",
      "Sadeleştir"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Pisagor Teoremi",
    "etiketler": ["pisagor", "dik üçgen", "hipotenüs", "pythagoras"],
    "icerik": "Dik üçgende dik kenarların kareleri toplamı hipotenüsün karesine eşittir.",
    "kurallar": [
      "a² + b² = c² (c: hipotenüs)",
      "c = √(a² + b²)",
      "Dik kenar bulma: a = √(c² - b²)",
      "Yaygın üçlüler: 3-4-5, 5-12-13, 8-15-17, 7-24-25"
    ],
    "ornek": "Dik kenarlar 6 ve 8 → c = √(36+64) = √100 = 10",
    "adimlar": [
      "Hipotenüsü belirle (dik açının karşısı)",
      "Bilinenleri formülde yerine koy",
      "Karekökü al",
      "Birimini yaz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Üslü Sayılar",
    "etiketler": ["üs", "kuvvet", "üslü sayı", "exponent"],
    "icerik": "a^n = a·a·...·a (n kere). a taban, n üs. Negatif üs: a^-n = 1/a^n.",
    "kurallar": [
      "a^m · a^n = a^(m+n)",
      "a^m / a^n = a^(m-n)",
      "(a^m)^n = a^(m·n)",
      "a^0 = 1 (a≠0)",
      "a^-n = 1/a^n",
      "(a·b)^n = a^n · b^n",
      "(a/b)^n = a^n / b^n"
    ],
    "ornek": "2³ · 2⁴ = 2^7 = 128",
    "adimlar": [
      "Tabanları eşitle (mümkünse)",
      "Kuralı uygula (çarpma → topla, bölme → çıkar)",
      "Sadeleştir"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Karekök",
    "etiketler": ["karekök", "sqrt", "kare kök", "kök alma"],
    "icerik": "√x, karesi x olan pozitif sayıdır. √4 = 2, √9 = 3. Tam kare olmayan sayılar sadeleştirilebilir: √8 = 2√2.",
    "kurallar": [
      "√(a·b) = √a · √b",
      "√(a/b) = √a / √b",
      "√(a²) = |a|",
      "(√a)² = a",
      "√a + √b ≠ √(a+b)",
      "Rasyonelleştirme: 1/√2 = √2/2"
    ],
    "ornek": "√50 = √(25·2) = √25 · √2 = 5√2",
    "adimlar": [
      "Sayıyı asal çarpanlara ayır",
      "Tam kare çarpanları dışarı çıkar",
      "Kalan kökü yaz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Mutlak Değer",
    "etiketler": ["mutlak değer", "absolute", "|x|"],
    "icerik": "|x|, x'in sıfıra olan uzaklığıdır. Her zaman ≥ 0. |x| = x (x≥0), |x| = -x (x<0).",
    "kurallar": [
      "|a| ≥ 0",
      "|a·b| = |a|·|b|",
      "|a/b| = |a|/|b|",
      "|a + b| ≤ |a| + |b| (üçgen eşitsizliği)",
      "|x| = a → x = a veya x = -a (a ≥ 0)",
      "|x| < a → -a < x < a"
    ],
    "ornek": "|x - 3| = 5 → x - 3 = 5 veya x - 3 = -5 → x = 8 veya x = -2",
    "adimlar": [
      "Mutlak değerli ifadeyi yalnız bırak",
      "İçerideki ifadeyi + ve - olarak ayır",
      "Her denklemi çöz"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Fonksiyonlar",
    "etiketler": ["fonksiyon", "function", "tanım kümesi", "değer kümesi", "bileşke"],
    "icerik": "Bir kümeden diğerine her elemana tek bir karşılık atayan kural. f: A → B. Tanım kümesi (domain): girdiler, değer kümesi (range): çıktılar.",
    "kurallar": [
      "Bire-bir: her farklı girdi farklı çıktı",
      "Örten: değer kümesindeki her eleman bir çıktı",
      "Bileşke: (f∘g)(x) = f(g(x))",
      "Ters fonksiyon: f⁻¹(f(x)) = x",
      "Doğrusal: f(x) = ax + b"
    ],
    "ornek": "f(x) = 2x + 1, g(x) = x². (f∘g)(3) = f(g(3)) = f(9) = 19",
    "adimlar": [
      "İçteki fonksiyonu önce çöz",
      "Sonucu dıştaki fonksiyonda yerine koy",
      "Tanım kümesi kısıtlarına dikkat et"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Asal Sayılar ve Çarpanlar",
    "etiketler": ["asal", "asal sayı", "çarpan", "ebob", "ekok", "prime"],
    "icerik": "Asal sayı: 1 ve kendisinden başka böleni olmayan 1'den büyük tam sayı. En küçük asal: 2 (tek çift asal).",
    "kurallar": [
      "2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31... asal sayılardır",
      "1 asal değildir",
      "En büyük asal bilinmiyor (sonsuz tane var - Öklid)",
      "EBOB: en büyük ortak bölen",
      "EKOK: en küçük ortak kat",
      "EBOB(a,b) · EKOK(a,b) = a · b"
    ],
    "ornek": "EBOB(12, 18) = 6, EKOK(12, 18) = 36. Kontrol: 6·36 = 216 = 12·18 ✓",
    "adimlar": [
      "Sayıları asal çarpanlarına ayır",
      "EBOB: ortak asalların en küçük üssünü al",
      "EKOK: tüm asalların en büyük üssünü al"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Polinomlar",
    "etiketler": ["polinom", "polynomial", "derece", "katsayı"],
    "icerik": "Tek değişkenli, negatif olmayan tamsayı kuvvetlerden oluşan ifade. P(x) = aₙxⁿ + ... + a₁x + a₀.",
    "kurallar": [
      "Derece: en yüksek üs",
      "Baş katsayı: en yüksek dereceli terimin katsayısı",
      "Sabit terim: değişkensiz terim",
      "Polinom bölmesi: bölünen = bölen·bölüm + kalan",
      "Kalan teoremi: P(a), P(x)'in (x-a)'ya bölümünden kalan",
      "Çarpan teoremi: P(a) = 0 ise (x-a) çarpandır"
    ],
    "ornek": "P(x) = 2x³ - 5x² + 3x - 1, derece 3, baş katsayı 2, sabit terim -1",
    "adimlar": [
      "Terimleri dereceye göre sırala",
      "Benzer terimleri birleştir",
      "İşlemleri yap"
    ]
  },
  {
    "ders": "Matematik",
    "konu": "Yüzde ve Faiz",
    "etiketler": ["yüzde", "faiz", "indirim", "zam", "percent"],
    "icerik": "Yüzde, 100'ün kesri. %25 = 25/100 = 0,25. Faiz: anapara · oran · süre / 100.",
    "kurallar": [
      "Bir sayının %p'si = sayı · p / 100",
      "Yüzde artış: (yeni - eski) / eski · 100",
      "Basit faiz: F = A · r · t / 100",
      "Bileşik faiz: A · (1 + r/100)^t",
      "İndirim sonrası: fiyat · (1 - oran/100)"
    ],
    "ornek": "1500 TL'nin %20'si = 1500 · 20/100 = 300 TL",
    "adimlar": [
      "Yüzde oranını ondalığa çevir",
      "Sayıyla çarp",
      "Sonucu yorumla"
    ]
  }
]
// content/fizik.json
[
  {
    "ders": "Fizik",
    "konu": "Hareket ve Hız",
    "etiketler": ["hız", "sürat", "hareket", "yol", "zaman", "ivme", "velocity"],
    "icerik": "Hız = yer değiştirme / zaman (vektörel). Sürat = alınan yol / zaman (skaler). İvme = hız değişimi / zaman.",
    "formuller": [
      "v = x / t (sabit hız)",
      "a = Δv / Δt",
      "v = v₀ + a·t",
      "x = v₀·t + ½·a·t²",
      "v² = v₀² + 2·a·x"
    ],
    "ornek": "120 km'yi 2 saatte alan araç: v = 120/2 = 60 km/h",
    "adimlar": [
      "Verilenleri ve isteneni yaz",
      "Birimleri SI'ya çevir (km/h → m/s için 3,6'ya böl)",
      "Uygun formülü seç",
      "Yerine koy ve hesapla"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Newton Yasaları",
    "etiketler": ["newton", "kuvvet", "ivme", "eylemsizlik", "etki tepki", "force"],
    "icerik": "1. Yasa (Eylemsizlik): Kuvvet yoksa hareket değişmez. 2. Yasa: F = m·a. 3. Yasa: Her etkiye eşit ve zıt bir tepki vardır.",
    "formuller": [
      "F = m · a",
      "1 N = 1 kg · m/s²",
      "Ağırlık: G = m · g (g ≈ 9,8 m/s²)",
      "Net kuvvet = kütle × ivme",
      "Sürtünme: F_s = μ · N"
    ],
    "ornek": "10 kg kütleye 20 N kuvvet uygulanırsa: a = F/m = 20/10 = 2 m/s²",
    "adimlar": [
      "Serbest cisim diyagramı çiz",
      "Tüm kuvvetleri göster",
      "Net kuvveti bul",
      "F = m·a uygula"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "İş, Enerji ve Güç",
    "etiketler": ["iş", "enerji", "güç", "kinetik", "potansiyel", "joule", "watt"],
    "icerik": "İş = kuvvet · yol (kuvvet yönünde). Enerji iş yapabilme kapasitesi. Güç = iş / zaman.",
    "formuller": [
      "W = F · x · cos θ",
      "Kinetik enerji: Ek = ½·m·v²",
      "Potansiyel enerji: Ep = m·g·h",
      "Mekanik enerji korunumu: Ek + Ep = sabit",
      "Güç: P = W / t = F · v",
      "1 J = 1 N·m, 1 W = 1 J/s"
    ],
    "ornek": "2 kg cisim 5 m/s hızla → Ek = ½·2·25 = 25 J",
    "adimlar": [
      "Kuvvet ve yol aynı yönde mi?",
      "Kinetik/potansiyel enerjiyi hesapla",
      "Enerji korunumu uygula",
      "Güç için zamana böl"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Elektrik ve Ohm Kanunu",
    "etiketler": ["ohm", "direnç", "gerilim", "akım", "voltaj", "elektrik"],
    "icerik": "V = I·R. Gerilim (V, volt), akım (I, amper) ve direnç (R, ohm) arasındaki ilişki. Seri: R_toplam = R₁+R₂. Paralel: 1/R = 1/R₁+1/R₂.",
    "formuller": [
      "V = I · R",
      "P = V · I = I²·R = V²/R",
      "Seri: R_toplam = R₁ + R₂ + ...",
      "Paralel: 1/R_toplam = 1/R₁ + 1/R₂ + ...",
      "Seri: akım aynı, gerilim bölünür",
      "Paralel: gerilim aynı, akım bölünür"
    ],
    "ornek": "12 V kaynağa 4 Ω direnç → I = V/R = 12/4 = 3 A",
    "adimlar": [
      "Devre tipini belirle (seri/paralel)",
      "Eşdeğer direnci bul",
      "Ohm kanununu uygula",
      "Güç gerekiyorsa P = V·I"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Basınç",
    "etiketler": ["basınç", "pressure", "pascal", "sıvı basıncı"],
    "icerik": "Basınç = kuvvet / yüzey alanı. P = F/A. Birimi Pascal (Pa = N/m²). Sıvı basıncı derinliğe bağlıdır.",
    "formuller": [
      "P = F / A",
      "Sıvı basıncı: P = ρ·g·h",
      "Atmosfer basıncı: 1 atm ≈ 101325 Pa",
      "1 Pa = 1 N/m²",
      "1 bar = 10⁵ Pa"
    ],
    "ornek": "100 N kuvvet 0,5 m² alana → P = 100/0,5 = 200 Pa",
    "adimlar": [
      "Kuvveti ve alanı belirle",
      "Birimleri SI'ya çevir",
      "P = F/A uygula",
      "Sıvıda ρ·g·h ekle"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Dalgalar ve Ses",
    "etiketler": ["dalga", "ses", "frekans", "periyot", "dalga boyu", "wave"],
    "icerik": "Dalga: enerji taşıyan titreşim. Ses, maddesel ortamda yayılan boyuna dalga. Boşlukta yayılmaz.",
    "formuller": [
      "v = λ · f (hız = dalga boyu × frekans)",
      "f = 1/T (frekans = 1/periyot)",
      "Ses hızı havada ≈ 343 m/s",
      "Işık hızı boşlukta c = 3·10⁸ m/s",
      "Ses hızı katıda > sıvıda > gazda"
    ],
    "ornek": "Frekans 500 Hz, dalga boyu 0,68 m → v = 500·0,68 = 340 m/s",
    "adimlar": [
      "Verilen büyüklükleri yaz",
      "v = λ·f bağlantısını kur",
      "Birimleri kontrol et",
      "Sonucu hesapla"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Işık ve Optik",
    "etiketler": ["ışık", "optik", "yansıma", "kırılma", "mercek", "ayna", "light"],
    "icerik": "Işık doğrusal yayılır, yansır, kırılır. Kırılma: snell yasası. Aynalar ve mercekler görüntü oluşturur.",
    "formuller": [
      "Yansıma: geliş açısı = yansıma açısı",
      "Snell: n₁·sin θ₁ = n₂·sin θ₂",
      "Kırılma indisi: n = c/v",
      "Mercek: 1/f = 1/d_o + 1/d_i",
      "Büyütme: m = -d_i/d_o",
      "İnce kenarlı mercek yakınsar, kalın kenarlı ıraksar"
    ],
    "ornek": "Suya (n=1,33) 30° ile giren ışık: sin θ₂ = 1·sin30/1,33 ≈ 0,376 → θ₂ ≈ 22°",
    "adimlar": [
      "Ortamların kırılma indislerini yaz",
      "Snell yasasını uygula",
      "Yansıma varsa açı korunur",
      "Mercek için ince mercek denklemi"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Isı ve Sıcaklık",
    "etiketler": ["ısı", "sıcaklık", "kalorimetre", "termal", "heat"],
    "icerik": "Sıcaklık ortalama kinetik enerji, ısı transfer edilen enerji. Q = m·c·ΔT.",
    "formuller": [
      "Q = m · c · ΔT",
      "Erime ısısı: Q = m · L_e",
      "Buharlaşma ısısı: Q = m · L_b",
      "Suyun özısısı: c = 1 cal/g·°C = 4186 J/kg·K",
      "Suyun erime ısısı: L_e = 334 kJ/kg",
      "Suyun kaynama ısısı: L_b = 2260 kJ/kg"
    ],
    "ornek": "2 kg suyu 20°C'den 80°C'ye ısıtmak: Q = 2·4186·60 ≈ 502 kJ",
    "adimlar": [
      "Hâl değişimi var mı?",
      "Sadece sıcaklık değişimi → Q=m·c·ΔT",
      "Hâl değişimi → Q=m·L",
      "Toplam ısıyı hesapla"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Momentum ve Çarpışma",
    "etiketler": ["momentum", "çarpışma", "esnek", "esnek olmayan", "impuls"],
    "icerik": "Momentum p = m·v. İmpuls F·Δt momentum değişimidir. Kapalı sistemde momentum korunur.",
    "formuller": [
      "p = m · v",
      "İmpuls: J = F·Δt = Δp",
      "Momentum korunumu: m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'",
      "Esnek çarpışmada kinetik enerji de korunur",
      "Esnek olmayan: cisimler birleşir, ortak hız"
    ],
    "ornek": "2 kg, 5 m/s → 4 kg, 2 m/s ile çarpışıp yapışırsa: v' = (10+8)/6 = 3 m/s",
    "adimlar": [
      "Önce/sonra momentumları yaz",
      "Korunum denklemini kur",
      "Bilinmeyeni çöz",
      "Enerji kaybı var mı kontrol et"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Denge ve Moment",
    "etiketler": ["denge", "moment", "tork", "kaldıraç", "torque"],
    "icerik": "Kuvvetin döndürme etkisi: moment = kuvvet · kuvvet kolu. Denge için net kuvvet ve net moment sıfır.",
    "formuller": [
      "Moment: M = F · d (dik uzaklık)",
      "Denge: ΣF = 0 ve ΣM = 0",
      "Kaldıraç: F₁·d₁ = F₂·d₂",
      "Makarada: sabit F=G, hareketli F=G/2",
      "1. tür kaldıraç: destek ortada"
    ],
    "ornek": "1 m'lik kaldıraçta 100 N, 2 m'lik kolda: F·2 = 100·1 → F = 50 N",
    "adimlar": [
      "Tüm kuvvetleri göster",
      "Destek noktasını belirle",
      "Moment denklemini kur",
      "Bilinmeyeni çöz"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Manyetizma",
    "etiketler": ["manyetizma", "mıknatıs", "manyetik alan", "elektromıknatıs"],
    "icerik": "Manyetik alan B, hareketli yüklere kuvvet uygular. Sağ el kuralı: akım → alan yönü.",
    "formuller": [
      "F = q·v·B·sin θ (Lorentz kuvveti)",
      "F = B·I·L (akım taşıyan tel)",
      "B = μ₀·I / (2π·r) (uzun tel)",
      "B = μ₀·N·I / L (selenoid)",
      "μ₀ = 4π·10⁻⁷ T·m/A"
    ],
    "ornek": "0,5 T alanda 2 A akım taşıyan 0,3 m tel: F = 0,5·2·0,3 = 0,3 N",
    "adimlar": [
      "Vektör yönlerini belirle",
      "Sağ el kuralını uygula",
      "Formülde yerine koy",
      "Yönü vektörel olarak yaz"
    ]
  },
  {
    "ders": "Fizik",
    "konu": "Serbest Düşme ve Atış",
    "etiketler": ["serbest düşme", "atış", "mermi", "düşme", "projectile"],
    "icerik": "Yerçekimi etkisiyle hareket. Yatay atışta yatay hız sabit, düşey hareket ivmeli.",
    "formuller": [
      "Serbest düşme: h = ½·g·t²",
      "v = g·t",
      "Yatay atış: x = v₀·t",
      "Düşey: y = ½·g·t²",
      "Eğik atış menzil: R = v₀²·sin(2θ)/g",
      "Maksimum yükseklik: h = v₀²·sin²θ/(2g)"
    ],
    "ornek": "20 m yüksekten bırakılan cisim: t = √(2·20/9,8) ≈ 2 s",
    "adimlar": [
      "Yatay ve düşey hareketi ayır",
      "Düşey: ivmeli hareket formülleri",
      "Yatay: sabit hız",
      "Zamanı birleştir"
    ]
  }
]
// content/kimya.json
[
  {
    "ders": "Kimya",
    "konu": "Mol Kavramı",
    "etiketler": ["mol", "avogadro", "mol kütlesi", "mol sayısı", "tanecik"],
    "icerik": "Mol, 6,02·10²³ tanecik içeren madde miktarıdır. Avogadro sayısı N_A = 6,02·10²³. Mol kütlesi M (g/mol), bir maddenin 1 molünün gram cinsinden kütlesidir.",
    "formuller": [
      "n = m / M (mol = kütle / mol kütlesi)",
      "N = n · N_A (tanecik sayısı)",
      "n = V / 22,4 (gazlar için NŞA'da, V litre)",
      "Mol kütlesi = atomik kütlelerin toplamı",
      "1 mol H₂O = 18 g = 6,02·10²³ molekül"
    ],
    "ornek": "36 g su kaç mol? n = 36/18 = 2 mol → 2·6,02·10²³ = 1,204·10²⁴ molekül",
    "adimlar": [
      "Verilenleri belirle (kütle, tanecik veya hacim)",
      "Mol kütlesini hesapla",
      "Uygun formülü seç",
      "Mol sayısını bul"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Kimyasal Tepkimeler",
    "etiketler": ["tepkime", "reaksiyon", "denklem denkleştirme", "sentez", "analiz"],
    "icerik": "Tepkimelerde atom sayısı korunur. Denkleştirme: her elementin her iki tarafta eşit olması. Tepkime türleri: sentez, analiz, yer değiştirme, çökelme, yanma.",
    "kurallar": [
      "Sentez: A + B → AB",
      "Analiz: AB → A + B",
      "Yer değiştirme: A + BC → AC + B",
      "Çift yer değiştirme: AB + CD → AD + CB",
      "Yanma: CₓHᵧ + O₂ → CO₂ + H₂O",
      "Denkleştirmede katsayı değiştirilir, alt indis değiştirilmez"
    ],
    "ornek": "2H₂ + O₂ → 2H₂O (4 H, 2 O her iki tarafta eşit)",
    "adimlar": [
      "Tepkime denklemini yaz",
      "Her elementin sayısını say",
      "Katsayıları ayarla (en karmaşık bileşikten başla)",
      "Kontrol et: her element eşit mi?"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Asit-Baz",
    "etiketler": ["asit", "baz", "ph", "nötralleşme", "turnusol"],
    "icerik": "Asit: H⁺ veren (proton donörü). Baz: H⁺ alan (proton akseptörü). pH = -log[H⁺]. pH < 7 asidik, = 7 nötr, > 7 bazik.",
    "formuller": [
      "pH = -log[H⁺]",
      "pOH = -log[OH⁻]",
      "pH + pOH = 14 (25°C'de)",
      "[H⁺]·[OH⁻] = 10⁻¹⁴",
      "Nötralleşme: asit + baz → tuz + su",
      "Kuvvetli asitler: HCl, HNO₃, H₂SO₄"
    ],
    "ornek": "[H⁺] = 10⁻³ M ise pH = 3 (asidik). [OH⁻] = 10⁻² M ise pOH = 2 → pH = 12 (bazik)",
    "adimlar": [
      "Verilen derişimi belirle",
      "pH veya pOH hesapla",
      "pH + pOH = 14 kontrolü yap",
      "Asidik/bazik/nötr yorumla"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Periyodik Tablo",
    "etiketler": ["periyodik", "element", "grup", "periyot", "metal", "ametal"],
    "icerik": "Elementler atom numarasına göre sıralanır. 18 grup (dikey), 7 periyot (yatay). Aynı grupta benzer kimyasal özellikler.",
    "kurallar": [
      "1A: alkali metaller (H hariç)",
      "2A: toprak alkali metaller",
      "7A: halojenler",
      "8A: soy gazlar (kararlı)",
      "Soldan sağa: metalik özellik azalır, elektronegatiflik artar",
      "Yukarıdan aşağıya: atom yarıçapı artar",
      "Geçiş metalleri: B grupları (3B-12B)"
    ],
    "ornek": "Na (11): 3. periyot, 1A grubu, alkali metal. Cl (17): 3. periyot, 7A grubu, halojen",
    "adimlar": [
      "Atom numarasını bul",
      "Elektron dizilimini yaz",
      "Son katman elektron sayısı → grup",
      "Katman sayısı → periyot"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Kimyasal Bağlar",
    "etiketler": ["bağ", "iyonik", "kovalent", "metalik", "bond", "elektron"],
    "icerik": "Atomlar bağ yaparken kararlı (soy gaz) elektron dizilimine ulaşır. İyonik: elektron transferi. Kovalent: elektron paylaşımı. Metalik: elektron denizi.",
    "kurallar": [
      "İyonik: metal + ametal (NaCl, MgO)",
      "Kovalent: ametal + ametal (H₂O, CO₂)",
      "Polar kovalent: farklı elektronegatiflik (HCl)",
      "Apolar kovalent: aynı atomlar (H₂, Cl₂)",
      "Metalik: metaller arası (Fe, Cu)",
      "Elektronegatiflik farkı > 1,7 → iyonik"
    ],
    "ornek": "NaCl: Na⁺ + Cl⁻ iyonik. H₂O: O-H kovalent (polar). CO₂: C=O çift bağ kovalent",
    "adimlar": [
      "Elementlerin türünü belirle (metal/ametal)",
      "Elektronegatiflik farkına bak",
      "Bağ türünü belirle",
      "Lewis yapısını çiz"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Çözeltiler ve Derişim",
    "etiketler": ["çözelti", "derişim", "molarite", "çözünme", "solvent"],
    "icerik": "Çözelti: çözünen + çözücü homojen karışım. Molarite: 1 litre çözeltideki mol sayısı. M = n/V(L).",
    "formuller": [
      "M = n / V (V litre cinsinden)",
      "n = M · V",
      "Seyreltme: M₁·V₁ = M₂·V₂",
      "% derişim = (çözünen/çözelti)·100",
      "ppm = (çözünen/çözelti)·10⁶",
      "Çözünürlük sıcaklıkla artar (genelde)"
    ],
    "ornek": "0,5 mol NaCl 2 L suda: M = 0,5/2 = 0,25 M",
    "adimlar": [
      "Mol sayısını hesapla",
      "Hacmi litreye çevir",
      "M = n/V uygula",
      "Seyreltmede M₁V₁ = M₂V₂ kullan"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Gazlar",
    "etiketler": ["gaz", "ideal gaz", "basınç", "hacim", "sıcaklık", "gaz yasaları"],
    "icerik": "İdeal gaz yasası: PV = nRT. R = 0,082 L·atm/mol·K. Gazlar sıkıştırılabilir, genleşir, karışır.",
    "formuller": [
      "PV = nRT (ideal gaz yasası)",
      "Boyle: P₁V₁ = P₂V₂ (sabit T)",
      "Charles: V₁/T₁ = V₂/T₂ (sabit P)",
      "Gay-Lussac: P₁/T₁ = P₂/T₂ (sabit V)",
      "Avogadro: V₁/n₁ = V₂/n₂",
      "R = 0,082 L·atm/mol·K",
      "Sıcaklık Kelvin cinsinden (K = °C + 273)"
    ],
    "ornek": "2 mol gaz 27°C'de 5 L hacimde: P = nRT/V = (2·0,082·300)/5 ≈ 9,84 atm",
    "adimlar": [
      "Verilenleri SI birimlerine çevir",
      "Sıcaklığı Kelvin'e çevir",
      "PV = nRT uygula",
      "Sabit değişkenli durumlarda oran kullan"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Atom ve Elektron Dizilimi",
    "etiketler": ["atom", "elektron", "proton", "nötron", "dizilim", "orbital"],
    "icerik": "Atom: proton (+), nötron (0) çekirdekte; elektron (-) katmanlarda. Elektron dizilimi: 1s², 2s², 2p⁶, 3s², 3p⁶, 4s²...",
    "kurallar": [
      "Proton sayısı = atom numarası = element kimliği",
      "Nötron sayısı = kütle no - proton no",
      "İzotop: aynı proton, farklı nötron",
      "İyon: elektron almış/vermiş atom",
      "Aufbau: enerji seviyesi düşükten yükseğe doldur",
      "Pauli: aynı orbitalde 2 elektron, zıt spin",
      "Hund: eşit enerjili orbitallere önce tek tek"
    ],
    "ornek": "Na (11): 1s² 2s² 2p⁶ 3s¹. Son katmanda 1 elektron → 1A grubu",
    "adimlar": [
      "Atom numarasını yaz",
      "Aufbau sırasını takip et",
      "Son katman elektron sayısını bul",
      "Grup ve periyodu belirle"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Kimyasal Denge",
    "etiketler": ["denge", "le chatelier", "denge sabiti", "equilibrium"],
    "icerik": "Tersinir tepkimelerde ileri ve geri hız eşitlendiğinde denge kurulur. Denge sabiti K = [ürünler]/[girenler].",
    "kurallar": [
      "aA + bB ⇌ cC + dD için K_c = [C]^c[D]^d / [A]^a[B]^b",
      "K > 1: ürünler baskın",
      "K < 1: girenler baskın",
      "Le Chatelier: dengeyi bozan etkiye karşı sistem direnir",
      "Sıcaklık artışı → endotermik yönü destekler",
      "Basınç artışı → mol sayısı az olan yönü destekler",
      "Katalizör dengeyi değiştirmez, hızlandırır"
    ],
    "ornek": "N₂ + 3H₂ ⇌ 2NH₃ (ekzotermik). Sıcaklık artarsa NH₃ azalır. Basınç artarsa NH₃ artar",
    "adimlar": [
      "Denge denklemini yaz",
      "Etkiyi belirle (sıcaklık, basınç, derişim)",
      "Le Chatelier uygula",
      "Yönü belirle (ileri/geri)"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Organik Kimya Temelleri",
    "etiketler": ["organik", "karbon", "alkol", "asit", "hidrokarbon"],
    "icerik": "Karbon bileşiklerini inceleyen kimya dalı. Karbon 4 bağ yapar. Zincir, dallanma, halka yapıları oluşturur.",
    "kurallar": [
      "Alkan: CₙH₂ₙ₊₂ (tek bağ)",
      "Alken: CₙH₂ₙ (çift bağ)",
      "Alkin: CₙH₂ₙ₋₂ (üç bağ)",
      "Alkol: -OH grubu (CₙH₂ₙ₊₁OH)",
      "Karboksilik asit: -COOH",
      "Aldehit: -CHO",
      "Keton: C=O",
      "Benzen: C₆H₆, aromatik halka"
    ],
    "ornek": "Metan CH₄, etanol C₂H₅OH, asetik asit CH₃COOH, benzen C₆H₆",
    "adimlar": [
      "Fonksiyonel grubu belirle",
      "Karbon zincirini say",
      "Adlandırma kuralını uygula",
      "İzomerleri kontrol et"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Yükseltgenme-İndirgenme",
    "etiketler": ["redoks", "yükseltgenme", "indirgenme", "elektron transferi"],
    "icerik": "Redoks tepkimelerinde elektron transferi olur. Yükseltgenme: elektron kaybı. İndirgenme: elektron kazanımı. İkisi birlikte gerçekleşir.",
    "kurallar": [
      "Yükseltgenme sayısı artar → yükseltgenme",
      "Yükseltgenme sayısı azalır → indirgenme",
      "Yükseltgen madde indirgenir, indirgen madde yükseltgenir",
      "Serbest elementlerin yükseltgenme sayısı 0",
      "Oksijen genelde -2, hidrojen +1",
      "Yükseltgenme sayıları toplamı = iyon yükü"
    ],
    "ornek": "Zn + Cu²⁺ → Zn²⁺ + Cu. Zn yükseltgenir (0→+2), Cu²⁺ indirgenir (+2→0)",
    "adimlar": [
      "Her elementin yükseltgenme sayısını belirle",
      "Değişimi bul",
      "Yükseltgenen/indirgenen belirle",
      "Yarı tepkimeleri denkleştir"
    ]
  },
  {
    "ders": "Kimya",
    "konu": "Radyoaktivite",
    "etiketler": ["radyoaktivite", "alfa", "beta", "gama", "yarılanma"],
    "icerik": "Kararsız çekirdeklerin ışıma yapması. Alfa (α): ⁴₂He, beta (β): elektron, gama (γ): yüksek enerjili foton.",
    "kurallar": [
      "Alfa bozunması: kütle -4, atom no -2",
      "Beta bozunması: kütle değişmez, atom no +1",
      "Gama: kütle ve atom no değişmez, sadece enerji",
      "Yarılanma: N = N₀·(1/2)^(t/T)",
      "Yarılanma süresi sabittir",
      "Alfa en az, gama en çok nüfuz eder"
    ],
    "ornek": "²³⁸U → ²³⁴Th + α. 8 g örnek 2 yarılanmada 2 g kalır",
    "adimlar": [
      "Bozunma türünü belirle",
      "Kütle ve atom numarası korunumu uygula",
      "Yarılanma formülünü kullan",
      "Zamanı hesapla"
    ]
  }
]
// content/biyoloji.json
[
  {
    "ders": "Biyoloji",
    "konu": "Hücre Yapısı",
    "etiketler": ["hücre", "organel", "zar", "çekirdek", "mitokondri"],
    "icerik": "Hücre canlıların temel yapı birimi. Prokaryot (çekirdeksiz) ve ökaryot (çekirdekli) olarak ikiye ayrılır. Organeller belirli işlevlere sahiptir.",
    "organeller": [
      "Çekirdek: DNA'yı barındırır, kalıtım merkezi",
      "Mitokondri: enerji üretimi (ATP), 'hücrenin güç santrali'",
      "Ribozom: protein sentezi",
      "Endoplazmik retikulum: madde taşıma, protein/lipid sentezi",
      "Golgi: paketleme ve salgılama",
      "Lizozom: sindirim enzimi",
      "Kloroplast: fotosentez (yalnızca bitki)",
      "Koful: su ve madde depolama"
    ],
    "ornek": "Bitki hücresi: çeper, kloroplast, büyük koful var. Hayvan hücresi: bunlar yok, sentrozom var",
    "adimlar": [
      "Hücre tipini belirle (bitki/hayvan/prokaryot)",
      "Organelleri listele",
      "İşlevini açıkla"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Fotosentez",
    "etiketler": ["fotosentez", "kloroplast", "klorofil", "ışık", "photosynthesis"],
    "icerik": "Bitkilerin güneş enerjisini kimyasal enerjiye çevirdiği süreç. Kloroplastta gerçekleşir. Klorofil pigmenti ışığı soğurur.",
    "formuller": [
      "6CO₂ + 6H₂O + ışık → C₆H₁₂O₆ + 6O₂",
      "Işık tepkimeleri: tilakoit zarda, ATP + NADPH üretir",
      "Calvin döngüsü: stromada, CO₂'den glikoz üretir",
      "Işık şiddeti artarsa hız artar (doyma noktasına kadar)",
      "CO₂ artarsa hız artar (doyma noktasına kadar)",
      "Sıcaklık enzimleri etkiler"
    ],
    "ornek": "Bir bitki güneşte: CO₂ alır, O₂ verir. Karanlıkta: sadece solunum, O₂ alır, CO₂ verir",
    "adimlar": [
      "Girenleri ve çıkanları yaz",
      "Işık ve karanlık tepkimeleri ayır",
      "Hangi faktörün sınırlayıcı olduğunu belirle",
      "Hızı yorumla"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Hücresel Solunum",
    "etiketler": ["solunum", "glikoliz", "krebs", "atp", "oksijen"],
    "icerik": "Besinlerden ATP üretimi. Oksijenli: glikoliz + Krebs + ETS (en verimli). Oksijensiz: fermantasyon (az ATP).",
    "formuller": [
      "Glikoliz: glikoz → 2 pirüvat + 2 ATP + 2 NADH",
      "Krebs: 2 ATP + 6 NADH + 2 FADH₂ + 4 CO₂",
      "ETS: NADH/FADH₂ → ATP (yaklaşık 30 ATP)",
      "Toplam oksijenli: ~32 ATP / glikoz",
      "Laktik asit fermantasyonu: 2 ATP",
      "Alkol fermantasyonu: 2 ATP + etanol + CO₂"
    ],
    "ornek": "1 glikoz oksijenli solunumda ~32 ATP üretir. Oksijensizde sadece 2 ATP",
    "adimlar": [
      "Oksijen var mı?",
      "Aşamaları sırala",
      "ATP sayısını hesapla",
      "Yan ürünleri yaz"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "DNA ve RNA",
    "etiketler": ["dna", "rna", "nükleotit", "baz", "genetik kod"],
    "icerik": "DNA: çift sarmal, deoksiriboz, A-T, G-C. RNA: tek sarmal, riboz, A-U, G-C. DNA kalıtımı taşır, RNA protein sentezinde görev alır.",
    "kurallar": [
      "DNA bazları: A (adenin), T (timin), G (guanin), C (sitimozin)",
      "RNA'da T yerine U (urasil)",
      "A=T, G≡C (Chargaff kuralı)",
      "DNA çift sarmal, antiparalel",
      "mRNA: protein sentezi için taşıyıcı",
      "tRNA: amino asit taşır",
      "rRNA: ribozom yapısı"
    ],
    "ornek": "DNA dizisi 5'-ATGC-3' ise karşı iplik 3'-TACG-5'. mRNA: 5'-AUGC-3'",
    "adimlar": [
      "İplik yönünü belirle (5'→3')",
      "Eşleşme kurallarını uygula",
      "Tamamlayıcı ipliği yaz",
      "RNA için T→U çevir"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Protein Sentezi",
    "etiketler": ["protein", "translasyon", "transkripsiyon", "kodon", "genetik"],
    "icerik": "DNA → mRNA (transkripsiyon) → protein (translasyon). Kodon: 3 nükleotit, bir amino asidi kodlar.",
    "kurallar": [
      "Transkripsiyon: çekirdekte, DNA → mRNA",
      "Translasyon: ribozomda, mRNA → protein",
      "Kodon: 3 baz = 1 amino asit",
      "64 kodon, 20 amino asit",
      "AUG: başlangıç kodonu (metionin)",
      "UAA, UAG, UGA: stop kodonları",
      "Genetik kod evrenseldir (neredeyse)"
    ],
    "ornek": "mRNA: AUG-GCA-UUU-UAA → Met-Ala-Phe-STOP",
    "adimlar": [
      "DNA'dan mRNA oluştur (T→U)",
      "Kodonlara ayır (3'erli)",
      "Kodon tablosundan amino asitleri bul",
      "Stop kodonuna kadar devam et"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Mitoz ve Mayoz",
    "etiketler": ["mitoz", "mayoz", "hücre bölünmesi", "kromozom"],
    "icerik": "Mitoz: vücut hücreleri, 2 özdeş hücre (2n→2n). Mayoz: üreme hücreleri, 4 farklı hücre (2n→n).",
    "kurallar": [
      "Mitoz: 1 bölünme, 2 hücre, kromozom sayısı korunur",
      "Mayoz: 2 bölünme, 4 hücre, kromozom yarıya iner",
      "Mitoz evreleri: profaz, metafaz, anafaz, telofaz",
      "Mayoz I: homolog kromozomlar ayrılır (crossing-over)",
      "Mayoz II: kardeş kromatitler ayrılır",
      "Crossing-over: genetik çeşitlilik",
      "Mayoz üreme hücrelerinde (gametlerde) görülür"
    ],
    "ornek": "İnsan vücut hücresi 46 kromozom. Mitozla 46→46, mayozla 46→23",
    "adimlar": [
      "Hücre tipini belirle (vücut/üreme)",
      "Mitoz mu mayoz mu?",
      "Evreleri sırala",
      "Kromozom sayısını kontrol et"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Kalıtım (Genetik)",
    "etiketler": ["kalıtım", "mendel", "genotip", "fenotip", "baskın", "çekinik"],
    "icerik": "Mendel yasaları: ayrılma, bağımsız dağılım. Genotip: gen yapısı (AA, Aa, aa). Fenotip: dış görünüş. Baskın (A) ve çekinik (a) aleller.",
    "kurallar": [
      "Baskın homozigot: AA",
      "Heterozigot: Aa (baskın görünür)",
      "Çekinik homozigot: aa",
      "Aa × Aa → 1AA : 2Aa : 1aa (fenotip 3:1)",
      "Aa × aa → 1Aa : 1aa (fenotip 1:1)",
      "Ayrılma yasası: aleller gametlere ayrı ayrı gider",
      "Bağımsız dağılım: farklı karakterler bağımsız"
    ],
    "ornek": "Aa × Aa çaprazı → %75 baskın fenotip, %25 çekinik. Genotip: 1:2:1",
    "adimlar": [
      "Genotipleri yaz",
      "Punnett karesi kur",
      "Olasılıkları hesapla",
      "Fenotip oranını yaz"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Enzimler",
    "etiketler": ["enzim", "katalizör", "substrat", "aktif bölge", "ph"],
    "icerik": "Biyolojik katalizörler, tepkimeleri hızlandırır. Protein yapılıdır. Substrata özgüdür. Aktivite sıcaklık ve pH'a bağlıdır.",
    "kurallar": [
      "Enzim + substrat → enzim-substrat kompleksi → ürün + enzim",
      "Enzim tepkimeden değişmeden çıkar",
      "Optimum sıcaklık: ~37°C (insan enzimleri)",
      "Yüksek sıcaklık enzimi denatüre eder (geri dönüşsüz)",
      "Optimum pH enzime göre değişir (pepsin: 2, tripsin: 8)",
      "Substrat derişimi artışı hızı artırır (doyma noktasına kadar)",
      "Aktivatör hızlandırır, inhibitör yavaşlatır"
    ],
    "ornek": "Amilaz nişastayı parçalar. 37°C, pH 7'de optimum. 80°C'de denatüre olur",
    "adimlar": [
      "Enzim ve substratı belirle",
      "Ortam koşullarını kontrol et",
      "Tepkime hızını yorumla",
      "İnhibitör/aktivatör etkisini belirle"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Ekosistem ve Besin Zinciri",
    "etiketler": ["ekosistem", "besin zinciri", "üretici", "tüketici", "ayrıştırıcı"],
    "icerik": "Canlılar ve çevre arasındaki ilişki. Enerji akışı tek yönlü, madde döngüsü çok yönlü.",
    "kurallar": [
      "Üretici (prodüktör): fotosentez (bitki, alg)",
      "Birincil tüketici (otçul): üreticiyi yer",
      "İkincil tüketici (etçil): otçulu yer",
      "Ayrıştırıcı (dekompozer): ölü organik maddeyi parçalar",
      "Enerji piramidinde %10 kuralı: bir üst basamağa %10 enerji geçer",
      "Besin zinciri: enerji akışı tek yönlü",
      "Besin ağı: çoklu zincirler"
    ],
    "ornek": "Ot → tavşan → tilki → kurt. Her basamakta enerji azalır, biyokütle azalır",
    "adimlar": [
      "Basamakları belirle",
      "Üretici/tüketici/ayrıştırıcı sınıfla",
      "Enerji akışını çiz",
      "Biyokütleyi yorumla"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Sinir Sistemi",
    "etiketler": ["sinir", "nöron", "beyin", "impuls", "sinaps"],
    "icerik": "Sinir sistemi: merkezi (beyin, omurilik) ve çevresel. Nöron: sinir hücresi. İmpuls: elektrokimyasal sinyal.",
    "kurallar": [
      "Nöron yapısı: dendrit, gövde, akson, miyelin kılıf",
      "Duyusal nöron: çevreden merkeze",
      "Motor nöron: merkezden kaslara",
      "Ara nöron: merkezi sinir sisteminde",
      "Sinaps: nöronlar arası bağlantı (nörotransmitter)",
      "Beyin: düşünme, öğrenme, hafıza",
      "Omurilik: refleks merkezi",
      "Beyincik: denge ve koordinasyon",
      "Omurilik soğanı: solunum, kalp atışı"
    ],
    "ornek": "Refleks: sıcak tabağa dokunma → omurilik → elin çekilmesi (beyin devreye girmeden)",
    "adimlar": [
      "Uyarı türünü belirle",
      "İletim yolunu çiz",
      "İlgili nöronları belirle",
      "Yanıtı açıkla"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Kan Dolaşımı",
    "etiketler": ["kan", "kalp", "damar", "dolaşım", "alyuvar"],
    "icerik": "Kalp pompası, damarlar taşıyıcı. Küçük dolaşım (kalp-akciğer), büyük dolaşım (kalp-vücut).",
    "kurallar": [
      "Kalp 4 odacıklı: 2 kulakçık (atriyum), 2 karıncık (ventrikül)",
      "Atardamar (arter): kalpten uzağa, oksijenli kan (akciğer atardamarı hariç)",
      "Toplardamar (ven): kalbe doğru, oksijensiz kan (akciğer toplardamarı hariç)",
      "Kılcal damar: madde alışverişi",
      "Küçük dolaşım: sağ kalp → akciğer → sol kalp",
      "Büyük dolaşım: sol kalp → vücut → sağ kalp",
      "Alyuvar: oksijen taşır (hemoglobin)",
      "Akyuvar: bağışıklık",
      "Kan pulcukları: pıhtılaşma"
    ],
    "ornek": "Oksijensiz kan sağ kulakçık → sağ karıncık → akciğer atardamarı → akciğer → oksijenlenir",
    "adimlar": [
      "Dolaşım yolunu çiz",
      "Kanın oksijen durumunu belirle",
      "Kalp odacıklarını sırala",
      "Damar türünü belirle"
    ]
  },
  {
    "ders": "Biyoloji",
    "konu": "Bağışıklık Sistemi",
    "etiketler": ["bağışıklık", "antikor", "antijen", "akyuvar", "immün"],
    "icerik": "Vücudu hastalıklardan koruyan sistem. Doğal ve kazanılmış bağışıklık. Antikor-antijen etkileşimi.",
    "kurallar": [
      "Doğal bağışıklık: deri, mide asidi, mukus",
      "Kazanılmış: hastalık geçirme veya aşı",
      "Antijen: yabancı madde",
      "Antikor: antijene özgü protein (B hücreleri)",
      "T hücreleri: hücre içi patojenler",
      "Aşı: zayıflatılmış/ölü patojen → hafıza hücreleri",
      "Aktif bağışıklık: vücut antikor üretir",
      "Pasif bağışıklık: hazır antikor (anne sütü, serum)"
    ],
    "ornek": "Grip geçiren kişi aynı suşa karşı bağışıklık kazanır (aktif doğal). Aşı da benzer koruma sağlar",
    "adimlar": [
      "Bağışıklık türünü belirle",
      "Antijen/antikor ilişkisini kur",
      "Hücre türlerini belirle",
      "Koruma mekanizmasını açıkla"
    ]
  }
]
// content/turkce.json
[
  {
    "ders": "Türkçe",
    "konu": "Cümle Ögeleri",
    "etiketler": ["özne", "yüklem", "nesne", "dolaylı tümleç", "cümle ögeleri"],
    "icerik": "Türkçede cümlenin temel ögeleri: yüklem, özne; yardımcı ögeler: nesne, dolaylı tümleç, zarf tümleci.",
    "kurallar": [
      "Yüklem: eylem veya durum bildirir (genelde sonda)",
      "Özne: yükleme 'kim/ne' sorusu (eylemi yapan)",
      "Belirtili nesne: yükleme 'neyi/kimi' (belirtme hâli -ı/-i)",
      "Belirtisiz nesne: 'ne' sorusu (yalın hâl)",
      "Dolaylı tümleç: 'kime/kimde/kimden/nereye' (bulunma/yönelme/çıkma hâli)",
      "Zarf tümleci: 'nasıl/ne zaman/neden/ne kadar'"
    ],
    "ornek": "Ali dün kitabı okulda okudu. → Yüklem: okudu. Özne: Ali. Belirtili nesne: kitabı. Dolaylı tümleç: okulda. Zarf: dün",
    "adimlar": [
      "Önce yüklemi bul",
      "Yükleme 'kim' sorusu → özne",
      "Yükleme 'neyi/kimi' → nesne",
      "Yükleme 'nereye/kimde' → dolaylı tümleç",
      "Yükleme 'nasıl/ne zaman' → zarf"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Sözcük Türleri",
    "etiketler": ["isim", "sıfat", "zarf", "zamir", "edat", "bağlaç", "ünlem"],
    "icerik": "Türkçede 8 sözcük türü: isim, sıfat, zamir, zarf, edat, bağlaç, ünlem, fiil. Bağlam içinde belirlenir.",
    "kurallar": [
      "İsim: varlıkları karşılar (ev, ağaç, sevgi)",
      "Sıfat: ismi niteler/ belirtir (kırmızı, üç, bu)",
      "Zamir: ismin yerini tutar (ben, sen, bu, kim)",
      "Zarf: fiili/sıfatı/zarfı belirtir (hızlı, dün, çok)",
      "Edat: tek başına anlamsız, ilgi kurar (için, gibi, kadar)",
      "Bağlaç: bağlar (ve, ama, fakat, çünkü)",
      "Ünlem: duygu ifade eder (eyvah, yaşasın)",
      "Fiil: eylem (koşmak, okumak)"
    ],
    "ornek": "Kırmızı (sıfat) elma (isim) daldan (isim) düştü (fiil)",
    "adimlar": [
      "Sözcüğün cümledeki işlevine bak",
      "Yanındaki sözcüklerle ilişkisini kur",
      "Türünü belirle"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Noktalama İşaretleri",
    "etiketler": ["nokta", "virgül", "noktalı virgül", "soru işareti", "noktalama"],
    "icerik": "Yazıda anlamı netleştiren işaretler. Temel: nokta, virgül, noktalı virgül, iki nokta, soru işareti, ünlem, kesme.",
    "kurallar": [
      "Nokta (.): Cümle sonu, kısaltma (Dr.), tarih (14.11.2026)",
      "Virgül (,): Eş görevli sözcükler, sıralama, ara söz",
      "Noktalı virgül (;): Virgülle ayrılmış grupları ayırır, bağlaçsız bağlı cümle",
      "İki nokta (:): Açıklama, örnek, alıntı öncesi",
      "Soru işareti (?): Soru cümlesi sonu",
      "Ünlem (!): Duygu, seslenme, emir",
      "Kesme ('): Özel isimlere gelen ekler (Ankara'ya)",
      "Tırnak: Doğrudan alıntı, eser adı"
    ],
    "ornek": "Kitabı okudum; sonra parka gittim. — Noktalı virgül iki bağlı cümleyi ayırdı",
    "adimlar": [
      "Cümle türünü belirle (soru/ünlem/düz)",
      "Ara söz/gruplar var mı?",
      "Uygun işareti seç"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Yazım Kuralları",
    "etiketler": ["yazım", "imla", "büyük harf", "birleşik", "ayrı yazım"],
    "icerik": "Türkçe yazım kuralları: büyük harf kullanımı, birleşik/ayrı yazım, sayıların yazımı, kısaltmalar.",
    "kurallar": [
      "Cümle başı büyük harfle başlar",
      "Özel isimler büyük harfle (Ankara, Ali, Türkiye)",
      "Özel isme gelen ek kesme ile (Ali'ye, Türkiye'nin)",
      "Kurum adları büyük harfle (Türk Dil Kurumu)",
      "Sayılar rakamla veya yazıyla (5 veya beş)",
      "Saat, tarih, para belirli biçimde (14.30, 1.500 TL)",
      "Birleşik sözcükler: hanımeli, başparmak",
      "Ayrı yazılan: her gün, bir çok (yanlış) → birçok (doğru)"
    ],
    "ornek": "yanlış: 'Ali okula gitti.' doğru: 'Ali okula gitti.' (Ali özel isim, büyük)",
    "adimlar": [
      "Özel isim mi? → büyük harf",
      "Ek alıyor mu? → kesme",
      "Birleşik mi ayrı mı? → TDK sözlüğü kontrol et"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Fiiller ve Fiil Çatısı",
    "etiketler": ["fiil", "kip", "çatı", "etken", "edilgen", "dönüşlü"],
    "icerik": "Fiil: eylem, oluş, durum. Kipler: haber (zaman) ve dilek. Çatı: özne-nesne ilişkisi.",
    "kurallar": [
      "Haber kipleri: -di (geçmiş), -miş (duyulan), -yor (şimdiki), -ecek (gelecek), -r (geniş)",
      "Dilek kipleri: -meli (gereklilik), -se (şart), -e (istek), emir",
      "Etken: özne eylemi yapar (Ali okudu)",
      "Edilgen: özne eylemi almaz (-ıl/-in) (Kitap okundu)",
      "Dönüşlü: özne kendine (-ın) (Yıkandı)",
      "İşteş: karşılıklı (-ış) (Konuştu)",
      "Geçişli: nesne alır (okudu - neyi?)",
      "Geçişsiz: nesne almaz (uyudu)"
    ],
    "ornek": "Ali camı kırdı (etken, geçişli). Cam kırıldı (edilgen). Ali yıkandı (dönüşlü)",
    "adimlar": [
      "Fiilin kipini belirle",
      "Özne-nesne ilişkisine bak",
      "Çatıyı belirle"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Paragraf",
    "etiketler": ["paragraf", "ana fikir", "konu", "yardımcı fikir", "anlatım"],
    "icerik": "Paragraf: bir düşünceyi işleyen cümle grubu. Yapı: giriş, gelişme, sonuç. Ana fikir: paragrafın özü.",
    "kurallar": [
      "Konu: ne anlatılıyor?",
      "Ana fikir: konu hakkında ne söyleniyor?",
      "Yardımcı fikir: ana fikri destekleyen düşünceler",
      "Giriş: konu tanıtılır",
      "Gelişme: örnek, açıklama, karşılaştırma",
      "Sonuç: toparlama, genel yargı",
      "Anlatım biçimleri: açıklama, tartışma, betimleme, öyküleme",
      "Düşünceyi geliştirme yolları: tanımlama, örnekleme, karşılaştırma, tanık gösterme, sayısal veri"
    ],
    "ornek": "Ana fikir genelde giriş veya sonuç cümlesindedir",
    "adimlar": [
      "Paragrafı oku",
      "Konuyu belirle",
      "Ana fikri tek cümleyle ifade et",
      "Yardımcı fikirleri sırala"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Ses Bilgisi",
    "etiketler": ["ses", "ünlü", "ünsüz", "hece", "fonetik"],
    "icerik": "Türkçede 29 harf: 8 ünlü (a,e,ı,i,o,ö,u,ü), 21 ünsüz. Ünlü uyumları ve ses olayları.",
    "kurallar": [
      "Büyük ünlü uyumu: son hece a,e,ı,i → a,e,ı,i; o,ö,u,ü → o,ö,u,ü",
      "Küçük ünlü uyumu: düzlük-yuvarlaklık uyumu",
      "Ünsüz yumuşaması: p,ç,t,k → b,c,d,ğ (ünlüyle başlayan ek)",
      "Ünsüz benzeşmesi: sert ünsüz + yumuşak ünsüz → sertleşir",
      "Ünlü düşmesi: ağız → ağzı",
      "Ünlü daralması: yemek → yiyor",
      "Kaynaştırma harfi: y, ş, s, n (araya giren)"
    ],
    "ornek": "kitap + ı → kitabı (p → b yumuşama). Ağız + ı → ağzı (ı düşmesi)",
    "adimlar": [
      "Sözcüğün hecelerini ayır",
      "Ünlü/ünsüz dizilimine bak",
      "Ses olayını belirle",
      "Kuralı uygula"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Anlatım Biçimleri",
    "etiketler": ["anlatım", "açıklama", "tartışma", "betimleme", "öyküleme"],
    "icerik": "Dört temel anlatım biçimi: açıklama (bilgi verme), tartışma (fikir çürütme), betimleme (görselleştirme), öyküleme (olay anlatma).",
    "kurallar": [
      "Açıklama: bilgi vermek, öğretmek",
      "Tartışma: bir fikri savunmak/çürütmek",
      "Betimleme: sözcüklerle resim çizmek",
      "Öyküleme: olay, kişi, zaman, mekân",
      "Betimleme: gözlem, duyusal ayrıntı",
      "Öyküleme: hareket, olay akışı",
      "Açıklama: tanım, örnek, sınıflama",
      "Tartışma: 'oysa', 'fakat', 'ancak' gibi karşıtlık ifadeleri"
    ],
    "ornek": "'Dağların zirvesi karla kaplıydı' — betimleme. 'Fotosentez bitkilerde görülür' — açıklama",
    "adimlar": [
      "Metni oku",
      "Amaç ne? (bilgi/görsel/olay/ikna)",
      "Anlatım biçimini belirle"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Söz Sanatları",
    "etiketler": ["söz sanatı", "edebi sanat", "mecaz", "benzetme", "istiare"],
    "icerik": "Edebi metinlerde anlamı güçlendiren sanatlar: benzetme, mecaz, kişileştirme, abartma, tezat, kinaye.",
    "kurallar": [
      "Benzetme (teşbih): 'gibi, kadar' ile karşılaştırma",
      "İstiare (eğretileme): benzetme ögelerinden biri gizli",
      "Kişileştirme (teşhis): insan özelliği verme",
      "Abartma (mübalağa): aşırı büyütme",
      "Tezat (karşıtlık): zıt kavramlar bir arada",
      "Kinaye: hem gerçek hem mecaz anlam",
      "Cinas: ses benzerliğiyle anlam farkı",
      "Tekrir: tekrar"
    ],
    "ornek": "'Ay yüzün gibi parlıyor' (benzetme). 'Rüzgar fısıldıyor' (kişileştirme). 'Bir derya kadar gözyaşı' (abartma)",
    "adimlar": [
      "Metni oku",
      "Anlam derinliği var mı?",
      "Karşılaştırma/kişileştirme/abartma belirle",
      "Sanatı adlandır"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Fiilimsi (Eylemsi)",
    "etiketler": ["fiilimsi", "eylemsi", "isim-fiil", "sıfat-fiil", "zarf-fiil"],
    "icerik": "Fiilden türeyip isim, sıfat veya zarf görevinde kullanılan sözcükler. Üç tür: isim-fiil, sıfat-fiil, zarf-fiil.",
    "kurallar": [
      "İsim-fiil: -mak/-mek, -ma/-me, -ış/-iş (okumak, okuma, okuyuş)",
      "Sıfat-fiil: -an/-en, -ası/-esi, -mış/-miş, -acak/-ecek (okuyan, okumuş)",
      "Zarf-fiil: -ken, -alı, -madan, -ince, -ip, -erek, -dıkça (okurken, okuyup)",
      "Fiilimsi cümlede yan cümle kurar",
      "Fiilimsi eylem anlamı taşır ama tam fiil değildir"
    ],
    "ornek": "Kitabı okumak (isim-fiil) güzeldir. Koşan (sıfat-fiil) çocuk yoruldu. Gelince (zarf-fiil) haber ver",
    "adimlar": [
      "Sözcüğe bak: -mak/-an/-ken eklerinden biri var mı?",
      "İşlevine bak: isim mi sıfat mı zarf mı?",
      "Fiilimsi türünü belirle"
    ]
  },
  {
    "ders": "Türkçe",
    "konu": "Cümle Türleri",
    "etiketler": ["cümle türü", "kurallı", "devrik", "olumlu", "olumsuz", "soru"],
    "icerik": "Cümleler yapı, yüklem türü, anlam, diziliş açısından sınıflandırılır.",
    "kurallar": [
      "Yapı: basit, birleşik (girişik, şartlı, ki'li, ki'li)",
      "Yüklem türü: fiil cümlesi, isim cümlesi",
      "Anlam: olumlu, olumsuz, soru, ünlem",
      "Diziliş: kurallı (yüklem sonda), devrik (yüklem sonda değil)",
      "Basit cümle: tek yüklem",
      "Birleşik: iki+ yüklem veya fiilimsi",
      "Girişik: fiilimsiyle",
      "Şartlı: -se/-sa ile"
    ],
    "ornek": "Ali okula gitti (basit, fiil, olumlu, kurallı). Okula gitti Ali (devrik, basit, olumlu)",
    "adimlar": [
      "Yüklemi bul",
      "Yapıyı belirle",
      "Anlamı belirle",
      "Dizilişi belirle"
    ]
  }
]
// content/tarih.json
[
  {
    "ders": "Tarih",
    "konu": "Osmanlı Devleti Kuruluş",
    "etiketler": ["osmanlı", "kuruluş", "osman bey", "beylik", "söğüt"],
    "icerik": "Osmanlı Devleti 1299'da Osman Bey tarafından Söğüt'te kuruldu. Anadolu Selçuklu Devleti'nin zayıflamasıyla ortaya çıktı. Kısa sürede Balkanlar ve Anadolu'da genişledi.",
    "kurallar": [
      "Kurucu: Osman Bey (Osman Gazi)",
      "Kuruluş yılı: 1299",
      "Merkez: Söğüt → Bursa → Edirne → İstanbul",
      "Orhan Bey: ilk düzenli ordu (yaya ve müsellem)",
      "I. Murat: Kapıkulu ordusu, Rumeli'ye geçiş",
      "II. Mehmet (Fatih): İstanbul'u fethetti (1453)"
    ],
    "ornek": "Osmanlı Beyliği, Bizans sınırında kuruldu ve gaza politikasıyla büyüdü",
    "adimlar": [
      "Dönemi belirle",
      "Padişahları sırala",
      "Önemli olayları kronolojik sırala",
      "Sonuçlarını yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "İstanbul'un Fethi",
    "etiketler": ["istanbul", "fetih", "1453", "fatih", "bizans"],
    "icerik": "1453'te II. Mehmet (Fatih) İstanbul'u fethetti. Bizans İmparatorluğu sona erdi. Orta Çağ kapandı, Yeni Çağ başladı.",
    "kurallar": [
      "Tarih: 29 Mayıs 1453",
      "Fetheden: Fatih Sultan Mehmet",
      "Şahi topları kullanıldı",
      "Gemiler karadan yürütüldü (Haliç'e)",
      "Sonuç: Bizans yıkıldı, İstanbul başkent oldu",
      "Orta Çağ sona erdi, Yeni Çağ başladı",
      "Bizans bilginleri İtalya'ya kaçtı → Rönesans'ı etkiledi"
    ],
    "ornek": "Fetih sonrası Ayasofya camiye çevrildi, şehir yeniden imar edildi",
    "adimlar": [
      "Nedenleri sırala",
      "Hazırlıkları açıkla",
      "Fetih sürecini anlat",
      "Sonuçlarını yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Kurtuluş Savaşı",
    "etiketler": ["kurtuluş savaşı", "milli mücadele", "atatürk", "1919", "1922"],
    "icerik": "1919-1922 yılları arasında Anadolu'da işgal güçlerine karşı verilen bağımsızlık savaşı. Mustafa Kemal önderliğinde kazanıldı.",
    "kurallar": [
      "19 Mayıs 1919: Mustafa Kemal Samsun'a çıktı",
      "Amasya Genelgesi: 'Milletin bağımsızlığını yine milletin azim ve kararı kurtaracaktır'",
      "Erzurum Kongresi, Sivas Kongresi: örgütlenme",
      "23 Nisan 1920: TBMM açıldı",
      "I. İnönü, II. İnönü, Sakarya: Batı cephesi zaferleri",
      "30 Ağustos 1922: Başkomutanlık Meydan Savaşı",
      "9 Eylül 1922: İzmir'in kurtuluşu",
      "24 Temmuz 1923: Lozan Antlaşması"
    ],
    "ornek": "Sakarya Savaşı (1921) sonrası Fransa ile Ankara Antlaşması imzalandı",
    "adimlar": [
      "Hazırlık dönemi (1919-1920)",
      "Cepheler (Doğu, Güney, Batı)",
      "Siyasi gelişmeler",
      "Lozan ile sonuçlanma"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Türkiye Cumhuriyeti'nin İlanı",
    "etiketler": ["cumhuriyet", "1923", "atatürk", "tbmm", "inkılap"],
    "icerik": "29 Ekim 1923'te cumhuriyet ilan edildi. Mustafa Kemal ilk cumhurbaşkanı seçildi. İnkılaplar dönemi başladı.",
    "kurallar": [
      "29 Ekim 1923: Cumhuriyet ilan edildi",
      "İlk cumhurbaşkanı: Mustafa Kemal Atatürk",
      "İlk başbakan: İsmet İnönü",
      "3 Mart 1924: Halifelik kaldırıldı",
      "1928: Harf devrimi",
      "1934: Kadınlara seçme-seçilme hakkı",
      "1937: Laiklik anayasaya girdi"
    ],
    "ornek": "Saltanat 1 Kasım 1922'de kaldırıldı, cumhuriyet 29 Ekim 1923'te ilan edildi",
    "adimlar": [
      "Cumhuriyet öncesi gelişmeler",
      "İlan süreci",
      "İnkılaplar",
      "Sonuçları yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "I. Dünya Savaşı",
    "etiketler": ["birinci dünya savaşı", "1914", "1918", "savaş", "ittifak"],
    "icerik": "1914-1918 yılları arasında büyük güçler arasında yapılan savaş. İttifak ve İtilaf devletleri karşı karşıya geldi. Osmanlı İttifak'ta yer aldı.",
    "kurallar": [
      "Başlangıç: 1914 (Sarıaybosna suikasti)",
      "Bitiş: 1918 (Mondros Ateşkesi)",
      "İttifak: Almanya, Avusturya-Macaristan, Osmanlı, Bulgaristan",
      "İtilaf: İngiltere, Fransa, Rusya, İtalya, ABD",
      "Osmanlı cepheleri: Çanakkale, Kafkas, Filistin, Irak, Galiçya",
      "Çanakkale: 18 Mart 1915 deniz zaferi",
      "Sonuç: imparatorluklar yıkıldı, yeni devletler kuruldu"
    ],
    "ornek": "Çanakkale'de Mustafa Kemal 'Ben size taarruzu emretmiyorum, ölmeyi emrediyorum' dedi",
    "adimlar": [
      "Nedenleri sırala",
      "Cepheleri belirle",
      "Osmanlı'nın rolünü açıkla",
      "Sonuçları yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Anadolu Uygarlıkları",
    "etiketler": ["hitit", "frig", "urartu", "lidya", "anadolu", "uygarlık"],
    "icerik": "Anadolu'da kurulmuş eski uygarlıklar: Hitit, Frig, Urartu, Lidya, İyon, Bizans, Selçuklu.",
    "kurallar": [
      "Hitit: Kızılırmak çevresi, Kadeş Antlaşması (MÖ 1280)",
      "Frig: Gordion merkezli, Midas efsanesi",
      "Urartu: Van çevresi, kale ve su kanalları",
      "Lidya: MÖ 7. yy, ilk parayı bastı",
      "İyon: Ege kıyıları, felsefe ve bilim",
      "Kadeş: tarihin ilk yazılı antlaşması",
      "Lidya: 'Karun kadar zengin' deyimi buradan"
    ],
    "ornek": "Hititler ile Mısırlılar arasında Kadeş Antlaşması (MÖ 1280) imzalandı",
    "adimlar": [
      "Uygarlıkları sırala",
      "Merkezlerini belirle",
      "Önemli özelliklerini açıkla",
      "Katkılarını yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Fransız Devrimi",
    "etiketler": ["fransız devrimi", "1789", "özgürlük", "eşitlik", "devrim"],
    "icerik": "1789'da Fransa'da monarşiye karşı başlayan devrim. Özgürlük, eşitlik, kardeşlik ilkeleri. Modern demokrasilerin temeli.",
    "kurallar": [
      "Başlangıç: 14 Temmuz 1789 (Bastille baskını)",
      "İlkeler: özgürlük, eşitlik, kardeşlik",
      "İnsan ve Yurttaş Hakları Bildirisi (1789)",
      "Kral XVI. Louis idam edildi (1793)",
      "Napolyon 1799'da iktidara geldi",
      "Sonuç: feodal düzen yıkıldı, milliyetçilik yayıldı",
      "Osmanlı'yı etkiledi: Tanzimat, Meşrutiyet"
    ],
    "ornek": "Bastille baskını devrimin simgesi oldu, 14 Temmuz Fransa'nın milli günü",
    "adimlar": [
      "Nedenleri sırala (ekonomik, sosyal, siyasi)",
      "Önemli olayları kronolojik sırala",
      "İlkeleri açıkla",
      "Dünyaya etkisini yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Sanayi Devrimi",
    "etiketler": ["sanayi", "endüstri", "buhar makinesi", "1750", "devrim"],
    "icerik": "18. yy ortalarında İngiltere'de başlayan, buhar gücünün üretime girmesiyle makineleşme dönemi. Tarım toplumundan sanayi toplumuna geçiş.",
    "kurallar": [
      "Başlangıç: ~1760 İngiltere",
      "Buhar makinesi: James Watt (1769)",
      "Dokuma, madencilik, demiryolu gelişti",
      "Kömür ve demir temel kaynaklar",
      "Şehirlere göç arttı",
      "İşçi sınıfı doğdu",
      "Osmanlı: Tanzimat döneminde etkilendi"
    ],
    "ornek": "Buharlı tren 1825'te İngiltere'de çalışmaya başladı, ulaşım devrimi",
    "adimlar": [
      "Ön koşulları belirle",
      "Teknolojik gelişmeleri sırala",
      "Sosyal/ekonomik etkileri açıkla",
      "Osmanlı'ya etkisini yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "Soğuk Savaş",
    "etiketler": ["soğuk savaş", "abd", "sovyetler", "1947", "1991", "nato"],
    "icerik": "II. Dünya Savaşı sonrası ABD ve Sovyetler Birliği arasındaki ideolojik ve siyasi gerginlik (1947-1991). Doğrudan sıcak çatışma olmadı.",
    "kurallar": [
      "ABD: kapitalizm, NATO (1949)",
      "SSCB: komünizm, Varşova Paktı (1955)",
      "Truman Doktrini (1947)",
      "Marshall Planı: Avrupa'ya ABD yardımı",
      "Berlin Duvarı: 1961-1989",
      "Küba Füze Krizi (1962)",
      "1991: SSCB dağıldı, savaş bitti",
      "Türkiye: NATO'ya 1952'de girdi"
    ],
    "ornek": "Berlin Duvarı 1989'da yıkıldı, 1991'de SSCB dağıldı, Soğuk Savaş sona erdi",
    "adimlar": [
      "Tarafları belirle",
      "Önemli olayları kronolojik sırala",
      "Türkiye'nin konumunu açıkla",
      "Sonuçları yorumla"
    ]
  },
  {
    "ders": "Tarih",
    "konu": "II. Dünya Savaşı",
    "etiketler": ["ikinci dünya savaşı", "1939", "1945", "hitler", "nazi"],
    "icerik": "1939-1945 yılları arasındaki küresel savaş. Mihver (Almanya, İtalya, Japonya) ile Müttefikler (İngiltere, SSCB, ABD, Fransa) arasında.",
    "kurallar": [
      "Başlangıç: 1 Eylül 1939 (Almanya Polonya'yı işgal etti)",
      "Mihver: Almanya, İtalya, Japonya",
      "Müttefik: İngiltere, SSCB, ABD, Fransa, Çin",
      "Holokost: 6 milyon Yahudi soykırımı",
      "Pearl Harbor (1941): ABD savaşa girdi",
      "Hiroşima-Nagazaki (1945): atom bombası",
      "Bitiş: 1945, BM kuruldu",
      "Türkiye: savaşa girmedi, 1945'te BM'ye üye"
    ],
    "ornek": "6 Ağustos 1945 Hiroşima, 9 Ağustos 1945 Nagazaki'ye atom bombası atıldı",
    "adimlar": [
      "Nedenleri sırala",
      "Cepheleri ve cephelerdeki gelişmeleri anlat",
      "Türkiye'nin tutumunu açıkla",
      "Sonuçları yorumla"
    ]
  }
]
// content/programlama.json
[
  {
    "ders": "Programlama",
    "konu": "Python Değişkenler ve Veri Tipleri",
    "etiketler": ["python", "değişken", "veri tipi", "int", "str", "float"],
    "icerik": "Python'da değişkenler dinamik tiplidir. Temel tipler: int (tam sayı), float (ondalık), str (metin), bool (True/False), list, tuple, dict, set.",
    "ornek": "x = 5 (int)\ny = 3.14 (float)\nz = 'merhaba' (str)\nb = True (bool)",
    "adimlar": [
      "Değişken adı seç (harf veya _ ile başlar)",
      "Değer ata",
      "type() ile tipini kontrol et",
      "Gerekirse tip dönüşümü yap: int(), str(), float()"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Döngüler",
    "etiketler": ["python", "döngü", "for", "while", "range"],
    "icerik": "for döngüsü: belirli sayıda veya iterable üzerinde. while döngüsü: koşul sağlandığı sürece. break: çıkar. continue: atla.",
    "ornek": "for i in range(5):\n    print(i)  # 0,1,2,3,4\n\nn = 0\nwhile n < 3:\n    n += 1",
    "adimlar": [
      "Kaç kere döneceğini belirle",
      "for mu while mi seç",
      "Koşulu yaz",
      "break/continue gerekli mi kontrol et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Fonksiyonlar",
    "etiketler": ["python", "fonksiyon", "def", "return", "parametre"],
    "icerik": "Fonksiyon, tekrar kullanılabilir kod bloğu. def anahtar kelimesiyle tanımlanır. Parametre alabilir, değer döndürebilir.",
    "ornek": "def topla(a, b):\n    return a + b\n\nprint(topla(3, 5))  # 8",
    "adimlar": [
      "def ile başla",
      "Fonksiyon adı ve parametreler yaz",
      "Gövdeyi girintile",
      "return ile sonucu döndür"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Listeler ve Sözlükler",
    "etiketler": ["python", "liste", "list", "sözlük", "dict", "append"],
    "icerik": "Liste: sıralı, değiştirilebilir koleksiyon [ ]. Sözlük: anahtar-değer çiftleri { }. set: benzersiz elemanlar.",
    "ornek": "liste = [1, 2, 3]\nliste.append(4)\nsözlük = {'ad': 'Ali', 'yaş': 20}\nprint(sözlük['ad'])  # Ali",
    "adimlar": [
      "Veri yapısını seç (sıralı mı, anahtarlı mı)",
      "Oluştur",
      "Eleman ekle/çıkar",
      "Döngüyle gez veya indexle eriş"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Koşullu İfadeler (if/elif/else)",
    "etiketler": ["python", "if", "elif", "else", "koşul", "mantık"],
    "icerik": "if: koşul doğruysa çalışır. elif: önceki koşullar yanlışsa kontrol eder. else: hiçbiri değilse çalışır.",
    "ornek": "x = 10\nif x > 0:\n    print('pozitif')\nelif x < 0:\n    print('negatif')\nelse:\n    print('sıfır')",
    "adimlar": [
      "Koşulları belirle",
      "if ile başla",
      "elif ile alternatifler ekle",
      "else ile geri kalanı yakala"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Hata Ayıklama (Debug)",
    "etiketler": ["hata", "debug", "try", "except", "exception"],
    "icerik": "Hatalar: sözdizimi (SyntaxError), çalışma zamanı (RuntimeError), mantık (LogicError). try/except ile yakalanır.",
    "ornek": "try:\n    x = 10 / 0\nexcept ZeroDivisionError:\n    print('Sıfıra bölünmez')",
    "adimlar": [
      "Hata mesajını oku",
      "Satır numarasını bul",
      "Değişken değerlerini yazdır (print)",
      "Düzelt ve tekrar dene"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Algoritma Temelleri",
    "etiketler": ["algoritma", "sıralama", "arama", "big o", "karmaşıklık"],
    "icerik": "Algoritma: problemi çözen adımlar. Sıralama (bubble, merge, quick), arama (linear, binary). Big-O: karmaşıklık ölçüsü.",
    "ornek": "Binary search: sıralı dizide ortadan başla, hedefe göre sol/sağ yarıya geç. O(log n)",
    "adimlar": [
      "Problemi anla",
      "Adımları yaz",
      "Verimliliği (Big-O) düşün",
      "Test et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Özyineleme (Recursion)",
    "etiketler": ["recursion", "özyineleme", "faktöriyel", "fibonacci"],
    "icerik": "Fonksiyonun kendini çağırması. Temel durum (base case) ve özyineleme adımı olmalı.",
    "ornek": "def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)",
    "adimlar": [
      "Temel durumu belirle (dur)",
      "Problemi küçük parçaya indir",
      "Kendini çağır",
      "Sonucu birleştir"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Nesne Yönelimli Programlama (OOP)",
    "etiketler": ["oop", "sınıf", "class", "nesne", "object", "kalıtım"],
    "icerik": "Sınıf (class): şablon. Nesne (object): sınıftan üretilen. Özellikler (attribute) ve metotlar (method). Kalıtım, kapsülleme, çok biçimlilik.",
    "ornek": "class Kopek:\n    def __init__(self, ad):\n        self.ad = ad\n    def havla(self):\n        print(f'{self.ad} havlıyor')\n\nk = Kopek('Karabaş')\nk.havla()",
    "adimlar": [
      "Sınıfı tanımla",
      "__init__ ile özellikleri ata",
      "Metotları ekle",
      "Nesne oluşturup kullan"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Dosya İşlemleri (Python)",
    "etiketler": ["dosya", "file", "open", "read", "write", "with"],
    "icerik": "open() ile dosya açılır. Modlar: 'r' okuma, 'w' yazma (üzerine), 'a' ekleme, 'b' binary. with bloğu otomatik kapatır.",
    "ornek": "with open('veri.txt', 'w', encoding='utf-8') as f:\n    f.write('Merhaba')\n\nwith open('veri.txt', 'r', encoding='utf-8') as f:\n    icerik = f.read()",
    "adimlar": [
      "Dosya yolunu belirle",
      "Modu seç (r/w/a)",
      "with bloğu kullan",
      "İşlem yap ve kapat"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Veri Yapıları (Stack, Queue, Tree)",
    "etiketler": ["stack", "queue", "yığın", "kuyruk", "ağaç", "veri yapısı"],
    "icerik": "Stack: LIFO (son giren ilk çıkar) — geri al, parantez kontrolü. Queue: FIFO (ilk giren ilk çıkar) — iş kuyruğu. Tree: hiyerarşik yapı (dosya sistemi).",
    "ornek": "stack = []\nstack.append(1)  # push\nstack.pop()      # pop (son eleman)\n\nfrom collections import deque\nq = deque()\nq.append(1)      # enqueue\nq.popleft()      # dequeue",
    "adimlar": [
      "İhtiyaca göre yapıyı seç",
      "Ekleme/çıkarma kuralını belirle",
      "Zaman karmaşıklığına dikkat et",
      "Test et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Modüller ve Kütüphaneler",
    "etiketler": ["modül", "import", "pip", "kütüphane", "package"],
    "icerik": "Modül: .py dosyası. Paket: modüller klasörü. import ile dahil edilir. pip ile dış kütüphane kurulur.",
    "ornek": "import math\nfrom datetime import date\n\nprint(math.sqrt(16))  # 4.0\nprint(date.today())",
    "adimlar": [
      "Standart kütüphane mi, dış mı?",
      "import veya from ... import ...",
      "pip install ile dış paket kur",
      "Kullan"
    ]
  }
    // content/genel.json
[
  {
    "ders": "Genel",
    "konu": "Etkili Ders Çalışma",
    "etiketler": ["çalışma", "ders", "verimli", "pomodoro", "motivasyon"],
    "icerik": "Verimli çalışma için: aktif hatırlama, aralıklı tekrar, pomodoro, uyku ve beslenme.",
    "kurallar": [
      "Pomodoro: 25 dk çalış, 5 dk mola",
      "Aktif hatırlama: oku değil, kendini test et",
      "Aralıklı tekrar: 1-2-4-8 gün aralıklarla",
      "Feynman tekniği: birine anlatıyormuş gibi anlat",
      "Uyku: öğrenilen bilgi uykuda pekişir",
      "Telefon: başka odada olsun",
      "Önce en zor ders, enerji yüksekken"
    ],
    "ornek": "Bir konuyu 2 saat okumak yerine, 4×25 dk çalış + kendini test et + 3 gün sonra tekrar",
    "adimlar": [
      "Hedef belirle",
      "Pomodoro uygula",
      "Aktif hatırla",
      "Aralıklı tekrar planla"
    ]
  },
  {
    "ders": "Genel",
    "konu": "Sınav Stratejisi",
    "etiketler": ["sınav", "test", "taktik", "zaman yönetimi", "kaygı"],
    "icerik": "Sınavda: önce kolay soruları çöz, zamanı böl, kaygıyı yönet, işaretleyerek ilerle.",
    "kurallar": [
      "Önce tüm soruları hızlıca gözden geçir",
      "Kolay sorulardan başla",
      "Zor soruyu işaretle, sonra dön",
      "Süreyi soru sayısına böl",
      "Boş bırakma (yanlış cevap götürmüyorsa)",
      "Kaygı: derin nefes, 4-7-8 tekniği",
      "Son 10 dk kontrol et"
    ],
    "ornek": "60 soru 60 dk → her soruya ~1 dk, 10 dk kontrol için ayır",
    "adimlar": [
      "Sınav öncesi hazırlık",
      "Sınav anı stratejisi",
      "Zaman yönetimi",
      "Kaygı yönetimi"
    ]
  },
  {
    "ders": "Genel",
    "konu": "Not Tutma Teknikleri",
    "etiketler": ["not", "not tutma", "cornell", "zihin haritası", "özet"],
    "icerik": "Etkili not tutma: Cornell yöntemi, zihin haritası, özet çıkarma. Amaç bilgiyi düzenlemek ve hatırlamak.",
    "kurallar": [
      "Cornell: sayfayı 3 böl (not/anahtar kelime/özet)",
      "Zihin haritası: merkez kavram, dallar",
      "Renk kodlaması: önemli/örnek/formül",
      "Kendi cümlelerinle yaz",
      "Kısaltmalar kullan",
      "Düzenli gözden geçir"
    ],
    "ornek": "Cornell: sağ büyük alana ders notları, sol dar alana anahtar sorular, alt alana özet",
    "adimlar": [
      "Yöntemi seç",
      "Ana konuyu belirle",
      "Alt başlıklara ayır",
      "Kendi kelimelerinle not al"
    ]
  },
  {
    "ders": "Genel",
    "konu": "Zaman Yönetimi",
    "etiketler": ["zaman", "plan", "program", "hedef", "verimlilik"],
    "icerik": "Zaman yönetimi: Eisenhower matrisi (acil/önemli), plan yapma, erteleme ile mücadele.",
    "kurallar": [
      "Eisenhower: acil-önemli, acil-değil, acil değil-önemli, acil değil-önemsiz",
      "Önemli ama acil olmayan işler en değerli (planlama, çalışma)",
      "Erteleme: görevi küçük parçalara böl",
      "2 dakika kuralı: 2 dk sürecek işi hemen yap",
      "Günlük plan yap, akşam değerlendir",
      "Öncelik sırala"
    ],
    "ornek": "Sınav 1 hafta sonra → önemli ama acil değil → bugün başla, her gün 1 saat",
    "adimlar": [
      "Görevleri listele",
      "Aciliyet/önem matrisine yerleştir",
      "Günlük plan yap",
      "Akşam kontrol et"
    ]
  },
  {
    "ders": "Genel",
    "konu": "Motivasyon ve Hedef Belirleme",
    "etiketler": ["motivasyon", "hedef", "smart", "alışkanlık"],
    "icerik": "SMART hedef: Spesifik, Ölçülebilir, Ulaşılabilir, İlgili, Zamanlı. Alışkanlıklar küçük başlar.",
    "kurallar": [
      "SMART: belirli, ölçülebilir, ulaşılabilir, ilgili, zamanlı",
      "Küçük başla (5 dk bile yeter)",
      "Alışkanlık zinciri: ipucu → rutin → ödül",
      "İlerlemeyi görselleştir (takvim, uygulama)",
      "Başarısızlık normal, devam et",
      "Kendini ödüllendir"
    ],
    "ornek": "Kötü hedef: 'Daha çok çalışacağım'. İyi hedef: 'Her gün 30 dk matematik çalışacağım, 1 ay boyunca'",
    "adimlar": [
      "Hedefi SMART yap",
      "Küçük başla",
      "Günlük alışkanlığa bağla",
      "İlerlemeyi takip et"
    ]
  },
  {
    "ders": "Genel",
    "konu": "Hafıza Teknikleri",
    "etiketler": ["hafıza", "hafıza teknikleri", "ezber", "mnemonic", "hatırlama"],
    "icerik": "Bilgiyi kalıcı hale getirme teknikleri: aralıklı tekrar, aktif hatırlama, hikâye, akrostiş, loci (yerleştirme).",
    "kurallar": [
      "Aralıklı tekrar: bilgi unutulmadan tekrar",
      "Aktif hatırlama: kapalı kitaptan hatırla",
      "Hikâye: bilgileri hikâyeye bağla",
      "Akrostiş: baş harflerle cümle",
      "Loci: bilgileri bir mekâna yerleştir",
      "Görselleştir",
      "Uyku öncesi 10 dk tekrar etkili"
    ],
    "ornek": "Güneş'ten uzak gezegenler: Merkür, Venüs, Dünya, Mars, Jüpiter, Satürn, Uranüs, Neptün → 'Merve Dün Markete Jüpiter'in Satürn'ü Uğradı Neptün'e'",
    "adimlar": [
      "Bilgiyi küçük parçalara böl",
      "Teknik seç (hikâye, akrostiş, loci)",
      "Tekrar planla",
      "Uygula"
    ]
  }
]// content/programlama.json
[
  {
    "ders": "Programlama",
    "konu": "Python Değişkenler ve Veri Tipleri",
    "etiketler": ["python", "değişken", "veri tipi", "int", "str", "float"],
    "icerik": "Python'da değişkenler dinamik tiplidir. Temel tipler: int (tam sayı), float (ondalık), str (metin), bool (True/False), list, tuple, dict, set.",
    "ornek": "x = 5 (int)\ny = 3.14 (float)\nz = 'merhaba' (str)\nb = True (bool)",
    "adimlar": [
      "Değişken adı seç (harf veya _ ile başlar)",
      "Değer ata",
      "type() ile tipini kontrol et",
      "Gerekirse tip dönüşümü yap: int(), str(), float()"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Döngüler",
    "etiketler": ["python", "döngü", "for", "while", "range"],
    "icerik": "for döngüsü: belirli sayıda veya iterable üzerinde. while döngüsü: koşul sağlandığı sürece. break: çıkar. continue: atla.",
    "ornek": "for i in range(5):\n    print(i)  # 0,1,2,3,4\n\nn = 0\nwhile n < 3:\n    n += 1",
    "adimlar": [
      "Kaç kere döneceğini belirle",
      "for mu while mi seç",
      "Koşulu yaz",
      "break/continue gerekli mi kontrol et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Fonksiyonlar",
    "etiketler": ["python", "fonksiyon", "def", "return", "parametre"],
    "icerik": "Fonksiyon, tekrar kullanılabilir kod bloğu. def anahtar kelimesiyle tanımlanır. Parametre alabilir, değer döndürebilir.",
    "ornek": "def topla(a, b):\n    return a + b\n\nprint(topla(3, 5))  # 8",
    "adimlar": [
      "def ile başla",
      "Fonksiyon adı ve parametreler yaz",
      "Gövdeyi girintile",
      "return ile sonucu döndür"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Python Listeler ve Sözlükler",
    "etiketler": ["python", "liste", "list", "sözlük", "dict", "append"],
    "icerik": "Liste: sıralı, değiştirilebilir koleksiyon [ ]. Sözlük: anahtar-değer çiftleri { }. set: benzersiz elemanlar.",
    "ornek": "liste = [1, 2, 3]\nliste.append(4)\nsözlük = {'ad': 'Ali', 'yaş': 20}\nprint(sözlük['ad'])  # Ali",
    "adimlar": [
      "Veri yapısını seç (sıralı mı, anahtarlı mı)",
      "Oluştur",
      "Eleman ekle/çıkar",
      "Döngüyle gez veya indexle eriş"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Koşullu İfadeler (if/elif/else)",
    "etiketler": ["python", "if", "elif", "else", "koşul", "mantık"],
    "icerik": "if: koşul doğruysa çalışır. elif: önceki koşullar yanlışsa kontrol eder. else: hiçbiri değilse çalışır.",
    "ornek": "x = 10\nif x > 0:\n    print('pozitif')\nelif x < 0:\n    print('negatif')\nelse:\n    print('sıfır')",
    "adimlar": [
      "Koşulları belirle",
      "if ile başla",
      "elif ile alternatifler ekle",
      "else ile geri kalanı yakala"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Hata Ayıklama (Debug)",
    "etiketler": ["hata", "debug", "try", "except", "exception"],
    "icerik": "Hatalar: sözdizimi (SyntaxError), çalışma zamanı (RuntimeError), mantık (LogicError). try/except ile yakalanır.",
    "ornek": "try:\n    x = 10 / 0\nexcept ZeroDivisionError:\n    print('Sıfıra bölünmez')",
    "adimlar": [
      "Hata mesajını oku",
      "Satır numarasını bul",
      "Değişken değerlerini yazdır (print)",
      "Düzelt ve tekrar dene"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Algoritma Temelleri",
    "etiketler": ["algoritma", "sıralama", "arama", "big o", "karmaşıklık"],
    "icerik": "Algoritma: problemi çözen adımlar. Sıralama (bubble, merge, quick), arama (linear, binary). Big-O: karmaşıklık ölçüsü.",
    "ornek": "Binary search: sıralı dizide ortadan başla, hedefe göre sol/sağ yarıya geç. O(log n)",
    "adimlar": [
      "Problemi anla",
      "Adımları yaz",
      "Verimliliği (Big-O) düşün",
      "Test et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Özyineleme (Recursion)",
    "etiketler": ["recursion", "özyineleme", "faktöriyel", "fibonacci"],
    "icerik": "Fonksiyonun kendini çağırması. Temel durum (base case) ve özyineleme adımı olmalı.",
    "ornek": "def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)",
    "adimlar": [
      "Temel durumu belirle (dur)",
      "Problemi küçük parçaya indir",
      "Kendini çağır",
      "Sonucu birleştir"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Nesne Yönelimli Programlama (OOP)",
    "etiketler": ["oop", "sınıf", "class", "nesne", "object", "kalıtım"],
    "icerik": "Sınıf (class): şablon. Nesne (object): sınıftan üretilen. Özellikler (attribute) ve metotlar (method). Kalıtım, kapsülleme, çok biçimlilik.",
    "ornek": "class Kopek:\n    def __init__(self, ad):\n        self.ad = ad\n    def havla(self):\n        print(f'{self.ad} havlıyor')\n\nk = Kopek('Karabaş')\nk.havla()",
    "adimlar": [
      "Sınıfı tanımla",
      "__init__ ile özellikleri ata",
      "Metotları ekle",
      "Nesne oluşturup kullan"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Dosya İşlemleri (Python)",
    "etiketler": ["dosya", "file", "open", "read", "write", "with"],
    "icerik": "open() ile dosya açılır. Modlar: 'r' okuma, 'w' yazma (üzerine), 'a' ekleme, 'b' binary. with bloğu otomatik kapatır.",
    "ornek": "with open('veri.txt', 'w', encoding='utf-8') as f:\n    f.write('Merhaba')\n\nwith open('veri.txt', 'r', encoding='utf-8') as f:\n    icerik = f.read()",
    "adimlar": [
      "Dosya yolunu belirle",
      "Modu seç (r/w/a)",
      "with bloğu kullan",
      "İşlem yap ve kapat"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Veri Yapıları (Stack, Queue, Tree)",
    "etiketler": ["stack", "queue", "yığın", "kuyruk", "ağaç", "veri yapısı"],
    "icerik": "Stack: LIFO (son giren ilk çıkar) — geri al, parantez kontrolü. Queue: FIFO (ilk giren ilk çıkar) — iş kuyruğu. Tree: hiyerarşik yapı (dosya sistemi).",
    "ornek": "stack = []\nstack.append(1)  # push\nstack.pop()      # pop (son eleman)\n\nfrom collections import deque\nq = deque()\nq.append(1)      # enqueue\nq.popleft()      # dequeue",
    "adimlar": [
      "İhtiyaca göre yapıyı seç",
      "Ekleme/çıkarma kuralını belirle",
      "Zaman karmaşıklığına dikkat et",
      "Test et"
    ]
  },
  {
    "ders": "Programlama",
    "konu": "Modüller ve Kütüphaneler",
    "etiketler": ["modül", "import", "pip", "kütüphane", "package"],
    "icerik": "Modül: .py dosyası. Paket: modüller klasörü. import ile dahil edilir. pip ile dış kütüphane kurulur.",
    "ornek": "import math\nfrom datetime import date\n\nprint(math.sqrt(16))  # 4.0\nprint(date.today())",
    "adimlar": [
      "Standart kütüphane mi, dış mı?",
      "import veya from ... import ...",
      "pip install ile dış paket kur",
      "Kullan"
    ]
  }
]# ai/engine.py
"""
EduCore-AI Motor v1.
Bilgi tabanı + sinir ağı intent sınıflandırıcı + matematik çözücüyü birleştirir.
Harici AI çağrısı YOK. Tamamen yerel.
"""
import os, re, json
from pathlib import Path
from datetime import datetime

# Kendi modüllerimiz
import sys
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_base import KnowledgeBase
from brain import load_intent_model, NeuralNet, TextVectorizer

# ─── Matematik çözücü (brain.py'den bağımsız, engine içinde) ───
import ast
from fractions import Fraction

_ALLOWED_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)

def _eval_node(node, env):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Fraction(str(node.value))
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        raise ValueError(f"bilinmeyen değişken: {node.id}")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _eval_node(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        l, r = _eval_node(node.left, env), _eval_node(node.right, env)
        if isinstance(node.op, ast.Add):  return l + r
        if isinstance(node.op, ast.Sub):  return l - r
        if isinstance(node.op, ast.Mult): return l * r
        if isinstance(node.op, ast.Div):  return l / r
        if isinstance(node.op, ast.Mod):  return l % r
        if isinstance(node.op, ast.Pow):
            if r.denominator != 1 or abs(r) > 20:
                raise ValueError("üs desteklenmiyor")
            return l ** int(r)
    raise ValueError("desteklenmeyen ifade")

def _fmt(v):
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"

def _poly(a, b, c):
    parts = []
    for coef, var in ((a, "x²"), (b, "x"), (c, "")):
        if coef == 0: continue
        mag = abs(coef)
        body = ("" if (mag == 1 and var) else _fmt(mag)) + var
        parts.append(("-" if coef < 0 else "+", body))
    if not parts: return "0"
    s = ("-" if parts[0][0] == "-" else "") + parts[0][1]
    return s + "".join(f" {sg} {bd}" for sg, bd in parts[1:])

def solve_math(q):
    """
    Kesin matematik çözücü.
    - Aritmetik: '15*4/3', '(2+3)^2'
    - Lineer: '2x+3=11'
    - Kuadratik: 'x^2-5x+6=0'
    """
    s = q.strip().lower()
    for a, b in (("^", "**"), ("×", "*"), ("÷", "/"), ("²", "**2"), ("³", "**3"), ("−", "-")):
        s = s.replace(a, b)
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    s = re.sub(r"[?\s]+$", "", s).rstrip("=").strip()

    # Güvenlik: sadece izin verilen karakterler
    if not re.fullmatch(r"[\d\s+\-*/().=x]+", s):
        return None
    if not re.search(r"\d", s):
        return None

    # Çarpma işaretlerini ekle: 3x -> 3*x, (2)(3) -> (2)*(3)
    s = re.sub(r"(\d|\))\s*(x|\()", r"\1*\2", s)
    s = re.sub(r"(x)\s*(\d|\()", r"\1*\2", s)
    s = re.sub(r"\)\s*(\d)", r")*\1", s)

    try:
        # Denklem çözümü
        if "=" in s and s.count("=") == 1:
            left, right = s.split("=")
            tree = ast.parse(f"({left})-({right})", mode="eval").body
            # 2. derece olduğunu doğrula (x=0,1,2,-1 ile test)
            f0 = _eval_node(tree, {"x": Fraction(0)})
            f1 = _eval_node(tree, {"x": Fraction(1)})
            f2 = _eval_node(tree, {"x": Fraction(2)})
            f_1 = _eval_node(tree, {"x": Fraction(-1)})
            # c, a+b, 4a+2b+c, a-b+c çözümü
            c = f0
            a = (f2 + f_1) / 2 - c
            b = (f1 - f_1) / 2
            # Doğrulama: 3. derece değil mi?
            f3 = _eval_node(tree, {"x": Fraction(3)})
            if f3 != 9*a + 3*b + c:
                return "Denklem 2. dereceden değil, çözemedim."

            poly = _poly(a, b, c)
            out = [f"**Denklem:** {poly} = 0"]
            out.append(f"**Katsayılar:** a={_fmt(a)}, b={_fmt(b)}, c={_fmt(c)}")

            if a == 0:
                if b == 0:
                    out.append("**Sonuç:** " + ("Her x çözümdür ✅" if c == 0 else "Çözüm yok ❌"))
                else:
                    x = -c / b
                    out.append(f"**Birinci derece:** x = -c/b = {_fmt(-c)}/{_fmt(b)}")
                    out.append(f"✅ **x = {_fmt(x)}**")
                return "\n".join(out)

            # Kuadratik
            D = b*b - 4*a*c
            out.append(f"**Diskriminant:** Δ = b² - 4ac = {_fmt(D)}")
            if D < 0:
                out.append("Δ < 0 → **gerçek kök yok** (karmaşık kökler)")
            elif D == 0:
                x = -b / (2*a)
                out.append(f"Δ = 0 → **çift kök:** x = -b/(2a) = {_fmt(x)}")
            else:
                from math import isqrt
                rn, rd = isqrt(D.numerator), isqrt(D.denominator)
                if rn*rn == D.numerator and rd*rd == D.denominator:
                    sd = Fraction(rn, rd)
                    x1 = (-b + sd) / (2*a)
                    x2 = (-b - sd) / (2*a)
                    out.append(f"√Δ = {_fmt(sd)}")
                    out.append(f"✅ **x₁ = {_fmt(x1)}**, **x₂ = {_fmt(x2)}**")
                else:
                    import math as _m
                    s1 = _m.sqrt(float(D))
                    x1 = (-float(b) + s1) / (2*float(a))
                    x2 = (-float(b) - s1) / (2*float(a))
                    out.append(f"√Δ ≈ {s1:.4f}")
                    out.append(f"✅ **x₁ ≈ {x1:.4g}**, **x₂ ≈ {x2:.4g}**")
            return "\n".join(out)

        # Sadece sayısal ifade
        if "x" in s:
            return None
        tree = ast.parse(s, mode="eval").body
        val = _eval_node(tree, {})
        return f"**Sonuç: {_fmt(val)}**"

    except (ValueError, ZeroDivisionError, SyntaxError, OverflowError, RecursionError):
        return None


# ─── Cevap üretici ───

INTRO = {
    "İlkokul": "Merhaba! Birlikte bakalım 👇",
    "Ortaokul": "Hadi adım adım çözelim:",
    "Lise": "Konuyu netleştirelim:",
    "Üniversite": "Akademik çerçevede:",
}

class EsilaEngine:
    """Kendi motorumuzun ana sınıfı. Tüm cevaplar buradan geçer."""

    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = Path(__file__).parent / "models"
        self.model_dir = Path(model_dir)
        self.kb = KnowledgeBase()
        self.net, self.vec, self.intents = None, None, None
        self._load_model()

    def _load_model(self):
        try:
            result = load_intent_model(str(self.model_dir))
            if result:
                self.net, self.vec, self.intents = result
        except Exception:
            self.net = None

    def classify_intent(self, text):
        """Metni sınıflandır: hangi ders/konu hakkında?"""
        if self.net is None:
            return None, 0.0
        X = self.vec.transform([text])
        probs = self.net.predict_proba(X)
        idx = int(probs.argmax())
        return self.intents[idx], float(probs[0, idx])

    def answer(self, question, level="Lise", subject=None, tone="Samimi"):
        """Ana cevap üretim metodu."""
        if not isinstance(question, str):
            return "Geçersiz soru."
        q = question.strip()
        if not q:
            return "Bir şey yazmadın 🙂"
        if len(q) > 2000:
            return "Soru çok uzun, kısaltır mısın?"

        # 1) Matematik kesin çözüm
        m = solve_math(q)
        if m:
            intro = INTRO.get(level, "")
            outro = "\n\n💬 Takıldığın adımı yaz, oradan devam edelim." if tone == "Samimi" else ""
            return f"{intro}\n\n{m}{outro}"

        # 2) Intent sınıflandırma
        intent, conf = self.classify_intent(q)

        # 3) Bilgi tabanı arama
        cards = self.kb.search(q, subject=subject, top_k=3, min_score=0.08)

        # 4) Selamlama, veda, teşekkür
        if intent == "selam" and conf > 0.4:
            return self._greet(level, tone)
        if intent == "veda" and conf > 0.4:
            return "Görüşürüz! 👋 Çalışmaya devam, başarılar."
        if intent == "tesekkur" and conf > 0.4:
            return "Rica ederim! Başka bir konuda yardımcı olabilir miyim? 😊"
        if intent == "yardim" and conf > 0.4:
            return self._help()

        # 5) Bilgi kartı varsa ondan cevap
        if cards:
            return self._compose_from_cards(cards, level, tone)

        # 6) Emin değilsek yol göster
        return self._fallback(level, intent, conf)

    def _greet(self, level, tone):
        if tone == "Kanka":
            return f"Selam kanka! 👋 Ne çalışıyoruz bugün? Matematik, fizik, kimya... hangisi olursa."
        return f"Merhaba! Bugün hangi ders üzerinde çalışmak istersin? ({', '.join(self.kb.by_subject.keys())})"

    def _help(self):
        subjects = ", ".join(self.kb.by_subject.keys())
        return (
            "**Ne yapabilirim:**\n\n"
            f"- Ders konularını açıklayabilirim: {subjects}\n"
            "- Matematik ifadelerini çözebilirim: `2x+3=11`, `x^2-5x+6=0`, `15*4/3`\n"
            "- Formülleri ve kuralları gösterebilirim\n"
            "- Adım adım çözüm sunabilirim\n\n"
            "Bir soru yaz, birlikte çözelim."
        )

    def _compose_from_cards(self, cards, level, tone):
        parts = [INTRO.get(level, "")]
        for i, c in enumerate(cards, 1):
            parts.append(f"### 📘 {c['konu']}")
            parts.append(c.get("icerik", ""))
            if c.get("formuller"):
                parts.append("**Formüller:**")
                for f in c["formuller"]:
                    parts.append(f"- `{f}`")
            if c.get("kurallar"):
                parts.append("**Kurallar:**")
                for r in c["kurall"]:
                    parts.append(f"- {r}")
            if c.get("organeller"):
                parts.append("**Organeller:**")
                for o in c["organeller"]:
                    parts.append(f"- {o}")
            if c.get("ornek"):
                parts.append(f"**Örnek:** {c['ornek']}")
            if c.get("adimlar"):
                parts.append("**Adımlar:**")
                for j, a in enumerate(c["adimlar"], 1):
                    parts.append(f"{j}. {a}")
            parts.append("")
        if tone == "Kanka":
            parts.append("😎 Daha spesifik sorarsan daha iyi yardım ederim.")
        return "\n".join(parts)

    def _fallback(self, level, intent, conf):
        subjects = ", ".join(self.kb.by_subject.keys())
        if intent and conf > 0.25:
            guess = f"Sanırım **{intent}** ile ilgili bir soru sordun ama emin değilim."
        else:
            guess = "Sorunu tam anlayamadım."
        return (
            f"{guess}\n\n"
            "Şunları deneyebilirsin:\n"
            f"1. Hangi ders olduğunu belirt: {subjects}\n"
            "2. Konuyu tek cümleye indir\n"
            "3. Matematik ifadesi ise doğrudan yaz: `2x+5=13`\n\n"
            "_İpucu: 'türev', 'fotosentez', 'ohm kanunu' gibi anahtar kelimelerle daha iyi sonuç alırsın._"
        )


# ─── Test ───
if __name__ == "__main__":
    print("=" * 70)
    print("EduCore-AI Motor Testi")
    print("=" * 70)
    engine = EsilaEngine()
    print(f"Yüklenen konu sayısı: {len(engine.kb.cards)}")
    print(f"Intent modeli: {'yüklü' if engine.net else 'YOK (önce ai/brain.py çalıştır)'}")
    print()

    tests = [
        ("merhaba", "Lise", "Samimi"),
        ("2x+3=11", "Lise", "Resmi"),
        ("x^2-5x+6=0", "Lise", "Resmi"),
        ("15*4/3", "Ortaokul", "Samimi"),
        ("türev nasıl alınır", "Lise", "Samimi"),
        ("fotosentez nedir", "Ortaokul", "Samimi"),
        ("ohm kanunu formülü", "Lise", "Resmi"),
        ("python döngü nasıl", "Üniversite", "Samimi"),
        ("kurtuluş savaşı ne zaman", "Lise", "Resmi"),
        ("teşekkürler", "Lise", "Samimi"),
    ]
    for q, lv, tn in tests:
        print(f"\n{'─'*70}\n❓ [{lv}] {q}\n{'─'*70}")
        ans = engine.answer(q, level=lv, tone=tn)
        print(ans[:600] + ("..." if len(ans) > 600 else ""))
