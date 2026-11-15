# -*- coding: utf-8 -*-
import hashlib
import html

import streamlit as st

from analyzer import analyze_text, CASES
from explanations import (CASE_ORDER, SHORT, RU, CASE_INFO, ENDINGS, POS_INFO,
                          GENDER_INFO, NUMBER_INFO, TENSE_INFO, ASPECT_INFO, deep_blocks)

st.set_page_config(page_title="Падеж | الحالات الروسية بالألوان", page_icon="🎨", layout="centered")

esc = html.escape
CONTACT = ""          # ضع هنا رابطاً أو بريداً لاستقبال الملاحظات (اختياري)
MAX_CHARS = 600

COLORS = {
    "nomn": ("#0072B2", "#FFFFFF"),
    "gent": ("#009E73", "#FFFFFF"),
    "datv": ("#E69F00", "#000000"),
    "accs": ("#D55E00", "#FFFFFF"),
    "ablt": ("#CC79A7", "#000000"),
    "loct": ("#56B4E9", "#000000"),
}

EXAMPLES = [
    "У меня нет времени.",
    "Я боюсь собак.",
    "Я помогаю брату и звоню маме.",
    "Мы с друзьями ездили на озеро.",
    "Я люблю друга и мать.",
    "Моя сестра живёт в большом доме вместе со своей семьёй.",
    "Он стал врачом и пользуется компьютером каждый день.",
    "Брат старше меня.",
]
PLACEHOLDER = "— اختر جملة جاهزة —"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Inter:wght@400;600;700&display=swap');
html, body, .stApp { font-family: 'Tajawal', 'Inter', sans-serif !important; }
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp textarea, .stApp input, .stApp button, .stApp [data-baseweb="tab"],
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"],
.stApp [data-baseweb="select"] div { font-family: 'Tajawal', 'Inter', sans-serif; }
.stApp {
  background:
    radial-gradient(900px 480px at 8% -8%, #e7efff 0%, rgba(231,239,255,0) 60%),
    radial-gradient(800px 460px at 100% 0%, #ffeede 0%, rgba(255,238,222,0) 55%),
    #fbfaf7;
  direction: rtl;
}
.block-container { max-width: 920px; padding-top: 1.6rem; padding-bottom: 4rem; }
.stApp textarea { direction: ltr; text-align: left; font-size: 1.15rem; }
.stApp h1, .stApp h2, .stApp h3 { letter-spacing: 0; }

.hero { text-align: center; padding: 26px 18px 18px; margin-bottom: 14px; border-radius: 22px;
  background: linear-gradient(135deg, rgba(48,84,150,.95), rgba(40,60,110,.95));
  color: #fff; box-shadow: 0 14px 40px rgba(30,50,100,.25); position: relative; overflow: hidden; }
.hero-title { font-size: 46px; font-weight: 800; line-height: 1.2; direction: ltr; }
.hero-title span { display: block; font-size: 22px; font-weight: 500; opacity: .92; direction: rtl; margin-top: 4px; }
.hero-sub { font-size: 17px; opacity: .92; margin-top: 8px; }
.strip { display: flex; height: 6px; border-radius: 6px; overflow: hidden; margin: 16px auto 0; max-width: 360px; }
.strip i { flex: 1; display: block; }

.card { background: rgba(255,255,255,.88); border: 1px solid rgba(48,84,150,.10); border-radius: 18px;
  padding: 16px 20px; box-shadow: 0 8px 26px rgba(30,50,100,.08); margin: 10px 0 14px; }
.sent { direction: ltr; text-align: left; font-size: 30px; line-height: 2.8; }
.w { position: relative; display: inline-block; padding: 1px 11px; margin: 0 2px; border-radius: 11px;
  cursor: default; transition: transform .12s, box-shadow .12s; box-shadow: 0 2px 6px rgba(0,0,0,.10); }
.w:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,.18); }
.w.plain { box-shadow: none; background: transparent; color: #1F2A44; padding: 1px 5px; }
.w.plain:hover { background: rgba(48,84,150,.08); transform: none; }

.tip { visibility: hidden; opacity: 0; position: absolute; top: calc(100% + 6px); left: 50%;
  transform: translateX(-50%); width: 270px; background: #1f2a44; color: #fff; padding: 10px 13px;
  border-radius: 12px; font-size: 14px; font-weight: 500; line-height: 1.75; direction: rtl; text-align: right;
  z-index: 999; transition: opacity .15s; box-shadow: 0 12px 28px rgba(0,0,0,.30); white-space: normal; }
.tip b { color: #ffd479; }
.w:hover .tip, .badge:hover .tip, .w:focus .tip { visibility: visible; opacity: 1; }
.w.first .tip { left: 0; transform: none; }
.w.last .tip { left: auto; right: 0; transform: none; }
.legend .badge .tip, .badges .badge .tip { left: auto; right: 0; transform: none; }
.legend .badge:last-child .tip { right: auto; left: 0; }

.legend { direction: rtl; display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.badge { position: relative; display: inline-block; padding: 4px 13px; border-radius: 999px; font-size: 15px;
  font-weight: 700; cursor: help; box-shadow: 0 2px 6px rgba(0,0,0,.12); }
.badge.soft { background: #eef3fb; color: #1F2A44; box-shadow: none; border: 1px solid rgba(48,84,150,.15); font-weight: 500; }
.badge .ru { direction: ltr; unicode-bidi: embed; }
.hint { color: #5a6784; font-size: 14px; margin-top: 8px; }

.wcard { background: #fff; border-radius: 18px; padding: 18px 22px; margin: 8px 0 12px;
  border: 1px solid rgba(48,84,150,.12); box-shadow: 0 10px 30px rgba(30,50,100,.10); }
.wcard-head { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.wcard-word { font-size: 38px; font-weight: 800; direction: ltr; color: #1F2A44; }
.wcard-lemma { color: #5a6784; font-size: 16px; }
.badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 12px; }
.reason { background: #f1f6ff; border-right: 5px solid #305496; border-radius: 12px; padding: 12px 16px;
  font-size: 18px; line-height: 1.8; }
.reason small { display: block; color: #5a6784; font-size: 13px; margin-bottom: 2px; }
.note { background: #fff6e5; border-right: 5px solid #E69F00; border-radius: 12px; padding: 10px 16px;
  margin-top: 10px; font-size: 16px; line-height: 1.8; }
.blk { background: #fbfcff; border: 1px solid rgba(48,84,150,.12); border-radius: 14px; padding: 12px 16px; margin: 10px 0; }
.blk-t { font-weight: 800; color: #305496; margin-bottom: 4px; font-size: 17px; }
.blk ul { margin: 6px 0 8px; padding-right: 22px; }
.ex { direction: ltr; unicode-bidi: embed; font-weight: 700; }
.tbl { width: 100%; border-collapse: collapse; direction: ltr; font-size: 16px; margin-top: 8px; }
.tbl th { background: #305496; color: #fff; padding: 7px 8px; text-align: center; }
.tbl td { padding: 7px 8px; text-align: center; border-bottom: 1px solid #e3e9f5; }
.tbl tr:nth-child(even) td { background: #f5f8fe; }
.tbl td.lbl { text-align: right; direction: rtl; font-weight: 700; }
.stTabs [data-baseweb="tab"] { font-size: 17px; font-weight: 700; }
.foot { text-align: center; color: #7b86a0; font-size: 13px; margin-top: 30px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

strip = "".join(f'<i style="background:{COLORS[c][0]}"></i>' for c in CASE_ORDER)
st.markdown(
    f'<div class="hero"><div class="hero-title">Падеж<span>حالات الأسماء الروسية بالألوان</span></div>'
    f'<div class="hero-sub">الصق جملة روسية، وشاهد حالة كل كلمة، واعرف السبب بالعربية خطوة بخطوة.</div>'
    f'<div class="strip">{strip}</div></div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- مساعدات العرض
def case_tip(code):
    ci = CASE_INFO[code]
    ex = ci["examples"][0]
    return (f'<span class="tip"><b>{esc(RU[code])}</b> ({SHORT[code]}) — {esc(ci["ar"])}<br>'
            f'{esc(ci["summary"])}<br><b>الأسئلة:</b> <span class="ex">{esc(ci["q"])}</span><br>'
            f'<b>مثال:</b> <span class="ex">{esc(ex[0])}</span> — {esc(ex[1])}</span>')


def word_tip(r):
    code = r.get("case_code")
    if code in COLORS:
        t = f'<b>{esc(RU[code])}</b> ({SHORT[code]})'
        if r.get("reason", "—") != "—":
            t += f'<br>{esc(r["reason"])}'
        if r.get("note", "—") != "—":
            t += f'<br>🧩 {esc(r["note"])}'
        return f'<span class="tip">{t}</span>'
    pos = r.get("pos", "—")
    t = f'<b>{esc(pos)}</b><br>' + esc(POS_INFO.get(pos, "كلمة ليس لها حالة هنا."))
    if r.get("reason", "—") != "—":
        t += f'<br>{esc(r["reason"])}'
    return f'<span class="tip">{t}</span>'


def sentence_html(rows, colored):
    word_idx = [i for i, r in enumerate(rows) if r["is_word"]]
    first, last = (word_idx[0], word_idx[-1]) if word_idx else (-1, -1)
    parts = []
    for i, r in enumerate(rows):
        w = esc(r["word"])
        if not r["is_word"]:
            parts.append(w)
            continue
        if parts:
            parts.append(" ")
        code = r.get("case_code")
        pos_cls = (" first" if i == first else "") + (" last" if i == last else "")
        if colored and code in COLORS:
            bg, fg = COLORS[code]
            parts.append(f'<span class="w{pos_cls}" style="background:{bg};color:{fg}">{w}{word_tip(r)}</span>')
        elif colored:
            parts.append(f'<span class="w plain{pos_cls}">{w}{word_tip(r)}</span>')
        else:
            parts.append(f'<span class="w plain{pos_cls}">{w}</span>')
    return f'<div class="card"><div class="sent">{"".join(parts)}</div></div>'


def legend_html():
    chips = ""
    for i, code in enumerate(CASE_ORDER):
        bg, fg = COLORS[code]
        chips += (f'<span class="badge" style="background:{bg};color:{fg}">'
                  f'<span class="ru">{esc(RU[code])}</span>{case_tip(code)}</span>')
    return f'<div class="legend">{chips}</div><div class="hint">مرّر المؤشر فوق أي لون أو كلمة ليظهر الشرح.</div>'


def soft_badge(text, tip):
    return f'<span class="badge soft">{esc(text)}<span class="tip">{esc(tip)}</span></span>'


def card_html(r):
    code = r.get("case_code")
    badges = ""
    if code in COLORS:
        bg, fg = COLORS[code]
        badges += (f'<span class="badge" style="background:{bg};color:{fg}">'
                   f'<span class="ru">{esc(RU[code])}</span> ({SHORT[code]}){case_tip(code)}</span>')
    pos = r.get("pos", "—")
    if pos != "—":
        badges += soft_badge(pos, POS_INFO.get(pos, ""))
    for key, table in (("gender", GENDER_INFO), ("number", NUMBER_INFO),
                       ("tense", TENSE_INFO), ("aspect", ASPECT_INFO)):
        v = r.get(key, "—")
        if v != "—":
            badges += soft_badge(v, table.get(v, ""))
    reason = ""
    if r.get("reason", "—") != "—":
        reason = f'<div class="reason"><small>لماذا هذه الحالة؟</small>{esc(r["reason"])}</div>'
    elif code not in COLORS:
        reason = '<div class="reason"><small>ملاحظة</small>هذه الكلمة ليس لها حالة هنا (فعل أو ظرف أو حرف أو ضمير ملكي ثابت...).</div>'
    note = ""
    if r.get("note", "—") != "—":
        note = f'<div class="note">🧩 {esc(r["note"])}</div>'
    lemma = f'<span class="wcard-lemma">الأصل: <span class="ex">{esc(r["lemma"])}</span></span>' if r.get("lemma") else ""
    return (f'<div class="wcard"><div class="wcard-head"><span class="wcard-word">{esc(r["word"])}</span>{lemma}</div>'
            f'<div class="badges">{badges}</div>{reason}{note}</div>')


def blocks_html(r):
    out = ""
    for icon, title, text in deep_blocks(r):
        out += f'<div class="blk"><div class="blk-t">{icon} {esc(title)}</div><div>{text}</div></div>'
    return out


def pick_word(rows, key, label):
    n = len(rows)
    if n == 0:
        return None
    if hasattr(st, "pills"):
        sel = st.pills(label, list(range(n)), format_func=lambda k: rows[k]["word"],
                       selection_mode="single", default=0, key=key)
        return rows[sel if sel is not None else 0]
    k = st.selectbox(label, list(range(n)), format_func=lambda k: rows[k]["word"], key=key)
    return rows[k]


@st.cache_data(show_spinner=False)
def run_analysis(t):
    return analyze_text(t)


def endings_table():
    head = "".join(f"<th>{SHORT[c]}</th>" for c in CASE_ORDER)
    rows = ""
    for name, desc, forms in ENDINGS:
        cells = "".join(f"<td>{esc(f)}</td>" for f in forms)
        rows += f'<tr><td class="lbl">{esc(name)} ({esc(desc)})</td>{cells}</tr>'
    return f'<table class="tbl"><tr><th>النموذج</th>{head}</tr>{rows}</table>'


# ---------------------------------------------------------------- الإدخال
if "text" not in st.session_state:
    st.session_state["text"] = EXAMPLES[0]


def _use_example():
    v = st.session_state.get("ex_pick")
    if v and v != PLACEHOLDER:
        st.session_state["text"] = v


st.text_area("اكتب أو الصق جملة روسية", key="text", height=100)
st.selectbox("أو اختر جملة جاهزة", [PLACEHOLDER] + EXAMPLES, key="ex_pick", on_change=_use_example)

text = st.session_state["text"]
if len(text) > MAX_CHARS:
    st.warning(f"النص طويل؛ سيتم تحليل أول {MAX_CHARS} حرفاً فقط.")
    text = text[:MAX_CHARS]
rows = run_analysis(text) if text.strip() else []
words = [r for r in rows if r["is_word"]]
tkey = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]

tab1, tab2, tab3, tab4 = st.tabs(["🔍 التحليل", "✏️ اختبر نفسك", "📚 دليل الحالات", "ℹ️ عن المشروع"])

# ---------------------------------------------------------------- التحليل
with tab1:
    if not words:
        st.info("اكتب جملة روسية في المربع أعلاه لتظهر النتيجة.")
    else:
        colored = st.toggle("إظهار الألوان", value=True)
        st.markdown(sentence_html(rows, colored), unsafe_allow_html=True)
        if colored:
            st.markdown(legend_html(), unsafe_allow_html=True)
        st.markdown("#### تفاصيل كلمة")
        r = pick_word(words, f"pick_{tkey}", "اختر كلمة لتظهر بطاقتها")
        st.markdown(card_html(r), unsafe_allow_html=True)
        with st.expander("🔎 اشرح لي أكثر", expanded=r.get("case_code") in COLORS):
            st.markdown(blocks_html(r), unsafe_allow_html=True)

# ---------------------------------------------------------------- اختبر نفسك
with tab2:
    st.markdown(sentence_html(rows, False), unsafe_allow_html=True)
    quiz = [w for w in words if w.get("case_code") in COLORS]
    if not quiz:
        st.info("لا توجد كلمات لها حالة في هذه الجملة.")
    else:
        st.caption("اختر كلمة، وخمّن حالتها، ثم اضغط «تحقق». (التحليل آلي وقد يخطئ أحياناً.)")
        r = pick_word(quiz, f"quiz_{tkey}", "اختر كلمة")
        guess = st.radio("ما حالة هذه الكلمة؟", CASE_ORDER,
                         format_func=lambda c: f"{RU[c]} ({SHORT[c]})", horizontal=True, key=f"guess_{tkey}")
        if st.button("تحقق", key=f"check_{tkey}"):
            if guess == r["case_code"]:
                st.success("إجابة صحيحة ✅")
            else:
                st.error(f"ليست صحيحة. الحالة الصحيحة: {RU[r['case_code']]} ({SHORT[r['case_code']]})")
            if r.get("reason", "—") != "—":
                st.info(r["reason"])
            if r.get("note", "—") != "—":
                st.warning(r["note"])
            with st.expander("🔎 اشرح لي أكثر", expanded=False):
                st.markdown(blocks_html(r), unsafe_allow_html=True)

# ---------------------------------------------------------------- دليل الحالات
with tab3:
    st.markdown("الروسية فيها **ست حالات**، وتتغير نهاية الاسم والصفة والضمير بحسب الحالة. "
                "هذا ملخص لكل حالة (والمقارنة مع العربية **تقريبية** وليست تطابقاً). مرّر المؤشر على الألوان لتذكّرها:")
    st.markdown(legend_html(), unsafe_allow_html=True)
    for code in CASE_ORDER:
        ci = CASE_INFO[code]
        bg, fg = COLORS[code]
        with st.expander(f"{RU[code]} ({SHORT[code]}) — {ci['ar']}  |  {ci['q']}"):
            uses = "".join(
                f'<li>{esc(u[0])}: <span class="ex">{esc(u[1])}</span> — {esc(u[2])}</li>' for u in ci["uses"])
            ex = "".join(f'<li><span class="ex">{esc(a)}</span> — {esc(b)}</li>' for a, b in ci["examples"])
            st.markdown(
                f'<div class="blk"><div class="blk-t" style="color:{bg}">الخلاصة</div>{esc(ci["summary"])}</div>'
                f'<div class="blk"><div class="blk-t">متى تُستعمل؟</div><ul>{uses}</ul></div>'
                f'<div class="blk"><div class="blk-t">مقارنة تقريبية مع العربية</div>{esc(ci["arabic"])}</div>'
                f'<div class="blk"><div class="blk-t">أمثلة</div><ul>{ex}</ul></div>',
                unsafe_allow_html=True)
    st.markdown("#### جدول نهايات نماذج")
    st.markdown(endings_table(), unsafe_allow_html=True)
    st.caption("لاحظ الأشكال المتطابقة: винительный = именительный في «стол» و«окно» و«тетрадь» و«мать»، "
               "وвинительный = родительный في «брат» (المذكر الحي).")

# ---------------------------------------------------------------- عن المشروع
with tab4:
    st.markdown("""
**Падеж** أداة تعليمية لتحليل الجمل الروسية وشرح حالات الأسماء بالعربية، موجّهة للمتعلمين الناطقين بالعربية.

**كيف تعمل؟** تجمع بين محلل صرفي (pymorphy3) ومحلل لبنية الجملة (spaCy)، ثم تطبّق قواعد لغوية مكتوبة يدوياً
(حروف الجر، الأفعال التي تطلب حالة معينة، النفي، التوافق، المقارنة...) لتشرح **سبب** الحالة وليس فقط اسمها.

**نقطة مهمة:** التحليل آلي وقد يخطئ، خصوصاً في الجمل الطويلة أو الأدبية المعقدة أو التي تتغير فيها الرتبة.
اختُبرت الأداة على مجموعات جمل مُرمَّزة يدوياً (نتائج أولية: نحو 98%-99% على الجمل التعليمية والنصوص الحقيقية
المستخدمة في التطوير)، فلا تعتمد عليها وحدها في الامتحانات، وراجع معلّمك عند الشك.
""")
    if CONTACT:
        st.markdown(f"**للملاحظات والأخطاء:** {CONTACT}")
    st.markdown('<div class="foot">صُمّم بواسطة  عبيده خليفه · نسخة تجريبية</div>', unsafe_allow_html=True)