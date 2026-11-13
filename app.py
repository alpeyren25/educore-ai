"""
================================================================================
PROJECT: EduCore AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.TrueAI.Core - Groups, Messaging & Persistent Session Edition
================================================================================
"""

import datetime
import sqlite3
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduCore AI - Akıllı Stüdyo", page_icon="🧠", layout="wide"
)

# Veritabanı Kurulumu
DB_PATH = "educore_master.db"


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
            created_at TEXT
        )
    """)
  # Gruplar Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT UNIQUE,
            creator_code TEXT,
            created_at TEXT
        )
    """)
  # Grup Mesajları Tablosu
  c.execute("""
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            sender_nick TEXT,
            sender_code TEXT,
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

# Oturum Durumu ve Sayfa Yenileme / 2 Hafta Kalıcılık Kontrolü
if "user" not in st.session_state:
  st.session_state.user = None

# Eğer session boşsa ama tarayıcı URL'sinde kayıtlı email varsa otomatik oturum aç (Yenileme sorunu çözümü)
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

if "messages" not in st.session_state:
  st.session_state.messages = []
if "notes" not in st.session_state:
  st.session_state.notes = []

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
    ],
    "Üniversite & Akademik": [
        "Yazılım & Algoritma",
        "İleri Matematik / Analiz",
        "Veri Yapıları",
        "Mühendislik Temelleri",
        "Genel Akademik",
    ],
}


# KÜFÜR VE HAKARET YAKALAMA MOTORU (Mizahi & Sert Tepki)
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
      return (
          f"Hey {nick}, kime bu hava? Küfürle yapay zekayı dize getireceğini"
          " sandıysan yanılıyorsun dostum. Kodlarım bozulmadı, sadece senin o"
          " boş yapmalarına aynı sertlikte gül geçiyorum! Hadi kendine çeki"
          " düzen ver de akıllıca bir ders sorusuyla devam edelim, ne"
          " dersin? 😎"
      )
  return None


# ZENGİNLEŞTİRİLMİŞ CEVAP MOTORU
def get_educore_response(query: str, nick: str, subj: str, grd: str) -> str:
  profanity_check = handle_profanity(query, nick)
  if profanity_check:
    return profanity_check

  q_low = query.lower().strip()
  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! EduCore AI motoru aktif. **{grd} - {subj}** branşında en"
        " karmaşık konuları bile en anlaşılır şekilde çözmek için buradayım."
        " Sormak istediğin soruyu veya konuyu yaz, başlayalım!"
    )

  return (
      f"**EduCore AI — Derinlemesine Akademik Analiz Raporu**\n"
      f"**Öğrenci:** {nick} | **Seviye:** {grd} | **Ders:** {subj}\n\n"
      f'🔍 Sorduğun **"{query}"** başlığını tüm alt dallarıyla inceledim. İşte'
      " bilmen gerekenler:\n\n"
      f"**1. Kavramsal Temel ve Mantık:**\n"
      f"• Bu konunun özü ezbere değil, mantığa dayanır. {subj} dalında bu"
      " kuralı kavramak sınavda hayat kurtarır.\n\n"
      f"**2. Adım Adım Çözüm / Strateji:**\n"
      "• **Adım 1:** Verilen verileri ve anahtar kelimeleri ayıkla.\n"
      "• **Adım 2:** Uygun formül veya yöntemi seçerek uygula.\n"
      "• **Adım 3:** Sonucu kontrol et.\n\n"
      f"💡 **EduCore Tavsiyesi:** Bu analizi kaydetmek veya soru üretmek için"
      " sol menüdeki sekmeleri kullanabilirsin {nick}!"
  )


# 1. GİRİŞ VE KAYIT EKRANI
if not st.session_state.user:
  col1, col2, col3 = st.columns([1, 1.8, 1])
  with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
            <div class="hero-box">
              <h2>EduCore AI Stüdyo</h2>
              <p style="margin:5px 0 0 0; color:#e2e8f0;">Akıllı Yerel Yapay Zeka Asistanı</p>
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
              "SELECT * FROM users WHERE email = ? AND password = ?",
              (l_email.strip().lower(), l_pass),
          )
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
            # Sayfa yenilense bile oturumun düşmemesi için query_params içine kaydediyoruz
            st.query_params["logged_email"] = row[1]
            st.success(f"Hoş geldin {row[3]}!")
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
          "İsim (Sana nasıl hitap edilsin?)",
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

            c.execute(
                "INSERT INTO users (email, password, nickname, grade,"
                " unique_code, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    r_email.strip().lower(),
                    r_pass,
                    r_nick.strip(),
                    r_grade,
                    unique_id_code,
                    str(datetime.date.today()),
                ),
            )
            conn.commit()
            conn.close()
            st.success(
                "✅ Kaydınız başarıyla oluşturuldu! Benzersiz Numaran:"
                f" {unique_id_code}. Şimdi 'Oturum Aç' sekmesinden giriş"
                " yapabilirsiniz."
            )
          except sqlite3.IntegrityError:
            st.error("❌ Bu Gmail adresi ile zaten bir hesap kayıtlı!")

# 2. ANA UYGULAMA EKRANI
else:
  current_user = st.session_state.user
  nick = current_user["nickname"]
  u_code = current_user.get("unique_code", "EDU-00001")

  st.sidebar.markdown(f"### 👤 Öğrenci: {nick}")
  st.sidebar.markdown(f"🆔 **Hesap No (ID):** `{u_code}`")
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
            f"Hafıza sıfırlandı {nick}! **{cat} - {subj}** dersindeyiz."
        ),
    }]
    st.rerun()

  st.markdown(
      f"""
        <div class="hero-box" style="padding: 20px;">
          <h2>EduCore AI Stüdyosu — {subj}</h2>
          <p style="margin:0; color:#e2e8f0;">{cat} | Akıllı Asistan: EduCore AI (Grup & ID Aktif)</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  tabs = st.tabs([
      "💬 Sohbet & Yerel AI",
      "👥 Gruplar & Mesajlaşma",
      "⚙️ Hesap & ID Yönetimi",
      "📋 Yazılı Senaryoları",
      "📝 Soru Üretici",
      "📄 Çalışma Kağıtları (PDF/İndir)",
      "📚 Notlar Arşivi",
  ])

  with tabs[0]:
    st.markdown(f"### 💬 EduCore AI Asistan ({cat} - {subj})")

    if not st.session_state.messages:
      st.session_state.messages = [{
          "role": "assistant",
          "content": (
              f"Merhaba {nick}! EduCore AI asistanın aktif. İlkokuldan"
              " üniversiteye kadar dilediğin dersi ve konuyu sormaya"
              " başlayabilirsin."
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
                ai_reply = get_educore_response(new_val, nick, subj, cat)
                st.session_state.messages.append(
                    {"role": "assistant", "content": ai_reply}
                )
                st.rerun()
        else:
          st.markdown(msg["content"])

    user_q = st.chat_input("EduCore AI'a soru sor veya konu anlatımı iste...")
    if user_q:
      st.session_state.messages.append({"role": "user", "content": user_q})
      ai_reply = get_educore_response(user_q, nick, subj, cat)
      st.session_state.messages.append(
          {"role": "assistant", "content": ai_reply}
      )
      st.session_state.last_material = ai_reply
      st.rerun()

  with tabs[1]:
    st.markdown("### 👥 Gruplar & Arkadaş Mesajlaşma Merkezi")
    st.markdown(
        "Arkadaşlarınla kendi ID numaranı kullanarak grup kurabilir ve bu"
        " odalarda karşılıklı mesajlaşabilirsiniz."
    )

    # Veritabanından mevcut grupları çek
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT group_name, creator_code FROM groups")
    all_groups = c.fetchall()
    conn.close()

    g_col1, g_col2 = st.columns(2)

    with g_col1:
      st.markdown("#### ➕ Yeni Grup Kur")
      new_g_name = st.text_input(
          "Grup Adı", placeholder="Örn: Vertex Çalışma Grubu"
      )
      if st.button("Grubu Oluştur", type="primary"):
        if new_g_name.strip():
          try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO groups (group_name, creator_code, created_at)"
                " VALUES (?, ?, ?)",
                (new_g_name.strip(), u_code, str(datetime.date.today())),
            )
            conn.commit()
            conn.close()
            st.success(f"✅ '{new_g_name}' grubu başarıyla kuruldu!")
            st.rerun()
          except sqlite3.IntegrityError:
            st.error("❌ Bu isimle bir grup zaten var!")
        else:
          st.warning("Lütfen bir grup adı girin.")

    with g_col2:
      st.markdown("#### 🚪 Gruba Katıl / Sohbet Seç")
      if all_groups:
        group_names = [g[0] for g in all_groups]
        selected_group = st.selectbox("Aktif Gruplar", group_names)
      else:
        selected_group = None
        st.info("Henüz kurulmuş bir grup yok. Sol taraftan ilk grubu sen kur!")

    if selected_group:
      st.markdown(f"---")
      st.markdown(f"### 💬 Grup Sohbet Odası: `{selected_group}`")

      # Mesajları veritabanından çek
      conn = sqlite3.connect(DB_PATH)
      c = conn.cursor()
      c.execute(
          "SELECT sender_nick, sender_code, message, created_at FROM"
          " group_messages WHERE group_name = ? ORDER BY id ASC",
          (selected_group,),
      )
      g_msgs = c.fetchall()
      conn.close()

      # Mesaj kutusu alanı
      chat_container = st.container(height=300)
      with chat_container:
        if g_msgs:
          for gm in g_msgs:
            s_nick, s_code, s_msg, s_date = gm
            st.markdown(
                f"**{s_nick}** `({s_code})`: {s_msg}  \n<span"
                f" style='font-size:11px; color:#94a3b8;'>{s_date}</span>",
                unsafe_allow_html=True,
            )
        else:
          st.info(
              "Bu grupta henüz mesaj yok. İlk mesajı sen göndererek sohbeti"
              " başlat!"
          )

      # Grup mesajı gönderme inputu
      with st.form(key="group_chat_form", clear_on_submit=True):
        g_msg_input = st.text_input(
            "Mesajını yaz...", placeholder="Buraya yazıp gönder..."
        )
        g_send_btn = st.form_submit_button("Gönder", type="primary")

        if g_send_btn and g_msg_input.strip():
          conn = sqlite3.connect(DB_PATH)
          c = conn.cursor()
          c.execute(
              "INSERT INTO group_messages (group_name, sender_nick, sender_code,"
              " message, created_at) VALUES (?, ?, ?, ?, ?)",
              (
                  selected_group,
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
    st.markdown("### ⚙️ Hesap Ayarları & Benzersiz ID Yönetimi")
    st.info(
        f"Sana Özel Sistem Numaran (ID): **`{u_code}`**\n*(Bu numara TC"
        " kimlik gibidir; arkadaşların bu numara ile seni tanır ve gruplarda"
        " eşleşirsin.)*"
    )

    with st.form("settings_form"):
      new_email = st.text_input(
          "Gmail Adresini Değiştir", value=current_user["email"]
      )
      new_nick = st.text_input("Hitap Adını Değiştir", value=nick)
      new_pass = st.text_input(
          "Yeni Şifre (Değiştirmek istemiyorsan boş bırak)", type="password"
      )

      save_changes = st.form_submit_button(
          "Ayarları Kaydet ve Güncelle", type="primary"
      )

      if save_changes:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if new_pass.strip():
          c.execute(
              "UPDATE users SET email = ?, nickname = ?, password = ? WHERE id"
              " = ?",
              (
                  new_email.strip().lower(),
                  new_nick.strip(),
                  new_pass,
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
    if st.button("🚀 Yazılı Senaryosunu Üret ve İncele", type="primary"):
      senaryo = (
          f"EDUCORE AI - KAPSAMLI YAZILI SENARYOSU: {cat} - {subj}\n\n"
          "📝 **Soru Dağılımı:**\n"
          "🔹 Soru 1 (Kavramsal Temel): Ünitenin kurallarını açıklayınız. (30"
          " Puan)\n"
          "🔹 Soru 2 (Pratik Çözüm): Örnek problemi adım adım çözünüz. (30"
          " Puan)\n"
          "🔹 Soru 3 (Sentez): Günlük hayattaki karşılığını yorumlayınız. (40"
          " Puan)\n\n"
          "💡 **Asistan Notu:** Bu çalışma kağıdını 'Çalışma Kağıtları (PDF)'"
          " sekmesinden indirebilirsin."
      )
      st.markdown(
          f"<div class='study-card'><pre"
          f" style='color:#f8fafc; white-space:pre-wrap;'>{senaryo}</pre></div>",
          unsafe_allow_html=True,
      )
      st.session_state.last_material = senaryo

  with tabs[4]:
    st.markdown(f"### 📝 Soru Üretici Stüdyosu ({subj})")
    t_in = st.text_input(
        "Soru İstenen Konu:", placeholder="Örn: Vektörler, Osmanlı Tarihi..."
    )
    if st.button("Soru Paketi Üret", type="primary"):
      if t_in:
        paket = (
            f"EDUCORE AI — SORU PAKETİ: {subj} — {t_in} ({cat})\n\n1. Soru:"
            f" `{t_in}` klasik sınav sorusu.\n2. Soru: Eleyici zor seviye soru."
        )
        st.markdown(
            f"<div class='study-card'><pre"
            f" style='color:#f8fafc; white-space:pre-wrap;'>{paket}</pre></div>",
            unsafe_allow_html=True,
        )
        st.session_state.last_material = paket

  with tabs[5]:
    st.markdown("### 📄 Çalışma Kağıtları & PDF İndirme Merkezi")
    mat = st.session_state.get(
        "last_material", "Henüz içerik üretilmedi."
    )
    st.markdown(
        f"<div class='study-card'><pre"
        f" style='color:#38bdf8; white-space:pre-wrap;'>{mat}</pre></div>",
        unsafe_allow_html=True,
    )
    st.download_button(
        label="📥 Çalışma Kağıdını İndir (.txt / PDF)",
        data=mat,
        file_name=f"EduCore_{subj}_CalismaKagidi.txt",
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
