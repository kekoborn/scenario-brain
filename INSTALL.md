# Инструкция по установке scenario-brain для Claude Code

**Для ChatGPT:** См. [INSTALL-CHATGPT.md](INSTALL-CHATGPT.md)

---

## Для себя (быстро)

```bash
# 1. Скопировать скилл
mkdir -p ~/.claude/skills/scenario-brain
cp skills/scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md

# 2. Проверить
ls ~/.claude/skills/scenario-brain/SKILL.md

# 3. Готово! Запускать через:
# /scenario-brain
```

---

## Для коллеги

### Вариант А: Весь проект (рекомендуется)

Передай коллеге весь репозиторий `scenario-brain/`:

```bash
# У коллеги:
cd ~/Projects
cp -r /path/to/scenario-brain ./scenario-brain
cd scenario-brain

# Установить скилл
mkdir -p ~/.claude/skills/scenario-brain
cp skills/scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md

# Готово
```

**Плюсы:**
- ✅ Все knowledge-base файлы на месте
- ✅ Примеры сессий для референса
- ✅ Templates и guidelines

**Минусы:**
- Нужно копировать ~50MB (если есть screenshots)

---

### Вариант Б: Только скилл (минимум)

Передай коллеге 3 файла:

1. `skills/scenario-brain-mvp.md`
2. `knowledge-base/TOV-analysis.md`
3. `knowledge-base/VISUAL-patterns-FINAL.md`

```bash
# У коллеги:
mkdir -p ~/scenario-brain/knowledge-base
mkdir -p ~/.claude/skills/scenario-brain

# Скопировать файлы
cp scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md
cp TOV-analysis.md ~/scenario-brain/knowledge-base/
cp VISUAL-patterns-FINAL.md ~/scenario-brain/knowledge-base/

# Готово
```

**Плюсы:**
- ✅ Легко передать (3 файла)
- ✅ Работает полностью

**Минусы:**
- ❌ Нет примеров сессий
- ❌ Нет templates (discovery-brief, hooks-module, b-roll)

---

### Вариант В: GitHub (если опубликуешь)

```bash
# У коллеги:
git clone https://github.com/kekoborn/scenario-brain
cd scenario-brain

# Установить скилл
mkdir -p ~/.claude/skills/scenario-brain
cp skills/scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md

# Готово
```

---

## Проверка установки

```bash
# 1. Проверить что скилл установлен
ls ~/.claude/skills/scenario-brain/SKILL.md

# 2. Проверить версию
head -5 ~/.claude/skills/scenario-brain/SKILL.md
# Должно быть: **Версия:** 1.7

# 3. Запустить Claude Code
claude

# 4. В чате написать:
/scenario-brain

# 5. Должен загрузиться скилл и начаться диалог
```

---

## Если скилл не работает

### Проблема 1: "Скилл не найден"

**Причина:** Файл не в `~/.claude/skills/scenario-brain/SKILL.md`

**Решение:**
```bash
# Проверить путь
ls -la ~/.claude/skills/scenario-brain/

# Должно быть:
# -rw-r--r--  1 user  staff  34K May 30 09:45 SKILL.md

# Если нет — переустановить:
mkdir -p ~/.claude/skills/scenario-brain
cp skills/scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md
```

---

### Проблема 2: "knowledge-base не найдена"

**Причина:** Скилл ищет файлы в `knowledge-base/`, а их нет

**Решение:**
```bash
# Создать knowledge-base рядом со скиллом
mkdir -p ~/scenario-brain/knowledge-base

# Скопировать файлы
cp TOV-analysis.md ~/scenario-brain/knowledge-base/
cp VISUAL-patterns-FINAL.md ~/scenario-brain/knowledge-base/

# Или скопировать всю папку
cp -r knowledge-base ~/scenario-brain/
```

---

### Проблема 3: "Generic контент вместо стиля Михаила"

**Причина:** `TOV-analysis.md` не найден или пустой

**Решение:**
```bash
# Проверить файл
cat ~/scenario-brain/knowledge-base/TOV-analysis.md | head -20

# Должно быть:
# # TOV-анализ стиля Михаила Дашкиева
# ...

# Если пустой — переустановить
cp knowledge-base/TOV-analysis.md ~/scenario-brain/knowledge-base/
```

---

## Обновление скилла

Когда выйдет новая версия:

```bash
# 1. Получить новый файл
# (через git pull или скопировать от коллеги)

# 2. Переустановить
cp skills/scenario-brain-mvp.md ~/.claude/skills/scenario-brain/SKILL.md

# 3. Проверить версию
head -5 ~/.claude/skills/scenario-brain/SKILL.md

# 4. Готово
```

---

## Удаление

```bash
# Удалить скилл
rm -rf ~/.claude/skills/scenario-brain

# Удалить knowledge-base (опционально)
rm -rf ~/scenario-brain

# Готово
```

---

**Версия:** 1.0  
**Дата:** 30 мая 2026
