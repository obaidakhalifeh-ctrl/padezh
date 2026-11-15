import os

import pymorphy3
import spacy

morph = pymorphy3.MorphAnalyzer()
MODEL = os.environ.get("PADEZH_MODEL", "ru_core_news_sm")
nlp = spacy.load(MODEL)

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
    # родительный
    "у": {"gent"}, "из": {"gent"}, "изо": {"gent"}, "из-за": {"gent"},
    "из-под": {"gent"}, "без": {"gent"}, "безо": {"gent"}, "для": {"gent"},
    "от": {"gent"}, "до": {"gent"}, "около": {"gent"}, "возле": {"gent"},
    "вокруг": {"gent"}, "после": {"gent"}, "вместо": {"gent"},
    "кроме": {"gent"}, "среди": {"gent"}, "против": {"gent"},
    "мимо": {"gent"}, "ради": {"gent"}, "внутри": {"gent"},
    "вдоль": {"gent"}, "посреди": {"gent"}, "вследствие": {"gent"},
    "насчёт": {"gent"}, "насчет": {"gent"},
    # дательный
    "к": {"datv"}, "ко": {"datv"}, "по": {"datv"}, "благодаря": {"datv"},
    "согласно": {"datv"}, "вопреки": {"datv"}, "навстречу": {"datv"},
    "подобно": {"datv"}, "вслед": {"datv"}, "наперекор": {"datv"},
    # творительный
    "над": {"ablt"}, "надо": {"ablt"}, "перед": {"ablt"},
    "передо": {"ablt"}, "между": {"ablt"},
    # предложный
    "о": {"loct"}, "об": {"loct"}, "обо": {"loct"}, "при": {"loct"},
    # винительный
    "через": {"accs"}, "сквозь": {"accs"}, "про": {"accs"},
    # أكثر من حالة حسب المعنى
    "в": {"accs", "loct"}, "во": {"accs", "loct"}, "на": {"accs", "loct"},
    "с": {"gent", "ablt", "accs"}, "со": {"gent", "ablt", "accs"},
    "за": {"accs", "ablt"}, "под": {"accs", "ablt"}, "подо": {"accs", "ablt"},
}
TRIGGERS = {"нет": {"gent"}}
# حروف جر ليها استعمالات إضافية بحالات ثانية، فما بنفرضها على spaCy
WEAK_PREPS = {"по", "о", "об", "обо"}
FIXED_POSSESSIVES = {"его", "её", "ее", "их"}   # ضمائر ملكية ثابتة بدون حالة

# أفعال بتطلب حالة معينة لمتممها المباشر (بدون حرف جر)
REKTION = {
    "gent": {"бояться", "испугаться", "пугаться", "избегать", "избежать",
             "достигать", "достичь", "добиваться", "добиться", "касаться",
             "коснуться", "лишаться", "лишиться", "требовать", "потребовать",
             "стесняться", "остерегаться", "опасаться", "сторониться",
             "придерживаться", "желать", "пожелать"},
    "datv": {"помогать", "помочь", "звонить", "позвонить", "советовать",
             "посоветовать", "мешать", "помешать", "доверять", "удивляться",
             "удивиться", "радоваться", "обрадоваться", "завидовать",
             "позавидовать", "принадлежать", "нравиться", "понравиться",
             "отвечать", "ответить", "верить", "поверить"},
    "ablt": {"пользоваться", "интересоваться", "заниматься", "увлекаться",
             "владеть", "руководить", "управлять", "гордиться", "любоваться",
             "наслаждаться", "обладать", "становиться", "стать", "казаться",
             "являться"},
}
VERB_CASE = {v: c for c, vs in REKTION.items() for v in vs}
REKTION_DEPS = ("obj", "iobj", "obl", "xcomp")

# ضمائر ملكية ثابتة: ما بتتصرف ولا إلها حالة (بتقابل الضمير المتصل بالعربية)
INVARIANT_POSS = {"его": "ـه", "её": "ـها", "ее": "ـها", "их": "ـهم"}


# ---------- الدوال ----------
def norm_case(p):
    c = p.tag.case
    c = CASE_NORM.get(c, c)
    return str(c) if c else None      # نص عادي، مش كائن pymorphy3


def spacy_case(token):
    vals = token.morph.get("Case")
    return SPACY_CASE.get(vals[0]) if vals else None


def is_fixed_possessive(token):
    """его/её/их لما بتوصف اسم بعدها (مش لما تكون ضمير شخصي)"""
    if token.text.lower() not in FIXED_POSSESSIVES:
        return False
    head = token.head
    if (head.i != token.i and head.pos_ in ("NOUN", "PROPN")
            and token.dep_ in ("det", "nmod", "amod")):
        return True
    # احتياطي: spaCy أحياناً بيغلط بالتصنيف، فبنشوف الكلمات اللي بعدها
    doc, i = token.doc, token.i
    nxt = doc[i + 1] if i + 1 < len(doc) else None
    nxt2 = doc[i + 2] if i + 2 < len(doc) else None
    if nxt is not None and nxt.pos_ in ("NOUN", "PROPN"):
        return True
    if (nxt is not None and nxt2 is not None
            and nxt.pos_ == "ADJ" and nxt2.pos_ in ("NOUN", "PROPN")):
        return True
    return False


def head_lemma(token):
    """أصل الفعل اللي الكلمة تابعة له (حتى لو spaCy غلط بتصنيف الفعل)"""
    head = token.head
    verbs = [p for p in morph.parse(head.text) if p.tag.POS in ("VERB", "INFN")]
    for p in verbs:                       # أولوية للأفعال اللي بجدول rection
        if p.normal_form in VERB_CASE:
            return p.normal_form
    if head.pos_ in ("VERB", "AUX") and verbs:
        return verbs[0].normal_form
    return None


def is_comparative_complement(token):
    """اسم أو ضمير بعد صيغة تفضيل بدون «чем»: родительный المقارنة (старше меня)"""
    head = token.head
    if head.i == token.i or head.pos_ not in ("ADJ", "ADV"):
        return False
    if token.pos_ not in ("NOUN", "PROPN", "PRON") or token.dep_ not in ("obj", "obl", "nmod"):
        return False
    if not any(p.tag.POS == "COMP" for p in morph.parse(head.text)):
        return False
    doc = token.doc
    near = [t.text.lower() for t in doc[max(0, token.i - 2):token.i]] + [c.text.lower() for c in head.children]
    return not any(w in ("чем", "нежели") for w in near)


def rektion_case(token):
    """الحالة اللي بيطلبها الفعل (أو صيغة التفضيل) لهالكلمة"""
    if get_prep(token):
        return None, None
    if token.dep_ in REKTION_DEPS:
        hl = head_lemma(token)
        case = VERB_CASE.get(hl)
        if case:
            return case, hl
    if is_comparative_complement(token):
        return "gent", "COMP"
    return None, None


PARTICLES_AFTER_HYPHEN = {"то", "нибудь", "либо", "таки", "ка"}


def force_no_case(token):
    """أجزاء كلمات مركبة وعبارات ثابتة ما إلها حالة"""
    doc, i = token.doc, token.i
    low = token.text.lower()
    if i > 0 and doc[i - 1].text == "-" and low in PARTICLES_AFTER_HYPHEN:
        return True                                   # какого-то، кто-нибудь
    if (i + 1 < len(doc) and doc[i + 1].text == "-"
            and not any(p.is_known for p in morph.parse(token.text))):
        nxt = doc[i + 2] if i + 2 < len(doc) else None
        proper = (token.text[:1].isupper() and nxt is not None
                  and nxt.text[:1].isupper())
        if not proper:                                # Санкт-Петербург: الاسمين مع بعض
            return True                               # финно-угорской، волжско-финского
    if low == "то" and [t.text.lower() for t in doc[i + 1:i + 3]] == ["и", "дело"]:
        return True                                   # то и дело
    if low == "дело" and [t.text.lower() for t in doc[max(0, i - 2):i]] == ["то", "и"]:
        return True
    return False


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
    # احتياطي: spaCy أحياناً بيغلط، فنشوف حرف الجر الملاصق قبل الاسم وصفاته
    if token.pos_ in ("NOUN", "PROPN", "PRON"):
        doc = token.doc
        j = token.i - 1
        while j >= 0 and ((doc[j].head.i == token.i
                           and doc[j].pos_ in ("ADJ", "DET", "NUM", "PRON"))
                          or doc[j].text == "-"
                          or (j + 1 < len(doc) and doc[j + 1].text == "-")):
            j -= 1
        if j >= 0 and doc[j].text.lower() in PREP_CASES:
            return doc[j].text.lower()
    return None


def choose_parse(token, prep):
    cands = candidates(token)
    exp, _ = rektion_case(token)
    if exp:                                  # 0) الفعل بيطلب حالة معينة
        for p in cands:
            if norm_case(p) == exp:
                return p, cands
    if (prep in PREP_CASES and len(PREP_CASES[prep]) == 1
            and prep not in WEAK_PREPS):     # 0.5) حرف جر بحالة وحيدة: بيتغلّب على spaCy
        for p in cands:
            if norm_case(p) in PREP_CASES[prep]:
                return p, cands
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


def explain_full(token, case_code, prep):
    """يرجع (نص السبب، نوع السبب، مفتاح) — النوع والمفتاح بيستعملهم شرح الواجهة"""
    head = token.head.text.lower()
    if prep and case_code in PREP_CASES.get(prep, set()):
        if prep in ("в", "во", "на"):
            if case_code == "accs":
                return (f"«{prep}» مع الاتجاه (حركة نحو مكان) يتطلب винительный", "prep", prep)
            return (f"«{prep}» مع المكان (سكون) يتطلب предложный", "prep", prep)
        allowed = PREP_CASES[prep]
        if len(allowed) == 1:
            return (f"حرف الجر «{prep}» يتطلب {CASES[case_code]}", "prep", prep)
        return (f"بعد حرف الجر «{prep}» (يأخذ أكثر من حالة بحسب المعنى)", "prep", prep)
    exp, hl = rektion_case(token)
    if exp and case_code == exp:
        if hl == "COMP":
            return (f"بعد صيغة التفضيل «{head}» (بدون чем): родительный المقارنة", "comparative", head)
        return (f"الفعل «{head}» ({hl}) يتطلب {CASES[exp]}", "rektion", hl)
    dep = token.dep_
    if (not prep and head in TRIGGERS and case_code in TRIGGERS[head]
            and token.dep_ in ("nsubj", "obj", "obl")):
        return (f"بعد «{head}»: النفي يتطلب родительный", "negation", head)
    if dep == "obj" and case_code == "accs":
        return (f"مفعول به مباشر للفعل «{head}»", "obj", head)
    if dep == "iobj" and case_code == "datv":
        return (f"مفعول غير مباشر للفعل «{head}»", "iobj", head)
    if dep == "nsubj" and case_code == "nomn":
        return ("فاعل الجملة", "nsubj", head)
    if dep == "obl" and case_code == "ablt" and not prep:
        return ("الأداة أو الوسيلة", "instrumental", head)
    if dep == "nmod" and case_code == "gent":
        return (f"مضاف إليه: تابع للاسم «{head}»", "genitive_attr", head)
    if dep in ("amod", "det") and case_code:
        return (f"تتوافق مع «{head}» في الحالة والجنس والعدد", "agreement", head)
    return ("—", "none", "")


def explain(token, case_code, prep):
    return explain_full(token, case_code, prep)[0]


def syncretism_full(parse, cands, case_code):
    """تنبيه لما شكل الكلمة بيصلح لأكثر من حالة: (النص، النوع)"""
    possible = {norm_case(p) for p in cands}
    if case_code == "accs" and "gent" in possible and parse.tag.animacy == "anim":
        return ("المذكر الحي (والجمع الحي): винительный يشبه родительный في الشكل", "anim_acc_gen")
    if case_code == "accs" and "nomn" in possible:
        return ("شكل هذه الكلمة مطابق لشكل именительный، والسياق هو الذي يحدد الحالة", "acc_nom")
    if len(possible) > 2:
        return ("شكل هذه الكلمة يصلح لأكثر من حالة، والسياق هو الذي يحدد", "multi")
    return ("—", "none")


def syncretism_note(parse, cands, case_code):
    return syncretism_full(parse, cands, case_code)[0]


def analyze_text(text):
    doc = nlp(text)

    # المرور الأول: اختيار تحليل لكل كلمة
    chosen = {}                       # فهرس الكلمة -> (التحليل، كل الاحتمالات)
    for token in doc:
        if token.is_punct or token.is_space:
            continue
        chosen[token.i] = choose_parse(token, get_prep(token))

    # المرور الثاني: الصفات والضمائر الملكية تتبع حالة الاسم اللي بتصفه
    for token in doc:
        if token.i not in chosen or token.dep_ not in ("amod", "det"):
            continue
        if is_fixed_possessive(token):
            continue
        head = token.head
        if head.i == token.i or head.i not in chosen:
            continue
        head_case = norm_case(chosen[head.i][0])
        if not head_case:
            continue
        p, cands = chosen[token.i]
        if norm_case(p) != head_case:
            for c in cands:           # بس إذا شكل الكلمة بيسمح بهالحالة
                if norm_case(c) == head_case:
                    chosen[token.i] = (c, cands)
                    break

    # المرور الثالث: بناء النتيجة
    rows = []
    for token in doc:
        if token.i not in chosen:
            rows.append({"word": token.text, "is_word": False})
            continue
        p, cands = chosen[token.i]
        if force_no_case(token):
            rows.append({
                "word": token.text, "is_word": True, "lemma": token.text.lower(),
                "pos": "جزء من كلمة مركبة أو عبارة ثابتة", "case_code": None,
                "case": "—", "gender": "—", "number": "—", "tense": "—",
                "aspect": "—", "reason": "—", "note": "—",
                "reason_kind": "none", "reason_key": "", "note_kind": "none",
                "head": token.head.text.lower(),
            })
            continue
        if is_fixed_possessive(token):
            rows.append({
                "word": token.text, "is_word": True, "lemma": p.normal_form,
                "pos": "ضمير ملكي ثابت", "case_code": None, "case": "—",
                "gender": "—", "number": "—", "tense": "—", "aspect": "—",
                "reason": "ضمير ملكي ثابت: لا يتغير بحسب الحالة، ويصف الاسم الذي بعده",
                "note": "—", "reason_kind": "possessive_fixed",
                "reason_key": token.text.lower(), "note_kind": "none",
                "head": token.head.text.lower(),
            })
            continue
        prep = get_prep(token)
        t = p.tag
        code = norm_case(p)
        pos = str(t.POS) if t.POS else None
        reason, rkind, rkey = explain_full(token, code, prep) if code else ("—", "none", "")
        note, nkind = syncretism_full(p, cands, code) if code else ("—", "none")
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
            "reason": reason,
            "note": note,
            "reason_kind": rkind,
            "reason_key": rkey,
            "note_kind": nkind,
            "head": token.head.text.lower(),
        })
    return rows