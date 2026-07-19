#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка v9. Гейты ДО записи файлов: комплектность, дубли, запрещённое, интеграция."""
import json, re, os, difflib, sys

D = "/Users/ruslanalyev/.claude/skills/scenario-brain/sessions/konkurentnaya-razvedka"
OUT = "/private/tmp/claude-501/-Users-ruslanalyev-Documents-Projects/bb2ed12b-f22b-4f39-ad42-afcb28996a33/tasks/wo0pekdtr.output"

res = json.load(open(OUT, encoding="utf-8"))["result"]
by_n = {b["n"]: b for b in res["blocks"]}

# Блок 14 «И чего? — проектизация» имел статус OK — берём исходный, не трогали.
orig14 = open(f"{D}/.blocks/14.md", encoding="utf-8").read()
m = re.match(r'##\s*(.+?)\n\n(.*)', orig14, re.S)
b14 = {"n": 900, "title": m.group(1).strip(), "text": m.group(2).strip(),
       "key": "Ранжированная табличка гипотез и три верхние строки на понедельник — вот артефакт разведки.",
       "viz": "Ранжированная таблица гипотез, подсвечены три верхние строки.",
       "applied": ["статус OK — содержание не менялось",
                   "убрано вводное «Смотрите.» в начале (сквозное требование ревью ко всем блокам)"]}
b14["text"] = re.sub(r'^Смотрите\.\s*', '', b14["text"])

ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 101, 11, 12, 13, 900, 15]
by_n[900] = b14

blocks = []
for i, n in enumerate(ORDER, 1):
    if n not in by_n:
        sys.exit(f"СТОП: блок n={n} не вернулся")
    b = dict(by_n[n]); b["new_n"] = i
    blocks.append(b)

# ---------- ГЕЙТ 1: комплектность ----------
empty = [b["new_n"] for b in blocks if not b.get("text", "").strip()]
if empty: sys.exit(f"СТОП: пустые блоки {empty}")
print(f"ГЕЙТ 1 комплектность: ✅ {len(blocks)}/16 блоков, пустых нет")

# ---------- ГЕЙТ 2: дубли между блоками ----------
dup = []
for i in range(len(blocks)):
    for j in range(i+1, len(blocks)):
        r = difflib.SequenceMatcher(None, blocks[i]["text"], blocks[j]["text"]).ratio()
        if r > 0.35: dup.append(f"Б{blocks[i]['new_n']}~Б{blocks[j]['new_n']}: {r:.0%}")
print(f"ГЕЙТ 2 дубли: {'✅ нет' if not dup else '⚠️ ' + '; '.join(dup)}")

# ---------- ГЕЙТ 3: запрещённое ----------
full = "\n".join(b["text"] for b in blocks)
BAN = {
    r'\bКФУ\b': "запрещённый термин",
    r'\bВоробьёв': "нет в базе Дашкиева",
    r'\bSolid\b': "заказчик: не называть конкретную партнёрку",
    r'двести двадцать тысяч': "цифра Solid — убрать",
    r'двадцать один филиал': "галлюцинация summary.md",
    r'пять тысяч рублей': "выдуманная цена клиента",
    r'\bДима\b|\bДимы\b|Портнягин': "заказчик: убрать имя из блока «Прожить»",
    r'\b(?:ты|тебе|тебя|твой|твоя|твои)\b': "обращение на «ты»",
    r'в пятьдесят раз выше': "выдумка",
    r'(?:изучил\w*|обошл\w*|сходил\w*|посетил\w*|разобрал\w*)\s+(?:более\s+|свыше\s+)?(?:двести|двухсот|200)\s+компаний': "ОПРОВЕРГНУТО: это 200 процессов, не компаний",
}
bad = False
for pat, why in BAN.items():
    hits = re.findall(pat, full, re.I)
    if hits:
        bad = True
        print(f"ГЕЙТ 3: ⚠️  {pat} → {len(hits)}× ({why}) :: {set(hits)}")
if not bad: print("ГЕЙТ 3 запрещённое: ✅ чисто")

# ---------- ГЕЙТ 4: вводные зачины ----------
starts = []
for b in blocks:
    first = b["text"].strip().split("\n")[0]
    if re.match(r'^(Смотрите|Давайте|А теперь по делу|И вот что|И практическое|А устроено)', first):
        starts.append(f"Б{b['new_n']}: «{first[:40]}…»")
print(f"ГЕЙТ 4 вводные зачины: {'✅ нет' if not starts else '⚠️ ' + '; '.join(starts)}")

# ---------- ГЕЙТ 5: интеграция ровно одна ----------
ni = full.count("[ИНТЕГРАЦИЯ")
print(f"ГЕЙТ 5 интеграция: {'✅ ровно 1' if ni == 1 else f'⚠️ {ni} шт'}")

if bad or empty:
    sys.exit("\n❌ ГЕЙТЫ НЕ ПРОЙДЕНЫ — файлы не записаны")

# ---------- ЗАПИСЬ ----------
clean = "# Конкурентная разведка — суфлёр (чистая речь) v9\n\n"
for b in blocks:
    clean += f"## {b['title']}\n\n{b['text'].strip()}\n\n"
open(f"{D}/scenario-clean.md", "w", encoding="utf-8").write(clean)

fin = "# Конкурентная разведка — сценарий v9 (после ревью)\n\n"
fin += "_16 блоков. Тех-стек и оргструктура разделены по правке. Этика сжата до двух абзацев._\n\n---\n\n"
for b in blocks:
    fin += f"## Блок {b['new_n']}. {b['title']}\n\n{b['text'].strip()}\n\n"
    fin += f"**Ключевая мысль:** {b.get('key','')}\n\n**Виз:** {b.get('viz','')}\n\n---\n\n"
open(f"{D}/scenario-final.md", "w", encoding="utf-8").write(fin)

# лог правок
log = "# Что внесено по ревью (v8 → v9)\n\n"
for b in blocks:
    log += f"## Блок {b['new_n']}. {b['title']}\n" + "".join(f"- {a}\n" for a in b.get("applied", [])) + "\n"
open(f"{D}/applied-review-v9.md", "w", encoding="utf-8").write(log)

json.dump(blocks, open(f"{D}/.blocks/v9.json", "w"), ensure_ascii=False, indent=1)

speech = re.sub(r'\[[^\]]*\]', '', full)
w = len(speech.split())
print(f"\n{'='*58}\n✅ ЗАПИСАНО: scenario-clean.md · scenario-final.md · applied-review-v9.md")
print(f"Слов в речи: {w}  →  ~{w/150:.0f}–{w/135:.0f} мин")
print(f"{'='*58}")
for b in blocks:
    print(f"  {b['new_n']:2d}. {b['title'][:48]:50s} {len(b['text'].split()):4d}")
