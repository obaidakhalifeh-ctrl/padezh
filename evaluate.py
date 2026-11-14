"""يقيس دقة الأداة على مجموعة اختبار (ملف xlsx).

الاستعمال:
  python evaluate.py                          # يقرأ gold_set.xlsx
  python evaluate.py blind_set.xlsx --blanks  # الخلية الفاضية = «بدون حالة»
"""
import sys
from collections import defaultdict, Counter
from openpyxl import load_workbook
from analyzer import analyze_text

CODE = {"nomn": "и.п", "gent": "р.п", "datv": "д.п",
        "accs": "в.п", "ablt": "т.п", "loct": "п.п"}


def find_col(header, prefix):
    for i, h in enumerate(header):
        if h and str(h).startswith(prefix):
            return i
    raise SystemExit(f"ما لقيت العمود: {prefix}")


def load_gold(path, blanks):
    ws = load_workbook(path, data_only=True)["gold"]
    rows = list(ws.iter_rows(values_only=True))
    h = rows[0]
    c_sid, c_tok = find_col(h, "رقم الجملة"), find_col(h, "رقم الرمز")
    c_word, c_gold = find_col(h, "الكلمة"), find_col(h, "الحالة الصحيحة")
    c_sent = find_col(h, "الجملة")
    sents, gold = {}, defaultdict(dict)
    for row in rows[1:]:
        if row[c_sid] is None:
            continue
        sid, tok = int(row[c_sid]), int(row[c_tok])   # إكسل أحياناً بيحفظ 1.0
        sents[sid] = row[c_sent]
        g = row[c_gold]
        if g:
            gold[sid][tok] = (row[c_word], str(g).strip())
        elif blanks:                                  # فاضي = بدون حالة
            gold[sid][tok] = (row[c_word], "—")
    return sents, gold


def main(path, blanks):
    sents, gold = load_gold(path, blanks)
    total = correct = 0
    per_case = defaultdict(lambda: [0, 0])
    errors = []
    for sid in sorted(gold):
        rows = analyze_text(sents[sid])
        for tok, (word, g) in gold[sid].items():
            r = rows[tok]
            if r["word"] != word:
                print(f"تحذير: عدم تطابق بالجملة {sid}: {word} ≠ {r['word']}")
                continue
            pred = CODE.get(r.get("case_code"), "—")
            total += 1
            per_case[g][1] += 1
            if pred == g:
                correct += 1
                per_case[g][0] += 1
            else:
                errors.append((sid, word, g, pred, r.get("reason", "—")))
    print(f"\nالدقة الكلية: {correct}/{total} = {100 * correct / total:.1f}%\n")
    print("الدقة حسب الحالة الصحيحة (— = بدون حالة):")
    for case, (ok, n) in sorted(per_case.items()):
        print(f"  {case}: {ok}/{n} = {100 * ok / n:.1f}%")
    print(f"\nالأخطاء ({len(errors)}):")
    for sid, word, g, pred, reason in errors:
        print(f"  جملة {sid}: {word} | الصحيح {g} | الأداة {pred} | {reason}")
    print("\nأكثر أنواع الأخطاء (الصحيح ← اللي طلع):")
    for (g, p), n in Counter((e[2], e[3]) for e in errors).most_common(8):
        print(f"  {g} ← {p}: {n}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "gold_set.xlsx", "--blanks" in sys.argv)