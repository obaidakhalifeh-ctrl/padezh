import pymorphy3
import spacy

morph = pymorphy3.MorphAnalyzer()
nlp = spacy.load("ru_core_news_sm")

# ---------- القواميس ----------
CASES = {
    "nomn": "именительный", "gent": "родительный", "datv": "дательный",
    "accs": "винительный", "ablt": "творительный", "loct": "предложный",
}
CASE_NORM = {"gen2": "gent", "acc2": "accs", "loc2": "loct"}
# ترميز spaCy للحالات
SPACY_CASE = {"Nom": "nomn", "Gen": "gent", "Dat": "datv",
              "Acc": "accs", "Ins": "ablt", "Loc": "loct"}

GENDERS = {"masc": "مذكر", "femn": "مؤنث", "neut": "محايد"}
NUMBERS = {"sing": "مفرد", "plur": "جمع"}
TENSES = {"past": "ماضي", "pres": "مضارع", "futr": "مستقبل"}
ASPECTS = {"perf": "كامل", "impf": "ناقص"}
POS_AR = {
    "NOUN": "اسم", "VERB": "فعل", "INFN": "فعل (مصدر)", "ADJF": "صفة",
    "ADJS": "صفة قصيرة", "PREP": "حرف جر", "NPRO": "ضمير",
    "ADVB": "ظرف", "CONJ": "حرف عطف", "PRCL": "أداة", "NUMR": "عدد",
    "PRED": "كلمة حالة (предикатив)", "PRTF": "اسم فاعل/مفعول (причастие)",
    "PRTS": "причастие قصير", "GRND": "ظرف فعلي (деепричастие)",
    "COMP": "صيغة تفضيل", "INTJ": "تعجب",
}

# مطابقة أنواع الكلمات بين spaCy و pymorphy3
POS_MAP = {
    "NOUN": {"NOUN"}, "PROPN": {"NOUN"},
    "VERB": {"VERB", "INFN", "PRTF", "PRTS", "GRND"},
    "AUX": {"VERB", "INFN"},
    "ADJ": {"ADJF", "ADJS", "PRTF"}, "DET": {"ADJF", "NPRO"},
    "PRON": {"NPRO"}, "ADP": {"PREP"},
    "ADV": {"ADVB", "COMP", "PRED"}, "NUM": {"NUMR", "NUMB"},
    "CCONJ": {"CONJ"}, "SCONJ": {"CONJ"}, "PART": {"PRCL"},
}

# ---------- القواعد ----------
PREP_CASES = {
    "у": {"gent"}, "из": {"gent"}, "без": {"gent"}, "для": {"gent"},
    "от": {"gent"}, "до": {"gent"}, "около": {"gent"},
    "к": {"datv"}, "по": {"datv"},
    "над": {"ablt"}, "перед": {"ablt"},
    "о": {"loct"}, "при": {"loct"},
    "в": {"accs", "loct"}, "на": {"accs", "loct"},
    "с": {"gent", "ablt", "accs"}, "за": {"accs", "ablt"},
}
TRIGGERS = {"нет": {"gent"}}


# ---------- الدوال ----------
def norm_case(p):
    c = p.tag.case
    c = CASE_NORM.get(c, c)
    return str(c) if c else None      # نص عادي، مش كائن pymorphy3


def spacy_case(token):
    vals = token.morph.get("Case")
    return SPACY_CASE.get(vals[0]) if vals else None


def candidates(token):
    """كل تحليلات pymorphy3 المتوافقة مع نوع الكلمة عند spaCy"""
    parses = morph.parse(token.text)
    ok = POS_MAP.get(token.pos_)
    cands = [p for p in parses if p.tag.POS in ok] if ok else parses
    return cands or parses


def get_prep(token):
    for child in token.children:
        if child.dep_ == "case" and child.pos_ == "ADP":
            return child.text.lower()
    return None


def choose_parse(token, prep):
    cands = candidates(token)
    sp = spacy_case(token)
    if sp:                                   # 1) حالة spaCy إن وافقت الصرف
        for p in cands:
            if norm_case(p) == sp:
                return p, cands
    if prep in PREP_CASES:                   # 2) احتياطي: قاعدة حرف الجر
        for p in cands:
            if norm_case(p) in PREP_CASES[prep]:
                return p, cands
    return cands[0], cands                   # 3) الأعلى احتمالاً


def explain(token, case_code, prep):
    head = token.head.text.lower()
    if prep and case_code in PREP_CASES.get(prep, set()):
        if prep in ("в", "на"):
            if case_code == "accs":
                return f"«{prep}» مع الاتجاه (حركة نحو مكان) بتطلب винительный"
            return f"«{prep}» مع المكان (سكون) بتطلب предложный"
        allowed = PREP_CASES[prep]
        if len(allowed) == 1:
            return f"حرف الجر «{prep}» بيطلب {CASES[case_code]}"
        return f"بعد حرف الجر «{prep}» (بياخد أكثر من حالة حسب المعنى)"
    dep = token.dep_
    if (not prep and head in TRIGGERS and case_code in TRIGGERS[head]
            and token.dep_ in ("nsubj", "obj", "obl")):
        return f"بعد «{head}»: النفي بياخد родительный"
    if dep == "obj" and case_code == "accs":
        return f"مفعول به مباشر للفعل «{head}»"
    if dep == "iobj" and case_code == "datv":
        return f"مفعول غير مباشر للفعل «{head}»"
    if dep == "nsubj" and case_code == "nomn":
        return "فاعل الجملة"
    if dep == "obl" and case_code == "ablt" and not prep:
        return "الأداة أو الوسيلة"
    if dep == "nmod" and case_code == "gent":
        return f"مضاف إليه: تابع للاسم «{head}»"
    if dep in ("amod", "det") and case_code:
        return f"بتتوافق مع «{head}» بالحالة والجنس والعدد"
    return "—"


def syncretism_note(parse, cands, case_code):
    """تنبيه لما شكل الكلمة بيصلح لأكثر من حالة"""
    possible = {norm_case(p) for p in cands}
    if case_code == "accs" and "gent" in possible and parse.tag.animacy == "anim":
        return "المذكر الحي (والجمع الحي): винительный بيشبه родительный بالشكل"
    if case_code == "accs" and "nomn" in possible:
        return "شكل هالكلمة نفس شكل именительный، والسياق هو اللي بحدد الحالة"
    if len(possible) > 2:
        return "شكل هالكلمة بيصلح لأكثر من حالة، والسياق بحدد"
    return "—"


def analyze_text(text):
    rows = []
    for token in nlp(text):
        if token.is_punct or token.is_space:
            rows.append({"word": token.text, "is_word": False})
            continue
        prep = get_prep(token)
        p, cands = choose_parse(token, prep)
        t = p.tag
        code = norm_case(p)
        pos = str(t.POS) if t.POS else None
        rows.append({
            "word": token.text,
            "is_word": True,
            "lemma": p.normal_form,
            "pos": POS_AR.get(pos, pos or "—"),
            "case_code": code,
            "case": CASES.get(code, "—"),
            "gender": GENDERS.get(t.gender, "—"),
            "number": NUMBERS.get(t.number, "—"),
            "tense": TENSES.get(t.tense, "—"),
            "aspect": ASPECTS.get(t.aspect, "—"),
            "reason": explain(token, code, prep) if code else "—",
            "note": syncretism_note(p, cands, code) if code else "—",
        })
    return rows