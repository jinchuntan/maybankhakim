// dash-shim.js
// A small stand-in for the Claude dashboard runtime, so that dashboard/page.html
// also runs in a normal browser (for example on GitHub Pages).
// It gives the page the same `dash` functions that it uses inside Claude:
// dash.loader, dash.calc, dash.draw, dash.data, dash.onData and dash.colors.
// The data files come from window.DASH_SOURCES, which index.html sets.

(function () {
  const loaders = {};
  const calcs = {};
  const draws = {};
  const dataFns = [];
  const state = {};
  let cache = {};

  function data(id) {
    if (state[id]) return state[id];
    if (calcs[id]) {
      if (!cache[id]) cache[id] = computeCalc(id);
      return cache[id];
    }
    return { status: 'missing', data: [] };
  }

  function computeCalc(id) {
    const c = calcs[id];
    const inputs = c.inputs.map(data);
    const notReady = inputs.find((d) => d.status !== 'ok');
    if (notReady) return { status: notReady.status, data: null, message: notReady.message };
    try {
      return { status: 'ok', data: c.fn(...inputs.map((d) => d.data)) };
    } catch (e) {
      console.error('calc ' + id, e);
      return { status: 'error', data: null, message: e.message };
    }
  }

  function render() {
    cache = {};
    dataFns.forEach((fn) => {
      try { fn(); } catch (e) { console.error('onData', e); }
    });
    Object.keys(draws).forEach((name) => {
      document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
        if (el.closest('[hidden]')) return;
        try { draws[name](el); } catch (e) { console.error('draw ' + name, e); }
      });
    });
  }

  async function load() {
    const sources = window.DASH_SOURCES || {};
    Object.keys(sources).forEach((id) => { state[id] = { status: 'loading', data: [] }; });
    render();
    await Promise.all(Object.entries(sources).map(async ([id, url]) => {
      try {
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) throw new Error(url + ': HTTP ' + res.status);
        const text = await res.text();
        const out = loaders[id] ? await loaders[id].fn({ answer: text }) : d3.csvParse(text);
        const rows = Array.isArray(out) ? out : (out.rows || out.data || []);
        state[id] = { status: 'ok', data: rows };
      } catch (e) {
        console.error('source ' + id, e);
        state[id] = { status: 'error', data: [], message: e.message };
      }
    }));
    render();
  }

  let timer = null;
  window.addEventListener('resize', () => {
    clearTimeout(timer);
    timer = setTimeout(render, 150);
  });

  window.dash = {
    loader: (id, opts) => { loaders[id] = opts; },
    calc: (id, opts) => { calcs[id] = opts; },
    draw: (name, fn) => {
      if (typeof fn === 'function') draws[name] = fn;
      else render();
    },
    data,
    onData: (fn) => {
      dataFns.push(fn);
      try { fn(); } catch (e) { console.error('onData', e); }
    },
    colors: ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)'],
    refresh: () => load(),
    params: () => ({}),
    setParams: () => {},
    resetParams: () => {},
    setLink: () => {},
  };

  window.dashStart = load;
})();
