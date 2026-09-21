# Шпаргалка для переноса в Google Sites

Файл генерируется автоматически (`python3 build.py`) из `content/pages.json`.

## Страницы

| № | Страница в Google Sites | Заголовок на обложке | Файл с текстом | Исходник на Tilda | Видео |
|---|---|---|---|---|---
| 1 | Главная страница | YUFU · ФРАКЦИЯ ДЕМОНОВ / Фракция демонов | `google-sites/01-index.html` | https://bloodpact-yufu.tilda.ws/ | https://www.youtube.com/watch?v=2P6JSigJ7xo |
| 2 | Демонический закон | YUFU / Демонический закон | `google-sites/02-law.html` | https://bloodpact-yufu.tilda.ws/law | https://www.youtube.com/watch?v=RMnzGUtdsls |
| 3 | Возвышение крови | YUFU / Возвышение крови | `google-sites/03-elevation.html` | https://bloodpact-yufu.tilda.ws/elevation | https://www.youtube.com/watch?v=Hb7SHEtpigc |
| 4 | Отряды | YUFU / Отряды | `google-sites/04-squads.html` | https://bloodpact-yufu.tilda.ws/squads | https://www.youtube.com/watch?v=Xdbl3z_21P4 |
| 5 | Шрамы | YUFU / Шрамы безотрядных | `google-sites/05-scars.html` | https://bloodpact-yufu.tilda.ws/scars | https://www.youtube.com/watch?v=bMxFePqtYoo |
| 6 | Пределы крови | YUFU / Пределы | `google-sites/06-limits.html` | https://bloodpact-yufu.tilda.ws/limits | https://www.youtube.com/watch?v=XVDBTsir2O4 |
| 7 | Битва крови | YUFU / Битвы крови | `google-sites/07-bloodbattle.html` | https://bloodpact-yufu.tilda.ws/bloodbattle | https://www.youtube.com/watch?v=XJsTQCXAJnY |
| 8 | Территории | YUFU / Территории | `google-sites/08-territories.html` | https://bloodpact-yufu.tilda.ws/territories | https://www.youtube.com/watch?v=ZmU692cglz8 |
| 9 | Поощрения | YUFU / Поощрения | `google-sites/09-incentives.html` | https://bloodpact-yufu.tilda.ws/incentives | https://www.youtube.com/watch?v=W_47yPcLm2U |
| 10 | Рейтинг | YUFU / Рейтинг | `google-sites/10-ranking.html` | https://bloodpact-yufu.tilda.ws/ranking | https://www.youtube.com/watch?v=GADE8Tkaa2Q |
| 11 | Суд | YUFU / Суд | `google-sites/11-court.html` | https://bloodpact-yufu.tilda.ws/court | https://www.youtube.com/watch?v=Sg0vFNo_Qig |

## Картинки

Старые картинки — с CDN Tilda (`python3 scripts/fetch_assets.py` кладёт их в `assets/img/`).
Новые (`blood-moon.jpg`, `progenitor.jpg`, `transformation.jpg`) — уже лежат в `assets/img/`.

| Файл | Где используется | Запасная ссылка |
|---|---|---|
| `cover.jpg` | фон обложек внутренних страниц | https://static.tildacdn.pub/tild3736-3037-4334-b863-353562353039/d946dbce69a24e0288d5.jpg |
| `og-image.png` | картинка для превью ссылки (og:image) | https://static.tildacdn.pub/tild6233-3966-4466-b663-643734636462/image.png |
| `territory-1.png` | Территории — после «Зал высших лун» | https://static.tildacdn.pub/tild6631-3432-4730-a366-346236323566/image.png |
| `territory-2.png` | Территории — после «Зал Доумы» | https://static.tildacdn.pub/tild3461-6166-4264-b434-633430366439/image.png |
| `territory-3.png` | Территории — после «Зал низших лун» | https://static.tildacdn.pub/tild6131-6164-4731-a135-663630663437/image.png |
| `territory-4.png` | Территории — после «Отрядные помещения» (1) | https://static.tildacdn.pub/tild3633-6536-4366-a333-396232373936/image.png |
| `territory-5.png` | Территории — после «Отрядные помещения» (2) | https://static.tildacdn.pub/tild3133-6530-4439-b132-306461663261/image.png |
| `champion.webp` | Рейтинг — круглое фото чемпиона (300×300) | https://static.tildacdn.pub/tild3938-6139-4036-a531-623036666330/i.webp |
| `blood-moon.jpg` | обложка главной + герой | https://bloodpact.su/assets/img/blood-moon.jpg |
| `progenitor.jpg` | главная — портрет Прародителя | https://bloodpact.su/assets/img/progenitor.jpg |
| `transformation.jpg` | главная — фон «Обращения», обложка «Возвышения крови» | https://bloodpact.su/assets/img/transformation.jpg |

## Видео на обложках

Видео с YouTube теперь грузится только по клику на кнопку ▶ —
поэтому обложка всегда показывает картинку, даже если YouTube недоступен.
Свой видеофайл (mp4/webm, будет играть фоном и грузиться всегда):
положи в `assets/video/`, укажи в `content/pages.json` → `cover_video`.
