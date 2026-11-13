"""
================================================================================
PROJECT: EduCore-AI - Akıllı Yerel Yapay Zeka Stüdyosu & Çin Seddi Enterprise
VERSION: v2026.Esila.CinSeddiEnterprise.MasterEdition - Ultimate Production
================================================================================
"""

import datetime
import hashlib
import hmac
import os
import re
import sqlite3
import time
import unicodedata
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduCore-AI Stüdyo | Esila Çin Seddi Enterprise",
    page_icon="🛡️",
    layout="wide",
)

# ===============================================================================
# 🛡️ GÜVENLİK VE KRİPTOGRAFİ MOTORU (ENTERPRISE ÇİN SEDDİ - 1000 KATMAN)
# ===============================================================================
DB_PATH = "educore_enterprise.db"


def secure_hash_password(password: str, salt: str = None) -> tuple[str, str]:
  """PBKDF2-HMAC-SHA256 Kriptografik Salted Şifreleme (100.000 İterasyon)"""
  if not salt:
    salt = os.urandom(16).hex()
  pwd_hash = hashlib.pbkdf2_hmac(
      "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
  )
  return pwd_hash.hex(), salt


def verify_secure_password(
    stored_hash: str, stored_salt: str, provided_password: str
) -> bool:
  pwd_hash = hashlib.pbkdf2_hmac(
      "sha256",
      provided_password.encode("utf-8"),
      bytes.fromhex(stored_salt),
      100_000,
  )
  return hmac.compare_digest(pwd_hash.hex(), stored_hash)


def log_security_incident(user_code: str, attack_type: str, raw_payload: str):
  """Çin Seddi Tarafından Engellenen Tehditleri Veritabanına Loglar"""
  try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS security_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_code TEXT,
                attack_type TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """)
    c.execute(
        "INSERT INTO security_audit_logs (user_code, attack_type, payload,"
        " timestamp) VALUES (?, ?, ?, ?)",
        (
            user_code or "ANONYMOUS",
            attack_type,
            raw_payload[:500],
            str(datetime.datetime.now()),
        ),
    )
    conn.commit()
    conn.close()
  except Exception:
    pass


def enterprise_cin_seddi_firewall(
    raw_input: str, user_code: str = None
) -> tuple[bool, str]:
  """Çin Seddi 1000-Katmanlı Eşzamanlı Tehdit Analiz Süzgeci"""
  if not raw_input or not raw_input.strip():
    return False, "Çin Seddi: Girdi boş bırakılamaz."

  if len(raw_input) > 4000:
    log_security_incident(user_code, "BUFFER_OVERFLOW", raw_input)
    return False, "🧱 Çin Seddi (Katman 85): Bellek sınır aşımı engellendi!"

  # 1. Adım: Unicode Normalizasyonu (Bypass Hilelerini Önleme)
  normalized_input = unicodedata.normalize("NFKC", raw_input)
  q_lower = normalized_input.lower()

  # 2. Adım: SQL Sızdırma & Blind SQLi İmzaları
  sql_patterns = [
      r"drop\s+table",
      r"union\s+select",
      r"exec\s*\(",
      r"--",
      r"or\s+['\"]?1['\"]?\s*=\s*['\"]?1",
      r"drop\s+database",
      r"information_schema",
      r"sqlite_master",
      r"benchmark\s*\(",
      r"sleep\s*\(",
      r"into\s+outfile",
      r"load_file",
  ]
  for pattern in sql_patterns:
    if re.search(pattern, q_lower):
      log_security_incident(user_code, "SQL_INJECTION", raw_input)
      return (
          False,
          "🧱 Çin Seddi (Katman 210): Kritik SQL sızdırma girişimi engellendi ve"
          " loglandı!",
      )

  # 3. Adım: XSS & Kod Enjeksiyon Kalkanları
  xss_patterns = [
      r"<script>",
      r"javascript:",
      r"onerror\s*=",
      r"onload\s*=",
      r"eval\s*\(",
      r"document\.cookie",
      r"<iframe",
      r"<object",
      r"vbscript:",
  ]
  for pattern in xss_patterns:
    if re.search(pattern, q_lower):
      log_security_incident(user_code, "XSS_ATTACK", raw_input)
      return (
          False,
          "🧱 Çin Seddi (Katman 450): Zararlı betik veya XSS engellendi!",
      )

  # 4. Adım: Toksisite ve Argo Filtreleme
  bad_words = [
      "küfür",
      "mal",
      "salak",
      "aptal",
      "orspu",
      "orospu",
      "sik",
      "amk",
      "aq",
      "amina",
      "piç",
      "orospu çocuğu",
      "ibne",
  ]
  for word in bad_words:
    pattern = r"\b" + re.escape(word) + r"\b"
    if re.search(pattern, q_lower):
      log_security_incident(user_code, "TOXICITY_FILTER", raw_input)
      return False, "TURNOVER_PROF"

  # 5. Adım: Rate Limiting & Bot Spam Kalkanı
  if "cin_seddi_last_req" in st.session_state:
    elapsed = time.time() - st.session_state.cin_seddi_last_req
    if elapsed < 0.25:
      log_security_incident(user_code, "RATE_LIMIT_FLOOD", raw_input)
      return (
          False,
          "🧱 Çin Seddi (Katman 900): Aşırı hızlı istek (Flood/Bot koruması)"
          " tetiklendi!",
      )
  st.session_state.cin_seddi_last_req = time.time()

  # 6. Adım: Anomali ve Karakter Yoğunluk Tespiti
  if q_lower.count("'") > 4 or q_lower.count(";") > 4 or q_lower.count("--") > 1:
    log_security_incident(user_code, "SYNTAX_ANOMALY", raw_input)
    return (
        False,
        "🧱 Çin Seddi (Katman 999): Şüpheli karakter yoğunluğu tespit edildi!",
    )

  return True, "Çin Seddi Onaylandı"


def init_db():
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()

  c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            password_salt TEXT,
            nickname TEXT,
            grade TEXT,
            unique_code TEXT,
            last_active TEXT,
            created_at TEXT
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS security_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT,
            attack_type TEXT,
            payload TEXT,
            timestamp TEXT
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            creator_code TEXT,
            created_at TEXT
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            member_code TEXT,
            UNIQUE(group_id, member_code)
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_nick TEXT,
            sender_code TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT,
            friend_code TEXT,
            status TEXT DEFAULT 'Kabul Edildi',
            UNIQUE(user_code, friend_code)
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS direct_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_code TEXT,
            receiver_code TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

  conn.commit()
  conn.close()


init_db()

# Arayüz Stilleri (Kurumsal Askeri Kırmızı/Lacivert Teması)
st.markdown(
    """
    <style>
    .stApp { background-color: #030712; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .hero-box {
        background: linear-gradient(135deg, #dc2626 0%, #4f46e5 50%, #06b6d4 100%);
        padding: 25px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(220, 38, 38, 0.4);
    }
    .study-card {
        background: #0f172a; border: 1px solid #ef4444; border-radius: 16px; padding: 22px; margin-bottom: 20px;
    }
    div.stButton > button {
        border-radius: 12px; font-weight: 800; background: linear-gradient(135deg, #dc2626 0%, #4f46e5 100%);
        color: white; border: none; min-height: 42px; width: 100%;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
  st.session_state.user = None

if st.session_state.user is None and "logged_email" in st.query_params:
  saved_email = st.query_params["logged_email"]
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()
  c.execute("SELECT * FROM users WHERE email = ?", (saved_email,))
  row = c.fetchone()
  conn.close()
  if row:
    st.session_state.user = {
        "id": row[0],
        "email": row[1],
        "nickname": row[4],
        "grade": row[5],
        "unique_code": row[6],
    }

if st.session_state.user:
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()
  c.execute(
      "UPDATE users SET last_active = ? WHERE unique_code = ?",
      (str(datetime.datetime.now()), st.session_state.user["unique_code"]),
  )
  conn.commit()
  conn.close()

CURRICULUM = {
    "İlkokul (1-4. Sınıf)": [
        "Türkçe",
        "Matematik",
        "Hayat Bilgisi",
        "Fen Bilimleri",
        "İngilizce",
    ],
    "Ortaokul (5-8. Sınıf / LGS)": [
        "Türkçe",
        "Matematik",
        "Fen Bilimleri",
        "Sosyal Bilgiler",
        "İngilizce",
        "İnkılap Tarihi",
    ],
    "Lise (9-11. Sınıf)": [
        "Türk Dili ve Edebiyatı",
        "Matematik",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Tarih",
        "Coğrafya",
        "İngilizce",
        "Felsefe",
    ],
    "YKS (12. Sınıf / Mezun)": [
        "TYT-AYT Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Türk Dili ve Edebiyatı",
        "Tarih",
        "Coğrafya",
        "İngilizce",
    ],
    "Üniversite & Akademik": [
        "Yazılım & Algoritma",
        "İleri Matematik / Analiz",
        "Veri Yapıları",
        "Mühendislik Temelleri",
        "Genel Akademik",
    ],
}


# ===============================================================================
# 🧠 ESİLA MASTER & "KANCA" SAMİMİ ADIM ADIM AÇIKLAMA MOTORU
# ===============================================================================
def get_esila_response(query: str, nick: str, subj: str, grd: str) -> str:
  user_code = (
      st.session_state.user["unique_code"]
      if st.session_state.user
      else "GUEST"
  )
  is_safe, msg = enterprise_cin_seddi_firewall(query, user_code)
  if not is_safe:
    if msg == "TURNOVER_PROF":
      return (
          f"Hey {nick}, kanka kime bu hava? Küfürle Esila'yı dize getireceğini"
          " sandıysan yanılıyorsun! Çin Seddi güvenlik duvarımız bunu anında"
          " tokatladı ve loglara kaydetti. Hadi kendine çeki düzen ver de"
          " akıllıca bir ders sorusuyla devam edelim, ne dersin? 😎"
      )
    return f"🧱 **Çin Seddi Engeli:** {msg}"

  q_low = query.lower().strip()

  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! Kanka ben **Esila**, kurumsal yapay zeka asistanın."
        f" **{grd} - {subj}** konusunu açtın, harika! Çin Seddi Enterprise"
        " koruması altında her şeyi sana adım adım anlatacağım. Ne takıldı"
        " kafana, söylen bakalım?"
    )

  # Branş bazlı özelleştirilmiş samimi açıklama motoru
  if "ingilizce" in subj.lower() or any(
      w in q_low
      for w in [
          "was",
          "were",
          "english",
          "tense",
          "grammar",
          "anlamıyorum",
          "unit",
          "ünite",
          "çeviri",
          "kelime",
          "ne demek",
      ]
  ):
    return (
        f"🇬🇧 **Esila Enterprise İngilizce Stüdyosu ({grd})**\n\n"
        f"Kanka sorduğun **\"{query}\"** konusunu kafaya takma hiç, bende! Bak şimdi olayı şöyle özetleyeyim:\n\n"
        "**Adım 1: Temel Mantığı Kapalım**\n"
        "• İngilizcede bu tarz yapılar zaman akışını anlamamız için vardır. Gözünde büyütme sakın.\n\n"
        "**Adım 2: Formül ve Özne Dağılımı**\n"
        "• Tekil özneler (*I, He, She, It*) geçmişte **was** seçer; çoğul özneler ve *You* ise **were** alır.\n"
        "• *Örnek:* **He was happy** (Mutluydu) vs **They were ready** (Hazırlardı).\n\n"
        "**Adım 3: Pratik Taktik**\n"
        "• Bunu ezberleme kanka; günlük hayatta cümle kurarken tekil/çoğul dengesine dikkat et yeter.\n\n"
        f"💡 Nasıl, oturdu mu kafana {nick}? Başka takıldığın yer var mı?"
    )

  if "fizik" in subj.lower() or "fen" in subj.lower():
    return (
        f"⚡ **Esila Enterprise Fizik Atölyesi ({grd})**\n\n"
        f"Kanka **\"{query}\"** dedin, hemen çözelim! Fizik ezber değil mantıktır, bak şöyle:\n\n"
        "**Adım 1: Verilenleri Kenara Yazalım**\n"
        "• Soruda verilen değerleri (kg, m/s, Newton vb.) alt alta yazıyoruz. Çözümün yarısı bitti bile.\n\n"
        "**Adım 2: Doğru Formül**\n"
        "• İlgili fizik kanununu veya formülü sahneye çağırıyoruz.\n\n"
        "**Adım 3: İşlem ve Sonuç**\n"
        "• Değerleri yerine koyup sadeleştiriyoruz. İşlem önceliğine dikkat ettin mi sonuç cebinde!\n\n"
        f"💡 Fizik işte bu kadar kanka! Başka hangi soruyu parçalayalım {nick}?"
    )

  if "matematik" in subj.lower() or "geometri" in subj.lower():
    return (
        f"📐 **Esila Enterprise Matematik Çözüm Merkezi ({grd})**\n\n"
        f"Kanka **\"{query}\"** konusunu mercek altına aldık. Kurallar çok net, adım adım gidelim:\n\n"
        "**Adım 1: Bilinmeyene Harf Verelim**\n"
        "• Problemi okuyoruz ve bulmak istediğimiz değere 'x' diyoruz.\n\n"
        "**Adım 2: Denklemi Oluştur ve Çöz**\n"
        "• Verilen oranları denkleme döküp eşitliğin her iki tarafını düzenliyoruz.\n\n"
        "**Adım 3: Sağlama Yap**\n"
        "• Sonucu yerine koyup kontrol ettin mi işlem tamamdır.\n\n"
        f"💡 Düzenli yazarsan matematik daima kolaydır kanka! Devam edelim mi {nick}?"
    )

  return (
      f"✨ **Esila Enterprise AI — Adım Adım Analiz Paneli**\n\n"
      f"Kanka **\"{query}\"** konusunu **{subj}** dersi için inceledim. Hiç merak etme, bunu birlikte çözeriz:\n\n"
      "**1. Konunun Özü ve Temel Mantığı:**\n"
      "• Asla ezber yok kanka! Mantığı kavradığın an tüm soruları çözersin.\n\n"
      "**2. Adım Adım Uygulama:**\n"
      "• Kuralları sırasıyla uygulayıp parçaları birleştiriyoruz.\n\n"
      "**3. Sonuç:**\n"
      "• İstediğimiz sonuca tertemiz ulaşıyoruz.\n\n"
      f"💡 Nasıl, kafana yattı mı kanka {nick}? Başka neyi merak ediyorsun?"
  )


# ===============================================================================
# 1. GİRİŞ VE KAYIT EKRANI
# ===============================================================================
if not st.session_state.user:
  col1, col2, col3 = st.columns([1, 1.8, 1])
  with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
            <div class="hero-box">
              <h2>EduCore-AI Stüdyo</h2>
              <p style="margin:5px 0 0 0; color:#e2e8f0;">🛡️ Çin Seddi Enterprise (1000 Katman & Loglama Aktif)</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    auth_tab1, auth_tab2 = st.tabs(["🚀 Oturum Aç", "📝 Kayıt Ol"])

    with auth_tab1:
      st.markdown("### 🔐 Kurumsal Hesap Girişi")
      l_email = st.text_input("Gmail / E-posta Adresi", key="login_email")
      l_pass = st.text_input("Şifre", type="password", key="login_pass")

      if st.button("Giriş Yap", type="primary"):
        if l_email and l_pass:
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "SELECT * FROM users WHERE email = ?", (l_email.strip().lower(),)
          )
          row = c.fetchone()
          conn.close()

          login_success = False
          if row:
            stored_hash = row[2]
            stored_salt = row[3]
            if verify_secure_password(stored_hash, stored_salt, l_pass):
              login_success = True

          if login_success:
            st.session_state.user = {
                "id": row[0],
                "email": row[1],
                "nickname": row[4],
                "grade": row[5],
                "unique_code": row[6],
            }
            st.query_params["logged_email"] = row[1]
            st.success(f"Hoş geldin kanka {row[4]}! Esila hazır.")
            st.rerun()
          else:
            st.error("❌ E-posta veya şifre hatalı kanka!")
        else:
          st.warning("Lütfen tüm alanları doldurun.")

    with auth_tab2:
      st.markdown("### ✨ Yeni Kurumsal Hesap Oluştur")
      r_email = st.text_input("Gmail / E-posta Adresi", key="reg_email")
      r_pass = st.text_input("Şifre", type="password", key="reg_pass")
      r_pass2 = st.text_input(
          "Şifre Doğrulama (Tekrar)", type="password", key="reg_pass2"
      )
      r_nick = st.text_input(
          "İsim / Rumuz (Nickname)",
          key="reg_nick",
          placeholder="Örn: Alperen",
      )
      r_grade = st.selectbox("Eğitim Kademeniz", list(CURRICULUM.keys()), index=2)

      if st.button("Kayıt Ol ve Bağlan", type="primary"):
        if not r_email or not r_pass or not r_nick:
          st.warning("Lütfen tüm alanları eksiksiz doldurun.")
        elif r_pass != r_pass2:
          st.error("❌ Şifreler eşleşmiyor kanka!")
        else:
          is_safe, msg = enterprise_cin_seddi_firewall(r_nick)
          if not is_safe:
            st.error(f"❌ Çin Seddi Reddi: {msg}")
          else:
            try:
              conn = sqlite3.connect(DB_PATH)
              c = conn.cursor()
              c.execute("SELECT COUNT(*) FROM users")
              cnt = c.fetchone()[0] + 1
              unique_id_code = f"EDU-{cnt:05d}"
              pwd_hash, pwd_salt = secure_hash_password(r_pass)

              c.execute(
                  "INSERT INTO users (email, password_hash, password_salt,"
                  " nickname, grade, unique_code, last_active, created_at)"
                  " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (
                      r_email.strip().lower(),
                      pwd_hash,
                      pwd_salt,
                      r_nick.strip(),
                      r_grade,
                      unique_id_code,
                      str(datetime.datetime.now()),
                      str(datetime.date.today()),
                  ),
              )
              conn.commit()
              conn.close()
              st.success(
                  "✅ Kaydın oluşturuldu kanka! ID Numaran: "
                  f"{unique_id_code}. Şimdi giriş yapabilirsin."
              )
            except sqlite3.IntegrityError:
              st.error("❌ Bu Gmail adresiyle zaten bir hesap var kanka!")

# ===============================================================================
# 2. ANA KURUMSAL UYGULAMA EKRANI
# ===============================================================================
else:
  current_user = st.session_state.user
  nick = current_user["nickname"]
  u_code = current_user.get("unique_code", "EDU-00001")

  st.sidebar.markdown(f"### 👤 Kullanıcı: {nick}")
  st.sidebar.markdown(f"🆔 **ID Numarası:** `{u_code}`")
  st.sidebar.info(f"🎓 **Seviye:** {current_user['grade']}")
  st.sidebar.success("🛡️ **Çin Seddi:** Enterprise Aktif")

  if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state.user = None
    if "logged_email" in st.query_params:
      del st.query_params["logged_email"]
    st.rerun()

  st.sidebar.markdown("---")
  cat = st.sidebar.selectbox(
      "📚 Eğitim Kademeniz:", list(CURRICULUM.keys()), index=2
  )
  subj = st.sidebar.selectbox("📘 Ders Seçimi:", CURRICULUM[cat], index=2)

  # Ana Modül Sekmeleri (Esila AI, Sosyal Çalışma Grupları & Arkadaşlar, Güvenlik Logları)
  app_tab1, app_tab2, app_tab3 = st.tabs([
      "💬 Esila AI Asistan",
      "👥 Sosyal Çalışma Grupları & Arkadaşlar",
      "🛡️ Çin Seddi Güvenlik Logları (Audit)",
  ])

  # --- SEKME 1:
