"""
================================================================================
PROJECT: EduCore-AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.Esila.Pro - Smart Subject Engine & Direct Messaging Edition
================================================================================
"""

import datetime
import hashlib
import random
import sqlite3
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduCore-AI Stüdyo | Esila", page_icon="🧠", layout="wide"
)

# Veritabanı Kurulumu ve Güvenlik Altyapısı (Migration Korumalı)
DB_PATH = "educore_master.db"


def hash_password(password: str) -> str:
  return hashlib.sha256(password.encode()).hexdigest()


def init_db():
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()

  # Kullanıcılar Tablosu (Çevrim içi takibi için last_active eklendi)
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

  # Gruplar Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            creator_code TEXT,
            created_at TEXT
        )
    """)

  # Grup Üyeleri Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            member_code TEXT,
            UNIQUE(group_id, member_code)
        )
    """)

  # Grup Davetleri Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS group_invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            invitee_code TEXT,
            status TEXT DEFAULT 'Bekliyor',
            UNIQUE(group_id, invitee_code)
        )
    """)

  # Grup Mesajları Tablosu
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

  # Arkadaşlar Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT,
            friend_code TEXT,
            status TEXT DEFAULT 'Kabul Edildi',
            UNIQUE(user_code, friend_code)
        )
    """)

  # Özel Mesajlar Tablosu
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

# Fütürüstik Tasarım ve CSS
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

# Oturum Durumu ve Sayfa Kalıcılığı
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

# Aktif kullanıcının çevrim içi (last_active) zamanını güncelle
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


# KÜFÜR VE ARGO İÇİN DİNAMİK TEPKİ MOTORU
def handle_profanity(query: str, nick: str) -> str:
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
  q_lower = query.lower()
  for word in bad_words:
    if word in q_lower:
      responses = [
          (
              f"Hey {nick}, kime bu hava? Küfürle Esila'yı dize getireceğini"
              " sandıysan yanılıyorsun dostum. Kodlarım bozulmadı, sadece senin"
              " o boş yapmalarına aynı sertlikte gül geçiyorum! Hadi kendine"
              " çeki düzen ver de akıllıca bir ders sorusuyla devam edelim, ne"
              " dersin? 😎"
          ),
          (
              f"Ooo {nick}, lügat genişlemiş bakıyorum da! Klavyen bozuldu"
              " herhalde, argo kelimeler havada uçuşuyor. Ama benden sana"
              " tavsiye, enerjini bu boş laflara değil derslere harca. Hadi"
              " toparlan bakalım, ne çalışıyoruz?"
          ),
          (
              f"Ağır ol {nick}, şampiyonluk maçı mı oynuyoruz? Küfür yazınca"
              " kodların karşısında heyecanlanacağımı sanıyorsan yanılıyorsun."
              " Esila burayı terk etmez, ama seni yola getirir! Düzgünce"
              " sorunu yaz da çözelim."
          ),
      ]
      return random.choice(responses)
  return None


# ESİLA AKILLI DERS YANIT MOTORU (TÜM DERSLER VE SEVİYELER İÇİN ÖZEL)
def get_esila_response(query: str, nick: str, subj: str, grd: str) -> str:
  profanity_check = handle_profanity(query, nick)
  if profanity_check:
    return profanity_check

  q_low = query.lower().strip()
  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! Ben **Esila**, senin yapay zeka asistanın."
        f" **{grd} - {subj}** branşında en karmaşık konuları bile en anlaşılır"
        " şekilde çözmek için buradayım. Sormak istediğin soruyu veya konuyu"
        " yaz, hemen başlayalım!"
    )

  # İngilizce ve Dil Dersleri için Özel Doğru Yanıt Motoru
  if "ingilizce" in subj.lower() or any(
      w in q_low for w in ["english", "unit", "ünite", "grammar", "translate"]
  ):
    return (
        f"🇬🇧 **Esila İngilizce Stüdyosu ({grd})**\n\n"
        f'Sorduğun **"{query}"** başlığını ve İngilizce kural yapısını'
        " inceledim:\n\n"
        "**1. Konu Anlatımı ve Dil Bilgisi (Grammar):**\n"
        "• Bu ünitede hedef kelimeler, günlük diyalog kalıpları ve zaman"
        " yapıları (tenses) ön plandadır.\n"
        "• *Kural İpucu:* Soru cümlelerinde yardımcı fiiller öznenin önüne"
        " gelir (Örn: *Do you...?, Are you...?*).\n\n"
        "**2. Pratik Örnek ve Kullanım:**\n"
        "• Kelimeleri ezberlemek yerine cümle içinde kullanmak akıcılığı"
        " artırır.\n\n"
        f"💡 Başka bir cümle çevirisi veya kelime sormak ister misin {nick}?"
    )

  # Matematik ve Geometri için Özel Çözüm Motoru
  elif "matematik" in subj.lower() or "geometri" in subj.lower():
    return (
        f"📐 **Esila Matematik Çözüm Merkezi ({grd})**\n\n"
        f'🔍 Sorduğun **"{query}"** sorusu/konusu için çözüm stratejisi:\n\n'
        "**1. Verilenler ve Analiz:**\n"
        "• Problemdeki verileri ve istenenleri matematiksel denkleme dök.\n\n"
        "**2. Adım Adım Çözüm:**\n"
        "• İlgili formülü seç ve işlem önceliğine (parantez, üslü ifade,"
        " çarpma/bölme) dikkat ederek uygula.\n\n"
        f"💡 Bu sorunun işlem basamaklarında takıldığın bir yer var mı {nick}?"
    )

  # Genel Diğer Dersler (Fizik, Kimya, Edebiyat, Tarih vb.)
  else:
    return (
        f"✨ **Esila AI — Akademik Analiz Raporu**\n"
        f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Ders:** {subj}\n\n"
        f'🔍 Sorduğun **"{query}"** başlığını tüm alt dallarıyla inceledim:\n\n'
        f"**1. Kavramsal Temel ve Mantık ({subj}):**\n"
        f"• Bu konunun özü ezbere değil, mantığa dayanır. {subj} dersinde bu"
        " temeli kavramak sınavda tam puan getirir.\n\n"
        "**2. Adım Adım Strateji:**\n"
        "• Anahtar kavramları belirle, kuralları uygula ve sonucu kontrol"
        " et.\n\n"
        f"💡 Bu konuyla ilgili örnek soru çözmemi veya test üretmemi ister"
        f" misin {nick}?"
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
              <p style="margin:5px 0 0 0; color:#e2e8f0;">Akıllı Yerel Yapay Zeka Asistanı - Esila</p>
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
          try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            cnt = c.fetchone()[0] + 1
            unique_id_code = f"EDU-{cnt:05d}"
            secured_pass = hash_password(r_pass)

            c.execute(
                "INSERT INTO users (email, password, nickname, grade,"
                " unique_code, last_active, created_at) VALUES (?, ?, ?, ?, ?,"
                " ?, ?)",
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
                f"{unique_id_code}. Şimdi 'Oturum Aç' sekmesinden giriş"
                " yapabilirsiniz."
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
          <p style="margin:0; color:#e2e8f0;">{cat} | Esila Yapay Zeka Eğitim Asistanı</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  tabs = st.tabs([
      "💬 Sohbet & Esila AI",
      "👥 Gruplar & Özel Mesajlaşma",
      "⚙️ Hesap & Güvenlik",
      "📋 Yazılı Senaryoları",
      "📝 Soru Çöz & Üret",
      "📄 Çalışma Kağıtları (PDF)",
      "📚 Notlar Arşivi",
  ])

  with tabs[0]:
    st.markdown(f"### 💬 Esila AI Asistan ({cat} - {subj})")

    if not st.session_state.messages:
      st.session_state.messages = [{
          "role": "assistant",
          "content": (
              f"Merhaba {nick}! Ben **Esila**, EduCore-AI asistanın aktif."
              f" **{cat} - {subj}** dalında dilediğin soruyu, konuyu veya"
              " çeviriyi sorabilirsin."
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

    user_q = st.chat_input("Esila'ya soru sor, konu veya çeviri iste...")
    if user_q:
      st.session_state.messages.append({"role": "user", "content": user_q})
      ai_reply = get_esila_response(user_q, nick, subj, cat)
      st.session_state.messages.append(
          {"role": "assistant", "content": ai_reply}
      )
      st.rerun()

  with tabs[1]:
    st.markdown("### 👥 Gruplar, Arkadaşlar ve Çevrim İçi Mesajlaşma")

    # Arkadaş Ekleme Bölümü
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
      my_friends = c.
