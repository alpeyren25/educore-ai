                            if st.form_submit_button("Sınavı bitir"):
                                if any(x is None for x in answers): st.error("Tüm soruları cevapla.")
                                else:
                                    score=sum(1 for i,x in enumerate(answers) if x==qs[i]["opts"][qs[i]["a"]])
                                    with db() as c: c.execute("INSERT OR IGNORE INTO exam_attempts(exam_id,student_id,answers_json,score,total,submitted) VALUES(?,?,?,?,?,?)",(ex["id"],me["id"],json.dumps(answers,ensure_ascii=False),score,len(qs),now()))
                                    award_xp(me["id"],25,"Sınav tamamlama"); st.success(f"Sonuç: {score}/{len(qs)}"); st.rerun()
        if st.button("Sınıf alanını kapat"):
            st.session_state.pop("active_classroom",None); st.rerun()


def page_question_bank(me):
    hero("📚 Soru Bankası", "Öğretmenler soru ekler; öğrenciler kendilerini test eder.")
    if me.get("role")=="teacher" or me["is_admin"]:
        with st.form("add_question",clear_on_submit=True):
            subject=st.selectbox("Ders",SUBJECTS); question=st.text_area("Soru",max_chars=1000)
            opts=[st.text_input(f"{letter} seçeneği",key=f"qb{letter}",max_chars=300) for letter in "ABCD"]
            correct=st.selectbox("Doğru cevap",list("ABCD")); explanation=st.text_area("Açıklama (isteğe bağlı)",max_chars=1000)
            if st.form_submit_button("Soruyu ekle"):
                if not question.strip() or any(not x.strip() for x in opts): st.error("Soru ve dört seçenek gerekli.")
                else:
                    with db() as c: c.execute("INSERT INTO question_bank(teacher_id,subject,question,options_json,answer_index,explanation,created) VALUES(?,?,?,?,?,?,?)",(me["id"],subject,question.strip(),json.dumps(opts,ensure_ascii=False),"ABCD".index(correct),explanation.strip(),now()))
                    st.success("Soru eklendi."); st.rerun()
    with db() as c: rows=c.execute("SELECT * FROM question_bank ORDER BY id DESC LIMIT 100").fetchall()
    if not rows: st.info("Henüz soru eklenmemiş."); return
    subjects=sorted({r["subject"] for r in rows}); selected=st.selectbox("Ders filtresi",["Tümü"]+subjects)
    rows=[r for r in rows if selected=="Tümü" or r["subject"]==selected]
    if "qb_index" not in st.session_state: st.session_state["qb_index"]=0
    idx=st.session_state["qb_index"]%len(rows); q=rows[idx]; options=json.loads(q["options_json"])
    st.caption(f"Soru {idx+1}/{len(rows)} · {q['subject']}"); st.markdown("### "+q["question"])
    choice=st.radio("Cevabın",list(range(4)),format_func=lambda i:f"{chr(65+i)}. {options[i]}",key=f"qbank_{q['id']}")
    if st.button("Cevabı kontrol et"):
        if choice==q["answer_index"]: st.success("Doğru cevap!"); award_xp(me["id"],5,"Soru bankası doğru cevap")
        else: st.error(f"Doğru cevap: {chr(65+q['answer_index'])}. {options[q['answer_index']]}")
        if q["explanation"]: st.info(q["explanation"])
    if st.button("Sonraki soru"):
        st.session_state["qb_index"]=(idx+1)%len(rows); st.rerun()


def page_progress(me):
    hero("🏆 Başarı ve İlerleme", "XP kazan, seviyeni yükselt ve rozetlerini gör.")
    xp=user_xp(me["id"]); level=xp//100+1; current=xp%100
    a,b,c=st.columns(3); a.metric("Toplam XP",xp); b.metric("Seviye",level); c.metric("Sonraki seviye",f"{100-current} XP")
    st.progress(current/100)
    refresh_badges(me["id"])
    with db() as c: badges=c.execute("SELECT badge_key,earned FROM user_badges WHERE user_id=? ORDER BY earned",(me["id"],)).fetchall()
    st.subheader("Rozetler")
    if not badges: st.caption("Henüz rozet yok. Çalışma kaydı ve tekrar kartları oluşturarak başlayabilirsin.")
    for b in badges:
        title,desc=BADGES.get(b["badge_key"],(b["badge_key"],"")); st.success(f"🏅 **{title}** — {desc}")
    with db() as c: events=c.execute("SELECT amount,reason,created FROM xp_events WHERE user_id=? ORDER BY id DESC LIMIT 20",(me["id"],)).fetchall()
    st.subheader("Son XP hareketleri")
    if events: st.dataframe([dict(x) for x in events],use_container_width=True,hide_index=True)


def page_teacher_admin(me):
    hero("🧑‍🏫 Öğretmen yetkileri", "Yönetici öğretmen hesaplarını buradan yetkilendirir.")
    if not me["is_admin"]:
        st.error("Bu alan sadece yöneticilere açık."); return
    with db() as c: users=c.execute("SELECT id,username,edu_id,role FROM users WHERE is_admin=0 ORDER BY username").fetchall()
    if not users: st.info("Kayıtlı kullanıcı yok."); return
    pick=st.selectbox("Kullanıcı",users,format_func=lambda u:f"{u['username']} · {u['edu_id']} · {u['role']}")
    role=st.selectbox("Rol",["student","teacher"],index=0 if pick["role"]=="student" else 1,format_func=lambda x:"Öğrenci" if x=="student" else "Öğretmen")
    if st.button("Rolü güncelle",type="primary"):
        with db() as c: c.execute("UPDATE users SET role=? WHERE id=? AND is_admin=0",(role,pick["id"]))
        audit(me["username"],"Kullanıcı Rolü Güncellendi",pick["username"]+":"+role,0); st.success("Rol güncellendi."); st.rerun()
    st.caption("Güvenlik için yeni kayıtlar varsayılan olarak öğrenci olur. Öğretmen rolünü yalnızca yönetici verir.")


def page_ai_plus(me):
    page_ai(me)
    st.divider(); st.subheader("📎 Fotoğraf veya PDF'den soru aktar")
    st.caption("Dosyalar bu uygulama içinde işlenir. OCR için Tesseract, PDF metni için pypdf kurulmalıdır.")
    uploaded=st.file_uploader("Soru görseli veya PDF seç",type=["png","jpg","jpeg","webp","pdf"],key="ai_upload")
    if uploaded:
        text_out=""
        try:
            if uploaded.type=="application/pdf":
                from pypdf import PdfReader
                reader=PdfReader(uploaded); text_out="\n".join((p.extract_text() or "") for p in reader.pages[:10])[:12000]
            else:
                from PIL import Image
                import pytesseract
                img=Image.open(uploaded).convert("RGB")
                text_out=pytesseract.image_to_string(img,lang="tur+eng")[:12000]
        except ImportError:
            st.error("Gerekli paket eksik. PDF için `pip install pypdf`; görsel OCR için `pip install pillow pytesseract` ve bilgisayara Tesseract kurulumu gerekir.")
        except Exception as e: st.error(f"Dosya okunamadı: {e}")
        if text_out:
            st.text_area("Dosyadan çıkarılan metin — kontrol edip Esila'ya gönderebilirsin",text_out,height=180,key="ocr_result")
            if st.button("Bu metni Esila'ya gönder"):
                ans=esila_answer("Lise","Diğer","Resmi",text_out,[])
                with db() as c: c.executemany("INSERT INTO ai_history(user_id,role,content,ts) VALUES(?,?,?,?)",[(me["id"],"user",text_out,now()),(me["id"],"assistant",ans,now())])
                st.success("Metin Esila sohbetine eklendi. Esila AI sayfasını aç.")


# ───────────────────────── ANA AKIŞ ─────────────────────────
def main():
    init_db()
    daily_backup(today())
    st.markdown(CSS, unsafe_allow_html=True)
    me=current_user()
    if not me:
        page_auth(); return
    # Rolü her istekte DB'den okunan kullanıcı kaydından alıyoruz.
    pages={
        "home":("🏠 Ana Sayfa",page_home),
        "ai":("🧠 Esila AI",page_ai_plus),
        "cards":(f"🃏 Kartlar ({due_count(me['id'])})",page_cards),
        "study":("📈 Çalışma Takibi",page_study),
        "academy":("🎓 Sınıflarım",page_academy),
        "questions":("📚 Soru Bankası",page_question_bank),
        "progress":("🏆 Başarılarım",page_progress),
        "friends":(f"👥 Arkadaşlar ({pending_count(me['id'])})",page_friends),
        "groups":("📚 Çalışma Odaları",page_groups),
        "dm":(f"💬 DM ({unread_count(me['id'])})",page_dm),
        "security":("🔐 Güvenlik",page_security),
    }
    if me["is_admin"]:
        pages["teacher_admin"]=("🧑‍🏫 Öğretmen yetkileri",page_teacher_admin)
        pages["audit"]=("📊 Denetim Paneli",page_audit)
    st.sidebar.title("🛡️ EduCore-AI")
    st.sidebar.caption(f"👤 {me['username']} · {me['edu_id']} · {'Yönetici' if me['is_admin'] else ('Öğretmen' if me.get('role')=='teacher' else 'Öğrenci')}")
    key=st.sidebar.radio("Menü",list(pages),format_func=lambda k:pages[k][0],label_visibility="collapsed")
    if st.sidebar.button("Çıkış",use_container_width=True): logout("Çıkış yapıldı."); st.rerun()
    pages[key][1](me)


main()
