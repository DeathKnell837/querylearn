/**
 * QueryLearn — Homepage Interactive & Animation Scripts
 * - Typewriter Code Comparison (SQL Declarative vs Python Procedural)
 * - Scroll Reveal via IntersectionObserver
 * - prefers-reduced-motion accessibility
 */

(function () {
  'use strict';

  // --- Accessibility Check ---
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  let prefersReducedMotion = motionQuery.matches;

  motionQuery.addEventListener('change', function (e) {
    prefersReducedMotion = e.matches;
    if (prefersReducedMotion) {
      stopTypewriter();
      renderStaticCode(currentLang);
    } else {
      startTypewriter(currentLang);
    }
  });

  // --- Code Snippets for the Task ---
  // Task: List the names of all courses in alphabetical order
  const SNIPPETS = {
    sql: {
      lang: 'sql',
      badge: 'SQL, declarative',
      code: `SELECT course_name
FROM Courses
ORDER BY course_name ASC;`
    },
    python: {
      lang: 'python',
      badge: 'Python, procedural, in-memory',
      code: `result = []
for c in courses:
    result.append(c['course_name'])
result.sort()`
    }
  };

  // --- HTML Escaping Helper ---
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // --- Syntax Highlighting Formatter ---
  function highlightCode(rawCode, language) {
    let escaped = escapeHtml(rawCode);

    if (language === 'sql') {
      // String literals
      escaped = escaped.replace(/('[^']*')/g, '<span class="hp-syn-str">$1</span>');
      // Numbers
      escaped = escaped.replace(/\b(\d+)\b/g, '<span class="hp-syn-num">$1</span>');
      // SQL Keywords
      const sqlKeywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER BY', 'GROUP BY', 'HAVING', 'ASC', 'DESC', 'LIMIT', 'JOIN', 'ON', 'AS'];
      const kwRegex = new RegExp('\\b(' + sqlKeywords.join('|') + ')\\b', 'g');
      escaped = escaped.replace(kwRegex, '<span class="hp-syn-kw">$1</span>');
      // Known tables
      escaped = escaped.replace(/\b(Courses)\b/g, '<span class="hp-syn-fn">$1</span>');
      // Columns
      escaped = escaped.replace(/\b(course_name|course_id)\b/g, '<span class="hp-syn-prop">$1</span>');
    } else if (language === 'python') {
      // String literals
      escaped = escaped.replace(/('[^']*')/g, '<span class="hp-syn-str">$1</span>');
      // Numbers
      escaped = escaped.replace(/\b(\d+)\b/g, '<span class="hp-syn-num">$1</span>');
      // Python Keywords
      const pyKeywords = ['for', 'in', 'if', 'else', 'elif', 'and', 'or', 'not', 'def', 'return', 'lambda'];
      const kwRegex = new RegExp('\\b(' + pyKeywords.join('|') + ')\\b', 'g');
      escaped = escaped.replace(kwRegex, '<span class="hp-syn-kw">$1</span>');
      // Built-in functions / methods
      escaped = escaped.replace(/\b(append|sort|print|len|range)\b/g, '<span class="hp-syn-fn">$1</span>');
      // Variable names
      escaped = escaped.replace(/\b(result|courses|c)\b/g, '<span class="hp-syn-prop">$1</span>');
    }

    return escaped;
  }

  // --- DOM Elements ---
  const codeElem = document.getElementById('hp-typed-code');
  const lineNumbersElem = document.getElementById('hp-line-numbers');
  const langStatusElem = document.getElementById('hp-lang-status');
  const tabSql = document.getElementById('hp-tab-sql');
  const tabPy = document.getElementById('hp-tab-python');

  let currentLang = 'sql';
  let charIndex = 0;
  let typeTimer = null;
  let pauseTimer = null;

  function updateTabsUI(activeLang) {
    if (tabSql && tabPy) {
      if (activeLang === 'sql') {
        tabSql.classList.add('active');
        tabSql.setAttribute('aria-selected', 'true');
        tabPy.classList.remove('active');
        tabPy.setAttribute('aria-selected', 'false');
      } else {
        tabPy.classList.add('active');
        tabPy.setAttribute('aria-selected', 'true');
        tabSql.classList.remove('active');
        tabSql.setAttribute('aria-selected', 'false');
      }
    }
    if (langStatusElem) {
      langStatusElem.textContent = SNIPPETS[activeLang].badge;
    }
  }

  function updateLineNumbers(text) {
    if (!lineNumbersElem) return;
    const lines = text.split('\n').length;
    let html = '';
    for (let i = 1; i <= Math.max(lines, 1); i++) {
      html += `<span>${i}</span>`;
    }
    lineNumbersElem.innerHTML = html;
  }

  function renderStaticCode(lang) {
    if (!codeElem) return;
    updateTabsUI(lang);
    const fullText = SNIPPETS[lang].code;
    codeElem.innerHTML = highlightCode(fullText, lang);
    updateLineNumbers(fullText);
  }

  function stopTypewriter() {
    if (typeTimer) {
      clearInterval(typeTimer);
      typeTimer = null;
    }
    if (pauseTimer) {
      clearTimeout(pauseTimer);
      pauseTimer = null;
    }
  }

  function startTypewriter(lang) {
    stopTypewriter();
    currentLang = lang;
    charIndex = 0;
    updateTabsUI(lang);

    const fullText = SNIPPETS[lang].code;
    const totalChars = fullText.length;
    const typingSpeed = lang === 'sql' ? 32 : 24; // Smooth typing cadence

    typeTimer = setInterval(function () {
      charIndex++;
      const currentSlice = fullText.slice(0, charIndex);
      if (codeElem) {
        codeElem.innerHTML = highlightCode(currentSlice, lang);
      }
      updateLineNumbers(currentSlice);

      if (charIndex >= totalChars) {
        clearInterval(typeTimer);
        typeTimer = null;

        // Pause on completed code before switching (SQL: 3.5s, Python: 4.2s)
        const pauseDuration = lang === 'sql' ? 3500 : 4200;
        pauseTimer = setTimeout(function () {
          const nextLang = lang === 'sql' ? 'python' : 'sql';
          startTypewriter(nextLang);
        }, pauseDuration);
      }
    }, typingSpeed);
  }

  // --- Tab Click Handlers (Allows User to Manually Switch) ---
  if (tabSql) {
    tabSql.addEventListener('click', function () {
      if (currentLang === 'sql' && typeTimer) return;
      if (prefersReducedMotion) {
        renderStaticCode('sql');
      } else {
        startTypewriter('sql');
      }
    });
  }

  if (tabPy) {
    tabPy.addEventListener('click', function () {
      if (currentLang === 'python' && typeTimer) return;
      if (prefersReducedMotion) {
        renderStaticCode('python');
      } else {
        startTypewriter('python');
      }
    });
  }

  // --- Scroll Reveal Animations with IntersectionObserver ---
  function initScrollReveal() {
    const cards = document.querySelectorAll('.hp-feature-card');
    if (!cards.length) return;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      cards.forEach(function (card) {
        card.classList.add('hp-revealed');
      });
      return;
    }

    const observerOptions = {
      root: null,
      rootMargin: '0px 0px -40px 0px',
      threshold: 0.15
    };

    const cardObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('hp-revealed');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    cards.forEach(function (card) {
      cardObserver.observe(card);
    });
  }

  // --- Initialize on DOMContentLoaded ---
  document.addEventListener('DOMContentLoaded', function () {
    initScrollReveal();

    if (prefersReducedMotion) {
      renderStaticCode('sql');
    } else {
      // Start typing after initial hero entry animations settle (~400ms)
      setTimeout(function () {
        startTypewriter('sql');
      }, 450);
    }
  });

})();
