/* =====================================================================
   ПАКТ КРОВИ — скрипты сайта (без библиотек, чистый JavaScript).
   Файл копируется сборкой в assets/app.js. Править тут ничего не надо.
   Каждый блок сам проверяет, есть ли нужные элементы на странице.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- Год в подвале ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Экран загрузки (только главная и только раз за сеанс) ----------
     Если человек уже открывал какую-то страницу сайта, экран пропускается:
     при переходе с другой страницы остаётся только шторка, без второй анимации. */
  (function () {
    var pre = document.querySelector(".preloader");
    if (!pre) return;
    if (document.documentElement.classList.contains("bp-seen")) { pre.remove(); return; }
    var num = pre.querySelector("[data-count]");
    var fill = pre.querySelector(".preloader__fill");
    document.body.style.overflow = "hidden";
    var start = performance.now(), dur = 1200;
    function tick(t) {
      var p = Math.min(1, (t - start) / dur);
      if (num) num.textContent = Math.round(p * 100) + "%";
      if (fill) fill.style.transform = "scaleX(" + p + ")";
      if (p < 1) requestAnimationFrame(tick);
      else setTimeout(function () {
        pre.classList.add("done");
        document.body.classList.add("ready");
        document.body.style.overflow = "";
        setTimeout(function () { pre.remove(); }, 1300);
      }, 300);
    }
    requestAnimationFrame(tick);
  })();

  /* ---------- Полоса прогресса + шапка при прокрутке + линия иерархии ---------- */
  (function () {
    var bar = document.querySelector(".progress");
    var nav = document.querySelector(".nav");
    var heroIn = document.querySelector(".hero__in");
    var heroCue = document.querySelector(".hero__cue");
    var heroMedia = document.querySelector(".hero__media");
    var rails = document.querySelectorAll(".timeline");
    function onScroll() {
      var y = window.scrollY || window.pageYOffset;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      if (bar && max > 0) bar.style.transform = "scaleX(" + Math.min(1, y / max) + ")";
      if (nav) nav.classList.toggle("scrolled", y > 60);
      // лёгкий параллакс героя
      if (heroIn && y < window.innerHeight * 1.2) {
        heroIn.style.transform = "translateY(" + y * 0.25 + "px)";
        heroIn.style.opacity = Math.max(0, 1 - y / (window.innerHeight * 0.7));
      }
      if (heroCue) heroCue.style.opacity = Math.max(0, 1 - y / (window.innerHeight * 0.5));
      if (heroMedia && y < window.innerHeight) {
        heroMedia.style.transform = "translateY(" + y * 0.18 + "px) scale(" + (1 + y / window.innerHeight * 0.08) + ")";
      }
      // заливка линии иерархии по мере прокрутки
      rails.forEach(function (tl) {
        var fill = tl.querySelector(".timeline__fill");
        if (!fill) return;
        var r = tl.getBoundingClientRect();
        var vh = window.innerHeight;
        var p = (vh * 0.75 - r.top) / (r.height + vh * 0.2);
        fill.style.transform = "scaleY(" + Math.max(0, Math.min(1, p)) + ")";
      });
    }
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) { window.requestAnimationFrame(function () { onScroll(); ticking = false; }); ticking = true; }
    }, { passive: true });
    onScroll();
  })();

  /* ---------- Мобильное меню ---------- */
  (function () {
    var openBtn = document.querySelector("[data-menu-open]");
    var menu = document.querySelector(".mmenu");
    if (!openBtn || !menu) return;
    var closeBtn = menu.querySelector("[data-menu-close]");
    function open() { menu.classList.add("open"); document.body.style.overflow = "hidden"; }
    function close() { menu.classList.remove("open"); document.body.style.overflow = ""; }
    openBtn.addEventListener("click", open);
    if (closeBtn) closeBtn.addEventListener("click", close);
    menu.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", close); });
  })();

  /* ---------- Появление блоков при прокрутке ---------- */
  (function () {
    var els = document.querySelectorAll(".reveal, .shead");
    if (!els.length || !("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    els.forEach(function (el) { io.observe(el); });
  })();

  /* ---------- Аккордеон: высота, и открыта только одна вкладка ---------- */
  (function () {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.querySelectorAll("[data-acc]").forEach(function (group) {
      group.querySelectorAll("details").forEach(function (d) {
        var body = d.querySelector(".acc__body");
        var head = d.querySelector("summary");
        if (!body || !head || reduce) {
          d.addEventListener("toggle", function () {
            if (d.open) group.querySelectorAll("details").forEach(function (o) { if (o !== d) o.open = false; });
          });
          return;
        }
        body.style.overflow = "hidden";
        body.style.transition = "height 0.42s cubic-bezier(0.22, 1, 0.36, 1)";
        body.style.height = d.open ? "auto" : "0px";
        function shut(item) {
          var b = item.querySelector(".acc__body");
          item._seq = (item._seq || 0) + 1;
          if (b) b.style.height = "0px";
          item.open = false;
        }
        head.addEventListener("click", function (e) {
          e.preventDefault();
          if (d.open) {
            var h = body.getBoundingClientRect().height;
            body.style.height = h + "px";
            d._seq = (d._seq || 0) + 1;
            var id = d._seq;
            requestAnimationFrame(function () {
              if (d._seq !== id) return;
              body.style.height = "0px";
            });
            setTimeout(function () {
              if (d._seq !== id) return;
              d.open = false;
              body.style.height = "0px";
            }, 460);
            return;
          }
          group.querySelectorAll("details").forEach(function (o) {
            if (o !== d && o.open) shut(o);
          });
          d._seq = (d._seq || 0) + 1;
          var id = d._seq;
          d.open = true;
          body.style.height = "0px";
          requestAnimationFrame(function () {
            if (d._seq !== id) return;
            body.style.height = body.scrollHeight + "px";
          });
          function opened(ev) {
            if (ev.propertyName !== "height" || d._seq !== id) return;
            body.style.height = "auto";
            body.removeEventListener("transitionend", opened);
          }
          body.addEventListener("transitionend", opened);
        });
      });
    });
  })();

  /* ---------- Вкладки привилегий ---------- */
  (function () {
    document.querySelectorAll("[data-tabs]").forEach(function (box) {
      var btns = box.querySelectorAll("[data-tab]");
      var panels = box.querySelectorAll("[data-panel]");
      btns.forEach(function (btn) {
        btn.addEventListener("click", function () {
          btns.forEach(function (b) { b.classList.toggle("active", b === btn); });
          panels.forEach(function (p) {
            var on = p.getAttribute("data-panel") === btn.getAttribute("data-tab");
            p.classList.toggle("active", on);
          });
        });
      });
    });
  })();

  /* ---------- Готовность героя (буквы встают после прелоадера) ---------- */
  if (!document.querySelector(".preloader")) document.body.classList.add("ready");

  /* ---------- Печати разделов: надёжный горизонтальный скролл ---------- */
  (function () {
    var box = document.querySelector("[data-seals]");
    if (!box) return;
    var track = box.querySelector(".nav__seals-track");
    if (!track) return;
    var active = track.querySelector(".seal--on");
    var prevBtn = box.querySelector("[data-seals-prev]");
    var nextBtn = box.querySelector("[data-seals-next]");
    var stateFrame = 0;

    function updateState() {
      stateFrame = 0;
      var max = Math.max(0, track.scrollWidth - track.clientWidth);
      var hasOverflow = max > 2;
      var left = Math.max(0, track.scrollLeft);
      var canLeft = hasOverflow && left > 4;
      var canRight = hasOverflow && left < max - 4;
      box.setAttribute("data-can-scroll-left", canLeft ? "true" : "false");
      box.setAttribute("data-can-scroll-right", canRight ? "true" : "false");
      if (prevBtn) prevBtn.disabled = !canLeft;
      if (nextBtn) nextBtn.disabled = !canRight;

      // Маска применяется только к ленте, не к стрелкам поверх неё.
      var mask = "none";
      if (canLeft && canRight) {
        mask = "linear-gradient(90deg, transparent, #000 26px, #000 calc(100% - 26px), transparent)";
      } else if (canRight) {
        mask = "linear-gradient(90deg, #000, #000 calc(100% - 26px), transparent)";
      } else if (canLeft) {
        mask = "linear-gradient(90deg, transparent, #000 26px, #000)";
      }
      track.style.webkitMaskImage = mask;
      track.style.maskImage = mask;
    }

    function scheduleState() {
      if (stateFrame) return;
      stateFrame = window.requestAnimationFrame(updateState);
    }

    function centerActive() {
      if (!active || !track.clientWidth) return;
      // offsetLeft зависит от offsetParent (это может быть вся шапка, не лента).
      // Считаем координату через прямоугольники, затем переводим её в scroll-space.
      var trackRect = track.getBoundingClientRect();
      var itemRect = active.getBoundingClientRect();
      var itemLeft = itemRect.left - trackRect.left + track.scrollLeft;
      var target = itemLeft - (track.clientWidth - itemRect.width) / 2;
      var max = Math.max(0, track.scrollWidth - track.clientWidth);
      track.scrollLeft = Math.max(0, Math.min(max, target));
    }

    function syncLayout() {
      centerActive();
      updateState();
    }

    // Выравниваем активный раздел после первого layout и после загрузки шрифтов.
    window.requestAnimationFrame(syncLayout);
    window.addEventListener("resize", syncLayout, { passive: true });
    window.addEventListener("orientationchange", syncLayout, { passive: true });
    window.addEventListener("load", syncLayout, { once: true });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(syncLayout).catch(function () {});
    }

    track.addEventListener("scroll", scheduleState, { passive: true });
    if (window.ResizeObserver) {
      var resizeObserver = new window.ResizeObserver(scheduleState);
      resizeObserver.observe(box);
      resizeObserver.observe(track);
    }

    // Обычная вертикальная прокрутка колеса листает вкладки по горизонтали.
    box.addEventListener("wheel", function (e) {
      var max = track.scrollWidth - track.clientWidth;
      if (max <= 2) return;
      var delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
      if (e.deltaMode === 1) delta *= 16;
      else if (e.deltaMode === 2) delta *= track.clientWidth;
      if (!delta) return;
      var before = track.scrollLeft;
      track.scrollLeft = Math.max(0, Math.min(max, before + delta));
      if (Math.abs(track.scrollLeft - before) > 0.1) e.preventDefault();
    }, { passive: false });

    function scrollPage(direction) {
      var amount = Math.max(180, track.clientWidth * 0.72) * direction;
      if (typeof track.scrollBy === "function") {
        track.scrollBy({ left: amount, behavior: "smooth" });
      } else {
        track.scrollLeft += amount;
      }
    }
    if (prevBtn) prevBtn.addEventListener("click", function () { scrollPage(-1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { scrollPage(1); });

    // Перетаскивание мышью. На телефонах остаётся нативный инерционный свайп.
    var isDown = false, startX = 0, scrollStart = 0, hasDragged = false;
    function stopDrag() {
      if (!isDown) return;
      isDown = false;
      setTimeout(function () {
        track.classList.remove("is-dragging");
        hasDragged = false;
      }, 80);
    }
    track.addEventListener("mousedown", function (e) {
      if (e.button !== 0) return;
      isDown = true;
      hasDragged = false;
      startX = e.clientX;
      scrollStart = track.scrollLeft;
    });
    window.addEventListener("mousemove", function (e) {
      if (!isDown) return;
      var dx = e.clientX - startX;
      if (Math.abs(dx) > 5) {
        hasDragged = true;
        track.classList.add("is-dragging");
        track.scrollLeft = scrollStart - dx;
      }
    });
    window.addEventListener("mouseup", stopDrag);
    window.addEventListener("blur", stopDrag);
    track.addEventListener("click", function (e) {
      if (!hasDragged) return;
      e.preventDefault();
      e.stopPropagation();
    }, true);
  })();

  /* ---------- Шкала главной ---------- */
  (function () {
    var links = document.querySelectorAll(".spine a[data-spy]");
    if (!links.length || !("IntersectionObserver" in window)) return;
    var map = {};
    links.forEach(function (a) { map[a.getAttribute("data-spy")] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = e.target.id;
        links.forEach(function (a) { a.classList.toggle("on", a.getAttribute("data-spy") === id); });
      });
    }, { rootMargin: "-40% 0px -45% 0px", threshold: 0.01 });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  })();

  /* ---------- Пометки «исключение / примечание» на свитках ---------- */
  (function () {
    document.querySelectorAll(".article p, .article li").forEach(function (el) {
      var t = (el.textContent || "").replace(/^\s+/, "");
      if (/^\[?\s*(исключен|примечан|пояснен|дополнен)/i.test(t)) el.classList.add("edict");
    });
  })();

  /* ---------- Закрыть кодекс по Escape ---------- */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var menu = document.querySelector(".mmenu.open");
    if (!menu) return;
    menu.classList.remove("open");
    document.body.style.overflow = "";
  });

  /* ---------- Переход между страницами (демоническая кровавая штора) ----------
     Уходим: кровавая штора поднимается снизу и накрывает экран, затем
     переход. Приходим: штора уже накрыта (html.veil-cover, ставится в <head>),
     показывает иероглиф и название страницы и уезжает вверх, открывая новую
     страницу. Без JS шторку убирает CSS-анимация.                         */
  (function () {
    var root = document.documentElement;
    var veil = document.querySelector("[data-veil]");
    var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

    function read(key, fallback) {
      try { return sessionStorage.getItem(key) || fallback; } catch (e) { return fallback; }
    }
    function write(key, value) {
      try { sessionStorage.setItem(key, value); } catch (e) {}
    }

    if (veil) {
      /* приход */
      if (root.classList.contains("veil-cover") && !reduceMotion) {
        var label = veil.querySelector("[data-veil-label]");
        var kanji = veil.querySelector("[data-veil-kanji]");
        if (label) label.textContent = read("bp-nav-label", "Пакт крови");
        if (kanji) kanji.textContent = read("bp-nav-sigil", "血");
      }
      var done = function () {
        if (veil.classList.contains("is-cover")) return;
        root.classList.remove("veil-cover");
        root.classList.add("veil-done");
        veil.classList.remove("is-cover");
        veil.classList.remove("is-away");
        document.body.classList.remove("is-leaving");
      };
      var panel = veil.querySelector(".veil__panel");
      if (panel) panel.addEventListener("animationend", function (e) {
        if (e.animationName === "veilAway") done();
      });
      setTimeout(done, reduceMotion ? 30 : 2400);

      /* уход */
      var leaving = false;
      function leave(href, title, sigil) {
        if (leaving) return;
        leaving = true;
        if (reduceMotion) { window.location.href = href; return; }
        write("bp-nav", "1");
        if (title) write("bp-nav-label", title);
        if (sigil) write("bp-nav-sigil", sigil);
        var label = veil.querySelector("[data-veil-label]");
        var kanji = veil.querySelector("[data-veil-kanji]");
        if (label && title) label.textContent = title;
        if (kanji && sigil) kanji.textContent = sigil;
        root.classList.remove("veil-done");
        veil.classList.remove("is-away");
        void veil.offsetWidth;

        var navigated = false;
        var fallback;
        function navigate() {
          if (navigated) return;
          navigated = true;
          if (panel) panel.removeEventListener("transitionend", onCoverEnd);
          clearTimeout(fallback);
          window.location.href = href;
        }
        function onCoverEnd(e) {
          if (e.target === panel && e.propertyName === "transform") navigate();
        }
        if (panel) panel.addEventListener("transitionend", onCoverEnd);
        veil.classList.add("is-cover");
        document.body.classList.add("is-leaving");
        // Fallback for browsers that do not emit transitionend.
        fallback = setTimeout(navigate, 1300);
      }

      document.addEventListener("click", function (e) {
        if (e.defaultPrevented || e.button !== 0) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
        if (!a) return;
        if (root.classList.contains("veil-cover") || leaving) { e.preventDefault(); return; }
        if (a.target && a.target !== "_self") return;
        if (a.hasAttribute("download")) return;
        var href = a.getAttribute("href");
        if (!href || href.charAt(0) === "#" || href.indexOf("mailto:") === 0 || href.indexOf("javascript:") === 0) return;
        var url;
        try { url = new URL(a.href, window.location.href); } catch (err) { return; }
        if (url.protocol !== window.location.protocol) return;
        if (url.host !== window.location.host) return;
        if (url.pathname === window.location.pathname && url.search === window.location.search) return;
        e.preventDefault();
        var title = a.getAttribute("data-nav-title") || (a.querySelector("span") ? a.querySelector("span").textContent.trim() : (a.textContent || "").trim().slice(0, 40));
        var sigil = a.getAttribute("data-nav-sigil") || (a.querySelector("i") ? a.querySelector("i").textContent.trim() : "");
        leave(a.href, title, sigil);
      }, false);

      /* Возврат «назад» из bfcache: сбрасываем незавершённую штору явно. */
      window.addEventListener("pageshow", function (e) {
        if (!e.persisted) return;
        leaving = false;
        root.classList.remove("veil-cover");
        root.classList.add("veil-done");
        veil.classList.remove("is-cover", "is-away");
        document.body.classList.remove("is-leaving");
      });
    }
  })();

  /* ---------- Свой курсор (только для мыши) ---------- */
  (function () {
    if (!window.matchMedia || !window.matchMedia("(pointer: fine)").matches) return;
    var c = document.querySelector(".cursor");
    if (!c) return;
    c.classList.add("on");
    var x = -100, y = -100, sx = -100, sy = -100;
    document.addEventListener("mousemove", function (e) {
      x = e.clientX; y = e.clientY;
      var t = e.target;
      c.classList.toggle("hover", !!(t && t.closest && t.closest("a, button, summary")));
    }, { passive: true });
    (function loop() {
      sx += (x - sx) * 0.25; sy += (y - sy) * 0.25;
      c.style.transform = "translate(" + sx + "px," + sy + "px)";
      requestAnimationFrame(loop);
    })();
  })();
})();
