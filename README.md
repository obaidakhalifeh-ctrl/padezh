# Падеж

أداة تعليمية تحلّل الجمل الروسية وتشرح الحالات الإعرابية الروسية (падежи) باللغة العربية
للمتعلمين الناطقين بالعربية.

*An educational tool that analyzes Russian sentences and explains cases in Arabic, for Arabic-speaking learners of Russian.*

## ما تفعله الأداة
- تلوّن كل كلمة حسب حالتها النحوية
- تشرح سبب الحالة بالعربية (حرف جر، مفعول به، نفي...)
- تنبّه إلى التطابق الشكلي بين الحالات (مثل المذكر الحي)
- وضع «اختبر نفسك» للتدريب

## التشغيل
pip install -r requirements.txt
python -m spacy download ru_core_news_sm
streamlit run app.py

## التقييم
تحتوي المجموعة الذهبية `gold_set.xlsx` على 100 جملة (512 كلمة) مرمّزة يدوياً.
شغّل `python evaluate.py` لقياس دقة الأداة.

## الحالة
نسخة تجريبية قيد التطوير.