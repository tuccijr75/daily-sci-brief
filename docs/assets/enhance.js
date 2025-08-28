/* docs/assets/enhance.js — additive, defensive, no dependencies */
(function(){
  const $ = (sel, root=document)=>root.querySelector(sel);
  const $$ = (sel, root=document)=>Array.from(root.querySelectorAll(sel));

  function cards(){
    // be defensive: accept several common card containers
    const candidates = $$('.brief-card, .card, [data-card], main article, .grid > div');
    // keep only elements that look like a result: has a link title + some text
    return candidates.filter(el=>{
      const h = el.querySelector("h2 a, h3 a, a[href]");
      const hasText = (el.textContent||"").trim().length > 40;
      return h && hasText;
    });
  }

  // Extract lightweight facets from visible text
  function getFacets(el){
    const txt = el.textContent.toLowerCase();
    const f = new Set();
    // broad buckets
    if (/\b(arxiv|preprint)\b/.test(txt)) f.add("Preprint");
    if (/\bpeer[-\s]?review/.test(txt))   f.add("Peer-reviewed");
    if (/\bbenchmark|sota|mmlu|leaderboard|winogrande|humaneval\b/.test(txt)) f.add("Benchmark");
    if (/\brobot|robotics|manipulation|control\b/.test(txt)) f.add("Robotics");
    if (/\bllm|language model|gpt|agent\b/.test(txt)) f.add("AI/ML");
    if (/\bbio|protein|genomics|cell|medical|health|drug\b/.test(txt)) f.add("Bio/Med");
    if (/\bmaterials?|battery|semiconductor|quantum\b/.test(txt)) f.add("Physical Sci");
    if (/\bpolicy|ethics|safety|governance\b/.test(txt)) f.add("Policy");
    if (/\bstartup|industry|open source|release|product\b/.test(txt)) f.add("Industry");
    return f;
  }

  // Build toolbar
  function buildToolbar(){
    const host = document.createElement('div');
    host.className = 'dsb-toolbar';
    host.innerHTML = `
      <div class="dsb-row">
        <span class="dsb-pill">Filters:</span>
        <button class="dsb-chip" data-chip="AI/ML">AI/ML</button>
        <button class="dsb-chip" data-chip="Robotics">Robotics</button>
        <button class="dsb-chip" data-chip="Bio/Med">Bio/Med</button>
        <button class="dsb-chip" data-chip="Physical Sci">Physical Sci</button>
        <button class="dsb-chip" data-chip="Policy">Policy</button>
        <button class="dsb-chip" data-chip="Industry">Industry</button>
        <button class="dsb-chip" data-chip="Benchmark">Benchmark</button>
        <button class="dsb-chip" data-chip="Peer-reviewed">Peer-reviewed</button>
        <button class="dsb-chip" data-chip="Preprint">Preprint</button>
        <span class="dsb-spacer"></span>
        <input class="dsb-input" id="dsb-q" placeholder="Search title/summary…" />
        <button class="dsb-chip" id="dsb-compact" title="Toggle compact view">Compact</button>
      </div>
    `;
    document.body.prepend(host);
    return host;
  }

  function apply(){
    const q = $('#dsb-q')?.value.trim().toLowerCase() || '';
    const want = new Set($$('.dsb-chip[data-active="1"]').map(b=>b.getAttribute('data-chip')));
    const list = cards();

    list.forEach(card=>{
      const facets = getFacets(card);
      const text = (card.textContent||'').toLowerCase();
      const matchQ = !q || text.includes(q);
      const matchChips = (want.size===0) || [...want].every(c=>facets.has(c));
      card.style.display = (matchQ && matchChips) ? '' : 'none';
      if (matchQ && matchChips) card.classList.add('dsb-card-up'); else card.classList.remove('dsb-card-up');
    });
  }

  function wire(){
    const bar = buildToolbar();
    // chip toggles
    $$('.dsb-chip[data-chip]', bar).forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const on = btn.getAttribute('data-active')==='1';
        btn.setAttribute('data-active', on ? '0' : '1');
        apply();
      });
    });
    // search
    $('#dsb-q', bar)?.addEventListener('input', ()=>{
      // small debounce
      clearTimeout(window.__dsb_t); window.__dsb_t=setTimeout(apply, 120);
    });
    // compact
    $('#dsb-compact', bar)?.addEventListener('click', ()=>{
      const root = document.documentElement;
      const enable = !root.classList.contains('dsb-compact');
      root.classList.toggle('dsb-compact', enable);
      $('#dsb-compact').setAttribute('data-active', enable ? '1' : '0');
    });

    apply();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else wire();
})();
