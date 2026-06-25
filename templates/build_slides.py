#!/usr/bin/env python3
"""
Сборка ОПОРНОГО в Google Slides из oporny-units.md.
Опорный = единицы смыслов: на слайде 3-4 готовых мысли (не топики), сгруппированных
внутри блока. Сверху — маленькая серая метка блока (знать, что за блок), сами тезисы —
крупно, нативными буллетами. Спикер сразу видит, что впереди и к чему ведёт.

Использование:
    python3 build_slides.py <oporny-units.md> "<Название видео>" [units_per_slide=4]

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
import subprocess, json, sys, math

if len(sys.argv) < 3:
    print('usage: build_slides.py <oporny-units.md> "<Название>" [units_per_slide=4]')
    sys.exit(1)
UNITS, TITLE = sys.argv[1], sys.argv[2]
PER = int(sys.argv[3]) if len(sys.argv) > 3 else 4   # 3-4 тезиса на слайд
SUBTITLE = "Опорные слайды · единицы смыслов"
GREY = {"opaqueColor": {"rgbColor": {"red": 0.45, "green": 0.45, "blue": 0.45}}}


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


def chunks(units, per):
    """Сбалансированно режем на группы по 3-4 (без слайда с одним тезисом)."""
    k = len(units)
    nslides = max(1, math.ceil(k / per))
    base, extra = divmod(k, nslides)
    out, i = [], 0
    for s in range(nslides):
        size = base + (1 if s < extra else 0)
        out.append(units[i:i + size])
        i += size
    return out


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

# 3. requests: титул + сгруппированные слайды (метка блока + 3-4 буллета)
reqs = [
    {"createSlide": {"objectId": "slide000", "slideLayoutReference": {"predefinedLayout": "TITLE"},
        "placeholderIdMappings": [
            {"layoutPlaceholder": {"type": "CENTERED_TITLE", "index": 0}, "objectId": "slide000t"},
            {"layoutPlaceholder": {"type": "SUBTITLE", "index": 0}, "objectId": "slide000s"}]}},
    {"insertText": {"objectId": "slide000t", "text": TITLE}},
    {"insertText": {"objectId": "slide000s", "text": SUBTITLE}},
]
g = 0
for label, units in blocks:
    for grp in chunks(units, PER):
        g += 1
        sid = f"grp{g:03d}"
        reqs.append({"createSlide": {"objectId": sid,
            "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
            "placeholderIdMappings": [
                {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": sid + "t"},
                {"layoutPlaceholder": {"type": "BODY", "index": 0}, "objectId": sid + "b"}]}})
        reqs.append({"insertText": {"objectId": sid + "t", "text": label}})
        reqs.append({"insertText": {"objectId": sid + "b", "text": "\n".join(grp)}})
        reqs.append({"createParagraphBullets": {"objectId": sid + "b",
            "textRange": {"type": "ALL"}, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        reqs.append({"updateTextStyle": {"objectId": sid + "b", "textRange": {"type": "ALL"},
            "style": {"fontSize": {"magnitude": 22, "unit": "PT"}}, "fields": "fontSize"}})
        reqs.append({"updateTextStyle": {"objectId": sid + "t", "textRange": {"type": "ALL"},
            "style": {"fontSize": {"magnitude": 13, "unit": "PT"}, "foregroundColor": GREY},
            "fields": "fontSize,foregroundColor"}})

# 4. batchUpdate (chunked; presentationId в --params)
for k in range(0, len(reqs), 90):
    gws("slides", "presentations", "batchUpdate",
        params={"presentationId": pid}, body={"requests": reqs[k:k + 90]})

# 5. удалить дефолтный слайд после добавления своих
if default_ids:
    gws("slides", "presentations", "batchUpdate", params={"presentationId": pid},
        body={"requests": [{"deleteObject": {"objectId": d}} for d in default_ids]})

print(f"единиц смыслов: {sum(len(u) for _, u in blocks)}  слайдов: {g + 1}")
print("LINK: https://docs.google.com/presentation/d/" + pid + "/edit")
