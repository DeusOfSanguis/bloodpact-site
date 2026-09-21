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

  /* ---------- Прелоадер (только главная, ~1.5 сек) ---------- */
  (function () {
    var pre = document.querySelector(".preloader");
    if (!pre) return;
    var num = pre.querySelector("[data-count]");
    var fill = pre.querySelector(".preloader__fill");
    document.body.style.overflow = "hidden";
    var start = performance.now(), dur = 1400;
    function tick(t) {
      var p = Math.min(1, (t - start) / dur);
      if (num) num.textContent = Math.round(p * 100) + "%";
      if (fill) fill.style.transform = "scaleX(" + p + ")";
      if (p < 1) requestAnimationFrame(tick);
      else setTimeout(function () {
        pre.classList.add("done");
        document.body.style.overflow = "";
        setTimeout(function () { pre.remove(); }, 1000);
      }, 350);
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

  /* ---------- Аккордеон: открыта только одна вкладка ---------- */
  (function () {
    document.querySelectorAll("[data-acc]").forEach(function (group) {
      group.querySelectorAll("details").forEach(function (d) {
        d.addEventListener("toggle", function () {
          if (d.open) group.querySelectorAll("details").forEach(function (o) { if (o !== d) o.open = false; });
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

  /* ---------- Видео на обложке: грузится ТОЛЬКО по клику ----------
     (Пока не нажали ▶ — видна картинка, поэтому обложка не бывает чёрной,
     даже если YouTube заблокирован или не грузится.) */
  (function () {
    document.querySelectorAll("[data-yt]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-yt");
        var scope = btn.closest(".hero");
        var slot = scope ? scope.querySelector(".hero__video") : null;
        if (!id || !slot) return;
        var src = "https://www.youtube-nocookie.com/embed/" + id +
          "?autoplay=1&mute=1&controls=1&loop=1&playlist=" + id +
          "&rel=0&modestbranding=1&playsinline=1";
        slot.innerHTML = '<iframe src="' + src + '" title="Видео" ' +
          'allow="autoplay; encrypted-media; fullscreen" allowfullscreen ' +
          'referrerpolicy="strict-origin-when-cross-origin"></iframe>';
        slot.classList.add("on");
        btn.style.display = "none";
      });
    });
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
