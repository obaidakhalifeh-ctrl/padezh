"""يقيس دقة الأداة على مجموعة الاختبار الذهبية (gold_set.xlsx)."""
import sys
from collections import defaultdict, Counter
from openpyxl import load_workbook
from analyzer import analyze_text

CODE = {"nomn": "и.п", "gent": "р.п", "datv": "д.п",
        "accs": "в.п", "ablt": "т.п", "loct": "п.п"}


def load_gold(path):
    ws = load_workbook(path, data_only=True)["gold"]
    sents, gold = {}, defaultdict(dict)
    for row in ws.iter_rows(min_row=2, values_only=True):
        sid, tok, word, lemma, tool, g, src, prio, sentence = row[:9]
        if sid is None:
            continue
        sid, tok = int(sid), int(tok)            # إكسل أحياناً بيحفظ الأرقام كـ 1.0
        sents[sid] = sentence
        if g:                                   # بس الصفوف اللي إلها حالة صحيحة
            gold[sid][tok] = (word, str(g).strip())
    return sents, gold


def main(path="gold_set.xlsx"):
    sents, gold = load_gold(path)
    total = correct = 0
    per_case = defaultdict(lambda: [0, 0])      # [صح, كل]
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
    print("الدقة حسب الحالة الصحيحة:")
    for case, (ok, n) in sorted(per_case.items()):
        print(f"  {case}: {ok}/{n} = {100 * ok / n:.1f}%")
    print(f"\nالأخطاء ({len(errors)}):")
    for sid, word, g, pred, reason in errors:
        print(f"  جملة {sid}: {word} | الصحيح {g} | الأداة {pred} | {reason}")
    print("\nأكثر أنواع الأخطاء (الصحيح ← اللي طلع):")
    for (g, p), n in Counter((e[2], e[3]) for e in errors).most_common(8):
        print(f"  {g} ← {p}: {n}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "gold_set.xlsx")