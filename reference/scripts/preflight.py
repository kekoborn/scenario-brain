#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight v4.0 — машинные гейты предсдачи для любого проекта скилла.

Запуск:
  python3 preflight.py --project <slug> [--staging .blocks-v12] [--write] [--report]

Гейты: комплектность · дубли · стоп-слова (reference/stop-words.md) · стоп-имена
(reference/stop-names.md) · вводные в начале блока · интеграции · хронометраж.
--write собирает scenario-clean-<staging>-draft.md ТОЛЬКО при зелёных гейтах.
--report пишет reports/preflight-<staging>.md.
Выход: код 0 = зелёно, 1 = есть blocker.
"""
import argparse, difflib, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # reference/
SKILL = os.path.dirname(BASE)                                               # scenario-brain/

def load_stop_patterns():
    """Парсит reference/stop-words.md: строки таблиц `| паттерн | тип | severity | почему |`."""
    path = os.path.join(BASE, "stop-words.md")
    pats = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*`(.+?)`\s*\|\s*(\S+)\s*\|\s*(blocker|minor)\s*\|\s*(.+?)\s*\|", line)
        if not m:
            continue
        pat, typ, sev, why = m.groups()
        pats.append({"pat": pat, "typ": typ, "sev": sev, "why": why})
    return pats

def load_stop_names():
    """Канонический паттерн — строка grep -inE "..." из stop-names.md (раздел «Проверка перед сдачей»)."""
    path = os.path.join(BASE, "stop-names.md")
    text = open(path, encoding="utf-8").read()
    m = re.search(r'grep\s+-\w+\s+"([^"]+)"', text)
    if m:
        return [p for p in m.group(1).split("|") if p.strip()]
    # фолбэк: фамилии из таблицы (первое слово жирной ячейки), с границей слова
    names = []
    for mm in re.finditer(r"\|\s*\*\*(?:\S+\s+)?(\S{4,})\*\*\s*\|", text):
        names.append(r"\b" + re.escape(mm.group(1)) + r"\w*")
    return names

def clean(t):
    return re.sub(r"\[[^\]]*\]", "", t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--staging", default=None, help="имя staging-папки, напр. .blocks-v12")
    ap.add_argument("--nblocks", type=int, default=16)
    ap.add_argument("--wpm", type=float, default=145.0)
    ap.add_argument("--target-min", type=float, default=41.0)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    D = os.path.join(SKILL, "sessions", a.project)
    if not os.path.isdir(D):
        sys.exit(f"нет проекта: {D}")
    staging = a.staging
    if not staging:
        cands = sorted([d for d in os.listdir(D) if d.startswith(".blocks-v")])
        if not cands:
            sys.exit("нет staging-папки .blocks-vNN (или укажи --staging)")
        staging = cands[-1]
    SRC = os.path.join(D, staging)

    lines_out, ok = [], True
    def say(s):
        print(s); lines_out.append(s)

    blocks, missing = [], []
    for n in range(1, a.nblocks + 1):
        p = os.path.join(SRC, f"{n:02d}.md")
        if not os.path.exists(p):
            missing.append(n); continue
        raw = open(p, encoding="utf-8").read().strip()
        m = re.match(r"##\s*(.+?)\n+(.*)", raw, re.S)
        if not m:
            missing.append(n); continue
        blocks.append({"n": n, "title": m.group(1).strip(), "text": m.group(2).strip()})

    # Г1 комплектность
    if missing or any(len(b["text"]) < 200 for b in blocks):
        short = [b["n"] for b in blocks if len(b["text"]) < 200]
        say(f"Г1 комплектность: ❌ нет {missing} / короткие {short}"); ok = False
    else:
        say(f"Г1 комплектность: ✅ {len(blocks)}/{a.nblocks}")

    # Г2 дубли
    dup = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            r = difflib.SequenceMatcher(None, clean(blocks[i]["text"]), clean(blocks[j]["text"])).ratio()
            if r > 0.35:
                dup.append(f"Б{blocks[i]['n']}~Б{blocks[j]['n']} {r:.0%}")
    say("Г2 дубли: ✅ нет" if not dup else "Г2 дубли: ❌ " + "; ".join(dup)); ok = ok and not dup

    full = "\n\n".join(f"[Б{b['n']}] {clean(b['text'])}" for b in blocks)

    # Г3 стоп-слова
    nb = nm = 0
    for p in load_stop_patterns():
        rx = p["pat"] if p["typ"].startswith("regex") else re.escape(p["pat"])
        flags = re.I | (re.M if "начало" in p["typ"] else 0)
        for m in re.finditer(rx, full, flags):
            blk = re.findall(r"\[Б(\d+)\]", full[:m.start()])
            tag = f"  Б{blk[-1] if blk else '?'} «{m.group(0)[:40]}» → {p['why'][:70]}"
            if p["sev"] == "blocker":
                nb += 1; say("  [B]" + tag)
            else:
                nm += 1
    say(f"Г3 стоп-слова: {'✅' if nb == 0 else '❌'} blocker={nb}, minor={nm}"); ok = ok and nb == 0

    # Г4 стоп-имена
    hits = [w for w in load_stop_names() if re.search(w, full, re.I)]
    say("Г4 стоп-имена: ✅ чисто" if not hits else f"Г4 стоп-имена: ❌ {hits}"); ok = ok and not hits

    # Г5 вводные
    intro = [f"Б{b['n']}" for b in blocks if re.match(r"\s*(Смотрите|Давайте|А теперь|И вот что)", clean(b["text"]))]
    say("Г5 вводные: ✅" if not intro else f"Г5 вводные: ❌ {intro}"); ok = ok and not intro

    # Г6 интеграции (коммерческая + лид-магнит; каждая помечена плашкой [ИНТЕГРАЦИЯ)
    integr = [b["n"] for b in blocks if "[ИНТЕГРАЦИЯ" in b["text"]]
    say(f"Г6 интеграции: {'✅' if len(integr) <= 2 else '❌'} в блоках {integr} (≤2)")
    ok = ok and len(integr) <= 2

    # хронометраж
    tot = sum(len(clean(b["text"]).split()) for b in blocks)
    mins = tot / a.wpm
    say(f"Хронометраж: {tot} слов ≈ {mins:.0f} мин (цель ≤ {a.target_min:.0f})")

    say("=== ЗЕЛЁНО ===" if ok else "=== КРАСНЫЕ ГЕЙТЫ ===")

    if a.report:
        os.makedirs(os.path.join(D, "reports"), exist_ok=True)
        rp = os.path.join(D, "reports", f"preflight-{staging.lstrip('.')}.md")
        open(rp, "w", encoding="utf-8").write("# Preflight " + staging + "\n\n```\n" + "\n".join(lines_out) + "\n```\n")
        print("отчёт:", rp)

    if not ok:
        sys.exit(1)

    if a.write:
        out = [f"# Суфлёр {staging}", ""]
        for b in blocks:
            out += [f"## {b['n']}. {b['title']}", "", b["text"], ""]
        dst = os.path.join(D, f"scenario-clean-{staging.lstrip('.')}-draft.md")
        open(dst, "w", encoding="utf-8").write("\n".join(out))
        print("записан:", dst)

if __name__ == "__main__":
    main()
