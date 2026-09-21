#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка сайта «Пакт крови» из папки content/.

Результат (GitHub Pages этого репозитория публикует КОРЕНЬ ветки main):
  ./                 — полноценный статический сайт: index.html, law/, squads/, … , 404.html
  ./embed/           — те же страницы без верхнего меню (для «Встроить → По URL» в Google Sites)
  google-sites/      — автономные HTML-сниппеты по одной странице
                       (для «Вставка → Встроить → Код для встраивания» в Google Sites)

Сборка пишет в корень репозитория, но удаляет только свои артефакты:
CNAME, .nojekyll, assets/img/, assets/video/, content/, scripts/, build.py и т. п. не трогаются.

Запуск:  python3 build.py [--asset-base https://.../assets/img/]
Зависимостей нет — только стандартная библиотека Python 3.
"""
import argparse
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
GS = os.path.join(ROOT, "google-sites")
IMG_DIR = os.path.join(SITE, "assets", "img")
VIDEO_DIR = os.path.join(SITE, "assets", "video")

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

MARQUEE_WORDS = ["КРОВЬ", "血", "ЛУНА", "月", "ВЕЧНОСТЬ", "鬼",
                 "ПАКТ", "約", "ТЬМА", "闇", "СИЛА", "力"]


def load():
    with open(os.path.join(CONTENT, "pages.json"), encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(CONTENT, "theme.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(CONTENT, "app.js"), encoding="utf-8") as f:
        js = f.read()
    return data, css, js


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
    kind: site | embed | snippet."""
    if kind == "embed":
        return "index.html" if slug == "index" else slug + ".html"
    if kind == "snippet":
        base = (data["site"].get("pages_url") or "https://bloodpact.su/").rstrip("/")
        return base + "/" if slug == "index" else base + "/" + slug + "/"
    return prefix + ("" if slug == "index" else slug + "/")


def resolve_asset(name, data, prefix="", asset_base=None):
    """Локальный файл (если лежит в assets/img) → иначе запасной URL из pages.json."""
    if asset_base:
        return asset_base.rstrip("/") + "/" + name
    if os.path.exists(os.path.join(IMG_DIR, name)):
        return f"{prefix}assets/img/{name}"
    return data["assets"][name]


def resolve_video(name, data, prefix="", asset_base=None):
    """Свой видеофайл для фона обложки: сначала ищем в assets/video/, потом в assets/img/."""
    for folder in ("video", "img"):
        if os.path.exists(os.path.join(SITE, "assets", folder, name)):
            if asset_base and folder == "img":
                return asset_base.rstrip("/") + "/" + name
            if asset_base and folder == "video":
                base = (data["site"].get("pages_url") or "https://bloodpact.su/").rstrip("/")
                return base + "/assets/video/" + name
            return f"{prefix}assets/{folder}/{name}"
    return ""


def render_fragment(fragment, data, prefix="", asset_base=None, kind="site"):
    """Подставляет {{img:файл}} и {{page:раздел}} в тексте страницы."""
    def repl_img(m):
        name = m.group(1)
        if name not in data["assets"] and not os.path.exists(os.path.join(IMG_DIR, name)):
            return m.group(0)  # неизвестное имя — оставляем как есть (например, пример в комментарии)
        return resolve_asset(name, data, prefix, asset_base)

    def repl_page(m):
        slug = m.group(1)
        if slug not in {p["slug"] for p in data["pages"]}:
            return m.group(0)
        return page_url(data, slug, kind, prefix)

    out = re.sub(r"\{\{img:([^}]+)\}\}", repl_img, fragment)
    return re.sub(r"\{\{page:([a-z0-9_-]+)\}\}", repl_page, out)


# ---------------------------------------------------------------- шапка ---

def render_nav(data, current_page):
    site = data["site"]
    up = rel_prefix(current_page)
    items = []
    for p in data["pages"]:
        if not p.get("nav"):
            continue
        cls = ' class="active" aria-current="page"' if p["slug"] == current_page["slug"] else ""
        items.append(f'<li><a href="{up}{page_path(p)}"{cls}>{html.escape(p["nav"])}</a></li>')
    home = "./" if current_page["slug"] == "index" else up
    return (
        '<header class="nav">'
        '<div class="nav__in">'
        f'<a class="nav__logo" href="{home}"><span class="nav__drop">🩸</span>'
        f'<span>{html.escape(site["home_label"]).replace("·", "<i>·</i>")}</span></a>'
        '<nav aria-label="Разделы"><ul class="nav__list">' + "".join(items) + "</ul></nav>"
        '<button class="nav__burger" data-menu-open aria-label="Меню">☰</button>'
        "</div></header>"
    )


def render_mmenu(data, current_page):
    """Полноэкранное меню для телефона."""
    up = rel_prefix(current_page)
    home = "./" if current_page["slug"] == "index" else up
    links = [f'<a href="{home}" style="transition-delay:.05s">Главная</a>']
    for i, p in enumerate(data["pages"]):
        if not p.get("nav"):
            continue
        links.append(
            f'<a href="{up}{page_path(p)}" style="transition-delay:{0.08 + i * 0.04:.2f}s">'
            f"{html.escape(p['title'])}</a>"
        )
    return (
        '<div class="mmenu" role="dialog" aria-label="Меню">'
        '<button class="mmenu__close" data-menu-close aria-label="Закрыть">✕</button>'
        "<nav>" + "".join(links) + "</nav>"
        '<span class="mmenu__foot">鬼 · кровь · честь</span>'
        "</div>"
    )


# ---------------------------------------------------------------- герой ---

def split_word(word, delay, cls):
    """Слово по буквам для анимации появления заголовка."""
    chars = "".join(
        f'<span class="ch" style="animation-delay:{delay + i * 0.055:.2f}s">'
        f"{'&nbsp;' if ch == ' ' else html.escape(ch)}</span>"
        for i, ch in enumerate(word)
    )
    return f'<span class="w {cls}">{chars}</span>'


def render_hero(page, data, prefix="", asset_base=None, kind="site", compact=False):
    """Обложка: фон-картинка (грузится всегда) + опционально свой видеофайл
    + опционально кнопка ▶ (YouTube грузится только по клику)."""
    is_index = page["slug"] == "index" and not compact
    bg = resolve_asset(page.get("cover_image") or "cover.jpg", data, prefix, asset_base)

    media = f'<img class="bg" src="{bg}" alt="" fetchpriority="high">'
    local = resolve_video(page.get("cover_video") or "", data, prefix, asset_base) \
        if page.get("cover_video") else ""
    if local:
        media = (
            f'<video class="bg" autoplay muted loop playsinline poster="{bg}">'
            f'<source src="{local}"></video>'
        )

    yt = (page.get("youtube") or "").strip()
    watch = ""
    video_slot = ""
    if yt:
        watch = (
            f'<button class="hero__watch" data-yt="{yt}" aria-label="Смотреть видео">'
            '<span class="play">▶</span><span>Видео</span></button>'
        )
        video_slot = '<div class="hero__video"></div>'

    if is_index:
        w1 = page.get("hero_title_1") or "ПАКТ"
        w2 = page.get("hero_title_2") or "КРОВИ"
        quote = page.get("hero_quote") or ""
        title = split_word(w1, 0.7, "bone") + split_word(w2, 1.0, "red")
        quote_html = f'<p class="hero__quote">{html.escape(quote)}</p>' if quote else ""
        btns = (
            '<div class="hero__btns">'
            '<a class="btn btn--blood" href="#faction"><span>Познать тьму</span></a>'
            '<a class="btn btn--ghost" href="#hierarchy">Иерархия</a>'
            "</div>"
        )
        kanji = (
            '<div class="hero__kanji">'
            '<span class="v">鬼ノ契約</span>'
            '<span class="line"></span>'
            '<span class="t">клятва демона</span>'
            "</div>"
        )
        cue = '<a class="hero__cue" href="#faction"><span>Склонись ниже</span><span>﹀</span></a>'
        cls = "hero"
        content = (
            f'<p class="hero__eyebrow">☾&nbsp;&nbsp;{html.escape(page["cover_uptitle"])}</p>'
            f'<h1 class="hero__title">{title}</h1>'
            f"{quote_html}{btns}"
        )
    else:
        title = split_word(page["cover_title"], 0.3, "bone")
        cue = '<a class="hero__cue" href="#content"><span>Читать</span><span>﹀</span></a>'
        cls = "hero hero--inner"
        kanji = ""
        content = (
            f'<p class="hero__eyebrow">{html.escape(page["cover_uptitle"])}</p>'
            f'<h1 class="hero__title">{title}</h1>'
        )

    return (
        f'<section class="{cls}">'
        f'<div class="hero__media">{media}</div>'
        '<div class="hero__shade"></div>'
        f"{kanji}"
        f'<div class="hero__in">{content}</div>'
        f"{cue}{video_slot}{watch}"
        "</section>"
    )


def render_marquee(reverse=False):
    def word(w):
        cls = "marquee__w k" if re.search(r"[\u4e00-\u9fff]", w) else "marquee__w"
        return f'<span><span class="{cls}">{w}</span><span class="marquee__dot"></span></span>'

    row = '<div class="marquee__row">' + "".join(word(w) for w in MARQUEE_WORDS) + "</div>"
    cls = "marquee marquee--reverse" if reverse else "marquee"
    return f'<div class="{cls}" aria-hidden="true"><div class="marquee__track">{row}{row}</div></div>'


# --------------------------------------------------------------- подвал ---

def render_footer(data, current_page):
    site = data["site"]
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
        '<p class="footer__quote">Кровь, что связывает нас, сильнее смерти. Ночь наша — и она будет длиться вечно.</p>'
        "</div>"
        '<div class="footer__side">'
        '<div class="footer__nav">' + "".join(links) + "</div>"
        '<a class="btn btn--ghost" href="#top">↑&nbsp;&nbsp;Наверх</a>'
        "</div>"
        "</div>"
        '<div class="footer__bot">'
        f'<p>© <span data-year>2026</span> {html.escape(site["name"])} · {html.escape(site["short"])}. Все права принадлежат ночи.</p>'
        "<p>鬼 · 血 · 月</p>"
        "</div>"
        "</div></footer>"
    )


def render_preloader():
    return (
        '<div class="preloader">'
        '<span class="preloader__kanji">血</span>'
        '<div class="preloader__bar">'
        '<div class="preloader__row"><span>Пробуждение</span><b data-count>0%</b></div>'
        '<div class="preloader__track"><div class="preloader__fill"></div></div>'
        "</div>"
        '<span class="preloader__foot">кровь помнит всё</span>'
        "</div>"
    )


# ------------------------------------------------------------- документ ---

def render_document(page, data, body, css_link=None, css_inline=None,
                    js_link=None, js_inline=None, body_class=""):
    site = data["site"]
    title = site["name"] if page["slug"] == "index" else f'{page["title"]} — {site["name"]}'
    base = (site.get("pages_url") or "https://bloodpact.su/").rstrip("/")
    og = base + "/assets/img/og-image.png"
    head_css = (
        f'<link rel="stylesheet" href="{css_link}">' if css_link else f"<style>\n{css_inline}\n</style>"
    )
    script = (
        f'<script src="{js_link}" defer></script>' if js_link else f"<script>\n{js_inline}\n</script>"
    )
    cls = ("grain " + body_class).strip()
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS_URL}">
{head_css}
</head>
<body id="top" class="{cls}">
{body}
{script}
</body>
</html>
"""


def youtube_link_block(page):
    """Для шпаргалки: ссылка на ролик + код вставки по клику."""
    yt = (page.get("youtube") or "").strip()
    if not yt:
        return "—"
    return f"https://www.youtube.com/watch?v={yt}"


def write_cheatsheet(data):
    """google-sites/ASSETS.md — шпаргалка для ручного переноса: страницы, видео, картинки."""
    lines = [
        "# Шпаргалка для переноса в Google Sites",
        "",
        "Файл генерируется автоматически (`python3 build.py`) из `content/pages.json`.",
        "",
        "## Страницы",
        "",
        "| № | Страница в Google Sites | Заголовок на обложке | Файл с текстом | Исходник на Tilda | Видео |",
        "|---|---|---|---|---|---",
    ]
    for i, p in enumerate(data["pages"], 1):
        lines.append(
            f"| {i} | {p['title']} | {p['cover_uptitle'].upper()} / {p['cover_title']} | "
            f"`google-sites/{i:02d}-{p['slug']}.html` | {p['source']} | {youtube_link_block(p)} |"
        )
    lines += [
        "",
        "## Картинки",
        "",
        "Старые картинки — с CDN Tilda (`python3 scripts/fetch_assets.py` кладёт их в `assets/img/`).",
        "Новые (`blood-moon.jpg`, `progenitor.jpg`, `transformation.jpg`) — уже лежат в `assets/img/`.",
        "",
        "| Файл | Где используется | Запасная ссылка |",
        "|---|---|---|",
    ]
    usage = {
        "cover.jpg": "фон обложек внутренних страниц",
        "og-image.png": "картинка для превью ссылки (og:image)",
        "blood-moon.jpg": "обложка главной + герой",
        "progenitor.jpg": "главная — портрет Прародителя",
        "transformation.jpg": "главная — фон «Обращения», обложка «Возвышения крови»",
        "territory-1.png": "Территории — после «Зал высших лун»",
        "territory-2.png": "Территории — после «Зал Доумы»",
        "territory-3.png": "Территории — после «Зал низших лун»",
        "territory-4.png": "Территории — после «Отрядные помещения» (1)",
        "territory-5.png": "Территории — после «Отрядные помещения» (2)",
        "champion.webp": "Рейтинг — круглое фото чемпиона (300×300)",
    }
    for name, url in data["assets"].items():
        lines.append(f"| `{name}` | {usage.get(name, '')} | {url} |")
    lines += [
        "",
        "## Видео на обложках",
        "",
        "Видео с YouTube теперь грузится только по клику на кнопку ▶ —",
        "поэтому обложка всегда показывает картинку, даже если YouTube недоступен.",
        "Свой видеофайл (mp4/webm, будет играть фоном и грузиться всегда):",
        "положи в `assets/video/`, укажи в `content/pages.json` → `cover_video`.",
        "",
    ]
    with open(os.path.join(GS, "ASSETS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# Исходники и служебные файлы в корне репозитория — сборка их не удаляет.
PROTECTED = {
    ".git", ".gitignore", ".nojekyll", "CNAME", "README.md", "LICENSE",
    "build.py", "content", "scripts", "google-sites", "assets",
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


def clean_dir(path):
    """Полностью очищает каталог, состоящий только из сгенерированных файлов."""
    if os.path.isdir(path):
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)


def build(asset_base=None):
    data, css, js = load()

    # чистим только свои артефакты и создаём выходные папки
    # (CNAME, .nojekyll, assets/img/, assets/video/, content/, scripts/ и build.py не трогаем)
    clean_site(p["slug"] for p in data["pages"])
    clean_dir(GS)
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(EMBED, exist_ok=True)
    os.makedirs(GS, exist_ok=True)

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

        # 1) полноценная страница сайта: index.html, law/index.html, … (в корне репозитория)
        up = rel_prefix(page)
        main_cls = ' id="content"' if is_index else ' id="content" class="article"'
        body = (
            '<div class="cursor" aria-hidden="true">'
            '<div class="cursor__ring"></div><div class="cursor__dot"></div></div>\n'
            '<div class="progress"></div>\n'
            + (render_preloader() if is_index else "")
            + render_nav(data, page)
            + render_mmenu(data, page)
            + render_hero(page, data, prefix=up, kind="site")
            + render_marquee()
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
        main_cls_e = ' id="content"' if is_index else ' id="content" class="article"'
        body = (
            render_hero(page, data, prefix="../", kind="embed", compact=True)
            + render_marquee()
            + f"<main{main_cls_e}>\n" + render_fragment(fragment, data, prefix="../", kind="embed") + "\n</main>\n"
        )
        out = render_document(page, data, body, css_link="../assets/style.css",
                              js_link="../assets/app.js", body_class="embed")
        with open(os.path.join(EMBED, page_href(page)), "w", encoding="utf-8") as f:
            f.write(out)

        # 3) автономный сниппет для «Код для встраивания» (все стили и скрипты внутри файла)
        base = asset_base  # None → запасные ссылки из pages.json
        main_cls_g = ' id="content"' if is_index else ' id="content" class="article"'
        body = (
            render_hero(page, data, asset_base=base, kind="snippet", compact=True)
            + render_marquee()
            + f"<main{main_cls_g}>\n" + render_fragment(fragment, data, asset_base=base, kind="snippet") + "\n</main>\n"
        )
        out = render_document(page, data, body, css_inline=css, js_inline=js, body_class="embed")
        name = f"{i + 1:02d}-{page['slug']}.html"
        with open(os.path.join(GS, name), "w", encoding="utf-8") as f:
            f.write(out)

    write_404(data, css, js)
    write_cheatsheet(data)

    # список страниц для README/проверки
    print("Собрано страниц:", len(data["pages"]))
    for p in data["pages"]:
        print(f"  /{page_path(p):14s}  ./{page_path(p)}index.html  ←  {p['source']}")
    if domain:
        print("Свой домен (CNAME):", domain)


def write_404(data, css, js):
    """404.html в корне — GitHub Pages показывает её для несуществующих адресов."""
    body = (
        '<div class="progress"></div>\n'
        '<section class="hero hero--inner">'
        '<div class="hero__shade"></div>'
        '<div class="hero__in">'
        '<p class="hero__eyebrow">Ошибка 404</p>'
        f'<h1 class="hero__title">{split_word("ПУСТОТА", 0.2, "bone")}</h1>'
        '<p class="hero__quote">Такой страницы нет даже у ночи.</p>'
        '<div class="hero__btns"><a class="btn btn--blood" id="home" href="/">На главную</a></div>'
        "</div></section>"
        "<script>(function(){var h=location.hostname,p=location.pathname.split('/');"
        "document.getElementById('home').href=/\\.github\\.io$/.test(h)&&p[1]?'/'+p[1]+'/':'/';})();</script>"
    )
    page = {"slug": "404", "title": "Страница не найдена"}
    out = render_document(page, data, body, css_inline=css, js_inline=js)
    with open(os.path.join(SITE, "404.html"), "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asset-base", default=None,
                    help="абсолютный URL папки с картинками для сниппетов google-sites/ "
                         "(например https://bloodpact.su/assets/img). "
                         "По умолчанию используются запасные ссылки из content/pages.json.")
    args = ap.parse_args()
    build(asset_base=args.asset_base)
