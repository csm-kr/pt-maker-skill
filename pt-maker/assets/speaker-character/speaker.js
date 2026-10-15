/* pt-maker speaker character helper v2 (owl)
   composition의 inline <script> 맨 앞(장면 timeline 코드보다 먼저)에 그대로 붙여 넣는다.
   build_animated_presentation.py는 composition의 inline script만 발표용 HTML로 옮기므로 <script src>로 불러오지 않는다.
   여러 composition에 중복으로 들어가도 첫 정의만 쓰인다.
   결정성 계약: 모든 변화는 넘겨받은 paused GSAP timeline의 절대 시각에만 추가한다.
   무한 반복, 타이머, 벽시계, 난수, 재생 호출을 쓰지 않는다. DOM 크기를 측정하지 않는다.
   paper-motion 기본값: 포즈와 대사는 트윈 없이 즉시 바뀐다. 깜빡임(blink)과 입 움직임(lipSync)은 요청할 때만 켠다. */
window.PtSpeaker = window.PtSpeaker || (function () {
  "use strict";
  var POSES = ["smile", "o", "wave", "side", "think"];
  /* 한글 중성 21개(ㅏ..ㅣ)별 입 벌림 정도: 넓게 1, 중간 .72, 작게 .45 */
  var VOWEL_OPEN = [1, 1, 1, 1, .72, .72, .72, .72, .72, 1, 1, .45, .72, .72, .72, .72, .45, .72, .45, .45, .45];

  function fail(message) { throw new Error("PtSpeaker: " + message); }

  function finite(value, label) {
    if (typeof value !== "number" || !isFinite(value)) fail(label + " must be a finite number of seconds");
    return value;
  }

  function openness(ch) {
    var code = ch.charCodeAt(0);
    if (code >= 0xac00 && code <= 0xd7a3) return VOWEL_OPEN[Math.floor(((code - 0xac00) % 588) / 28)];
    if (/[0-9A-Za-zㄱ-ㆎ]/.test(ch)) return [.55, .8, 1][code % 3];
    return /\s/.test(ch) ? -0.6 : -1.6;
  }

  /* options: { start, tween: false, lipSync: false }
     start는 t=0 포즈(없으면 root의 data-pose). data-pose는 정지 포즈(인쇄·첫 진입 전)이므로 장면의 마지막 포즈를 적는다.
     tween=true면 포즈를 0.12초 교차, 대사를 짧게 튀어나오게 한다. lipSync=true면 say() 동안 부리가 움직인다. */
  function attach(tl, target, options) {
    if (!tl || typeof tl.to !== "function") fail("attach() needs the composition's paused GSAP timeline");
    var opts = Object.assign({ start: null, tween: false, lipSync: false }, options || {});
    var root = typeof target === "string" ? document.querySelector(target) : target;
    if (!root) fail("speaker root not found: " + target);
    var variants = Array.from(root.querySelectorAll("[data-poses]")).map(function (el) {
      return { el: el, poses: el.getAttribute("data-poses").trim().split(/\s+/) };
    });
    if (!variants.length) fail("speaker has no [data-poses] parts");
    var eyes = Array.from(root.querySelectorAll(".spk-eye"));
    var jaws = Array.from(root.querySelectorAll(".spk-jaw"));
    var bubbles = root.querySelectorAll(".spk-bubble");
    var startPose = opts.start || root.getAttribute("data-pose") || "smile";
    if (POSES.indexOf(startPose) < 0) fail("unknown start pose: " + startPose);

    /* 깜빡임 기준점은 그림 좌표(data-origin)로 고정한다. */
    eyes.forEach(function (el) {
      var origin = el.getAttribute("data-origin");
      if (!origin) fail("every .spk-eye needs data-origin=\"x y\"");
      window.gsap.set(el, { svgOrigin: origin });
    });

    /* t=0 출발 포즈. immediateRender가 없으면 한 번도 렌더되지 않은 timeline의 t=0이
       CSS 정지 포즈로 보여 seek 순서에 따라 첫 프레임이 달라진다. */
    function rest(targets, vars) {
      if (targets.length === 0) return;
      tl.set(targets, Object.assign({ immediateRender: true }, vars), 0);
    }
    variants.forEach(function (v) { rest([v.el], { autoAlpha: v.poses.indexOf(startPose) >= 0 ? 1 : 0 }); });
    rest(eyes, { scaleY: 1 });
    rest(jaws, { y: 0 });
    rest(bubbles, { autoAlpha: 0, scale: 1, y: 0 });

    var api = {
      /* 포즈 교체: smile(기본 진행) | o(놀람·반론) | wave(질문·CTA) | side(내레이션) | think(생각) */
      pose: function (name, at) {
        if (POSES.indexOf(name) < 0) fail("unknown pose: " + name);
        finite(at, "pose time");
        variants.forEach(function (v) {
          var vars = { autoAlpha: v.poses.indexOf(name) >= 0 ? 1 : 0 };
          if (opts.tween) tl.to(v.el, Object.assign({ duration: .12, ease: "none" }, vars), at);
          else tl.set(v.el, vars, at);
        });
        return api;
      },

      /* 정해진 시각마다 한 번 깜빡임(기본 꺼짐: 부르지 않으면 깜빡이지 않는다). */
      blink: function (times) {
        (times || []).forEach(function (t) {
          finite(t, "blink time");
          tl.set(eyes, { scaleY: .1 }, t);
          tl.set(eyes, { scaleY: 1 }, t + .12);
        });
        return api;
      },

      /* index번째 대사를 at~until 동안 보인다. keep=true면 until 뒤에도 남긴다.
         lipSync(attach 옵션 또는 say 옵션)가 켜져 있으면 대사 음절 수만큼 부리를 움직이고 until 전에 닫는다. */
      say: function (index, at, until, sayOptions) {
        var bubble = bubbles[index];
        if (!bubble) fail("speech line #" + index + " not found");
        finite(at, "say start");
        finite(until, "say end");
        if (until <= at + .4) fail("say end must be at least 0.4s after start");
        var o = Object.assign({ keep: false, lipSync: opts.lipSync, syllable: .13 }, sayOptions || {});
        if (opts.tween) {
          tl.fromTo(bubble, { autoAlpha: 0, scale: .9, y: 10 },
            { autoAlpha: 1, scale: 1, y: 0, duration: .18, ease: "power3.out", immediateRender: false }, at);
          if (!o.keep) tl.to(bubble, { autoAlpha: 0, duration: .12, ease: "none" }, until - .12);
        } else {
          tl.set(bubble, { autoAlpha: 1 }, at);
          if (!o.keep) tl.set(bubble, { autoAlpha: 0 }, until);
        }
        if (o.lipSync && jaws.length) {
          var step = o.syllable;
          var limit = until - .2;
          var t = at + .12;
          Array.from(bubble.textContent.trim()).forEach(function (ch) {
            var level = openness(ch);
            if (t + step > limit) return;
            if (level < 0) { t += step * -level; return; }
            tl.to(jaws, { y: 5 * level, duration: step * .42, ease: "sine.out" }, t);
            tl.to(jaws, { y: 0, duration: step * .4, ease: "sine.in" }, t + step * .5);
            t += step;
          });
        }
        return api;
      }
    };
    return api;
  }

  return { version: 2, poses: POSES.slice(), attach: attach };
})();
