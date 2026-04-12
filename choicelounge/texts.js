/**
 * Choice Lounge - Site Text Loader
 *
 * 텍스트 수정 방법:
 *   texts.json 을 편집한 뒤 페이지를 새로고침하면 반영됩니다.
 *
 * HTML 사용법:
 *   <element data-i18n="stats.title">기본값</element>
 *   <element data-i18n-attr="placeholder:hero.scroll">기본값</element>
 *
 * 배열 인덱스 접근:
 *   data-i18n="stats.items.0.num"
 */
(function () {
  // texts.json 경로: 페이지 깊이와 무관하게 동일한 위치에서 로드
  var depth = location.pathname.replace(/\/[^/]*$/, '').replace(/^\//, '').split('/').filter(Boolean).length;
  var base = depth > 0 ? '../'.repeat(depth) : './';
  var jsonPath = base + 'texts.json';

  fetch(jsonPath)
    .then(function (r) { return r.json(); })
    .then(function (texts) {
      // 전역 접근용 (인라인 스크립트에서 CL_TEXTS.hero.typingWords 처럼 사용)
      window.CL_TEXTS = texts;

      // data-i18n 속성으로 텍스트 치환
      document.querySelectorAll('[data-i18n]').forEach(function (el) {
        var val = resolve(texts, el.getAttribute('data-i18n'));
        if (val !== null) el.textContent = val;
      });

      // data-i18n-html 속성으로 innerHTML 치환
      document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
        var val = resolve(texts, el.getAttribute('data-i18n-html'));
        if (val !== null) el.innerHTML = val;
      });

      // data-i18n-attr="attrName:key.path" 형식으로 속성값 치환
      // 예) data-i18n-attr="href:contact.phone" → href="01012345678"
      document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
        el.getAttribute('data-i18n-attr').split(',').forEach(function (pair) {
          var parts = pair.trim().split(':');
          if (parts.length < 2) return;
          var attr = parts[0];
          var key  = parts.slice(1).join(':');
          var val  = resolve(texts, key);
          if (val !== null) el.setAttribute(attr, val);
        });
      });

      // <title> 치환: <title data-i18n-title="page.home.title">…</title>
      var titleEl = document.querySelector('title[data-i18n-title]');
      if (titleEl) {
        var val = resolve(texts, titleEl.getAttribute('data-i18n-title'));
        if (val !== null) document.title = val;
      }

      // 이벤트: 텍스트 로드 완료 후 추가 처리가 필요한 경우
      document.dispatchEvent(new CustomEvent('cl:texts-loaded', { detail: texts }));
    })
    .catch(function (err) {
      console.warn('[texts.js] texts.json 로드 실패:', err);
    });

  /** dot-notation 키로 중첩 객체 접근 (e.g. "stats.items.0.num") */
  function resolve(obj, path) {
    var result = path.split('.').reduce(function (o, k) {
      return o != null ? o[k] : null;
    }, obj);
    return result != null ? result : null;
  }
})();
