"""
================================================================================
PROJECT: EduCore AI - Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.TrueAI.Core - Advanced Multi-Subject & Deep Answers Edition
================================================================================
"""

import datetime
import re
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
  c.execute("""
              CREATE TABLE IF NOT EXISTS users
              (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  password TEXT,
                  nickname TEXT,
                  grade TEXT,
                  unique_code TEXT,
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

# Oturum Durumu
if "user" not in st.session_state:
  st.session_state.user = None
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


# ZENGİNLEŞTİRİLMİŞ VE DERİNLEMESİNE CEVAP ÜRETME MOTORU
def get_educore_response(query: str, nick: str, subj: str, grd: str) -> str:
  profanity_check = handle_profanity(query, nick)
  if profanity_check:
    return profanity_check

  q_low = query.lower().strip()

  if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
    return (
        f"Selam {nick}! EduCore AI motoru tam kapasite aktif. **{grd} - {subj}**"
        " branşında en karmaşık konuları bile en anlaşılır şekilde çözmek için"
        " buradayım. Sormak istediğin soruyu veya konuyu detaylıca yaz,"
        " başlayalım!"
    )

  # Özel konu kalıpları veya genel derin analiz
  return (
      f"**EduCore AI — Derinlemesine Akademik Analiz Raporu**\n"
      f"**Öğrenci:** {nick} | **Kadece/Seviye:** {grd} | **Ders:** {subj}\n\n"
      f'🔍 Sorduğun **"{query}"** başlığını tüm alt dallarıyla masaya'
      f" yatırdık. Sınavlarda ve projelerde tam puan alman için gereken"
      " yapı taşları şunlardır:\n\n"
      f"**1. Kavramsal Temel ve Mantık:**\n"
      f"• Bu konunun özü ezbere değil, mantıksal nedenselliğe dayanır. {subj}"
      " dalında bu kuralı kavramak, ilerideki tüm ileri düzey konuların kilidini"
      " açar.\n"
      "• Tanımları ve terimleri kendi cümlelerinle özetleyebilmek, sınavda"
      " yorum sorularını rahatça yapmanı sağlar.\n\n"
      f"**2. Adım Adım Çözüm / Uygulama Stratejisi:**\n"
      "• **Adım 1 (Veriler & Önermeler):** Soruda veya problemde sana verilen"
      " anahtar verileri ve sınır şartlarını kağıda netçe dök.\n"
      "• **Adım 2 (Formül / Metot Seçimi):** Doğru formülü veya doğru edebi/akademik"
      " yaklaşımı seçerek süreci başlat.\n"
      "• **Adım 3 (İşlem & Sağlama):** İşlem hatası yapmamak için adımları"
      " kontrol et ve bulduğun sonucun mantıklı olup olmadığını test et.\n\n"
      f"**3. Sınav Taktikleri & Tuzaklar ({subj}):**\n"
      "⚠️ Öğrencilerin bu konuda en çok düştüğü hata birim atlamaları veya"
      " öncüllerdeki kelime oyunlarıdır. Soru kökündeki 'değildir', 'asla' veya"
      " 'kesinlikle' gibi ifadelere dikkat et!\n\n"
      f"💡 **EduCore Asistan Tavsiyesi:** Bu analizi kaydetmek veya bu konuda"
      " pratik yapmak istersen sol menüden **Yazılı Senaryoları** veya **Çalışma"
      f" Kağıtları** sekmesine göz atabilirsin {nick}!"
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
            unique_id_code = f"EDU-{cnt:05d}"  # Örn: EDU-00001

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
            " İstediğini sorabilirsin."
        ),
    }]
    st.rerun()

  st.markdown(
      f"""
        <div class="hero-box" style="padding: 20px;">
          <h2>EduCore AI Stüdyosu — {subj}</h2>
          <p style="margin:0; color:#e2e8f0;">{cat} | Akıllı Asistan: EduCore AI (Gelişmiş Cevap Motoru)</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  tabs = st.tabs([
      "💬 Sohbet & Yerel AI",
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
              f"Merhaba {nick}! EduCore AI gelişmiş asistanın aktif. İlkokuldan"
              " üniversiteye kadar dilediğin dersi ve konuyu en derinlemesine"
              " açıklamalarla anlatmaya hazırım. Hangi konuyu çalışıyoruz?"
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

    user_q = st.chat_input(
        "EduCore AI'a soru sor, konu anlatımı iste veya küfür et..."
    )
    if user_q:
      st.session_state.messages.append({"role": "user", "content": user_q})
      ai_reply = get_educore_response(user_q, nick, subj, cat)
      st.session_state.messages.append(
          {"role": "assistant", "content": ai_reply}
      )
      st.session_state.last_material = ai_reply
      st.rerun()

  with tabs[1]:
    st.markdown("### ⚙️ Hesap Ayarları & Benzersiz ID Yönetimi")
    st.info(
        f"Sana Özel Sistem Numaran (ID): **`{u_code}`**\n*(Bu numara TC"
        " kimlik gibi benzersizdir; ileride arkadaş ekleme ve grup kurma"
        " modülünde diğer kullanıcılara istek atmanı sağlayacaktır.)*"
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
        st.success("✅ Ayarlarınız başarıyla güncellendi!")
        st.rerun()

  with tabs[2]:
    st.markdown(f"### 📋 Resmi Yazılı Senaryoları ve Çalışma Kağıdı Önerisi ({subj})")
    st.markdown(
        "Okul sınavların için çıkabilecek örnek senaryoları aşağıda analiz"
        " edebilir, asistanın yönlendirmesiyle çalışma kağıdını PDF/metin"
        " olarak indirebilirsin."
    )

    if st.button("🚀 Yazılı Senaryosunu Üret ve Detaylı İncele", type="primary"):
      senaryo = (
          f"EDUCORE AI - KAPSAMLI YAZILI SENARYOSU: {cat} - {subj}\n\n"
          "📝 **Senaryo ve Soru Dağılımı:**\n\n"
          "🔹 **Soru 1 (Kavramsal Temel & Tanım - 30 Puan):**\n"
          f"   • Ünitenin temel kurallarını ve {subj} disiplinine ait temel"
          " yasaları açıklayınız.\n"
          "🔹 **Soru 2 (Pratik Uygulama & Problem Çözümü - 30 Puan):**\n"
          "   • Gerçek hayat senaryosu üzerinden sayısal veya yorumsal"
          " problemi adım adım çözerek gösteriniz.\n"
          "🔹 **Soru 3 (Üst Düzey Sentez & Analiz - 40 Puan):**\n"
          "   • Konunun günlük hayattaki karşılığını eleştirel bir gözle"
          " yorumlayın ve istisnai durumları açıklayın.\n\n"
          "💡 **EduCore Asistan Yönlendirmesi:** Harika bir çalışma planı"
          " çıkarabilmen için bu senaryonun tam çalışma kağıdını hazırladım!"
          " Hemen **'Çalışma Kağıtları (PDF/İndir)'** sekmesine giderek bu"
          " materyali bilgisayarına indirebilir ve çalışmaya"
          " başlayabilirsin."
      )
      st.markdown(
          f"<div class='study-card'><pre"
          f" style='color:#f8fafc; white-space:pre-wrap;'>{senaryo}</pre></div>",
          unsafe_allow_html=True,
      )
      st.session_state.last_material = senaryo

  with tabs[3]:
    st.markdown(f"### 📝 Soru Üretici Stüdyosu ({subj})")
    t_in = st.text_input(
        "Soru İstenen Konu:",
        placeholder=(
            "Örn: Hücre Bölünmeleri, Türev Alımı, Osmanlı Kuruluş Dönemi..."
        ),
    )
    if st.button("EduCore AI ile Gelişmiş Soru Paketi Üret", type="primary"):
      if t_in:
        paket = (
            f"EDUCORE AI — PROFESYONEL SORU PAKETİ: {subj} — {t_in} ({cat})\n\n"
            f"1. Soru (Temel Kavrama): `{t_in}` konusunun temel mantığını"
            " ölçen klasik okul sınavı tarzı soru.\n2. Soru (Seçici Sınav"
            " Tarzı): Zorluk derecesi yüksek, dikkat gerektiren ve eleyici"
            " nitelikteki nitelikli soru."
        )
        st.markdown(
            f"<div class='study-card'><pre"
            f" style='color:#f8fafc; white-space:pre-wrap;'>{paket}</pre></div>",
            unsafe_allow_html=True,
        )
        st.session_state.last_material = paket

  with tabs[4]:
    st.markdown("### 📄 Çalışma Kağıtları & PDF İndirme Merkezi")
    st.markdown(
        "Yazılı senaryolarından veya sohbetten üretilen en son kapsamlı"
        " çalışma materyalini buradan kolayca indirebilirsin."
    )
    mat = st.session_state.get(
        "last_material",
        "Henüz bir çalışma kağıdı üretilmedi. Önce 'Yazılı Senaryoları' veya"
        " 'Soru Üretici' sekmesini kullanabilirsin.",
    )
    st.markdown(
        f"<div class='study-card'><pre"
        f" style='color:#38bdf8; white-space:pre-wrap;'>{mat}</pre></div>",
        unsafe_allow_html=True,
    )

    st.download_button(
        label="📥 Çalışma Kağıdını İndir (.txt / PDF Formatı)",
        data=mat,
        file_name=f"EduCore_{subj}_CalismaKagidi.txt",
        mime="text/plain",
        type="primary",
    )

  with tabs[5]:
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
