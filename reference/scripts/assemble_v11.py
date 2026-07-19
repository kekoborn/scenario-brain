#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка v11 из .blocks-v11/NN.md. Гейты ДО записи файлов.
Запуск: python3 assemble_v11.py [--write]   (без --write — только гейты, файлы не трогает)
"""
import re, os, sys, difflib

D = "/Users/ruslanalyev/.claude/skills/scenario-brain/sessions/konkurentnaya-razvedka"
SRC = os.path.join(D, ".blocks-v11")
NBLOCKS = 16
WRITE = "--write" in sys.argv

# ---------- чтение ----------
blocks = []
missing = []
for n in range(1, NBLOCKS + 1):
    p = os.path.join(SRC, f"{n:02d}.md")
    if not os.path.exists(p):
        missing.append(n); continue
    raw = open(p, encoding="utf-8").read().strip()
    m = re.match(r"##\s*(.+?)\n+(.*)", raw, re.S)
    if not m:
        missing.append(n); continue
    title, text = m.group(1).strip(), m.group(2).strip()
    blocks.append({"n": n, "title": title, "text": text})

ok = True
# ---------- ГЕЙТ 1: комплектность ----------
if missing:
    print(f"ГЕЙТ 1 комплектность: ❌ нет блоков {missing}"); ok = False
else:
    empty = [b["n"] for b in blocks if len(b["text"]) < 200]
    if empty: print(f"ГЕЙТ 1 комплектность: ❌ подозрительно короткие {empty}"); ok = False
    else: print(f"ГЕЙТ 1 комплектность: ✅ {len(blocks)}/16")

def clean(t):  # речь без [показ:] и ремарок
    t = re.sub(r"\[показ:[^\]]*\]", "", t)
    t = re.sub(r"\[[^\]]*\]", "", t)
    return t

# ---------- ГЕЙТ 2: дубли между блоками ----------
dup = []
for i in range(len(blocks)):
    for j in range(i + 1, len(blocks)):
        r = difflib.SequenceMatcher(None, clean(blocks[i]["text"]), clean(blocks[j]["text"])).ratio()
        if r > 0.35: dup.append(f"Б{blocks[i]['n']}~Б{blocks[j]['n']}: {r:.0%}")
if dup: print("ГЕЙТ 2 дубли: ❌ " + "; ".join(dup)); ok = False
else: print("ГЕЙТ 2 дубли: ✅ нет")

# ---------- ГЕЙТ 3: запрещённое ----------
full = "\n\n".join(f"[Б{b['n']}] {clean(b['text'])}" for b in blocks)
BAN = {
    # стоп-имена (reference/stop-names.md)
    r"Миллер|Миссис\s*Лазер|Гезаров|Аяз|Шабутдинов": "СТОП-ИМЯ (уголовные дела)",
    # обращение
    r"\b(?:ты|тебе|тебя|тобой|твой|твоя|твоё|твои)\b": "обращение на «ты»",
    # стоп-термины клиента
    r"\bКФУ\b": "запрещённый термин (→ «причины успеха»)",
    r"деньги\s+(?:где-то\s+)?лежат|золото\s+(?:уже\s+)?лежит": "«деньги лежат» — стоп",
    r"вы(?:йти|ход)\s+из\s+операционк": "«выйти из операционки» — стоп",
    # rejected-факты (web-фактчек 17.07)
    r"8[,.]3\s*%|восемь\s+и\s+три\s+десятых|три\s+целых\s+пять": "AmEx 8,3→3,5 — не подтверждено",
    r"67\s*подпроцесс": "«67 подпроцессов» — не найдено",
    r"105\s*поиск": "Keys.so «105 поисков» — не найдено",
    r"на\s*14\s*%|\+\s*14\s*%|четырнадцать\s+процентов": "win-loss +14% — не подтверждено",
    r"86\s*%[^.]{0,40}17\s*%": "Xerox 86→17 — единственная пара цифр запрещена (источники расходятся)",
    r"512\s*филиал": "Педант 512 — устарело (→ ~700)",
    r"сто\s+с\s+лишним\s+миллиардов": "ВИ — теперь 180+ млрд",
    r"тысяч[аи]?\s+A/B|миллион\s+A/B|тысяч[аи]?\s+(?:а|э)[\s-]?б[\s-]?тестов": "FitStars: число тестов pending (F7)",
    # прошлые баны (build_v9)
    r"\bВоробьёв": "нет в базе Дашкиева",
    r"\bSolid\b": "не называть партнёрку",
    r"двадцать один филиал|21\s*филиал": "галлюцинация summary.md",
    r"Портнягин": "убрать имя",
    r"изюм": "метафора убрана по правке Б4.1",
    r"Джобс|Starbucks|Старбакс|Макдоналдс|McDonald": "ротация кейсов: вырезаны совсем (S17)",
    # регистр
    r"понимаете,\s*да|помашите|плюсаните": "пустой вопрос / студийная механика",
    r"жоп\w|впихивать\s+невпихуемое|разводят": "риторика гопника",
}
bad = []
for pat, why in BAN.items():
    for m in re.finditer(pat, full, re.I):
        ctx = full[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        blk = re.findall(r"\[Б(\d+)\]", full[:m.start()])
        bad.append(f"  Б{blk[-1] if blk else '?'} «…{ctx}…» → {why}")
if bad:
    print(f"ГЕЙТ 3 запрещённое: ❌ {len(bad)} вхождений"); print("\n".join(bad[:25])); ok = False
else:
    print("ГЕЙТ 3 запрещённое: ✅ чисто")

# ---------- ГЕЙТ 4: вводные в начале блока ----------
intro = [f"Б{b['n']}" for b in blocks if re.match(r"\s*(Смотрите|Давайте|А теперь|И вот что|Итак, давайте)", clean(b["text"]))]
if intro: print(f"ГЕЙТ 4 вводные: ❌ {', '.join(intro)}"); ok = False
else: print("ГЕЙТ 4 вводные: ✅ чисто")

# ---------- ГЕЙТ 5: интеграция ровно одна ----------
integr = [b["n"] for b in blocks if re.search(r"выезд|⟨N мест⟩|⟨даты⟩|⟨ссылка⟩", b["text"])]
ph = len(re.findall(r"⟨[^⟩]+⟩", full))
if len(integr) == 1: print(f"ГЕЙТ 5 интеграция: ✅ в Б{integr[0]}, плейсхолдеров {ph}")
else: print(f"ГЕЙТ 5 интеграция: ❌ блоки {integr}"); ok = False

# ---------- хронометраж ----------
tot = 0
print("\nХронометраж (слова чистой речи):")
for b in blocks:
    w = len(clean(b["text"]).split()); tot += w
    print(f"  Б{b['n']:>2} {b['title'][:44]:<46} {w}")
print(f"  ИТОГО: {tot} слов ≈ {tot/145:.0f} мин (цель ≤ 6000/41)")
if tot > 6300: print("  ⚠️ длиннее цели — резать Б2/Б6/Б7");

print("\n" + ("=== ГЕЙТЫ ЗЕЛЁНЫЕ ===" if ok else "=== ЕСТЬ КРАСНЫЕ ГЕЙТЫ — ФАЙЛЫ НЕ ПИШЕМ ==="))
if not ok: sys.exit(1)

if WRITE:
    out = ["# «Конкурентная разведка» — суфлёр v11", ""]
    for b in blocks:
        out.append(f"## {b['n']}. {b['title']}"); out.append("")
        out.append(b["text"]); out.append("")
    open(os.path.join(D, "scenario-clean-v11-draft.md"), "w", encoding="utf-8").write("\n".join(out))
    print(f"Записан {D}/scenario-clean-v11-draft.md")
else:
    print("(dry-run: без --write файлы не пишутся)")
