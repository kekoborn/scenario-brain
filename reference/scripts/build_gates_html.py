#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""avatar.md / tov.md → читаемые HTML-страницы в стиле review.html."""
import markdown, re, os

D = "/Users/ruslanalyev/.claude/skills/scenario-brain/sessions/konkurentnaya-razvedka"

CSS = """
:root{--bg:#f4f4f5;--card:#fff;--ink:#1a1a1e;--muted:#6b6b76;--line:#e4e4e8;
 --accent:#2f6df0;--ok:#16a34a;--bad:#dc2626;--warn:#d97706;
 --shadow:0 1px 2px rgba(0,0,0,.04),0 8px 24px rgba(0,0,0,.05);}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1c1c20;--ink:#ececf0;--muted:#9a9aa6;
 --line:#2c2c33;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.4);}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:0 0 80px;}
.wrap{max-width:860px;margin:0 auto;padding:28px 20px;}
.nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
 padding:10px 20px;margin:0 -20px 22px;z-index:10;display:flex;gap:8px;flex-wrap:wrap}
.nav a{font-size:13px;text-decoration:none;color:var(--muted);border:1px solid var(--line);
 background:var(--card);padding:5px 11px;border-radius:99px}
.nav a.on{color:#fff;background:var(--accent);border-color:var(--accent)}
h1{font-size:27px;letter-spacing:-.02em;margin:6px 0 18px}
h2{font-size:19px;margin:34px 0 12px;padding:14px 16px;background:var(--card);
 border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;box-shadow:var(--shadow)}
h3{font-size:16px;margin:22px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
p,li{margin:8px 0}
ul,ol{padding-left:22px}
blockquote{margin:12px 0;padding:10px 16px;border-left:3px solid var(--line);
 background:var(--card);border-radius:0 8px 8px 0;color:var(--muted)}
code{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:13px}
table{border-collapse:collapse;width:100%;margin:14px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;font-size:14px}
th{background:var(--card)}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
strong{font-weight:650}
li:has(> strong:first-child){margin:10px 0}
"""

PAGES = [("avatar.md", "avatar.html", "Аватар аудитории"),
         ("tov.md", "tov.html", "Tone of Voice — Михаил Дашкиев")]

def nav(cur):
    links = [("review.html","Сценарий"), ("avatar.html","Аватар"), ("tov.html","TOV")]
    return '<div class="nav">' + "".join(
        f'<a href="{h}" class="{"on" if h==cur else ""}">{t}</a>' for h, t in links) + '</div>'

for src, out, title in PAGES:
    md = open(f"{D}/{src}", encoding="utf-8").read()
    body = markdown.markdown(md, extensions=["tables", "sane_lists", "nl2br"])
    # подсветка запретов/разрешений
    body = body.replace("❌", '<span style="color:var(--bad)">❌</span>')
    body = body.replace("✅", '<span style="color:var(--ok)">✅</span>')
    body = body.replace("⚠️", '<span style="color:var(--warn)">⚠️</span>')
    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Конкурентная разведка</title><style>{CSS}</style></head>
<body><div class="wrap">{nav(out)}{body}</div></body></html>"""
    open(f"{D}/{out}", "w", encoding="utf-8").write(html)
    print(f"  ✅ {out}  ({len(html)//1024} КБ)")

# добавить навигацию в review.html, если её ещё нет
rp = f"{D}/review.html"
r = open(rp, encoding="utf-8").read()
if 'class="nav"' not in r:
    r = r.replace('<div class="wrap">', '<div class="wrap">' + nav("review.html"), 1)
    style_add = """.nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
 padding:10px 20px;margin:0 -20px 18px;z-index:20;display:flex;gap:8px;flex-wrap:wrap}
.nav a{font-size:13px;text-decoration:none;color:var(--muted);border:1px solid var(--line);
 background:var(--card);padding:5px 11px;border-radius:99px}
.nav a.on{color:#fff;background:var(--accent);border-color:var(--accent)}"""
    r = r.replace("</style>", style_add + "\n</style>", 1)
    open(rp, "w", encoding="utf-8").write(r)
    print("  ✅ review.html — добавлена навигация между страницами")
else:
    print("  — review.html: навигация уже есть")
