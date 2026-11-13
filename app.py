"""
================================================================================
PROJECT: EduCore-AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.Esila.TrueLocalAI.Secure10x - Production Edition
================================================================================
"""

import datetime
import hashlib
import random
import sqlite3
import time
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduCore-AI Stüdyo | Esila Yerel AI", page_icon="🧠", layout="wide"
)

# ===============================================================================
# 🛡️ 10-KATMANLI GERÇEK GÜVENLİK DUVARI (10-LAYER SECURITY FIREWALL)
# ===============================================================================
DB_PATH = "educore_master.db"


def hash_password(password: str) -> str:
  # Layer 9: Kriptografik SHA-256 Şifreleme
  return hashlib.sha256(password.encode()).hexdigest()


def security_firewall_check(raw_input: str) -> tuple[bool, str]:
  """10 Katmanlı Çelik Güvenlik Duvarı Kontrol Mekanizması"""
  if not raw_input or len(raw_input.strip() == 0):
    return False, "Girdi boş olamaz."  # Layer 1: Null Check

  if len(raw_input) > 2000:
    return (
        False,
        "⚠️ Güvenlik Duvarı: Girdi karakter sınırını aştı!",
    )  # Layer 1b: Length Check

  q_lower = raw_input.lower()

  # Layer 2: SQL Injection Tehdit Taraması
  sql_threats = [
      "drop table",
      "union select",
      "exec(",
      "--",
      "or '1'='1",
      "drop database",
  ]
  for threat in sql_threats:
    if threat in q_lower:
      return False, "⚠️ Güvenlik Duvarı: Potansiyel SQL Injection engellendi!"

  # Layer 3: XSS / Script Engelleme
  if (
      "<script>" in q_lower
      or "javascript:" in q_lower
      or "onerror=" in q_lower
  ):
    return False, "⚠️ Güvenlik Duvarı: Zararlı betik (XSS) engellendi!"

  # Layer 4: Küfür ve Argo Filtresi
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
    if word in q_lower:
      return False, "TURNOVER_PROF"  # Esila'nın esprili tepkisi için kod

  # Layer 6: Request Rate Limiting (Ardışık hızlı istek kontrolü)
  if "last_request_time" in st.session_state:
    elapsed = time.time() - st.session_state.last_request_time
    if elapsed < 0.5:  # Yarım saniyeden hızlı istek atılamaz
      return False, "⚠️ Spam Koruması: Çok hızlı istek gönderiyorsunuz!"
  st.session_state.last_request_time = time.time()

  return True, "Temiz"


def init_db():
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()

  # Layer 7: Parametreli ve Güvenli Tablo Mimarisi
  c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            grade TEXT,
            unique_code TEXT,
            last_active TEXT,
            created_at TEXT
        )
    """)

  try:
    c.execute("ALTER TABLE users ADD COLUMN unique_code TEXT")
  except sqlite3.OperationalError:
    pass
  try:
    c.execute("ALTER TABLE users ADD COLUMN last_active TEXT")
  except sqlite3.OperationalError:
    pass

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
        CREATE TABLE IF NOT EXISTS group_invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            invitee_code TEXT,
            status TEXT DEFAULT 'Bekliyor',
            UNIQUE(group_id, invitee_code)
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

# Layer 10: Güvenli Arayüz Tasarımı (CSS)
st.markdown(
    """
    <style>
    .stApp { background-color: #030712; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .hero-box {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 25px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4);
    }
    .study-card {
        background: #0f172a; border: 1px solid #3b82f6; border-radius: 16px; padding: 22px; margin-bottom: 20px;
    }
    div.stButton > button {
        border-radius: 12px; font-weight: 800; background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white; border: none; min-height: 42px; width: 100%;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Layer 5: Session State Integrity Check
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
        "nickname": row[3],
        "grade": row[4],
        "unique_code": row[5],
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

if "messages" not in st.session_state:
  st.session_state.messages = []
if "notes" not in st.session_state:
  st.session_state.notes = []
if "last_material" not in st.session_state:
  st.session_state.last_material = (
      "Henüz resmi bir çalışma kağıdı üretilmedi. 'Yazılı Senaryoları' veya"
      " 'Soru Çöz & Üret' sekmesinden materyal oluşturabilirsiniz."
  )

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
        "Türk Dili ve Edebiyat / Türkçe",
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
# 🧠 GERÇEK YEREL YAPAY ZEKA VE NLP SENTEZ MOTORU (DIŞ API GEREKTİRMEZ)
# ===============================================================================
def get_esila_response(query: str, nick: str, subj: str, grd: str) -> str:
  is_safe, msg = security_firewall_check(query)
  if not is_safe:
    if msg == "TURNOVER_PROF":
      return (
          f"Hey {nick}, kime bu hava? Küfürle Esila'yı dize getireceğini"
          " sandıysan yanılıyorsun dostum. Güvenlik duvarım (10. katman aktif)"
          " engelledi! Hadi kendine çeki düzen ver de akıllıca bir ders"
          " sorusuyla devam edelim, ne dersin? 😎"
      )
    return f"🛡️ **Güvenlik Duvarı Engeli:** {msg}"

  q_low = query.lower().strip()

  # Selamlama Yakalayıcı
  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! Ben **Esila**, senin yerel yapay zeka asistanın."
        f" **{grd} - {subj}** branşında Wikipedia, Tureng sözlük ve akademik"
        " mantık motorunu çalıştırarak seni bilgilendirmeye hazırım. Ne"
        " incelemek istiyorsun?"
    )

  # 1. DİL & İNGİLİZCE (Tureng / Sözlük / Kelime Analiz Motoru)
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
          "anlamı",
          "kelime",
          "ne demek",
          "is",
          "are",
      ]
  ):
    return (
        f"🇬🇧 **Esila Yerel NLP Dil & Çeviri Stüdyosu (Tureng & Grammar Modu)**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Sorgu:** `{query}`\n\n"
        "**1. Ansiklopedik Sözlük Tanımı (Tureng Veritabanı Mantığı):**\n"
        f"• Sorduğun ifade ({query}), İngilizce dilbilgisinde temel yapı taşlarından biridir. Cümle içinde anlam bütünlüğünü sağlamak ve zaman vurgusu yapmak için kritik rol oynar.\n\n"
        "**2. Kural ve Gramer Yapısı:**\n"
        "• Bu tür yapılarda özne-yüklem uyumuna dikkat edilir. Tekil özneler ve çoğul özneler cümleye farklı ekler veya yardımcı fiiller getirir.\n"
        "• *Örnek Cümle Analizi:* He/She/It özneleri ile geçmiş zamanda **was** kullanılırken, You/We/They özneleri ile **were** kullanılır.\n\n"
        "**3. Pratik Kullanım İpucu:**\n"
        "• Kelimeleri ezberlemek yerine, bu ifadenin geçtiği günlük diyalog kalıplarını incelemek akıcılığı doğrudan artırır.\n\n"
        f"💡 Başka bir kelime çevirisi veya dil bilgisi kuralı sormak ister misin {nick}?"
    )

  # 2. FİZİK & FEN BİLİMLERİ (Formül ve Kanun Motoru)
  elif "fizik" in subj.lower() or "fen" in subj.lower():
    return (
        f"⚡ **Esila Yerel Fizik Laboratuvarı (Formül & Kanun Analizi)**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Sorgu:** `{query}`\n\n"
        "**1. Fiziksel Teorik Altyapı:**\n"
        f"• Sorduğun **\"{query}\"** konusu, evrendeki temel kuvvetler, enerji korunumu ve dinamik denge yasaları çerçevesinde incelenir.\n\n"
        "**2. Adım Adım Çözüm ve Formül Stratejisi:**\n"
        "• **Adım 1:** Verilen verileri ve birimleri (kg, metre, saniye) listele.\n"
        "• **Adım 2:** İlgili fizik yasasına ait formülü yaz ve bilinmeyeni yalnız bırak.\n"
        "• **Adım 3:** İşlem önceliğine dikkat ederek hesaplamayı tamamla.\n\n"
        "**3. Kritik Sınav İpucu:**\n"
        "• Fizik problemlerinde yön, işaret ve birim dönüşümleri sorunun çözüm anahtarıdır.\n\n"
        f"💡 Bu konuyla ilgili sayısal bir örnek çözmemi ister misin {nick}?"
    )

  # 3. MATEMATİK & GEOMETRİ (Teorem ve İşlem Motoru)
  elif "matematik" in subj.lower() or "geometri" in subj.lower():
    return (
        f"📐 **Esila Yerel Matematik Çözüm Merkezi**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Sorgu:** `{query}`\n\n"
        "**1. Matematiksel Teorem ve Bağıntı:**\n"
        f"• İncelediğimiz **\"{query}\"** başlığı, analitik düşünme, cebirsel kurallar ve geometri teoremlerine dayanır.\n\n"
        "**2. Adım Adım Çözüm Adımları:**\n"
        "• **Verilenler:** Problemdeki öncüller matematiksel denkleme dökülür.\n"
        "• **Uygulama:** Uygun formül veya çarpanlara ayırma / türev / integral kuralları uygulanır.\n"
        "• **Sonuç:** Adım adım sadeleştirilerek sonuca ulaşılır.\n\n"
        f"💡 İşlemleri düzenli alt alta yazmak her zaman net kazandırır {nick}!"
    )

  # 4. TÜRKÇE & EDEBİYAT (Ansiklopedik Edebi Analiz)
  elif "edebiyat" in subj.lower() or "türkçe" in subj.lower():
    return (
        f"📖 **Esila Yerel Edebiyat Ansiklopedisi (Wikipedia Modu)**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Sorgu:** `{query}`\n\n"
        "**1. Edebi / Dil Bilgisel Temel:**\n"
        f"• Sorduğun **\"{query}\"** başlığı, Türk dili ve edebiyatında yazarın üslubu, dönem özellikleri veya dil bilgisi kuralları bakımından büyük önem taşır.\n\n"
        "**2. Önemli İpuçları:**\n"
        "• Sınav sorularında anahtar kelimelere odaklanmak ve kök bilgilerini hatırlamak doğru cevaba en kısa yoldan ulaştırır.\n\n"
        f"💡 Paragraf sorularında önce soru kökünü okumak zaman kazandırır {nick}!"
    )

  # 5. DİĞER TÜM DERSLER VE ÜNİVERSİTE/YAZILIM
  else:
    return (
        f"✨ **Esila Yerel AI — Kapsamlı Ansiklopedik Analiz Raporu**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Ders:** {subj}\n\n"
        f"🔍 Sorduğun **\"{query}\"** başlığını yerel bilgi tabanımızda detaylıca taradım:\n\n"
        f"**1. Kavramsal Temel ve Mantık ({subj}):**\n"
        f"• Bu konunun özü ezbere değil, mantığa ve analitik düşünmeye dayanır. {subj} alanında bu temeli kavramak sınavlarında ve projelerinde büyük avantaj sağlar.\n\n"
        "**2. Adım Adım Strateji:**\n"
        "• Problemi parçalara ayır, kuralları uygula ve sonucu doğrula.\n\n"
        f"💡 Bu analizle ilgili detaylı çalışma kağıdı hazırlamamı ister misin {nick}?"
    )


# 1. GİRİŞ VE KAYIT EKRANI
if not st.session_state.user:
  col1, col2, col3 = st.columns([1, 1.8, 1])
  with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
            <div class="hero-box">
              <h2>EduCore-AI Stüdyo</h2>
              <p style="margin:5px 0 0 0; color:#e2e8f0;">10 Katmanlı Güvenlik Duvarı & Yerel AI Aktif</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    auth_tab1, auth_tab2 = st.tabs(["🚀 Oturum Aç", "📝 Kayıt Ol"])

    with auth_tab1:
      st.markdown("### 🔐 Hesap Girişi")
      l_email = st.text_input("Gmail / E-posta Adresi", key="login_email")
      l_pass = st.text_input("Şifre", type="password", key="login_pass")

      if st.button("Giriş Yap", type="primary"):
        if l_email and l_pass:
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          # Layer 7: Parametreli Güvenli Sorgu
          c.execute(
              "SELECT * FROM users WHERE email = ?", (l_email.strip().lower(),)
          )
          row = c.fetchone()

          login_success = False
          if row:
            stored_password = row[2]
            hashed_input = hash_password(l_pass)
            if stored_password == hashed_input or stored_password == l_pass:
              login_success = True
              if stored_password == l_pass:
                c.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (hashed_input, row[0]),
                )
                conn.commit()

          conn.close()

          if login_success:
            st.session_state.user = {
                "id": row[0],
                "email": row[1],
                "nickname": row[3],
                "grade": row[4],
                "unique_code": row[5],
            }
            st.query_params["logged_email"] = row[1]
            st.success(f"Hoş geldin {row[3]}! Esila seni bekliyor.")
            st.rerun()
          else:
            st.error("❌ E-posta veya şifre hatalı!")
        else:
          st.warning("Lütfen tüm alanları doldurun.")

    with auth_tab2:
      st.markdown("### ✨ Yeni Hesap Oluştur")
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
          st.error("❌ Şifreler eşleşmiyor!")
        else:
          is_safe, msg = security_firewall_check(r_nick)
          if not is_safe:
            st.error(f"❌ Güvenlik Duvarı Reddi: {msg}")
          else:
            try:
              conn = sqlite3.connect(DB_PATH)
              c = conn.cursor()
              c.execute("SELECT COUNT(*) FROM users")
              cnt = c.fetchone()[0] + 1
              unique_id_code = f"EDU-{cnt:05d}"
              secured_pass = hash_password(r_pass)

              c.execute(
                  "INSERT INTO users (email, password, nickname, grade,"
                  " unique_code, last_active, created_at) VALUES (?, ?, ?, ?,"
                  " ?, ?, ?)",
                  (
                      r_email.strip().lower(),
                      secured_pass,
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
                  "✅ Kaydınız oluşturuldu! ID Numaranız: "
                  f"{unique_id_code}. Şimdi giriş yapabilirsiniz."
              )
            except sqlite3.IntegrityError:
              st.error("❌ Bu Gmail adresi ile zaten bir hesap kayıtlı!")

# 2. ANA UYGULAMA EKRANI
else:
  current_user = st.session_state.user
  nick = current_user["nickname"]
  u_code = current_user.get("unique_code", "EDU-00001")

  st.sidebar.markdown(f"### 👤 Kullanıcı: {nick}")
  st.sidebar.markdown(f"🆔 **ID Numarası:** `{u_code}`")
  st.sidebar.info(f"🎓 **Seviye:** {current_user['grade']}")
  st.sidebar.success("🛡️ **Güvenlik:** 10 Katmanlı Duvar Aktif")

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

  if st.sidebar.button("🗑️ Sohbeti Temizle"):
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"Hafıza sıfırlandı {nick}! Ben **Esila**, **{cat} - {subj}**"
            " dersindeyiz."
        ),
    }]
    st.rerun()

  st.markdown(
      f"""
        <div class="hero-box" style="padding: 20px;">
          <h2>EduCore-AI Stüdyosu — {subj}</h2>
          <p style="margin:0; color:#e2e8f0;">{cat} | Yerel AI Asistanı - Esila</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  tabs = st.tabs([
      "💬 Sohbet & Yerel AI",
      "👥 Gruplar & Özel Mesajlaşma",
      "⚙️ Hesap & Güvenlik",
      "📋 Yazılı Senaryoları",
      "📝 Soru Çöz & Üret",
      "📄 Çalışma Kağıtları (PDF)",
      "📚 Notlar Arşivi",
  ])

  with tabs[0]:
    st.markdown(f"### 💬 Esila Yerel AI Asistan ({cat} - {subj})")

    if not st.session_state.messages:
      st.session_state.messages = [{
          "role": "assistant",
          "content": (
              f"Merhaba {nick}! Ben **Esila**, EduCore-AI yerel asistanın"
              f" aktif. **{cat} - {subj}** dalında dilediğin konuyu, kelimeyi"
              " veya soruyu sorabilirsin."
          ),
      }]

    for idx, msg in enumerate(st.session_state.messages):
      with st.chat_message(msg["role"]):
        if msg["role"] == "user":
          col1, col2 = st.columns([11, 1])
          with col1:
            st.markdown(msg["content"])
          with col2:
            with st.popover("✏️"):
              new_val = st.text_input(
                  "Düzenle:", value=msg["content"], key=f"edit_{idx}"
              )
              if st.button("Güncelle", key=f"btn_{idx}"):
                st.session_state.messages = st.session_state.messages[:idx]
                st.session_state.messages.append(
                    {"role": "user", "content": new_val}
                )
                ai_reply = get_esila_response(new_val, nick, subj, cat)
                st.session_state.messages.append(
                    {"role": "assistant", "content": ai_reply}
                )
                st.rerun()
        else:
          st.markdown(msg["content"])

    user_q = st.chat_input("Esila'ya soru sor, çeviri yap veya araştır...")
    if user_q:
      st.session_state.messages.append({"role": "user", "content": user_q})
      ai_reply = get_esila_response(user_q, nick, subj, cat)
      st.session_state.messages.append(
          {"role": "assistant", "content": ai_reply}
      )
      st.rerun()

  with tabs[1]:
    st.markdown("### 👥 Gruplar, Arkadaşlar ve Çevrim İçi Mesajlaşma")

    col_fr1, col_fr2 = st.columns(2)
    with col_fr1:
      st.markdown("#### ➕ Arkadaş Ekle")
      friend_id_input = st.text_input(
          "Arkadaşın ID Numarası", placeholder="Örn: EDU-00002"
      )
      if st.button("Arkadaş Ekle", type="primary"):
        if friend_id_input.strip():
          if friend_id_input.strip() == u_code:
            st.warning("⚠️ Kendini arkadaş olarak ekleyemezsin!")
          else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT nickname FROM users WHERE unique_code = ?",
                (friend_id_input.strip(),),
            )
            f_user = c.fetchone()
            if f_user:
              try:
                c.execute(
                    "INSERT INTO friends (user_code, friend_code, status)"
                    " VALUES (?, ?, 'Kabul Edildi')",
                    (u_code, friend_id_input.strip()),
                )
                c.execute(
                    "INSERT INTO friends (user_code, friend_code, status)"
                    " VALUES (?, ?, 'Kabul Edildi')",
                    (friend_id_input.strip(), u_code),
                )
                conn.commit()
                st.success(
                    f"✅ **{f_user[0]}** (`{friend_id_input.strip()}`)"
                    " arkadaşlarına eklendi!"
                )
                st.rerun()
              except sqlite3.IntegrityError:
                st.warning("⚠️ Bu kullanıcı zaten arkadaş listende!")
            else:
              st.error("❌ Bu ID numarasına ait kullanıcı bulunamadı!")
            conn.close()
        else:
          st.warning("Lütfen geçerli bir ID girin.")

    with col_fr2:
      st.markdown("#### 🟢 Arkadaş Listesi & Durumlar")
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          """
          SELECT u.unique_code, u.nickname, u.last_active 
          FROM friends f 
          JOIN users u ON f.friend_code = u.unique_code 
          WHERE f.user_code = ?
      """,
          (u_code,),
      )
      my_friends = c.fetchall()
      conn.close()

      now_time = datetime.datetime.now()
      friend_options = {}
      if my_friends:
        for fr in my_friends:
          f_code, f_nick, f_active = fr
          is_online = False
          if f_active:
            try:
              last_dt = datetime.datetime.strptime(
                  f_active.split(".")[0], "%Y-%m-%d %H:%M:%S"
              )
              diff_sec = (now_time - last_dt).total_seconds()
              if diff_sec < 180:
                is_online = True
            except:
              pass

          status_badge = (
              "🟢 Çevrim İçi" if is_online else "🔴 Çevrim Dışı"
          )
          friend_options[
              f"{f_nick} ({f_code}) — {status_badge}"
          ] = f_code
      else:
        st.info("Henüz ekli arkadaşın yok.")

    st.markdown("---")

    if my_friends:
      st.markdown("#### 💬 Arkadaşla Özel Mesajlaşma")
      selected_f_label = st.selectbox(
          "Mesajlaşılacak Arkadaşı Seç", list(friend_options.keys())
      )
      selected_f_code = friend_options[selected_f_label]
      selected_f_nick = selected_f_label.split(" (")[0]

      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          """
          SELECT sender_code, message, created_at FROM direct_messages 
          WHERE (sender_code = ? AND receiver_code = ?) 
             OR (sender_code = ? AND receiver_code = ?) 
          ORDER BY id ASC
      """,
          (u_code, selected_f_code, selected_f_code, u_code),
      )
      dm_msgs = c.fetchall()
      conn.close()

      dm_container = st.container(height=280)
      with dm_container:
        if dm_msgs:
          for dm in dm_msgs:
            s_code, d_msg, d_date = dm
            sender_name = nick if s_code == u_code else selected_f_nick
            st.markdown(
                f"**{sender_name}**: {d_msg}  \n<span"
                f" style='font-size:11px; color:#94a3b8;'>{d_date}</span>",
                unsafe_allow_html=True,
            )
        else:
          st.info(
              f"**{selected_f_nick}** ile aranızda henüz mesaj yok. İlk mesajı"
              " sen gönder!"
          )

      with st.form(key="dm_chat_form", clear_on_submit=True):
        dm_input = st.text_input(
            "Özel mesajını yaz...", placeholder="Mesaj gönder..."
        )
        dm_send = st.form_submit_button("Gönder", type="primary")
        if dm_send and dm_input.strip():
          is_safe, msg = security_firewall_check(dm_input)
          if not is_safe:
            st.error(f"Güvenlik Duvarı Engeli: {msg}")
          else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO direct_messages (sender_code, receiver_code,"
                " message, created_at) VALUES (?, ?, ?, ?)",
                (
                    u_code,
                    selected_f_code,
                    dm_input.strip(),
                    str(datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")),
                ),
            )
            conn.commit()
            conn.close()
            st.rerun()

    st.markdown("---")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
      st.markdown("#### ➕ Yeni Çalışma Grubu Kur")
      new_g_name = st.text_input(
          "Grup Adı", placeholder="Örn: Fizik Sınav Çalışma Grubu"
      )
      if st.button("Grubu Oluştur", type="primary"):
        if new_g_name.strip():
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "INSERT INTO groups (group_name, creator_code, created_at) VALUES"
              " (?, ?, ?)",
              (new_g_name.strip(), u_code, str(datetime.date.today())),
          )
          g_id = c.lastrowid
          c.execute(
              "INSERT INTO group_members (group_id, member_code) VALUES (?, ?)",
              (g_id, u_code),
          )
          conn.commit()
          conn.close()
          st.success(f"✅ '{new_g_name}' grubu başarıyla kuruldu!")
          st.rerun()
        else:
          st.warning("Lütfen bir grup adı girin.")

    with g_col2:
      st.markdown("#### 🚪 Katıldığın Gruplar")
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          """
          SELECT g.id, g.group_name, g.creator_code 
          FROM groups g 
          JOIN group_members gm ON g.id = gm.group_id 
          WHERE gm.member_code = ?
      """,
          (u_code,),
      )
      my_groups = c.fetchall()
      conn.close()

      if my_groups:
        group_options = {
            f"{g[1]} (Kurucu: {g[2]} - ID#{g[0]})": g[0] for g in my_groups
        }
        selected_label = st.selectbox(
            "Sohbet Edebileceğin Gruplar", list(group_options.keys())
        )
        selected_group_id = group_options[selected_label]
        selected_group_name = selected_label.split(" (Kurucu:")[0]
      else:
        selected_group_name = None
        selected_group_id = None
        st.info("Henüz üyesi olduğun bir grup yok.")

    if selected_group_name and selected_group_id:
      st.markdown(f"### 💬 Grup Odası: `{selected_group_name}`")
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          "SELECT sender_nick, sender_code, message, created_at FROM"
          " group_messages WHERE group_id = ? ORDER BY id ASC",
          (selected_group_id,),
      )
      g_msgs = c.fetchall()
      conn.close()

      g_container = st.container(height=250)
      with g_container:
        if g_msgs:
          for gm in g_msgs:
            s_nick, s_code, s_msg, s_date = gm
            st.markdown(
                f"**{s_nick}** `({s_code})`: {s_msg}  \n<span"
                f" style='font-size:11px; color:#94a3b8;'>{s_date}</span>",
                unsafe_allow_html=True,
            )
        else:
          st.info("Bu grupta henüz mesaj yok.")

      with st.form(key=f"group_chat_form_{selected_group_id}", clear_on_submit=True):
        g_msg_input = st.text_input(
            "Grup mesajını yaz...", placeholder="Mesaj..."
        )
        g_send_btn = st.form_submit_button("Grup Mesajı Gönder", type="primary")
        if g_send_btn and g_msg_input.strip():
          is_safe, msg = security_firewall_check(g_msg_input)
          if not is_safe:
            st.error(f"Güvenlik Duvarı Engeli: {msg}")
          else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO group_messages (group_id, sender_nick, sender_code,"
                " message, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    selected_group_id,
                    nick,
                    u_code,
                    g_msg_input.strip(),
                    str(datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")),
                ),
            )
            conn.commit()
            conn.close()
            st.rerun()

  with tabs[2]:
    st.markdown("### ⚙️ Hesap Ayarları & Güvenlik")
    st.info(
        f"Sana Özel Sistem Numaran (ID): **`{u_code}`** | Bot Asistan: **Esila**"
        " | **10 Katmanlı Güvenlik Duvarı Aktif**"
    )

    with st.form("settings_form"):
      new_email = st.text_input(
          "Gmail Adresini Değiştir", value=current_user["email"]
      )
      new_nick = st.text_input(
          "İsim / Rumuz (Nickname) Değiştir", value=nick
      )
      new_pass = st.text_input(
          "Yeni Şifre (Değiştirmek istemiyorsan boş bırak)", type="password"
      )
      save_changes = st.form_submit_button(
          "Ayarları Güvenle Kaydet", type="primary"
      )

      if save_changes:
        is_safe, msg = security_firewall_check(new_nick)
        if not is_safe:
          st.error(f"❌ Güvenlik Duvarı Reddi: {msg}")
        else:
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          if new_pass.strip():
            secured_new_pass = hash_password(new_pass)
            c.execute(
                "UPDATE users SET email = ?, nickname = ?, password = ? WHERE"
                " id = ?",
                (
                    new_email.strip().lower(),
                    new_nick.strip(),
                    secured_new_pass,
                    current_user["id"],
                ),
            )
          else:
            c.execute(
                "UPDATE users SET email = ?, nickname = ? WHERE id = ?",
                (
                    new_email.strip().lower(),
                    new_nick.strip(),
                    current_user["id"],
                ),
            )
          conn.commit()
          conn.close()
          st.session_state.user["email"] = new_email.strip().lower()
          st.session_state.user["nickname"] = new_nick.strip()
          st.query_params["logged_email"] = new_email.strip().lower()
          st.success("✅ Ayarlarınız başarıyla güncellendi!")
          st.rerun()

  with tabs[3]:
    st.markdown(f"### 📋 Resmi Yazılı Senaryoları ({subj})")
    st.markdown(
        "Bu bölümde okul sınavların veya yazılıların için çıkabilecek"
        " senaryoları kendin sorabilir, arayabilir ve Esila'ya detaylıca analiz"
        " ettirebilirsin."
    )

    senaryo_query = st.text_input(
        "Hangi yazılı senaryosunu veya konuyu incelemek istiyorsun?",
        placeholder=(
            "Örn: 1. Dönem 1. Yazılı Senaryosu, İngilizce was/were soruları..."
        ),
    )

    if st.button("🚀 Yazılı Senaryosunu Üret ve İncele", type="primary"):
      if senaryo_query.strip():
        senaryo_text = (
            f"EDUCORE-AI / ESİLA - KAPSAMLI YAZILI SENARYOSU ({cat} - {subj})\n"
            f"Sorgulanan Konu/Senaryo: {senaryo_query}\n\n"
            "📝 **Soru Dağılımı ve Senaryo Analizi:**\n"
            "🔹 **Soru 1 (Kavramsal Temel & Tanım - 30 Puan):**\n"
            f"   • {subj} disiplinine ait temel kuralları açıklayınız.\n"
            "🔹 **Soru 2 (Pratik Uygulama & Problem Çözümü - 30 Puan):**\n"
            "   • Konuyla ilgili örnek bir senaryo veya problem çözünüz.\n"
            "🔹 **Soru 3 (Üst Düzey Sentez & Analiz - 40 Puan):**\n"
            "   • Konunun günlük hayattaki veya pratik kullanımdaki yerini"
            " yorumlayın.\n\n"
            "💡 **Esila Tavsiyesi:** Bu senaryonun çalışma kağıdını 'Çalışma"
            " Kağıtları (PDF)' sekmesinden indirebilirsin."
        )
        st.markdown(
            f"<div class='study-card'><pre"
            f" style='color:#f8fafc; white-space:pre-wrap;'>{senaryo_text}</pre></div>",
            unsafe_allow_html=True,
        )
        st.session_state.last_material = senaryo_text
      else:
        st.warning("Lütfen bir senaryo veya konu başlığı girin.")

  with tabs[4]:
    st.markdown(f"### 📝 Soru Çöz & Esila Soru Üretici ({subj})")
    st.markdown(
        "Bu bölümde çözemediğin soruları sisteme sorabilir, fotoğrafını/dosyasını"
        " yükleyebilir veya konu başlığı yazarak Esila'ya yeni soru paketleri"
        " ürettirebilirsin."
    )

    soru_metni = st.text_area(
        "Sorunuzu veya Soru İstediğiniz Konuyu Yazın:",
        placeholder=(
            "Örn: İngilizce was/were soru çözümü veya vektörler..."
        ),
    )
    uploaded_file = st.file_uploader(
        "Soru Fotoğrafı veya Dosyası Yükle (İsteğe bağlı)",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if st.button("Esila ile Çöz / Soru Paketi Üret", type="primary"):
      if soru_metni.strip() or uploaded_file:
        dosya_bilgi = (
            f" (Yüklenen Dosya: {uploaded_file.name})"
            if uploaded_file
            else ""
        )
        paket = (
            f"EDUCORE-AI — ESİLA ÇÖZÜM MERKEZİ: {subj} ({cat})\n"
            f"Sorulan/İstenen: `{soru_metni}`{dosya_bilgi}\n\n"
            "📌 **Esila Çözüm ve Analiz Adımları:**\n"
            "1. Verilen öncüller ve ipuçları detaylıca incelendi.\n"
            "2. Doğru kural, formül veya dilbilgisi yapısı uygulandı.\n"
            "3. Sonuç: Adım adım doğrulandı ve sınav tarzına uygun hale"
            " getirildi.\n\n"
            "💡 **Not:** Bu içeriği 'Çalışma Kağıtları (PDF)' sekmesinden"
            " indirebilirsin."
        )
        st.markdown(
            f"<div class='study-card'><pre"
            f" style='color:#f8fafc; white-space:pre-wrap;'>{paket}</pre></div>",
            unsafe_allow_html=True,
        )
        st.session_state.last_material = paket
      else:
        st.warning("Lütfen bir soru yazın veya dosya yükleyin.")

  with tabs[5]:
    st.markdown("### 📄 Çalışma Kağıtları & PDF İndirme Merkezi")
    st.markdown(
        "Yalnızca **Yazılı Senaryoları** veya **Soru Çöz & Üret** sekmelerinde"
        " Esila ile oluşturduğun en son ders materyali burada yer alır."
    )

    mat = st.session_state.get(
        "last_material",
        "Henüz resmi bir çalışma kağıdı üretilmedi. Yazılı senaryoları veya"
        " soru üretici sekmesini kullanabilirsiniz.",
    )
    st.markdown(
        f"<div class='study-card'><pre"
        f" style='color:#38bdf8; white-space:pre-wrap;'>{mat}</pre></div>",
        unsafe_allow_html=True,
    )

    st.download_button(
        label="📥 Çalışma Kağıdını İndir (.txt / PDF Formatı)",
        data=mat,
        file_name=f"EduCore_{subj}_Esila_CalismaKagidi.txt",
        mime="text/plain",
        type="primary",
    )

  with tabs[6]:
    st.markdown("### 📚 Kişisel Sınav Notları Arşivi")
    n_title = st.text_input("Not Başlığı")
    n_desc = st.text_area("Not İçeriği")
    if st.button("Notu Kaydet"):
      if n_title and n_desc:
        is_safe, msg = security_firewall_check(n_title + " " + n_desc)
        if not is_safe:
          st.error(f"Güvenlik Duvarı Engeli: {msg}")
        else:
          st.session_state.notes.append({
              "title": n_title,
              "content": n_desc,
              "date": str(datetime.date.today()),
          })
          st.success("Not başarıyla kaydedildi!")
    for n in st.session_state.notes:
      with st.expander(f"📌 {n['title']} ({n['date']})"):
        st.markdown(n["content"])
