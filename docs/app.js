const JSON_URL = './daily.json';
const list = document.getElementById('list');
const gen = document.getElementById('generated');
const btn = document.getElementById('refresh');

async function load() {
  try {
    const res = await fetch(JSON_URL + `?t=${Date.now()}`);
    const data = await res.json();
    gen.textContent = `Updated ${new Date(data.generated_at).toLocaleString()}`;
    list.innerHTML = '';
    for (const it of data.items) {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="meta"><span class="tag">${it.tag}</span><span>${it.source_domain}</span><span>${it.published_ts ? new Date(it.published_ts*1000).toLocaleDateString() : ''}</span></div>
        <div class="title"><a href="${it.link}" target="_blank" rel="noopener">${it.title}</a></div>
        <div class="summary">${escapeHtml(it.summary)}</div>
      `;
      list.appendChild(card);
    }
  } catch (e) {
    gen.textContent = 'Offline or failed to load.';
  }
}
btn.addEventListener('click', load);
load();

function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
