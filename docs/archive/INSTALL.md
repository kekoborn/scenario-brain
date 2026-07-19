# Инструкция по установке scenario-brain для Claude Code

**Для ChatGPT:** См. [INSTALL-CHATGPT.md](INSTALL-CHATGPT.md)

> Скилл — это **папка** `~/.claude/skills/scenario-brain/` с `SKILL.md` в корне и
> вспомогательными файлами рядом (`references/`, `knowledge-base/`, `templates/`,
> `research-rules.md`). Поэтому ставим не один файл, а всю папку — проще всего клонировать
> репозиторий прямо в каталог скиллов.

---

## Установка (рекомендуется) — один командой

```bash
git clone https://github.com/kekoborn/scenario-brain.git ~/.claude/skills/scenario-brain
```

Готово. Открой новую сессию Claude Code и набери `/scenario-brain`.

Если папка уже существует и не пустая — сначала убери старое:
```bash
rm -rf ~/.claude/skills/scenario-brain
git clone https://github.com/kekoborn/scenario-brain.git ~/.claude/skills/scenario-brain
```

---

## Без git (скачать ZIP)

1. Открой https://github.com/kekoborn/scenario-brain → кнопка **Code** → **Download ZIP**.
2. Распакуй.
3. Скопируй содержимое распакованной папки в `~/.claude/skills/scenario-brain/` так,
   чтобы `SKILL.md` лежал по пути `~/.claude/skills/scenario-brain/SKILL.md`.

---

## Проверка установки

```bash
# 1. SKILL.md на месте
ls ~/.claude/skills/scenario-brain/SKILL.md

# 2. Вспомогательные файлы рядом
ls ~/.claude/skills/scenario-brain/references ~/.claude/skills/scenario-brain/knowledge-base
```

Затем в Claude Code: открой новую сессию → `/scenario-brain` → должен начаться диалог.

---

## Обновление

```bash
cd ~/.claude/skills/scenario-brain
git pull
```

(Если ставил из ZIP — скачай свежий ZIP и перезапиши папку.)

---

## Если скилл не работает

**«Скилл не найден» / `/scenario-brain` нет в списке**
- Проверь путь: `ls -la ~/.claude/skills/scenario-brain/SKILL.md` — файл должен существовать.
- Перезапусти Claude Code / открой новую сессию (список скиллов читается при старте).

**«Generic-контент вместо стиля Михаила»**
- Не докопировались вспомогательные файлы. Проверь, что рядом со `SKILL.md` есть папки
  `knowledge-base/` и `references/`. Если нет — переустанови (клон целиком, см. выше).

---

## Удаление

```bash
rm -rf ~/.claude/skills/scenario-brain
```

---

**Источник правды:** канон `~/.claude/skills/scenario-brain/`; этот репозиторий — зеркало.
