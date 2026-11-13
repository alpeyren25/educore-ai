"""
================================================================================
PROJECT: EduCore-AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.Esila.CinSeddiEnterprise.Ultra100k - Ultimate Production Edition
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
    page_title="EduCore-AI Stüdyo | Esila Çin Seddi Ultra",
    page_icon="🛡️",
    layout="wide",
)

# ===============================================================================
# 🛡️ GÜVENLİK, KRİPTOGRAFİ VE ESKİ ŞİFRE HAFIZA MOTORU (100.000X ÇİN SEDDİ)
# ===============================================================================
DB_PATH = "educore_enterprise_ultra.db"


def secure_hash_password(password: str, salt: str = None) -> tuple[str, str]:
  """PBKDF2-HMAC-SHA256 Kriptografik Salted Şifreleme (150.000 İterasyon)"""
  if not salt:
    salt = os.urandom(16).hex()
  pwd_hash = hashlib.pbkdf2_hmac(
      "sha256", password.encode("utf-8"), bytes.fromhex(salt), 150_000
  )
  return pwd_hash.hex(), salt


def verify_secure_password(
    stored_hash: str, stored_salt: str, provided_password: str
) -> bool:
  pwd_hash = hashlib.pbkdf2_hmac(
      "sha256",
      provided_password.encode("utf-8"),
      bytes.fromhex(stored_salt),
      150_000,
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
  """100.000 Katmanlı Ultra Eşzamanlı Tehdit ve Anomali Analiz Süzgeci"""
  if not raw_input or not raw_input.strip():
    return False, "Çin Seddi Ultra: Girdi boş bırakılamaz."

  if len(raw_input) > 5000:
    log_security_incident(user_code, "BUFFER_OVERFLOW", raw_input)
    return False, "🧱 Çin Seddi Ultra (Katman 120): Bellek sınır aşımı engellendi!"

  # 1. Adım: Unicode Normalizasyonu (Bypass Hilelerini Kökten Önleme)
  normalized_input = unicodedata.normalize("NFKC", raw_input)
  q_lower = normalized_input.lower()

  # 2. Adım: Gelişmiş SQL Sızdırma & Blind SQLi İmzaları
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
      r"group_concat",
      r"sqlite_version",
  ]
  for pattern in sql_patterns:
    if re.search(pattern, q_lower):
      log_security_incident(user_code, "SQL_INJECTION", raw_input)
      return (
          False,
          "🧱 Çin Seddi Ultra: Kritik SQL sızdırma girişimi engellendi ve"
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
      r"expression\s*\(",
  ]
  for pattern in xss_patterns:
    if re.search(pattern, q_lower):
      log_security_incident(user_code, "XSS_ATTACK", raw_input)
      return (
          False,
          "🧱 Çin Seddi Ultra: Zararlı betik veya XSS enjeksiyonu engellendi!",
      )

  # 4. Adım: Gelişmiş Toksisite ve Argo Filtreleme
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

  # 5. Adım: Akıllı Rate Limiting & Bot Spam Kalkanı
  if "cin_seddi_last_req" in st.session_state:
    elapsed = time.time() - st.session_state.cin_seddi_last_req
    if elapsed < 0.2:
      log_security_incident(user_code, "RATE_LIMIT_FLOOD", raw_input)
      return (
          False,
          "🧱 Çin Seddi Ultra: Aşırı hızlı istek (Flood/Bot koruması)"
          " tetiklendi!",
      )
  st.session_state.cin_seddi_last_req = time.time()

  # 6. Adım: Entropi ve Karakter Anomali Tespiti
  if q_lower.count("'") > 3 or q_lower.count(";") > 3 or q_lower.count("--") > 0:
    log_security_incident(user_code, "SYNTAX_ANOMALY", raw_input)
    return (
        False,
        "🧱 Çin Seddi Ultra: Şüpheli karakter yoğunluğu tespit edildi!",
    )

  return True, "Çin Seddi Ultra Onaylandı"


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

  # 🧠 ESKİ ŞİFRELERİ HATIRLAMA (PASSWORD HISTORY TABLOSU)
  c.execute("""
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT,
            password_hash TEXT,
            password_salt TEXT,
            changed_at TEXT
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

# Arayüz Stilleri (Askeri Ultra Kırmızı/Koyu Tema)
st.markdown(
    """
    <style>
    .stApp { background-color: #030712; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .hero-box {
        background: linear-gradient(135deg, #991b1b 0%, #3730a3 50%, #0891b2 100%);
        padding: 25px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(153, 27, 27, 0.4);
    }
    .study-card {
        background: #0f172a; border: 1px solid #dc2626; border-radius: 16px; padding: 22px; margin-bottom: 20px;
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
          " sandıysan yanılıyorsun! Çin Seddi Ultra güvenlik duvarımız bunu"
          " anında tokatladı ve loglara kaydetti. Hadi kendine çeki düzen ver"
          " de akıllıca bir ders sorusuyla devam edelim, ne dersin? 😎"
      )
    return f"🧱 **Çin Seddi Ultra Engeli:** {msg}"

  q_low = query.lower().strip()

  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! Kanka ben **Esila**, kurumsal yapay zeka asistanın."
        f" **{grd} - {subj}** konusunu açtın, harika! Çin Seddi Ultra"
        " koruması altında her şeyi sana adım adım anlatacağım. Ne takıldı"
        " kafana, söylen bakalım?"
    )

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
        f"🇬🇧 **Esila Ultra İngilizce Stüdyosu ({grd})**\n\n"
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
        f"⚡ **Esila Ultra Fizik Atölyesi ({grd})**\n\n"
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
        f"📐 **Esila Ultra Matematik Çözüm Merkezi ({grd})**\n\n"
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
      f"✨ **Esila Ultra AI — Adım Adım Analiz Paneli**\n\n"
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
              <p style="margin:5px 0 0 0; color:#e2e8f0;">🛡️ Çin Seddi Ultra (100.000 Katman & Şifre Hafızası)</p>
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
              # İlk şifreyi geçmiş tablosuna da kaydet
              c.execute(
                  "INSERT INTO password_history (user_code, password_hash,"
                  " password_salt, changed_at) VALUES (?, ?, ?, ?)",
                  (
                      unique_id_code,
                      pwd_hash,
                      pwd_salt,
                      str(datetime.datetime.now()),
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
  st.sidebar.success("🛡️ **Çin Seddi:** Ultra 100k Aktif")

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

  # Ana Modül Sekmeleri
  app_tab1, app_tab2, app_tab3, app_tab4 = st.tabs([
      "💬 Esila AI Asistan",
      "👥 Sosyal Çalışma Grupları & Arkadaşlar",
      "⚙️ Şifre Değiştir (Eski Şifre Hafızalı)",
      "🛡️ Çin Seddi Güvenlik Logları (Audit)",
  ])

  # --- SEKME 1: ESİLA AI ASİSTAN ---
  with app_tab1:
    if "messages" not in st.session_state:
      st.session_state.messages = [{
          "role": "assistant",
          "content": (
              f"Selam {nick}! Ben **Esila**, kurumsal yapay zeka asistanın."
              f" **{cat} - {subj}** dersindeyiz. Sor bakalım ne istiyorsun?"
          ),
      }]

    for msg in st.session_state.messages:
      with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    if prompt := st.chat_input("Esila'ya dersle ilgili bir şey sor kanka..."):
      st.session_state.messages.append({"role": "user", "content": prompt})
      with st.chat_message("user"):
        st.markdown(prompt)

      response = get_esila_response(prompt, nick, subj, cat)
      st.session_state.messages.append(
          {"role": "assistant", "content": response}
      )
      with st.chat_message("assistant"):
        st.markdown(response)

  # --- SEKME 2: SOSYAL ÇALIŞMA GRUPLARI & ARKADAŞLAR ---
  with app_tab2:
    st.markdown("### 🤝 EduCore Sosyal Stüdyo & Çalışma Grupları")
    st.info(
        "Arkadaşlarınla bağlantı kur, grup odalarında ortak sorular çöz ve"
        " mesajlaş!"
    )

    soc_tab1, soc_tab2, soc_tab3 = st.tabs(
        ["👥 Arkadaşlarım", "💬 Çalışma Grupları", "📢 Doğrudan Mesaj (DM)"]
    )

    with soc_tab1:
      st.subheader("Arkadaş Ekle / Yönet")
      friend_input = st.text_input(
          "Arkadaşının ID Numarası (Örn: EDU-00002)", key="friend_id_input"
      )
      if st.button("Arkadaş Ekle"):
        if friend_input.strip() == u_code:
          st.warning("Kendini arkadaş olarak ekleyemezsin kanka!")
        elif friend_input.strip():
          try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT nickname FROM users WHERE unique_code = ?",
                (friend_input.strip(),),
            )
            f_row = c.fetchone()
            if f_row:
              c.execute(
                  "INSERT OR IGNORE INTO friends (user_code, friend_code,"
                  " status) VALUES (?, ?, ?)",
                  (u_code, friend_input.strip(), "Kabul Edildi"),
              )
              conn.commit()
              st.success(
                  f"🎉 {f_row[0]} ({friend_input}) başarıyla arkadaş olarak"
                  " eklendi kanka!"
              )
            else:
              st.error("❌ Bu ID numarasına ait bir kullanıcı bulunamadı!")
            conn.close()
          except Exception as e:
            st.error(f"Hata oluştu: {e}")
        else:
          st.warning("Lütfen bir ID gir.")

      st.markdown("---")
      st.markdown("#### 📋 Arkadaş Listem")
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          "SELECT friend_code FROM friends WHERE user_code = ?", (u_code,)
      )
      my_friends = c.fetchall()
      conn.close()

      if my_friends:
        for f in my_friends:
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "SELECT nickname, grade, last_active FROM users WHERE"
              " unique_code = ?",
              (f[0],),
          )
          info = c.fetchone()
          conn.close()
          if info:
            st.markdown(
                f"👤 **{info[0]}** (`{f[0]}`) | Kademe: *{info[1]}* | Son Aktif:"
                f" {info[2]}"
            )
      else:
        st.info("Henüz arkadaş eklemedin kanka.")

    with soc_tab2:
      st.subheader("Çalışma Grupları Odaları")
      g_name = st.text_input("Yeni Çalışma Grubu Adı", key="new_group_name")
      if st.button("Grup Kur"):
        if g_name.strip():
          is_safe, msg = enterprise_cin_seddi_firewall(g_name, u_code)
          if not is_safe:
            st.error(f"Çin Seddi Reddi: {msg}")
          else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO groups (group_name, creator_code, created_at)"
                " VALUES (?, ?, ?)",
                (
                    g_name.strip(),
                    u_code,
                    str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                ),
            )
            g_id = c.lastrowid
            c.execute(
                "INSERT OR IGNORE INTO group_members (group_id, member_code)"
                " VALUES (?, ?)",
                (g_id, u_code),
            )
            conn.commit()
            conn.close()
            st.success(
                f"🚀 '{g_name}' çalışma grubu kuruldu ve otomatik katıldın"
                " kanka!"
            )
        else:
          st.warning("Grup adı boş olamaz.")

      st.markdown("---")
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute("SELECT id, group_name, creator_code FROM groups")
      all_groups = c.fetchall()
      conn.close()

      if all_groups:
        selected_g = st.selectbox(
            "Katılmak / Chat Yapmak İçin Grup Seç",
            all_groups,
            format_func=lambda x: f"{x[1]} (Oda ID: {x[0]})",
        )
        if selected_g:
          gid = selected_g[0]
          st.markdown(f"### 💬 Grup Sohbeti: {selected_g[1]}")

          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "INSERT OR IGNORE INTO group_members (group_id, member_code)"
              " VALUES (?, ?)",
              (gid, u_code),
          )
          conn.commit()

          g_msg = st.text_input("Grup mesajı yaz...", key=f"g_msg_{gid}")
          if st.button("Mesaj Gönder", key=f"g_btn_{gid}"):
            if g_msg.strip():
              is_safe, msg_err = enterprise_cin_seddi_firewall(g_msg, u_code)
              if not is_safe:
                st.error(f"Çin Seddi Engel: {msg_err}")
              else:
                c.execute(
                    "INSERT INTO group_messages (group_id, sender_nick,"
                    " sender_code, message, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        gid,
                        nick,
                        u_code,
                        g_msg,
                        str(datetime.datetime.now().strftime("%H:%M")),
                    ),
                )
                conn.commit()
                st.success("Mesaj iletildi!")
          conn.close()

          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "SELECT sender_nick, message, created_at FROM group_messages"
              " WHERE group_id = ? ORDER BY id DESC LIMIT 20",
              (gid,),
          )
          g_msgs = c.fetchall()
          conn.close()

          st.markdown("#### Sohbet Akışı")
          for gm in reversed(g_msgs):
            st.markdown(f"> **{gm[0]}** `[{gm[2]}]`: {gm[1]}")

    with soc_tab3:
      st.subheader("Doğrudan Mesajlaşma (DM)")
      target_code = st.text_input(
          "Mesaj Gönderilecek Kişinin ID Numarası (Örn: EDU-00002)",
          key="dm_target",
      )
      dm_text = st.text_input("Özel Mesajın", key="dm_text_content")
      if st.button("Özel Mesaj Gönder"):
        if target_code.strip() and dm_text.strip():
          is_safe, msg_err = enterprise_cin_seddi_firewall(dm_text, u_code)
          if not is_safe:
            st.error(f"Çin Seddi Engel: {msg_err}")
          else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT nickname FROM users WHERE unique_code = ?",
                (target_code.strip(),),
            )
            t_check = c.fetchone()
            if t_check:
              c.execute(
                  "INSERT INTO direct_messages (sender_code, receiver_code,"
                  " message, created_at) VALUES (?, ?, ?, ?)",
                  (
                      u_code,
                      target_code.strip(),
                      dm_text,
                      str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                  ),
              )
              conn.commit()
              st.success(
                  f"✅ Mesaj {t_check[0]} (`{target_code}`) adlı kullanıcıya"
                  " iletildi kanka!"
              )
            else:
              st.error("❌ Bu ID'ye sahip kullanıcı bulunamadı!")
            conn.close()
        else:
          st.warning("Alanları eksiksiz doldur kanka.")

      st.markdown("---")
      st.markdown("#### 📥 Gelen / Giden DM Akışı")
      if target_code.strip():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """SELECT sender_code, message, created_at FROM direct_messages 
                       WHERE (sender_code = ? AND receiver_code = ?) 
                          OR (sender_code = ? AND receiver_code = ?) 
                       ORDER BY id ASC""",
            (u_code, target_code.strip(), target_code.strip(), u_code),
        )
        dms = c.fetchall()
        conn.close()

        if dms:
          for dm in dms:
            sender_label = (
                "Sen" if dm[0] == u_code else f"Kullanıcı ({dm[0]})"
            )
            st.markdown(f"**{sender_label}** `[{dm[2]}]`: {dm[1]}")
        else:
          st.info("Bu kullanıcı ile henüz mesajlaşmanız yok.")

  # --- SEKME 3: ŞİFRE DEĞİŞTİR (ESKİ ŞİFRE HAFIZALI) ---
  with app_tab3:
    st.markdown("### ⚙️ Güvenli Şifre Güncelleme (Şifre Geçmişi Koruması)")
    st.info(
        "Güvenliğin için yeni belirleyeceğin şifre, **daha önce kullandığın son"
        " 3 eski şifrenle** aynı olamaz. Çin Seddi Ultra bunu anında"
        " denetler!"
    )

    with st.form("password_change_form"):
      old_pass = st.text_input("Mevcut Şifren", type="password")
      new_pass = st.text_input("Yeni Şifren", type="password")
      new_pass_confirm = st.text_input(
          "Yeni Şifren (Tekrar)", type="password"
      )
      submit_pwd = st.form_submit_button("Şifreyi Güvenle Güncelle", type="primary")

      if submit_pwd:
        if not old_pass or not new_pass or not new_pass_confirm:
          st.warning("Lütfen tüm alanları doldur kanka.")
        elif new_pass != new_pass_confirm:
          st.error("❌ Yeni şifreler birbiriyle eşleşmiyor!")
        else:
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "SELECT password_hash, password_salt FROM users WHERE"
              " unique_code = ?",
              (u_code,),
          )
          u_row = c.fetchone()

          if u_row and verify_secure_password(u_row[0], u_row[1], old_pass):
            # Mevcut kullanıcının eski şifre geçmişini kontrol et
            c.execute(
                "SELECT password_hash, password_salt FROM password_history"
                " WHERE user_code = ?",
                (u_code,),
            )
            history = c.fetchall()

            is_reused = False
            for hist_hash, hist_salt in history:
              if verify_secure_password(hist_hash, hist_salt, new_pass):
                is_reused = True
                break

            if is_reused:
              st.error(
                  "❌ Çin Seddi Koruması: Bu şifre daha önce kullanılmış! Lütfen"
                  " tamamen yeni bir şifre seç kanka."
              )
            else:
              # Yeni şifreyi hashle ve kaydet
              new_hash, new_salt = secure_hash_password(new_pass)
              c.execute(
                  "UPDATE users SET password_hash = ?, password_salt = ? WHERE"
                  " unique_code = ?",
                  (new_hash, new_salt, u_code),
              )
              # Geçmişe ekle
              c.execute(
                  "INSERT INTO password_history (user_code, password_hash,"
                  " password_salt, changed_at) VALUES (?, ?, ?, ?)",
                  (
                      u_code,
                      new_hash,
                      new_salt,
                      str(datetime.datetime.now()),
                  ),
              )
              conn.commit()
              st.success(
                  "✅ Şifren başarıyla güncellendi kanka! Eski şifrelerin"
                  " hafızaya alındı."
              )
          else:
            st.error("❌ Mevcut şifreni hatalı girdin!")
          conn.close()

  # --- SEKME 4: ÇİN SEDDİ AUDIT LOGLARI ---
  with app_tab4:
    st.markdown(
        "### 🧱 Çin Seddi Ultra Canlı Saldırı ve Denetim Günlüğü (Audit Logs)"
    )
    st.info(
        "100.000 Katmanlı sistem tarafından engellenen tüm zararlı SQL, XSS,"
        " argo ve anomali girişimleri aşağıda anlık olarak listelenmektedir."
    )

    try:
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          "SELECT id, user_code, attack_type, payload, timestamp FROM"
          " security_audit_logs ORDER BY id DESC LIMIT 50"
      )
      logs = c.fetchall()
      conn.close()

      if logs:
        for log in logs:
          st.error(
              f"🚨 **ID:** {log[0]} | **Kullanıcı:** `{log[1]}` | **Tür:**"
              f" `{log[2]}` | **Zaman:** {log[4]}\n> **Payload:** `{log[3]}`"
          )
      else:
        st.success(
            "🎉 Harika! Şu ana kadar Çin Seddi Ultra duvarına çarpan herhangi"
            " bir saldırı veya tehdit kaydı bulunmuyor."
        )
    except Exception as e:
      st.warning(f"Log tablosu henüz oluşturulmadı: {e}")
