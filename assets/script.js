(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let theme = systemDark ? 'dark' : 'light';

  const icons = {
    dark: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
    light: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
  };

  const applyTheme = () => {
    root.dataset.theme = theme;
    toggle.innerHTML = icons[theme];
    toggle.setAttribute('aria-label', theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему');
  };

  applyTheme();
  toggle.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    applyTheme();
  });

  const loadTime = new Date();
  document.querySelector('#load-time').textContent = loadTime.toLocaleString('ru-RU');
  document.querySelector('#https-status').textContent = location.protocol === 'https:' ? 'Активен' : 'Не активен';

  document.querySelector('#run-check').addEventListener('click', () => {
    const output = document.querySelector('#check-result');
    const expectedHost = 'bloodpact.su';
    const hostOk = location.hostname === expectedHost || location.hostname === `www.${expectedHost}`;
    const protocolOk = location.protocol === 'https:';

    if (hostOk && protocolOk) {
      output.textContent = '✓ Домен и HTTPS работают корректно';
    } else if (hostOk) {
      output.textContent = '△ Домен работает, но HTTPS ещё не активен';
    } else {
      output.textContent = `△ Страница открыта через ${location.hostname || 'локальный файл'}`;
    }
  });
})();
