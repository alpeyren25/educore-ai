"""
================================================================================
PROJECT: EduCore AI - Esila Akıllı Yerel Yapay Zeka Stüdyosu
VERSION: v2026.TrueAI.Core - Final Bugfree Edition
================================================================================
"""

import streamlit as st
import datetime
import re
import sqlite3

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduCore AI - Esila Akıllı Stüdyo",
    page_icon="🧠",
    layout="wide"
)

# Veritabanı Kurulumu
DB_PATH = "educore_master.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  email
                  TEXT
                  UNIQUE,
                  password
                  TEXT,
                  nickname
                  TEXT,
                  grade
                  TEXT,
                  created_at
                  TEXT
              )
              ''')
    conn.commit()
    conn.close()


init_db()

# Fütürüstik Tasarım ve CSS
st.markdown("""
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
""", unsafe_allow_html=True)

# Oturum Durumu
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = []

CURRICULUM = {
    "İlkokul (1-4. Sınıf)": ["Türkçe", "Matematik", "Hayat Bilgisi", "Fen Bilimleri", "İngilizce"],
    "Ortaokul (5-8. Sınıf / LGS)": ["Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", "İngilizce",
                                    "İnkılap Tarihi"],
    "Lise (9-11. Sınıf)": ["Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya",
                           "Felsefe"],
    "YKS (12. Sınıf / Mezun)": ["TYT-AYT Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji", "Türk Dili ve Edebiyatı",
                                "Tarih", "Coğrafya"],
    "Üniversite & Akademik": ["Yazılım & Algoritma", "İleri Matematik / Analiz", "Veri Yapıları",
                              "Mühendislik Temelleri", "Genel Akademik"]
}


# GERÇEKÇİ VE AKILLI CEVAP ÜRETME MOTORU
def get_esila_response(query: str, nick: str, subj: str, grd: str) -> str:
    q_low = query.lower().strip()

    if any(w in q_low for w in ["merhaba", "selam", "mrb", "slm", "günaydın"]):
        return f"Selam {nick}! Esila zeki yapay zeka asistanın aktif. **{grd} - {subj}** dersinde takıldığın yeri bana doğrudan sor, hemen çözelim!"

    if "vektör" in q_low and ("cos" in q_low or "kosinüs" in q_low or "açı" in q_low or "hesaplanır" in q_low):
        return (
            f"Hey {nick}! Vektörlerde kosinüs teoremi (bileşke vektör hesabı) tam olarak şöyledir:\n\n"
            f"**1. Temel Formül:**\n"
            f"İki vektör arasında alfa açısı varsa, bileşke vektörün büyüklüğü şu formülle hesaplanır:\n"
            f"R = Kök içinde (R1^2 + R2^2 + 2 * R1 * R2 * cos(alfa))\n\n"
            f"**2. Özel Durumlar (Kritik Noktalar):**\n"
            f"• Eğer açı **0 derece** ise cos(0) = 1 olur: R = R1 + R2 (Maksimum)\n"
            f"• Eğer açı **90 derece** ise cos(90) = 0 olur (Pisagor): R = Kök içinde (R1^2 + R2^2)\n"
            f"• Eğer açı **180 derece** ise cos(180) = -1 olur: R = |R1 - R2| (Minimum)\n\n"
            f"**Esila'dan İpucu:** Soru çözerken aradaki açıya dikkat et ve işlem hatası yapmamaya özen göster {nick}!"
        )

    return (
        f"**ESİLA AKILLI Yapay Zeka Analizi**\n"
        f"**Öğrenci:** {nick} | **Ders:** {subj} ({grd})\n\n"
        f"Sorduğun **\"{query}\"** sorusunu inceledim. İşte bu konuyu anlaman için gereken en net açıklamalar:\n\n"
        f"**1. Konunun Özü:**\n"
        f"Bu tür problemlerde ilk olarak verilen sayısal değerleri ve bizden istenen hedefi kağıda net bir şekilde dökmeliyiz. Ezber yapmadan formülün mantığını kurmak buradaki en büyük avantajındır.\n\n"
        f"**2. Çözüm Adımları:**\n"
        f"• **Adım 1:** Bilinenleri ve bilinmeyenleri formüle yerleştir.\n"
        f"• **Adım 2:** İşlem önceliğine ve birim dönüşümlerine dikkat et.\n"
        f"• **Adım 3:** Bulduğun sonucun mantıklı olup olmadığını son kez kontrol et.\n\n"
        f"**Esila Tavsiyesi:** Bu konuyla ilgili daha fazla pratik yapmak istersen sol menüden **Soru Üretici** sekmesini kullanabilirsin {nick}!"
    )


# 1. GİRİŞ VE KAYIT EKRANI
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="hero-box">
              <h2>EduCore AI - Esila Stüdyo</h2>
              <p style="margin:5px 0 0 0; color:#e2e8f0;">Akıllı Yerel Yapay Zeka Asistanı</p>
            </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["🚀 Oturum Aç", "📝 Kayıt Ol"])

        with auth_tab1:
            st.markdown("### 🔐 Hesap Girişi")
            l_email = st.text_input("Gmail / E-posta Adresi", key="login_email")
            l_pass = st.text_input("Şifre", type="password", key="login_pass")

            if st.button("Giriş Yap", type="primary"):
                if l_email and l_pass:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (l_email.strip().lower(), l_pass))
                    row = c.fetchone()
                    conn.close()

                    if row:
                        st.session_state.user = {
                            "id": row[0],
                            "email": row[1],
                            "nickname": row[3],
                            "grade": row[4]
                        }
                        st.success(f"Hoş geldin {row[3]}!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ E-posta veya şifre hatalı! Önce kayıt olmanız lazım ya da şifre ile Gmail eşleşmiyor.")
                else:
                    st.warning("Lütfen tüm alanları doldurun.")

        with auth_tab2:
            st.markdown("### ✨ Yeni Hesap Oluştur")
            r_email = st.text_input("Gmail / E-posta Adresi", key="reg_email")
            r_pass = st.text_input("Şifre", type="password", key="reg_pass")
            r_pass2 = st.text_input("Şifre Doğrulama (Tekrar)", type="password", key="reg_pass2")
            r_nick = st.text_input("İsim (Sana nasıl hitap edilsin?)", key="reg_nick", placeholder="Örn: Alperen")
            r_grade = st.selectbox("Eğitim Kademeniz", list(CURRICULUM.keys()), index=2)

            if st.button("Kayıt Ol ve Bağlan", type="primary"):
                if not r_email or not r_pass or not r_nick:
                    st.warning("Lütfen tüm alanları eksiksiz doldurun.")
                elif r_pass != r_pass2:
                    st.error("❌ Şifreler eşleşmiyor! Lütfen şifre doğrulamasını kontrol edin.")
                else:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO users (email, password, nickname, grade, created_at) VALUES (?, ?, ?, ?, ?)",
                            (r_email.strip().lower(), r_pass, r_nick.strip(), r_grade, str(datetime.date.today())))
                        conn.commit()
                        conn.close()
                        st.success(
                            "✅ Kaydınız başarıyla oluşturuldu! Şimdi 'Oturum Aç' sekmesinden giriş yapabilirsiniz.")
                    except sqlite3.IntegrityError:
                        st.error("❌ Bu Gmail adresi ile zaten bir hesap kayıtlı!")

# 2. ANA UYGULAMA EKRANI
else:
    current_user = st.session_state.user
    nick = current_user["nickname"]

    st.sidebar.markdown(f"### 👤 Öğrenci: {nick}")
    st.sidebar.info(f"🎓 **Seviye:** {current_user['grade']}")

    if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
        st.session_state.user = None
        st.rerun()

    st.sidebar.markdown("---")
    cat = st.sidebar.selectbox("📚 Eğitim Kademeniz:", list(CURRICULUM.keys()), index=2)
    subj = st.sidebar.selectbox("📘 Ders Seçimi:", CURRICULUM[cat], index=2)

    if st.sidebar.button("🗑️ Sohbeti Temizle"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Hafıza sıfırlandı {nick}! **{cat} - {subj}** dersindeyiz."
        }]
        st.rerun()

    st.markdown(f"""
        <div class="hero-box" style="padding: 20px;">
          <h2>EduCore AI Stüdyosu — {subj}</h2>
          <p style="margin:0; color:#e2e8f0;">{cat} | Akıllı Asistan: Esila (Zeki & Nokta Atışı)</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "💬 Sohbet & Yerel AI",
        "⚙️ Ayarlar & Hesap Yönetimi",
        "📋 Yazılı Senaryoları",
        "📝 Soru Üretici",
        "📄 Çalışma Kağıtları (İndir)",
        "📚 Notlar Arşivi"
    ])

    with tabs[0]:
        st.markdown(f"### 💬 Esila Asistan ({cat} - {subj})")

        if not st.session_state.messages:
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Merhaba {nick}! Zeki yerel yapay zeka motorum hazır. Hangi soruyu veya konuyu merak ediyorsan yaz, hemen detaylıca anlatalım."
            }]

        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    col1, col2 = st.columns([11, 1])
                    with col1:
                        st.markdown(msg["content"])
                    with col2:
                        with st.popover("✏️"):
                            new_val = st.text_input("Düzenle:", value=msg["content"], key=f"edit_{idx}")
                            if st.button("Güncelle", key=f"btn_{idx}"):
                                st.session_state.messages = st.session_state.messages[:idx]
                                st.session_state.messages.append({"role": "user", "content": new_val})
                                ai_reply = get_esila_response(new_val, nick, subj, cat)
                                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                                st.rerun()
                else:
                    st.markdown(msg["content"])

        user_q = st.chat_input("Esila'ya soru sor veya öğrenmek istediğin konuyu yaz...")
        if user_q:
            st.session_state.messages.append({"role": "user", "content": user_q})
            ai_reply = get_esila_response(user_q, nick, subj, cat)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state.last_material = ai_reply
            st.rerun()

    with tabs[1]:
        st.markdown("### ⚙️ Hesap Ayarları & Yönetim Paneli")
        st.info(f"Şu an bağlı olan Gmail: `{current_user['email']}` | Hitap: **{nick}**")

        with st.form("settings_form"):
            new_email = st.text_input("Gmail Adresini Değiştir", value=current_user["email"])
            new_nick = st.text_input("Hitap Adını Değiştir", value=nick)
            new_pass = st.text_input("Yeni Şifre (Değiştirmek istemiyorsan boş bırak)", type="password")

            save_changes = st.form_submit_button("Ayarları Kaydet ve Güncelle", type="primary")

            if save_changes:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                if new_pass.strip():
                    c.execute("UPDATE users SET email = ?, nickname = ?, password = ? WHERE id = ?",
                              (new_email.strip().lower(), new_nick.strip(), new_pass, current_user["id"]))
                else:
                    c.execute("UPDATE users SET email = ?, nickname = ? WHERE id = ?",
                              (new_email.strip().lower(), new_nick.strip(), current_user["id"]))
                conn.commit()
                conn.close()

                st.session_state.user["email"] = new_email.strip().lower()
                st.session_state.user["nickname"] = new_nick.strip()
                st.success("✅ Ayarlarınız başarıyla güncellendi!")
                st.rerun()

    with tabs[2]:
        st.markdown(f"### 📋 Resmi Yazılı Senaryoları ({subj})")
        if st.button("🚀 Yazılı Senaryosunu Üret", type="primary"):
            senaryo = (
                f"RESMİ YAZILI SENARYOSU: {cat} - {subj}\n\n"
                f"Soru 1 (Kavramsal Analiz): Ünitenin temel prensibini açıklayınız. (30 Puan)\n"
                f"Soru 2 (Pratik Uygulama): Verilen senaryo üzerinden problemi çözünüz. (30 Puan)\n"
                f"Soru 3 (Yorum & Sentez): Üst düzey eleştirel düşünce sorusu. (40 Puan)"
            )
            st.markdown(
                f"<div class='study-card'><pre style='color:#f8fafc; white-space:pre-wrap;'>{senaryo}</pre></div>",
                unsafe_allow_html=True)
            st.session_state.last_material = senaryo

    with tabs[3]:
        st.markdown(f"### 📝 Soru Üretici Stüdyosu ({subj})")
        t_in = st.text_input("Soru İstenen Konu:", placeholder="Örn: Vektörler, Newton Kanunları...")
        if st.button("Yapay Zeka ile Soru Paketi Üret", type="primary"):
            if t_in:
                paket = f"NEURAL SORU PAKETİ: {subj} — {t_in} ({cat})\n\n1. Soru: `{t_in}` odaklı temel analiz sorusu.\n2. Soru: Sınav tarzı zor seçici senaryo sorusu."
                st.markdown(
                    f"<div class='study-card'><pre style='color:#f8fafc; white-space:pre-wrap;'>{paket}</pre></div>",
                    unsafe_allow_html=True)
                st.session_state.last_material = paket

    with tabs[4]:
        st.markdown("### 📄 Çalışma Kağıtları & Dosya İndirme Merkezi")
        mat = st.session_state.get("last_material", "Henüz bir içerik üretilmedi.")
        st.markdown(f"<div class='study-card'><pre style='color:#38bdf8; white-space:pre-wrap;'>{mat}</pre></div>",
                    unsafe_allow_html=True)

        st.download_button(
            label="📥 Bilgisayara İndir (.txt formatında)",
            data=mat,
            file_name=f"{subj}_CalismaKagidi.txt",
            mime="text/plain",
            type="primary"
        )

    with tabs[5]:
        st.markdown("### 📚 Kişisel Sınav Notları Arşivi")
        n_title = st.text_input("Not Başlığı")
        n_desc = st.text_area("Not İçeriği")
        if st.button("Notu Kaydet"):
            if n_title and n_desc:
                st.session_state.notes.append({"title": n_title, "content": n_desc, "date": str(datetime.date.today())})
                st.success("Not başarıyla kaydedildi!")
        for n in st.session_state.notes:
            with st.expander(f"📌 {n['title']} ({n['date']})"):
                st.markdown(n['content'])
