#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пересборка review.html под v9: 16 блоков, пересчитанные таймкоды."""
import json, re, sys

D = "/Users/ruslanalyev/.claude/skills/scenario-brain/sessions/konkurentnaya-razvedka"
P = f"{D}/review.html"
blocks = json.load(open(sys.argv[2] if len(sys.argv) > 2 else f"{D}/.blocks/v9.json", encoding="utf-8"))

WPM = 145.0  # темп чтения вслух

def mmss(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"

cur = 0.0
arr = []
for b in blocks:
    speech = re.sub(r'\[[^\]]*\]', '', b["text"])
    dur = len(speech.split()) / WPM * 60
    arr.append({
        "n": b["new_n"],
        "t": b["title"],
        "time": f"{mmss(cur)}–{mmss(cur + dur)}",
        "key": b.get("key", ""),
        "text": b["text"].strip(),
    })
    cur += dur

html = open(P, encoding="utf-8").read()
new_js = "const BLOCKS = " + json.dumps(arr, ensure_ascii=False, indent=2) + ";"

html2, n = re.subn(r'const BLOCKS = \[.*?\n\];', lambda _m: new_js, html, count=1, flags=re.S)
if n != 1:
    sys.exit("СТОП: не нашёл массив BLOCKS — файл не тронут")

VER = sys.argv[1] if len(sys.argv) > 1 else "v10"
html2 = re.sub(r'Конкурентная разведка · \d+ блоков · v\d+[^<]*',
    f"Конкурентная разведка · {len(arr)} блоков · {VER}", html2)
# КРИТИЧНО: версия обязана входить в ключ localStorage, иначе браузер восстановит
# ответы прошлой версии и вернёт уже внесённые правки как новые.
html2, k = re.subn(r'const SCENARIO_VERSION = "v\d+";', f'const SCENARIO_VERSION = "{VER}";', html2)
if k != 1:
    sys.exit("СТОП: не нашёл SCENARIO_VERSION — ключ хранилища не версионируется, ревью подсунет старые ответы")

open(P, "w", encoding="utf-8").write(html2)

# ГЕЙТ: JSON валиден и полон
m = re.search(r'const BLOCKS = (\[.*?\n\]);', open(P, encoding="utf-8").read(), re.S)
chk = json.loads(m.group(1))
print(f"✅ review.html пересобран: {len(chk)} блоков, хронометраж 0:00–{mmss(cur)}")
assert len(chk) == 16, "должно быть 16"
assert all(x["text"].strip() for x in chk), "есть пустые"
for x in chk:
    print(f"  {x['n']:2d}. {x['t'][:46]:48s} {x['time']}")
