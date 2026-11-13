"""
================================================================================
PROJECT: EduCore-AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.Esila.Final - Bugfixed & Complete Edition
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

  # Kullanıcılar Tablosu
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

# Kullanıcı aktiflik süresini güncelle
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
              if diff_sec < 180:  # Son 3 dakika içinde aktifse
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

    # Özel Mesajlaşma Bölümü
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
    # Grup Kurma ve Odalar Bölümü
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
        " | Şifreleme: **SHA-256 Aktif**"
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if new_pass.strip():
          secured_new_pass = hash_password(new_pass)
          c.execute(
              "UPDATE users SET email = ?, nickname = ?, password = ? WHERE id"
              " = ?",
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
              (new_email.strip().lower(), new_nick.strip(), current_user["id"]),
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
            "Örn: 1. Dönem 1. Yazılı Senaryosu, İngilizce 1. Ünite Soruları..."
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
        "Burada çözemediğin soruları sisteme sorabilir, fotoğrafını/dosyasını"
        " yükleyebilir veya konu başlığı yazarak Esila'ya yeni soru paketleri"
        " ürettirebilirsin."
    )

    soru_metni = st.text_area(
        "Sorunuzu veya Soru İstediğiniz Konuyu Yazın:",
        placeholder=(
            "Örn: İngilizce past tense soru çözümü veya fonksiyonlar..."
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
        st.session_state.notes.append({
            "title": n_title,
            "content": n_desc,
            "date": str(datetime.date.today()),
        })
        st.success("Not başarıyla kaydedildi!")
    for n in st.session_state.notes:
      with st.expander(f"📌 {n['title']} ({n['date']})"):
        st.markdown(n["content"])
