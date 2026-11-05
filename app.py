import html
import streamlit as st
from analyzer import analyze_text, CASES

st.set_page_config(page_title="Падеж", page_icon="🎨")

COLORS = {
    "nomn": ("#0072B2", "#FFFFFF"),
    "gent": ("#009E73", "#FFFFFF"),
    "datv": ("#E69F00", "#000000"),
    "accs": ("#D55E00", "#FFFFFF"),
    "ablt": ("#CC79A7", "#000000"),
    "loct": ("#56B4E9", "#000000"),
}

HINTS = {
    "nomn": "الفاعل، والصيغة الأساسية للاسم",
    "gent": "الإضافة، والنفي، وبعد حروف مثل у و из و без",
    "datv": "المفعول غير المباشر («لـ»)، وبعد к و по",
    "accs": "المفعول به المباشر، وبعد в و на مع الحركة",
    "ablt": "الأداة أو الوسيلة («بـ»)، وبعد с و над",
    "loct": "المكان بعد в و на مع السكون، وبعد о و при",
}


def sentence_html(rows, colored):
    parts = []
    for r in rows:
        w = html.escape(r["word"])
        if not r["is_word"]:
            parts.append(w)
            continue
        if parts:
            parts.append(" ")
        code = r["case_code"]
        if colored and code in COLORS:
            bg, fg = COLORS[code]
            parts.append(
                f'<span style="background:{bg};color:{fg};'
                f'padding:2px 8px;border-radius:6px;">{w}</span>'
            )
        else:
            parts.append(w)
    return (
        '<div dir="ltr" style="font-size:28px;line-height:2.4;">'
        + "".join(parts) + "</div>"
    )


def legend_html():
    chips = ""
    for code, (bg, fg) in COLORS.items():
        chips += (
            f'<span style="background:{bg};color:{fg};padding:4px 10px;'
            f'border-radius:6px;margin:4px;display:inline-block;">'
            f'{CASES[code]}</span>'
        )
    return f'<div dir="ltr">{chips}</div>'


def card_html(r):
    fields = [
        ("الأصل", "lemma"), ("النوع", "pos"), ("الحالة", "case"),
        ("الجنس", "gender"), ("العدد", "number"), ("الزمن", "tense"),
        ("كامل/ناقص", "aspect"), ("السبب", "reason"), ("ملاحظة", "note"),
    ]
    lines = ""
    for label, key in fields:
        if r.get(key, "—") != "—":
            lines += f"<p><b>{label}:</b> {html.escape(str(r[key]))}</p>"
    return (
        '<div dir="rtl" style="border:1px solid #888;border-radius:10px;'
        'padding:12px 18px;">'
        f'<h3 dir="ltr">{html.escape(r["word"])}</h3>{lines}</div>'
    )


# ---------- الصفحة ----------
st.title("🎨 Падеж")
st.caption("الصق جملة روسية وشوف حالة كل كلمة وليش")

text = st.text_area("الجملة الروسية", value="У меня нет времени.", height=100)
rows = analyze_text(text)
words = [r for r in rows if r["is_word"]]

tab1, tab2 = st.tabs(["🔍 تحليل", "✏️ اختبر نفسك"])

with tab1:
    colored = st.toggle("إظهار الألوان", value=True)
    st.markdown(sentence_html(rows, colored), unsafe_allow_html=True)
    if colored:
        st.markdown(legend_html(), unsafe_allow_html=True)
        with st.expander("شو يعني كل لون؟"):
            for code in COLORS:
                st.write(f"**{CASES[code]}**: {HINTS[code]}")
    if words:
        i = st.selectbox(
            "اختار كلمة لتشوف تفاصيلها",
            range(len(words)),
            format_func=lambda k: words[k]["word"],
        )
        st.markdown(card_html(words[i]), unsafe_allow_html=True)

with tab2:
    st.markdown(sentence_html(rows, False), unsafe_allow_html=True)
    quiz = [r for r in words if r["case_code"] in COLORS]
    if not quiz:
        st.info("ما في كلمات إلها حالة بهالجملة.")
    else:
        k = st.selectbox(
            "اختار كلمة",
            range(len(quiz)),
            format_func=lambda k: quiz[k]["word"],
        )
        guess = st.radio(
            "شو حالة هالكلمة؟",
            list(COLORS.keys()),
            format_func=lambda c: CASES[c],
            horizontal=True,
        )
        if st.button("تحقق"):
            r = quiz[k]
            if guess == r["case_code"]:
                st.success("صح ✅")
            else:
                st.error(f"مش صح. الحالة الصحيحة: {CASES[r['case_code']]}")
            if r["reason"] != "—":
                st.info(r["reason"])
            if r.get("note", "—") != "—":
                st.warning(r["note"])