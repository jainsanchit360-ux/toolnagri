/* ToolNagri core site script. No external dependencies. */
(function () {
  "use strict";

  // ---------- Mobile nav ----------
  // Deferred to DOMContentLoaded since this script now loads in <head> (so
  // window.ToolNagri is ready before any inline body script runs), meaning
  // the header/nav elements don't exist yet at parse time.
  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector(".nav-toggle");
    var links = document.querySelector(".nav-links");
    if (toggle && links) {
      toggle.addEventListener("click", function () {
        var open = links.classList.toggle("open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
  });

  // ---------- Search ----------
  function scoreMatch(tool, q) {
    q = q.toLowerCase();
    var name = tool.name.toLowerCase();
    if (name === q) return 100;
    if (name.startsWith(q)) return 80;
    if (name.includes(q)) return 60;
    for (var i = 0; i < tool.keywords.length; i++) {
      var k = tool.keywords[i].toLowerCase();
      if (k === q) return 70;
      if (k.includes(q)) return 40;
    }
    if (tool.category.includes(q)) return 20;
    return 0;
  }

  function searchTools(query) {
    if (!query || !query.trim()) return [];
    var results = TOOLS.map(function (t) { return { tool: t, score: scoreMatch(t, query.trim()) }; })
      .filter(function (r) { return r.score > 0; })
      .sort(function (a, b) { return b.score - a.score; })
      .map(function (r) { return r.tool; });
    return results.slice(0, 8);
  }

  function initSearch(inputId, resultsId) {
    var input = document.getElementById(inputId);
    var resultsBox = document.getElementById(resultsId);
    if (!input || !resultsBox) return;

    function render(q) {
      var results = searchTools(q);
      if (!q.trim()) { resultsBox.style.display = "none"; resultsBox.innerHTML = ""; return; }
      if (results.length === 0) {
        resultsBox.innerHTML = '<div class="search-empty">No tools found for "' + escapeHtml(q) + '". Try a different word.</div>';
      } else {
        resultsBox.innerHTML = results.map(function (t) {
          return '<a href="/tools/' + t.slug + '.html"><span class="cat">' + escapeHtml(catName(t.category)) + '</span><br>' + escapeHtml(t.name) + "</a>";
        }).join("");
      }
      resultsBox.style.display = "block";
    }

    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("focus", function () { if (input.value.trim()) render(input.value); });
    document.addEventListener("click", function (e) {
      if (!resultsBox.contains(e.target) && e.target !== input) resultsBox.style.display = "none";
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        var results = searchTools(input.value);
        if (results.length) window.location.href = "/tools/" + results[0].slug + ".html";
      }
      if (e.key === "Escape") resultsBox.style.display = "none";
    });
  }

  function catName(slug) {
    var c = CATEGORIES.find(function (c) { return c.slug === slug; });
    return c ? c.name : slug;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  window.ToolNagri = window.ToolNagri || {};
  window.ToolNagri.initSearch = initSearch;
  window.ToolNagri.searchTools = searchTools;
  window.ToolNagri.escapeHtml = escapeHtml;

  // ---------- Recents / favourites (localStorage, no account) ----------
  var RECENTS_KEY = "tn_recent_tools";
  var FAVS_KEY = "tn_favourite_tools";

  function readList(key) {
    try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) { return []; }
  }
  function writeList(key, list) {
    try { localStorage.setItem(key, JSON.stringify(list)); } catch (e) { /* storage unavailable, fail silently */ }
  }
  function trackRecent(slug) {
    var list = readList(RECENTS_KEY).filter(function (s) { return s !== slug; });
    list.unshift(slug);
    writeList(RECENTS_KEY, list.slice(0, 8));
  }
  function toggleFavourite(slug) {
    var list = readList(FAVS_KEY);
    var i = list.indexOf(slug);
    if (i >= 0) { list.splice(i, 1); } else { list.unshift(slug); }
    writeList(FAVS_KEY, list);
    return list.indexOf(slug) >= 0;
  }
  function isFavourite(slug) { return readList(FAVS_KEY).indexOf(slug) >= 0; }

  window.ToolNagri.trackRecent = trackRecent;
  window.ToolNagri.toggleFavourite = toggleFavourite;
  window.ToolNagri.isFavourite = isFavourite;
  window.ToolNagri.readList = readList;

  // Auto-track current tool page as "recent". Deferred to DOMContentLoaded since this
  // script now loads in <head> (so window.ToolNagri is ready before any inline body
  // script runs), meaning document.body doesn't exist yet at parse time.
  document.addEventListener("DOMContentLoaded", function () {
    var pageSlug = document.body.getAttribute("data-tool-slug");
    if (pageSlug) trackRecent(pageSlug);
  });

  // ---------- Copy-to-clipboard helper ----------
  window.ToolNagri.copyText = function (text, btn) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(function () {
      if (btn) {
        var orig = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(function () { btn.textContent = orig; }, 1500);
      }
    });
  };

  // ---------- Simple analytics event hook (wired to GA only if configured) ----------
  window.ToolNagri.track = function (eventName, params) {
    if (typeof gtag === "function") gtag("event", eventName, params || {});
  };
})();
