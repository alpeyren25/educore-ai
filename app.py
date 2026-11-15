
import os
import re
import hmac
import time
import sqlite3
import hashlib
import secrets
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone

import streamlit as st

# ============================================================
# MYRIADWALL AI
# Independent local knowledge and defensive security prototype
# ============================================================

APP_NAME = "MYRIADWALL AI"
VERSION = "0.1.0"
DB_PATH = os.getenv("MYRIADWALL_DB", "myriadwall.db")

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- DATABASE -------------------------------

@contextmanager
def database():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize_database():
    with database() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)


initialize_database()


def now():
    return datetime.now(timezone.utc).isoformat()


# -------------------- AUTHENTICATION -------------------------

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000
    ).hex()


def register_user(username, password):
    username = username.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        return False, "Kullanıcı adı 3-30 karakter olmalı."

    if len(password) < 12:
        return False, "Şifre en az 12 karakter olmalı."

    salt = secrets.token_hex(16)
    hashed = password_hash(password, salt)

    try:
        with database() as db:
            db.execute(
                """INSERT INTO users
                (username,password_hash,salt,created_at)
                VALUES(?,?,?,?)""",
                (username, hashed, salt, now())
            )
        return True, "Hesap oluşturuldu."
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten kullanılıyor."


def authenticate(username, password):
    with database() as db:
        user = db.execute(
            "SELECT * FROM users WHERE username=?",
            (username.strip().lower(),)
        ).fetchone()

    if user is None:
        return None

    candidate = password_hash(password, user["salt"])

    if hmac.compare_digest(candidate, user["password_hash"]):
        return dict(user)

    return None


# -------------------- AI KNOWLEDGE ENGINE -------------------

WORD_PATTERN = re.compile(
    r"[a-zA-Z0-9_çğıöşüÇĞİÖŞÜ-]{2,}",
    re.UNICODE
)


def tokenize(text):
    return [
        word.casefold()
        for word in WORD_PATTERN.findall(text)
    ]


def analyze_knowledge(question, documents):
    query_words = Counter(tokenize(question))

    if not query_words:
        return {
            "answer": "Sorunu biraz daha açık ifade et.",
            "confidence": 0,
            "sources": []
        }

    scored = []

    for doc in documents:
        content = doc["title"] + " " + doc["content"]
        document_words = Counter(tokenize(content))

        matches = sum(
            min(count, document_words.get(word, 0))
            for word, count in query_words.items()
        )

        score = matches / max(1, sum(query_words.values()))

        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)

    if not scored or scored[0][0] < 0.12:
        return {
            "answer": (
                "Bu konuda bilgi tabanımda yeterli bilgi bulamadım. "
                "Bilgi deposuna yeni bilgiler ekleyebilirsin."
            ),
            "confidence": 0,
            "sources": []
        }

    selected = scored[:3]

    answer_parts = []
    sources = []

    for score, doc in selected:
        excerpt = doc["content"][:1000]

        answer_parts.append(
            f"### {doc['title']}\n{excerpt}"
        )

        sources.append({
            "title": doc["title"],
            "score": round(score, 3)
        })

    return {
        "answer": "\n\n".join(answer_parts),
        "confidence": round(selected[0][0], 3),
        "sources": sources
    }


def get_documents(user_id):
    with database() as db:
        rows = db.execute(
            """SELECT id,title,content
            FROM knowledge WHERE user_id=?
            ORDER BY id DESC""",
            (user_id,)
        ).fetchall()

    return [dict(row) for row in rows]


def save_knowledge(user_id, title, content):
    with database() as db:
        db.execute(
            """INSERT INTO knowledge
            (user_id,title,content,created_at)
            VALUES(?,?,?,?)""",
            (user_id, title.strip(), content.strip(), now())
        )


# -------------------- SECURITY ENGINE -----------------------

SEVERITY = {
    "Düşük": 1,
    "Orta": 2,
    "Yüksek": 3,
    "Kritik": 4
}


def analyze_security_event(category, severity, description):
    score = SEVERITY.get(severity, 1) * 25

    recommendations = [
        "Olayı güvenilir sistem günlüklerinden doğrula.",
        "İlgili kullanıcı ve sistem kayıtlarını incele.",
        "Yetkili yöneticiye olay hakkında bilgi ver."
    ]

    if severity in ("Yüksek", "Kritik"):
        recommendations.insert(
            0,
            "Öncelikli güvenlik incelemesi gerçekleştir."
        )

    if "giriş" in category.lower():
        recommendations.append(
            "Kimlik doğrulama kayıtlarını incele."
        )

    return {
        "score": score,
        "recommendations": recommendations,
        "automatic_block": False
    }


def save_event(user_id, category, severity, description):
    with database() as db:
        db.execute(
            """INSERT INTO events
            (user_id,category,severity,description,created_at)
            VALUES(?,?,?,?,?)""",
            (user_id, category, severity, description, now())
        )


def get_events(user_id):
    with database() as db:
        rows = db.execute(
            """SELECT * FROM events
            WHERE user_id=?
            ORDER BY id DESC LIMIT 200""",
            (user_id,)
        ).fetchall()

    return [dict(row) for row in rows]


# -------------------- UI STYLE ------------------------------

st.markdown("""
<style>
.stApp {
    background: #090d16;
    color: #e8edf7;
}
[data-testid="stSidebar"] {
    background: #101827;
}
div[data-testid="stMetric"] {
    background: #141f30;
    border: 1px solid #26364d;
    padding: 16px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #dce8ff;
}
.stButton button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# -------------------- LOGIN SCREEN ---------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:

    st.title("🛡️ MYRIADWALL AI")
    st.caption("Independent AI & Defensive Security Platform")

    login_tab, register_tab = st.tabs(
        ["Giriş Yap", "Hesap Oluştur"]
    )

    with login_tab:
        username = st.text_input("Kullanıcı adı")
        password = st.text_input(
            "Şifre",
            type="password",
            key="login_password"
        )

        if st.button("Giriş Yap", use_container_width=True):
            user = authenticate(username, password)

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")

    with register_tab:
        new_username = st.text_input(
            "Yeni kullanıcı adı",
            key="new_username"
        )

        new_password = st.text_input(
            "Yeni şifre (en az 12 karakter)",
            type="password"
        )

        confirm_password = st.text_input(
            "Şifreyi tekrar gir",
            type="password"
        )

        if st.button(
            "Hesap Oluştur",
            use_container_width=True
        ):
            if new_password != confirm_password:
                st.error("Şifreler eşleşmiyor.")
            else:
                success, message = register_user(
                    new_username,
                    new_password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.stop()


# -------------------- MAIN APPLICATION -----------------------

user = st.session_state.user

st.sidebar.title("🛡️ MYRIADWALL")
st.sidebar.caption("AI SECURITY PLATFORM")
st.sidebar.divider()

page = st.sidebar.radio(
    "Yönetim",
    [
        "Genel Bakış",
        "AI Asistanı",
        "Bilgi Deposu",
        "Güvenlik Merkezi",
        "Güvenlik Katmanları",
        "Hesap"
    ]
)

st.sidebar.divider()
st.sidebar.write(f"👤 {user['username']}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.user = None
    st.rerun()


# -------------------- DASHBOARD ------------------------------

if page == "Genel Bakış":

    st.title("MYRIADWALL AI")
    st.caption("Akıllı savunma ve yerel bilgi platformu")

    documents = get_documents(user["id"])
    events = get_events(user["id"])

    critical = sum(
        1 for event in events
        if event["severity"] == "Kritik"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("AI Motoru", "Aktif")
    col2.metric("Bilgi Kaydı", len(documents))
    col3.metric("Güvenlik Olayı", len(events))
    col4.metric("Kritik Olay", critical)

    st.divider()

    st.subheader("Sistem Durumu")

    status_data = {
        "AI Knowledge Engine": "Çalışıyor",
        "Security Analysis": "Çalışıyor",
        "Database": "Çalışıyor",
        "External AI API": "Kullanılmıyor",
        "Network Firewall": "Bağlı değil"
    }

    for name, status in status_data.items():
        st.write(f"**{name}:** {status}")

    st.info(
        "Bu sürüm yerel bilgi tabanı ve kaydedilmiş olaylar "
        "üzerinde çalışır. Gerçek zamanlı ağ izleme yapmaz."
    )


# -------------------- AI ASSISTANT ---------------------------

elif page == "AI Asistanı":

    st.title("🤖 MyriadWall AI Asistanı")

    st.write(
        "Yerel bilgi tabanındaki kaynaklardan cevap bul."
    )

    question = st.text_area(
        "Sorunu yaz",
        placeholder="Örneğin: Güçlü şifre nasıl oluşturulur?"
    )

    if st.button("Soruyu Analiz Et"):
        if question.strip():
            result = analyze_knowledge(
                question,
                get_documents(user["id"])
            )

            st.subheader("AI Yanıtı")
            st.markdown(result["answer"])

            st.metric(
                "Eşleşme Güveni",
                f"%{result['confidence'] * 100:.1f}"
            )

            if result["sources"]:
                st.subheader("Kaynaklar")
                for source in result["sources"]:
                    st.write(
                        f"- {source['title']} "
                        f"({source['score']})"
                    )

            st.caption(
                "Bu sürüm bir bilgi erişim motorudur; "
                "eğitilmiş büyük dil modeli değildir."
            )
        else:
            st.warning("Önce bir soru yaz.")


# -------------------- KNOWLEDGE BASE -------------------------

elif page == "Bilgi Deposu":

    st.title("📚 Bilgi Deposu")

    with st.form("knowledge_form"):
        title = st.text_input("Bilgi başlığı")
        content = st.text_area(
            "Bilgi içeriği",
            height=200
        )

        submitted = st.form_submit_button(
            "Bilgiyi Kaydet"
        )

        if submitted:
            if len(title.strip()) < 2:
                st.error("Başlık çok kısa.")
            elif len(content.strip()) < 10:
                st.error("İçerik en az 10 karakter olmalı.")
            else:
                save_knowledge(
                    user["id"],
                    title,
                    content
                )
                st.success("Bilgi kaydedildi.")
                st.rerun()

    st.divider()
    st.subheader("Kayıtlı Bilgiler")

    for doc in get_documents(user["id"]):
        with st.expander(doc["title"]):
            st.write(doc["content"])


# -------------------- SECURITY CENTER ------------------------

elif page == "Güvenlik Merkezi":

    st.title("🔐 Güvenlik Merkezi")

    st.write(
        "Güvenlik olaylarını kaydet ve yerel analiz motoruyla değerlendir."
    )

    with st.form("event_form"):

        category = st.selectbox(
            "Olay kategorisi",
            [
                "Şüpheli giriş",
                "Kimlik doğrulama",
                "Uygulama hatası",
                "Yetkisiz erişim bildirimi",
                "Diğer"
            ]
        )

        severity = st.selectbox(
            "Önem seviyesi",
            ["Düşük", "Orta", "Yüksek", "Kritik"]
        )

        description = st.text_area(
            "Olay açıklaması"
        )

        submitted = st.form_submit_button(
            "Olayı Analiz Et ve Kaydet"
        )

        if submitted:
            if len(description.strip()) < 5:
                st.error("Daha ayrıntılı bir açıklama gir.")
            else:
                result = analyze_security_event(
                    category,
                    severity,
                    description
                )

                save_event(
                    user["id"],
                    category,
                    severity,
                    description
                )

                st.success("Olay kaydedildi.")

                st.metric(
                    "Risk Puanı",
                    f"{result['score']}/100"
                )

                for recommendation in result["recommendations"]:
                    st.write(f"• {recommendation}")

                st.rerun()

    st.divider()
    st.subheader("Son Güvenlik Olayları")

    for event in get_events(user["id"]):
        with st.expander(
            f"{event['severity']} — {event['category']} — #{event['id']}"
        ):
            st.write(event["description"])
            st.caption(event["created_at"])


# -------------------- DEFENSE LAYERS -------------------------

elif page == "Güvenlik Katmanları":

    st.title("🧱 MyriadWall Savunma Mimarisi")

    layers = [
        ("01", "Kimlik Kontrolü", "Hesap ve kimlik doğrulama"),
        ("02", "Girdi Doğrulama", "Kullanıcı girdilerinin kontrolü"),
        ("03", "Yetki Kontrolü", "Kullanıcı erişim sınırları"),
        ("04", "Veri Güvenliği", "Veri bütünlüğü ve erişim"),
        ("05", "Olay Kaydı", "Güvenlik kayıtları"),
        ("06", "Risk Analizi", "Olay önem derecelendirmesi"),
        ("07", "Bilgi Koruması", "Bilgi tabanı erişim kontrolü"),
        ("08", "Oturum Yönetimi", "Oturum kontrolü"),
        ("09", "Hata Yönetimi", "Hata ve istisna yönetimi"),
        ("10", "Raporlama", "Güvenlik raporları")
    ]

    for number, name, description in layers:
        with st.container(border=True):
            st.markdown(f"### {number} — {name}")
            st.caption(description)

    st.warning(
        "Bunlar uygulamadaki mantıksal güvenlik kontrolleridir. "
        "10 ayrı ağ güvenlik duvarı veya 10 aktif trafik filtresi değildir."
    )


# -------------------- ACCOUNT --------------------------------

elif page == "Hesap":

    st.title("👤 Hesap Bilgileri")

    st.write("Kullanıcı:", user["username"])
    st.write("Hesap ID:", user["id"])
    st.write("Sürüm:", VERSION)

    st.info(
        "Bu ilk sürümde yönetici yetkisi ve normal kullanıcı "
        "yetkisi ayrımı henüz uygulanmamıştır."
    )


# -------------------- FOOTER ---------------------------------

st.sidebar.divider()
st.sidebar.caption(f"{APP_NAME} v{VERSION}")
st.sidebar.caption("Independent Development Project")
