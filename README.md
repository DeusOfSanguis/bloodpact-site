# bloodpact.su

Базовая страница для проверки подключения домена **bloodpact.su** к GitHub Pages.

## Публикация

1. Откройте **Settings → Pages**.
2. В блоке **Build and deployment** выберите **Deploy from a branch**.
3. Укажите ветку **main** и каталог **/(root)**, затем нажмите **Save**.
4. В поле **Custom domain** укажите `bloodpact.su` и сохраните.
5. После выпуска сертификата включите **Enforce HTTPS**.

DNS для корневого домена:

- `A @ 185.199.108.153`
- `A @ 185.199.109.153`
- `A @ 185.199.110.153`
- `A @ 185.199.111.153`
- `CNAME www DeusOfSanguis.github.io`

Изменения сайта публикуются после коммита в ветку `main`.
