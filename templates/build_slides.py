#!/usr/bin/env python3
"""
Сборка ОПОРНОГО в Google Slides из oporny-units.md.
Опорный = единицы смыслов послайдно: один слайд = одна готовая мысль (не топик).

Использование:
    python3 build_slides.py <oporny-units.md> "<Название видео>"

Формат oporny-units.md:
    ## Блок N. Название
    - <одна единица смысла>
    - <одна единица смысла>

Требует gws (Google Workspace CLI). Печатает ссылку на готовую презентацию.

Грабли gws slides:
  • presentationId для batchUpdate/get идёт в --params, НЕ в теле запроса;
  • objectId должен быть длиной >= 5 символов;
  • дефолтный слайд 'p' удаляем ТОЛЬКО после добавления своих (нельзя удалить последний).
"""
import subprocess, json, sys

if len(sys.argv) < 3:
    print("usage: build_slides.py <oporny-units.md> \"<Название>\"")
    sys.exit(1)
UNITS, TITLE = sys.argv[1], sys.argv[2]
SUBTITLE = "Опорные слайды · единицы смыслов"


def gws(*args, body=None, params=None):
    cmd = ["gws", *args]
    if params is not None:
        cmd += ["--params", json.dumps(params, ensure_ascii=False)]
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    i = r.stdout.find("{")
    if i < 0:
        raise RuntimeError("no json: " + r.stdout + r.stderr)
    res = json.loads(r.stdout[i:])
    if isinstance(res, dict) and "error" in res:
        raise RuntimeError("API error: " + json.dumps(res["error"], ensure_ascii=False))
    return res


# 1. parse units
blocks, cur = [], None
for ln in open(UNITS, encoding="utf-8"):
    if ln.startswith("## "):
        cur = (ln[3:].strip(), [])
        blocks.append(cur)
    elif ln.startswith("- ") and cur:
        cur[1].append(ln[2:].strip())

# 2. create presentation
pres = gws("slides", "presentations", "create", body={"title": TITLE + " — опорные слайды"})
pid = pres["presentationId"]
default_ids = [s["objectId"] for s in pres.get("slides", [])]

# 3. build requests: title slide + слайд на каждую единицу смысла
reqs = [
    {"createSlide": {"objectId": "slide000", "slideLayoutReference": {"predefinedLayout": "TITLE"},
        "placeholderIdMappings": [
            {"layoutPlaceholder": {"type": "CENTERED_TITLE", "index": 0}, "objectId": "slide000t"},
            {"layoutPlaceholder": {"type": "SUBTITLE", "index": 0}, "objectId": "slide000s"}]}},
    {"insertText": {"objectId": "slide000t", "text": TITLE}},
    {"insertText": {"objectId": "slide000s", "text": SUBTITLE}},
]
n = 1
for label, units in blocks:
    for u in units:
        sid = f"slide{n:03d}"
        reqs.append({"createSlide": {"objectId": sid,
            "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
            "placeholderIdMappings": [
                {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": sid + "t"},
                {"layoutPlaceholder": {"type": "BODY", "index": 0}, "objectId": sid + "b"}]}})
        reqs.append({"insertText": {"objectId": sid + "t", "text": label}})
        reqs.append({"insertText": {"objectId": sid + "b", "text": u}})
        n += 1

# 4. batchUpdate (chunked; presentationId в --params)
CH = 90
for k in range(0, len(reqs), CH):
    gws("slides", "presentations", "batchUpdate",
        params={"presentationId": pid}, body={"requests": reqs[k:k + CH]})

# 5. удалить дефолтный слайд после добавления своих
if default_ids:
    gws("slides", "presentations", "batchUpdate", params={"presentationId": pid},
        body={"requests": [{"deleteObject": {"objectId": d}} for d in default_ids]})

print(f"units: {n - 1}  slides: {n}")
print("LINK: https://docs.google.com/presentation/d/" + pid + "/edit")
