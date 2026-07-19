#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Детерминированный скан: вытащить ВСЕ цифры и имена/бренды из суфлёра.
Цифры в сценарии прописью — ловим и словами, и знаками."""
import re, json, sys

SRC = "/Users/ruslanalyev/.claude/skills/scenario-brain/sessions/konkurentnaya-razvedka/scenario-clean.md"
txt = open(SRC, encoding="utf-8").read()

# --- разрезаем по блокам ---
blocks = []
parts = re.split(r'^#{1,3}\s*(?:БЛОК|Блок)\s*(\d+)[^\n]*$', txt, flags=re.M)
if len(parts) > 1:
    for i in range(1, len(parts), 2):
        blocks.append((int(parts[i]), parts[i+1]))
else:
    blocks = [(0, txt)]

NUMWORDS = (r'(?:нол|один|одна|одно|два|две|три|четыр|пят|шест|сем|восем|девят|десят|'
            r'одиннадцат|двенадцат|тринадцат|четырнадцат|пятнадцат|шестнадцат|семнадцат|'
            r'восемнадцат|девятнадцат|двадцат|тридцат|сорок|сорока|пятьдесят|пятидесят|шестьдесят|шестидесят|'
            r'семьдесят|семидесят|восемьдесят|восьмидесят|девяност|сто|ст[аоу]|двест|трист|четырест|'
            r'пятьсот|пятисот|шестьсот|шестисот|семьсот|восемьсот|девятьсот|'
            r'тысяч|миллион|миллиард|половин|треть|четверт)')

# контекст вокруг числа
UNIT = r'(?:процент\w*|руб\w*|₽|тысяч\w*|миллион\w*|миллиард\w*|раз\w*|лид\w*|клиент\w*|' \
       r'год\w*|лет|мес\w*|дн\w*|филиал\w*|город\w*|конверси\w*|чек\w*|операц\w*|заяв\w*)'

rows = []
for n, body in blocks:
    # предложения
    sents = re.split(r'(?<=[.!?])\s+', body)
    for s in sents:
        s_clean = s.strip()
        if not s_clean or s_clean.startswith(("**", "#", "-", "[")):
            continue
        has_digit = re.search(r'\d', s_clean)
        has_word = re.search(NUMWORDS, s_clean, re.I)
        if not (has_digit or has_word):
            continue
        # отсекаем ложные срабатывания: "один из", "одна из", "в один момент"
        if has_word and not has_digit:
            if not re.search(NUMWORDS + r'\w*\s+' + UNIT, s_clean, re.I) and \
               not re.search(r'\bв\s+' + NUMWORDS + r'\w*\s+раз', s_clean, re.I):
                continue
        rows.append({"block": n, "sentence": re.sub(r'\s+', ' ', s_clean)[:400]})

print(f"Найдено предложений с числами: {len(rows)}\n")
by_block = {}
for r in rows:
    by_block.setdefault(r["block"], []).append(r["sentence"])
for n in sorted(by_block):
    print(f"\n{'='*70}\nБЛОК {n} — {len(by_block[n])} шт.\n{'='*70}")
    for s in by_block[n]:
        print(f"  • {s}")

json.dump(rows, open("/private/tmp/claude-501/-Users-ruslanalyev-Documents-Projects/bb2ed12b-f22b-4f39-ad42-afcb28996a33/scratchpad/claims.json", "w"),
          ensure_ascii=False, indent=1)

# --- имена и бренды ---
print(f"\n\n{'='*70}\nИМЕНА / БРЕНДЫ (латиница + Капс)\n{'='*70}")
names = {}
for n, body in blocks:
    for m in re.finditer(r'\b[A-Z][A-Za-z\.\-]{2,}\b|\b[А-ЯЁ][а-яё]{2,}(?:\s+[А-ЯЁ][а-яё]{2,})?', body):
        w = m.group(0)
        names.setdefault(w, set()).add(n)
STOP = set("Это Но Если Вот Когда Потому Который Она Они Мы Вы Так Как Что Все Тот Там Здесь Тогда Даже Просто Может Надо Нужно Есть Была Было Были Один Одна Два Три Первый Второй Третий Наш Ваш Его Их Для При Про Над Под Без Через Перед После После Более Менее Самый Такой Такая Каждый Любой Другой Ещё Еще Уже Только Тоже Также Или Либо Ведь Хотя Пока Чтобы Затем Далее Итак Значит Например Кстати Именно Почти Сразу Снова Опять Вдруг Вместе Вместо Кроме Между Среди Около Против Ради Сквозь Вдоль Мимо".split())
for w in sorted(names):
    if w in STOP or len(w) < 3:
        continue
    print(f"  {w:35s} → блоки {sorted(names[w])}")
