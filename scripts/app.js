(function () {
  'use strict';

  const menuBtn = document.querySelector('.menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }

  document.querySelectorAll('.wds-tabber').forEach(function (tabber) {
    const tabs = Array.from(tabber.querySelectorAll('.wds-tabs__tab'));
    const panes = Array.from(tabber.querySelectorAll(':scope > .wds-tab__content'));
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function (e) {
        e.preventDefault();
        tabs.forEach(function (t) { t.classList.remove('wds-is-current'); });
        panes.forEach(function (p) { p.classList.remove('wds-is-current'); });
        tab.classList.add('wds-is-current');
        if (panes[i]) panes[i].classList.add('wds-is-current');
      });
    });
  });

  document.querySelectorAll('[class*="mw-customtoggle-"]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (e.target.closest('a') && e.target.closest('a') !== el) return;
      const names = [];
      el.className.split(/\s+/).forEach(function (c) {
        if (c.indexOf('mw-customtoggle-') === 0) names.push(c.slice('mw-customtoggle-'.length));
      });
      names.forEach(function (name) {
        document.querySelectorAll('#mw-customcollapsible-' + name + ', .mw-customcollapsible-' + name).forEach(function (target) {
          target.classList.toggle('mw-collapsed');
        });
      });
    });
  });

  document.querySelectorAll('#work_preference_table_shift').forEach(function (btn) {
    btn.style.cursor = 'pointer';
    btn.addEventListener('click', function () {
      ['mw-customcollapsible-work_preference_table_stat', 'mw-customcollapsible-work_preference_table_level'].forEach(function (id) {
        const node = document.getElementById(id);
        if (node) node.classList.toggle('mw-collapsed');
      });
    });
  });

  const abInputHost = document.getElementById('Abnormality-search-input');
  if (abInputHost) {
    const wrap = document.createElement('div');
    const input = document.createElement('input');
    input.type = 'search';
    input.placeholder = '异想体编号 / 名称';
    input.setAttribute('aria-label', '筛选异想体');
    input.style.width = 'min(100%, 280px)';
    input.style.padding = '8px 10px';
    input.style.background = '#221f18';
    input.style.border = '1px solid #3d3828';
    input.style.color = '#e6e1d1';
    wrap.appendChild(input);
    abInputHost.appendChild(wrap);
    const loading = document.getElementById('Abnormality-search-loading');
    if (loading) loading.style.display = 'none';
    input.addEventListener('input', function () {
      const q = input.value.toLowerCase().trim();
      document.querySelectorAll('.Abnormality-search-item').forEach(function (item) {
        const hit = !q || (item.textContent || '').toLowerCase().indexOf(q) !== -1;
        item.classList.toggle('hidden', !hit);
      });
    });
  }

  const searchForm = document.querySelector('.searchbox');
  const searchInput = searchForm && searchForm.querySelector('input[name="q"]');
  if (searchForm && searchInput && /search\.html$/.test(location.pathname)) {
    const params = new URLSearchParams(location.search);
    if (params.get('q') && !searchInput.value) searchInput.value = params.get('q');
  }

  const resultsHost = document.getElementById('search-results');
  if (resultsHost) {
    const assetsPrefix = resultsHost.getAttribute('data-assets') || './assets/';
    const q = (new URLSearchParams(location.search).get('q') || '').trim();
    const qbox = document.getElementById('q-display');
    if (qbox) qbox.textContent = q ? '“' + q + '”' : '全部条目';
    fetch(assetsPrefix + 'search.json')
      .then(function (r) { return r.json(); })
      .then(function (items) {
        const needle = q.toLowerCase();
        const hits = needle
          ? items.map(function (it) {
              const title = (it.title + ' ' + (it.display || '')).toLowerCase();
              const blob = (title + ' ' + (it.text || '') + ' ' + (it.categories || []).join(' ')).toLowerCase();
              if (blob.indexOf(needle) === -1) return null;
              var rank = 3;
              if (title.indexOf(needle) !== -1) rank = 0;
              else if ((it.title || '').toLowerCase().indexOf(needle) !== -1) rank = 1;
              else if ((it.categories || []).join(' ').toLowerCase().indexOf(needle) !== -1) rank = 2;
              return { it: it, rank: rank };
            }).filter(Boolean).sort(function (a, b) { return a.rank - b.rank; }).slice(0, 80).map(function (x) { return x.it; })
          : items.slice(0, 40);
        if (!hits.length) {
          resultsHost.innerHTML = '<p class="empty">没有找到匹配条目。试试编号（如 O-03-03）或中文名。</p>';
          return;
        }
        resultsHost.innerHTML = hits.map(function (it) {
          const cats = (it.categories || []).slice(0, 4).join(' · ');
          return '<a class="search-hit" href="' + it.href + '"><b>' + escapeHtml(it.title) + '</b><small>' +
            escapeHtml(it.snippet || it.text || '') + (cats ? ' · ' + escapeHtml(cats) : '') + '</small></a>';
        }).join('');
      })
      .catch(function () {
        resultsHost.innerHTML = '<p class="empty">搜索索引未能加载。</p>';
      });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
})();
