#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка сайта «Пакт крови» из папки content/.

Результат (GitHub Pages этого репозитория публикует КОРЕНЬ ветки main):
  ./                 — полноценный статический сайт: index.html, law/, squads/, … , 404.html
  ./embed/           — те же страницы без верхнего меню (для «Встроить → По URL» в Google Sites)

Сборка пишет в корень репозитория, но удаляет только свои артефакты:
CNAME, .nojekyll, assets/img/, content/, scripts/, build.py и т. п. не трогаются.

Запуск:  python3 build.py
Зависимостей нет — только стандартная библиотека Python 3.
"""
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
# Сайт собирается в корень репозитория: Pages публикует main / (root).
SITE = ROOT
EMBED = os.path.join(SITE, "embed")
IMG_DIR = os.path.join(SITE, "assets", "img")

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='.9em' font-size='90'%3E%F0%9F%A9%B8%3C/text%3E%3C/svg%3E"
)

FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Unbounded:wght@300;400;600;800;900"
    "&family=Cormorant:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600"
    "&family=Manrope:wght@300;400;500;600;700;800"
    "&display=swap"
)

# Бегущая строка — цитаты демонов (Луны и Прародитель).
# Список правится в content/pages.json → "quotes" → "marquee".
# Здесь — только запасной вариант, если в pages.json его нет.
MARQUEE_QUOTES = [
    {"text": "Я — живое существо, бесконечно близкое к совершенству.",
     "author": "Мудзан Кибуцуджи · Прародитель демонов"},
    {"text": "Будь благодарен за кровь. Не пролей на землю ни капли — иначе голова и тело расстанутся.",
     "author": "Кокушибо · Первая Высшая Луна"},
    {"text": "Стань демоном, Кёджуро. Мы сможем сражаться вечно.",
     "author": "Аказа · Третья Высшая Луна"},
]

# Печать раздела: иероглиф на обложке, в кодексе и на свитке.
SIGIL = {
    "index": "血",
    "law": "法",
    "elevation": "昇",
    "squads": "隊",
    "scars": "傷",
    "limits": "限",
    "bloodbattle": "闘",
    "territories": "域",
    "incentives": "賞",
    "ranking": "位",
    "court": "裁",
}

# Короткие подписи боковой шкалы главной (не пункты меню).
SPINE = [
    ("faction", "01", "Демоны"),
    ("laws", "02", "Устав"),
    ("moons", "03", "Луны"),
    ("rebirth", "04", "Кровь"),
    ("hierarchy", "05", "Ранги"),
    ("privileges", "06", "Власть"),
]


def load():
    with open(os.path.join(CONTENT, "pages.json"), encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(CONTENT, "theme.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(CONTENT, "app.js"), encoding="utf-8") as f:
        js = f.read()
    data["lists"] = load_lists()
    return data, css, js


def load_lists():
    """Часто меняющиеся списки из content/data/*.json (правятся в админке /admin/)."""
    lists = {}
    data_dir = os.path.join(CONTENT, "data")
    for name in ("squads", "ranking"):
        path = os.path.join(data_dir, name + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                lists[name] = json.load(f)
        else:
            lists[name] = {}
    return lists


def page_href(page):
    """Имя файла для плоских версий (embed/)."""
    return "index.html" if page["slug"] == "index" else page["slug"] + ".html"


def page_path(page):
    """Путь страницы на сайте — как на Tilda: / , /law/, /squads/ …
    (./index.html, ./law/index.html, …)."""
    return "" if page["slug"] == "index" else page["slug"] + "/"


def rel_prefix(page):
    """Относительный путь до корня сайта из данной страницы."""
    return "" if page["slug"] == "index" else "../"


def page_url(data, slug, kind, prefix=""):
    """Ссылка на раздел сайта для подстановки {{page:slug}} в текстах.
    kind: site | embed."""
    if kind == "embed":
        return "index.html" if slug == "index" else slug + ".html"
    return prefix + ("" if slug == "index" else slug + "/")


def resolve_asset(name, data, prefix=""):
    """Локальный файл (если лежит в assets/img) → иначе запасной URL из pages.json."""
    if os.path.exists(os.path.join(IMG_DIR, name)):
        return f"{prefix}assets/img/{name}"
    return data["assets"][name]


def render_fragment(fragment, data, prefix="", kind="site"):
    """Подставляет {{img:файл}} и {{page:раздел}} в тексте страницы."""
    def repl_img(m):
        name = m.group(1)
        if name not in data["assets"] and not os.path.exists(os.path.join(IMG_DIR, name)):
            return m.group(0)  # неизвестное имя — оставляем как есть (например, пример в комментарии)
        return resolve_asset(name, data, prefix)

    def repl_page(m):
        slug = m.group(1)
        if slug not in {p["slug"] for p in data["pages"]}:
            return m.group(0)
        return page_url(data, slug, kind, prefix)

    out = re.sub(r"\{\{img:([^}]+)\}\}", repl_img, fragment)
    out = re.sub(r"\{\{page:([a-z0-9_-]+)\}\}", repl_page, out)
    out = out.replace("{{marquee}}", render_marquee(data, False))
    out = out.replace("{{marquee:reverse}}", render_marquee(data, True))
    out = out.replace("{{squads}}", render_squads(data))
    out = out.replace("{{ranking-top}}", render_ranking_top(data))
    return out


# ---------------------------------------------------------------- шапка ---

def _sigil(page):
    return page.get("sigil") or SIGIL.get(page["slug"], "鬼")


def render_nav(data, current_page):
    """Шапка: печать фракции + печати разделов + кнопка кодекса."""
    site = data["site"]
    up = rel_prefix(current_page)
    home = "./" if current_page["slug"] == "index" else up
    seals = []
    home_on = current_page["slug"] == "index"
    seals.append(
        f'<a class="seal{" seal--on" if home_on else ""}" href="{home}"'
        + (' aria-current="page"' if home_on else "")
        + f'><i>{SIGIL["index"]}</i><span>Пакт</span></a>'
    )
    for p in data["pages"]:
        if not p.get("nav"):
            continue
        on = p["slug"] == current_page["slug"]
        seals.append(
            f'<a class="seal{" seal--on" if on else ""}" href="{up}{page_path(p)}"'
            + (' aria-current="page"' if on else "")
            + f'><i>{html.escape(_sigil(p))}</i><span>{html.escape(p["nav"])}</span></a>'
        )
    return (
        '<header class="nav">'
        '<div class="nav__in">'
        f'<a class="nav__logo" href="{home}"><span class="nav__drop">{SIGIL["index"]}</span>'
        f'<span>{html.escape(site["home_label"]).replace("·", "<i>·</i>")}</span></a>'
        '<div class="nav__seals" data-seals><div class="nav__seals-track">'
        + "".join(seals) +
        "</div></div>"
        '<button class="nav__burger" data-menu-open aria-label="Открыть кодекс">'
        '<span class="nav__burger-k">鬼</span><span class="nav__burger-t">Кодекс</span></button>'
        "</div></header>"
    )


def render_mmenu(data, current_page):
    """Кодекс — переключение разделов печатями, а не списком ссылок."""
    up = rel_prefix(current_page)
    home = "./" if current_page["slug"] == "index" else up
    cards = []
    entries = [("index", "Главная", "Клятва крови", home, SIGIL["index"])]
    for p in data["pages"]:
        if not p.get("nav"):
            continue
        entries.append((p["slug"], p["title"], p["nav"], up + page_path(p), _sigil(p)))
    for i, (slug, title, short, href, sig) in enumerate(entries):
        on = " on" if slug == current_page["slug"] else ""
        cards.append(
            f'<a class="codex__card{on}" href="{href}" style="transition-delay:{0.04 + i * 0.035:.2f}s">'
            f'<span class="codex__n">{i:02d}</span>'
            f'<span class="codex__t">{html.escape(title)}</span>'
            f'<span class="codex__s">{html.escape(short)}</span>'
            f'<span class="codex__k" aria-hidden="true">{html.escape(sig)}</span>'
            "</a>"
        )
    return (
        '<div class="mmenu" role="dialog" aria-label="Кодекс фракции">'
        '<div class="mmenu__bar">'
        '<p class="mmenu__brand"><i>血</i><span>Кодекс фракции</span></p>'
        '<button class="mmenu__close" data-menu-close aria-label="Закрыть">✕</button>'
        "</div>"
        '<nav class="codex">' + "".join(cards) + "</nav>"
        '<span class="mmenu__foot">鬼 · кровь · честь · ночь не отпускает</span>'
        "</div>"
    )


def render_spine():
    """Боковая шкала разделов главной — только широкие экраны."""
    links = []
    for anchor, num, label in SPINE:
        links.append(
            f'<a href="#{anchor}" data-spy="{anchor}"><i>{num}</i><span>{label}</span></a>'
        )
    return '<nav class="spine" aria-label="Разделы главной">' + "".join(links) + "</nav>"


# ---------------------------------------------------------------- герой ---

def split_word(word, delay, cls):
    """Слово по буквам для анимации появления заголовка."""
    chars = "".join(
        f'<span class="ch" style="animation-delay:{delay + i * 0.055:.2f}s">'
        f"{'&nbsp;' if ch == ' ' else html.escape(ch)}</span>"
        for i, ch in enumerate(word)
    )
    return f'<span class="w {cls}">{chars}</span>'


def render_quote(text, author, css_class):
    """Единый вид цитат с подписью персонажа."""
    text = (text or "").strip()
    if not text:
        return ""
    quote = f'<span class="quote__text">«{html.escape(text)}»</span>'
    cite = f'<cite class="quote__author">— {html.escape(author)}</cite>' if author else ""
    return f'<p class="{css_class}">{quote}{cite}</p>'


def render_hero(page, data, prefix="", kind="site", compact=False):
    """Обложка со статичной картинкой; встроенные видеоплееры отключены."""
    is_index = page["slug"] == "index" and not compact
    bg = resolve_asset(page.get("cover_image") or "cover.jpg", data, prefix)
    media = f'<img class="bg" src="{bg}" alt="" fetchpriority="high">'

    if is_index:
        w1 = page.get("hero_title_1") or "ПАКТ"
        w2 = page.get("hero_title_2") or "КРОВИ"
        quote = page.get("hero_quote") or ""
        title = split_word(w1, 0.7, "bone") + split_word(w2, 1.0, "red")
        quote_html = render_quote(quote, page.get("hero_quote_author"), "hero__quote")
        # Кнопки «Познать тьму» и «Иерархия» на обложке не нужны — убраны.
        kanji = (
            '<div class="hero__kanji">'
            '<span class="v">鬼ノ契約</span>'
            '<span class="line"></span>'
            '<span class="t">клятва демона</span>'
            "</div>"
        )
        cue = '<a class="hero__cue" href="#faction" aria-label="Дальше"><span aria-hidden="true">﹀</span></a>'
        cls = "hero"
        content = (
            f'<p class="hero__eyebrow">☾&nbsp;&nbsp;{html.escape(page["cover_uptitle"])}</p>'
            f'<h1 class="hero__title">{title}</h1>'
            f"{quote_html}"
        )
        crest = ""
    else:
        sig = html.escape(_sigil(page))
        label = page.get("nav") or page["cover_uptitle"]
        title = f'<span class="hero__plain"><span>{html.escape(page["cover_title"])}</span></span>'
        cue = '<a class="hero__cue" href="#content"><span>Читать свиток</span><span>﹀</span></a>'
        cls = "hero hero--inner"
        kanji = (
            '<div class="hero__kanji">'
            f'<span class="v">{sig}</span>'
            '<span class="line"></span>'
            f'<span class="t">{html.escape(label)}</span>'
            "</div>"
        )
        crest = f'<div class="hero__crest" aria-hidden="true"><span>{sig}</span></div>'
        content = (
            f'<p class="hero__eyebrow">{sig}&nbsp;&nbsp;{html.escape(page["cover_uptitle"])}</p>'
            f'<h1 class="hero__title">{title}</h1>'
        )
    return (
        f'<section class="{cls}">'
        f'<div class="hero__media">{media}</div>'
        '<div class="hero__shade"></div>'
        f"{kanji}{crest}"
        f'<div class="hero__in">{content}</div>'
        f"{cue}"
        "</section>"
    )


def render_marquee(data=None, reverse=False):
    """Бегущая строка: цитаты демонов вместо отдельных слов."""
    quotes = ((data or {}).get("quotes") or {}).get("marquee") or MARQUEE_QUOTES

    def item(q):
        text = html.escape(str(q.get("text", "")).strip())
        author = html.escape(str(q.get("author", "")).strip())
        cite = f'<span class="marquee__a">— {author}</span>' if author else ""
        return (f'<span class="marquee__item"><span class="marquee__q">«{text}»</span>'
                f'{cite}<span class="marquee__dot"></span></span>')

    row = '<div class="marquee__row">' + "".join(item(q) for q in quotes) + "</div>"
    cls = "marquee marquee--reverse" if reverse else "marquee"
    return f'<div class="{cls}" aria-hidden="true"><div class="marquee__track">{row}{row}</div></div>'


# ------------------------------------------------------- списки из data/ ---

def render_squad_card(sq, parent_name=None, is_sub=False):
    """Карточка отряда/подотряда из content/data/squads.json.
    parent_name — название родительского отряда (для подотрядов);
    is_sub — подотряд: заголовок уровнем ниже (h4) и подчинённое оформление."""
    tag = "h4" if is_sub else "h3"
    parts = [f'<{tag} class="squad">{html.escape(str(sq.get("name", "")).strip())}</{tag}>']
    parent = str(sq.get("parent", "") or "").strip()
    label = str(sq.get("parent_label", "") or "").strip()
    if parent_name and not parent:
        parent = str(parent_name).strip()
        label = label or "Подотряд"
    # У вложенного подотряда родителя не повторяем: он и так показан внутри
    # группы своего основного отряда. Плашка нужна только самостоятельным
    # отрядам с явно указанным руководством (например, Сакуран/Джингу).
    if parent and not is_sub:
        label = label or "Подотряд"
        parts.append(
            f'<p class="squad-parent"><strong>{html.escape(label)}:</strong> {html.escape(parent)}</p>'
        )
    owner = str(sq.get("owner", "") or "").strip()
    if owner:
        parts.append(f"<p><strong>Владелец отряда</strong> - {html.escape(owner)}</p>")
    for ov in sq.get("overseers") or []:
        role = str(ov.get("role", "") or "").strip()
        if role:
            parts.append(f"<p><strong>{html.escape(role)}</strong></p>")
        for person in ov.get("people") or []:
            person = str(person).strip()
            if person:
                parts.append(f"<p>{html.escape(person)}</p>")
    desc = str(sq.get("description", "") or "").strip()
    if desc:
        parts.append(f"<p>{html.escape(desc)}</p>")
    tasks = [str(t).strip() for t in (sq.get("tasks") or []) if str(t).strip()]
    if tasks:
        label = str(sq.get("tasks_label", "") or "Задачи отряда:").strip() or "Задачи отряда:"
        parts.append(f"<p><strong>{html.escape(label)}</strong></p>")
        parts.append("<ul>" + "".join(f"<li>{html.escape(t)}</li>" for t in tasks) + "</ul>")
    note_label = str(sq.get("note_label", "") or "").strip()
    note_text = str(sq.get("note_text", "") or "").strip()
    if note_label or note_text:
        strong = f"<strong>{html.escape(note_label)}</strong> " if note_label else ""
        parts.append(
            f'<p class="note note--exception">{strong}{html.escape(note_text)}</p>'
        )
    cls = "squad-card squad-card--sub" if is_sub else "squad-card squad-card--main"
    return f'<div class="{cls}">\n' + "\n".join(parts) + "\n</div>"


def render_squads(data):
    """{{squads}} — как в меню админки: основной отряд, под ним его подотряды,
    затем следующий основной отряд и его подотряды, и так далее
    (порядок и вложенность — из content/data/squads.json: у отряда есть subs).
    Каждый основной отряд выводится отдельной группой (секцией), подотряды —
    вложенным блоком внутри неё."""
    squads = ((data.get("lists") or {}).get("squads") or {}).get("squads") or []
    groups = []
    for sq in squads:
        group = ['<section class="s squad-group">', render_squad_card(sq)]
        subs = sq.get("subs") or []
        if subs:
            group.append('<div class="squad-subs">')
            group.append('<p class="squad-subs__cap">Подотряды</p>')
            for sub in subs:
                group.append(render_squad_card(sub, parent_name=sq.get("name"), is_sub=True))
            group.append("</div>")
        group.append("</section>")
        groups.append("\n".join(group))
    if not groups:
        return ""
    return "\n".join(groups)


def render_ranking_top(data):
    """Чемпион и таблица мест ({{ranking-top}}) из content/data/ranking.json."""
    rk = (data.get("lists") or {}).get("ranking") or {}
    champ = rk.get("champion") or {}
    name = str(champ.get("name", "") or "").strip() or "Пока нет чемпиона"
    free = bool(champ.get("free", True))
    status = str(champ.get("status", "") or "").strip() or ("Место свободно" if free else "")
    aria = "Место чемпиона пока свободно" if free else "Печать чемпиона"
    champion = (
        '<section class="s narrow center champion">\n'
        '<h2 class="xl c-gold">Чемпион</h2>\n'
        f'<div class="avatar-mark" role="img" aria-label="{html.escape(aria)}">\n'
        '<span class="avatar-mark__kanji" aria-hidden="true">位</span>\n'
        f'<span class="avatar-mark__label">{html.escape(status)}</span>\n'
        "</div>\n"
        f'<p class="name c-darkred">{html.escape(name)}</p>\n'
        "</section>"
    )
    rows = []
    for e in rk.get("entries") or []:
        label = str(e.get("label", "") or "").strip()
        ename = str(e.get("name", "") or "").strip()
        if not label and not ename:
            continue
        if e.get("highlight"):
            span = f'<span class="c-darkred">{html.escape(label)} - </span>' if label else ""
            rows.append(f"<p><strong>{span}{html.escape(ename)}</strong></p>")
        else:
            tail = f" - {html.escape(ename)}" if ename else " -"
            rows.append(f"<p>▶ {html.escape(label)}{tail}</p>")
    table = '<section class="s narrow center">\n' + "\n".join(rows) + "\n</section>"
    return champion + "\n<hr>\n" + table


# --------------------------------------------------------------- подвал ---

def render_footer(data, current_page):
    site = data["site"]
    quote = data["quotes"]["footer"]
    up = rel_prefix(current_page)
    links = []
    for p in data["pages"]:
        if not p.get("nav"):
            continue
        links.append(f'<a href="{up}{page_path(p)}">{html.escape(p["nav"])}</a>')
    return (
        '<footer class="footer">'
        '<div class="footer__glow"></div>'
        '<div class="footer__in">'
        '<div class="footer__top">'
        "<div>"
        f'<p class="footer__up">{html.escape(site["short"])} · Фракция демонов</p>'
        '<p class="footer__big"><span class="stroke">Пакт</span> <span class="fill">Крови</span></p>'
        + render_quote(quote["text"], quote["author"], "footer__quote")
        + "</div>"
        '<div class="footer__side">'
        '<div class="footer__nav">' + "".join(links) + "</div>"
        '<a class="btn btn--ghost" href="#top">↑&nbsp;&nbsp;Наверх</a>'
        "</div>"
        "</div>"
        '<div class="footer__bot">'
        f'<p>© <span data-year>2026</span> {html.escape(site["name"])}. Сайт фракции демонов.</p>'
        "<p>鬼 · 血 · 月</p>"
        "</div>"
        "</div></footer>"
    )


def render_preloader():
    return (
        '<div class="preloader">'
        '<span class="preloader__kanji">血</span>'
        '<div class="preloader__bar">'
        '<div class="preloader__row"><span>Возгордись</span><b data-count>0%</b></div>'
        '<div class="preloader__track"><div class="preloader__fill"></div></div>'
        "</div>"
        '<span class="preloader__foot">своей расой, своей кровью</span>'
        "</div>"
    )


# ------------------------------------------------------------- документ ---

def render_document(page, data, body, css_link=None, css_inline=None,
                    js_link=None, js_inline=None, body_class=""):
    site = data["site"]
    title = site["name"] if page["slug"] == "index" else f'{page["title"]} — {site["name"]}'
    base = (site.get("pages_url") or "https://bloodpact.su/").rstrip("/")
    og = base + "/assets/img/blood-moon.jpg"
    head_css = (
        f'<link rel="stylesheet" href="{css_link}">' if css_link else f"<style>\n{css_inline}\n</style>"
    )
    script = (
        f'<script src="{js_link}" defer></script>' if js_link else f"<script>\n{js_inline}\n</script>"
    )
    slug = page.get("slug") or "page"
    sig = html.escape(SIGIL.get(slug, ""))
    cls = f"page-{slug} {body_class}".strip()
    # Экран загрузки показывается только один раз за сеанс: если человек уже открывал
    # любую страницу сайта, при следующих переходах остаётся только шторка (один переход, а не два).
    visit = (
        "<script>try{"
        "if(sessionStorage.getItem('bp-visited')){document.documentElement.classList.add('bp-seen');}"
        "else{sessionStorage.setItem('bp-visited','1');}"
        "}catch(e){}</script>"
    )
    return f"""<!DOCTYPE html>
<html lang="{site['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(site['description'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(site['description'])}">
<meta property="og:image" content="{og}">
<link rel="icon" href="{FAVICON}">
{visit}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS_URL}">
{head_css}
</head>
<body id="top" class="{cls}" data-sigil="{sig}">
<div class="veil" aria-hidden="true"></div>
{body}
{script}
</body>
</html>
"""


# Исходники и служебные файлы в корне репозитория — сборка их не удаляет.
PROTECTED = {
    ".git", ".gitignore", ".nojekyll", "CNAME", "README.md", "LICENSE",
    ".github", "admin", "build.py", "content", "scripts", "assets",
}


def clean_site(page_slugs):
    """Удаляет из корня только артефакты прошлой сборки:
    index.html, 404.html, embed/ и каталоги страниц (law/, squads/, …)."""
    generated = {"index.html", "404.html", "embed"} | set(page_slugs)
    generated -= {"index"}  # главная — это index.html в корне, а не каталог
    for name in generated:
        if name in PROTECTED:
            raise SystemExit(f"Слаг страницы «{name}» конфликтует со служебным файлом — переименуйте страницу.")
        p = os.path.join(SITE, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)


def build():
    data, css, js = load()

    # чистим только свои артефакты и создаём выходные папки
    # (CNAME, .nojekyll, assets/img/, content/, scripts/ и build.py не трогаем)
    clean_site(p["slug"] for p in data["pages"])
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(EMBED, exist_ok=True)

    with open(os.path.join(SITE, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(css)
    with open(os.path.join(SITE, "assets", "app.js"), "w", encoding="utf-8") as f:
        f.write(js)
    open(os.path.join(SITE, ".nojekyll"), "w").close()

    site = data["site"]

    # свой домен для GitHub Pages: CNAME в корне
    domain = (site.get("domain") or "").strip().lower()
    if domain:
        with open(os.path.join(SITE, "CNAME"), "w", encoding="utf-8") as f:
            f.write(domain + "\n")

    for i, page in enumerate(data["pages"]):
        with open(os.path.join(CONTENT, page["slug"] + ".html"), encoding="utf-8") as f:
            fragment = f.read().strip()

        is_index = page["slug"] == "index"
        sig = html.escape(_sigil(page))

        # 1) полноценная страница сайта: index.html, law/index.html, … (в корне репозитория)
        up = rel_prefix(page)
        main_cls = ' id="content"' if is_index else f' id="content" class="article" data-kanji="{sig}"'
        body = (
            '<div class="cursor" aria-hidden="true">'
            '<div class="cursor__ring"></div><div class="cursor__dot"></div></div>\n'
            '<div class="progress"></div>\n'
            + (render_preloader() if is_index else "")
            + (render_spine() if is_index else "")
            + render_nav(data, page)
            + render_mmenu(data, page)
            + render_hero(page, data, prefix=up, kind="site")
            + render_marquee(data)
            + f"<main{main_cls}>\n" + render_fragment(fragment, data, prefix=up, kind="site") + "\n</main>\n"
            + render_footer(data, page)
        )
        out = render_document(page, data, body, css_link=f"{up}assets/style.css",
                              js_link=f"{up}assets/app.js")
        out_dir = os.path.join(SITE, page_path(page))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(out)

        # 2) embed-версия без меню (для «Встроить по URL» в Google Sites)
        main_cls_e = ' id="content"' if is_index else f' id="content" class="article" data-kanji="{sig}"'
        body = (
            render_hero(page, data, prefix="../", kind="embed", compact=True)
            + render_marquee(data)
            + f"<main{main_cls_e}>\n" + render_fragment(fragment, data, prefix="../", kind="embed") + "\n</main>\n"
        )
        out = render_document(page, data, body, css_link="../assets/style.css",
                              js_link="../assets/app.js", body_class="embed")
        with open(os.path.join(EMBED, page_href(page)), "w", encoding="utf-8") as f:
            f.write(out)

    write_404(data, css, js)

    # список страниц для README/проверки
    print("Собрано страниц:", len(data["pages"]))
    for p in data["pages"]:
        print(f"  /{page_path(p):14s}  ./{page_path(p)}index.html  ←  {p['source']}")
    if domain:
        print("Свой домен (CNAME):", domain)


def write_404(data, css, js):
    """404.html в корне — GitHub Pages показывает её для несуществующих адресов."""
    quote = data["quotes"]["not_found"]
    body = (
        '<div class="progress"></div>\n'
        '<section class="hero hero--inner">'
        '<div class="hero__shade"></div>'
        '<div class="hero__in">'
        '<p class="hero__eyebrow">Ошибка 404</p>'
        f'<h1 class="hero__title">{split_word("ПУСТОТА", 0.2, "bone")}</h1>'
        + render_quote(quote["text"], quote["author"], "hero__quote")
        + '<div class="hero__btns"><a class="btn btn--blood" id="home" href="/"><span>На главную</span></a></div>'
        "</div></section>"
        "<script>(function(){var h=location.hostname,p=location.pathname.split('/');"
        "document.getElementById('home').href=/\\.github\\.io$/.test(h)&&p[1]?'/'+p[1]+'/':'/';})();</script>"
    )
    page = {"slug": "404", "title": "Страница не найдена"}
    out = render_document(page, data, body, css_inline=css, js_inline=js)
    with open(os.path.join(SITE, "404.html"), "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    build()
