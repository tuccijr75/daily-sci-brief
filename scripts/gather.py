import os, re, json, hashlib, time, csv, math, textwrap
archive_write('docs', daily)
# END

import time
archive_write('docs', daily)
# END

from datetime import datetime, timedelta, timezone
archive_write('docs', daily)
# END

import feedparser, tldextract
archive_write('docs', daily)
# END

from bs4 import BeautifulSoup
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

# --- Load config ---
archive_write('docs', daily)
# END

import yaml
archive_write('docs', daily)
# END

with open("config/sources.yaml", "r", encoding="utf-8") as f:
archive_write('docs', daily)
# END

    CFG = yaml.safe_load(f)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

FEEDS = CFG.get("feeds", [])
archive_write('docs', daily)
# END

PEER_DOMAINS = set(CFG.get("peer_review_domains", []))
archive_write('docs', daily)
# END

CATEGORIES = CFG.get("categories", {})
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

TODAY = datetime.now(timezone.utc)
archive_write('docs', daily)
# END

SINCE = TODAY - timedelta(days=2)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

WATCH = []
archive_write('docs', daily)
# END

if os.path.exists("config/watchlist.txt"):
archive_write('docs', daily)
# END

    with open("config/watchlist.txt", "r", encoding="utf-8") as f:
archive_write('docs', daily)
# END

        WATCH = [w.strip().lower() for w in f if w.strip()]
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

SIG_RE = re.compile("|".join([
archive_write('docs', daily)
# END

  r"state[ -]?of[ -]?the[ -]?art|\bSOTA\b", r"benchmark|surpass|exceed",
archive_write('docs', daily)
# END

  r"human[ -]?level", r"RLHF|RAG|agent", r"clinical trial|phase [I|II|III]",
archive_write('docs', daily)
# END

  r"semiconductor|lithograph|EUV|photonic|materials"
archive_write('docs', daily)
# END

]), re.I)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def strip_html(text): 
archive_write('docs', daily)
# END

    return " ".join(BeautifulSoup(text or "", "html.parser").get_text(" ").split())
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def norm(entry, feed_url):
archive_write('docs', daily)
# END

    link = entry.get("link") or entry.get("id") or ""
archive_write('docs', daily)
# END

    title = (entry.get("title") or "").strip()
archive_write('docs', daily)
# END

    summary = strip_html(entry.get("summary") or entry.get("description") or "")
archive_write('docs', daily)
# END

    ts = None
archive_write('docs', daily)
# END

    for k in ("published_parsed","updated_parsed"):
archive_write('docs', daily)
# END

        if getattr(entry, k, None):
archive_write('docs', daily)
# END

            ts = time.mktime(getattr(entry, k))
archive_write('docs', daily)
# END

            break
archive_write('docs', daily)
# END

    domain = reg_domain(\) or reg_domain(\)
archive_write('docs', daily)
# END

    uid = hashlib.sha1((link or title).encode("utf-8")).hexdigest()
archive_write('docs', daily)
# END

    return {
archive_write('docs', daily)
# END

        "id": uid, "title": title, "link": link, "summary_raw": summary[:3000],
archive_write('docs', daily)
# END

        "source_domain": domain, "published_ts": int(ts) if ts else None
archive_write('docs', daily)
# END

    }
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def tag_category(text):
archive_write('docs', daily)
# END

    t = text.lower()
archive_write('docs', daily)
# END

    for cat, rule in CATEGORIES.items():
archive_write('docs', daily)
# END

        if any(substr in t for substr in rule.get("any", [])):
archive_write('docs', daily)
# END

            return cat
archive_write('docs', daily)
# END

    return "General Tech/Science"
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def is_peer_reviewed(domain, link):
archive_write('docs', daily)
# END

    d = (domain or "").lower()
archive_write('docs', daily)
# END

    if any(d.endswith(pd) for pd in PEER_DOMAINS): 
archive_write('docs', daily)
# END

        return True
archive_write('docs', daily)
# END

    # DOI sniff
archive_write('docs', daily)
# END

    if re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", link): 
archive_write('docs', daily)
# END

        return True
archive_write('docs', daily)
# END

    return False
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def score(it):
archive_write('docs', daily)
# END

    s = 0
archive_write('docs', daily)
# END

    if is_peer_reviewed(it.get("source_domain",""), it.get("link","")): s += 3
archive_write('docs', daily)
# END

    if "arxiv.org" in it.get("source_domain",""): s += 2
archive_write('docs', daily)
# END

    if SIG_RE.search(it.get("title","")) or SIG_RE.search(it.get("summary_raw","")): s += 2
archive_write('docs', daily)
# END

    ts = it.get("published_ts")
archive_write('docs', daily)
# END

    if ts:
archive_write('docs', daily)
# END

        ageh = (TODAY - datetime.fromtimestamp(ts, tz=timezone.utc)).total_seconds()/3600
archive_write('docs', daily)
# END

        s += 2 if ageh <= 24 else (1 if ageh <= 48 else 0)
archive_write('docs', daily)
# END

    # watchlist boost
archive_write('docs', daily)
# END

    t = (it.get("title","") + " " + it.get("summary_raw","")).lower()
archive_write('docs', daily)
# END

    if any(w in t for w in WATCH): s += 3
archive_write('docs', daily)
# END

    return s
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def summarize_extractive(text, max_sent=2):
archive_write('docs', daily)
# END

    sents = re.split(r"(?<=[.!?])\s+", text.strip())
archive_write('docs', daily)
# END

    if not sents: return ""
archive_write('docs', daily)
# END

    # prefer sentences with signal terms
archive_write('docs', daily)
# END

    keyed = sorted(sents, key=lambda s: -len(re.findall(SIG_RE, s)))
archive_write('docs', daily)
# END

    chosen = keyed[:max_sent] if any(re.findall(SIG_RE, text)) else sents[:max_sent]
archive_write('docs', daily)
# END

    out = " ".join(chosen).strip()
archive_write('docs', daily)
# END

    return out[:480]
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def summarize_llm(title, text):
archive_write('docs', daily)
# END

    key = os.getenv("OPENAI_API_KEY")
archive_write('docs', daily)
# END

    if not key: 
archive_write('docs', daily)
# END

        return None
archive_write('docs', daily)
# END

    try:
archive_write('docs', daily)
# END

import requests
archive_write('docs', daily)
# END

# --- added by automation: logging + timed HTTP ---
archive_write('docs', daily)
# END

def log(msg: str) -> None:
archive_write('docs', daily)
# END

    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

try:
archive_write('docs', daily)
# END

    import requests as _requests
archive_write('docs', daily)
# END

    class _TimedRequests:
archive_write('docs', daily)
# END

        def __init__(self, base):
archive_write('docs', daily)
# END

            self._base = base
archive_write('docs', daily)
# END

        def get(self, url, *args, **kwargs):
archive_write('docs', daily)
# END

            kwargs.setdefault('timeout', 8)  # hard cap per-request
archive_write('docs', daily)
# END

            log(f"GET  {url}")
archive_write('docs', daily)
# END

            t0 = time.time()
archive_write('docs', daily)
# END

            try:
archive_write('docs', daily)
# END

                return self._base.get(url, *args, **kwargs)
archive_write('docs', daily)
# END

            finally:
archive_write('docs', daily)
# END

                dt = time.time() - t0
archive_write('docs', daily)
# END

                log(f"DONE {url} ({dt:.1f}s)")
archive_write('docs', daily)
# END

    requests = _TimedRequests(_requests)  # monkey-patch only .get
archive_write('docs', daily)
# END

except Exception as _e:
archive_write('docs', daily)
# END

    print("WARN: timed requests wrapper not installed:", _e, flush=True)
archive_write('docs', daily)
# END

# --- end added block ---import time
archive_write('docs', daily)
# END

        prompt = f"Summarize in 2 tight sentences for a science/tech brief. Title: {title}\nContent: {text[:3000]}"
archive_write('docs', daily)
# END

        headers = {"Authorization": f"Bearer {key}", "Content-Type":"application/json"}
archive_write('docs', daily)
# END

        # OpenAI responses format vary by model; using /v1/chat/completions with a safe default
archive_write('docs', daily)
# END

        body = {
archive_write('docs', daily)
# END

            "model": "gpt-4o-mini",
archive_write('docs', daily)
# END

            "messages": [
archive_write('docs', daily)
# END

                {"role":"system","content":"You write crisp, factual, non-hype scientific summaries."},
archive_write('docs', daily)
# END

                {"role":"user","content": prompt}
archive_write('docs', daily)
# END

            ],
archive_write('docs', daily)
# END

            "temperature": 0.2,
archive_write('docs', daily)
# END

            "max_tokens": 140
archive_write('docs', daily)
# END

        }
archive_write('docs', daily)
# END

        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=20)
archive_write('docs', daily)
# END

        r.raise_for_status()
archive_write('docs', daily)
# END

        data = r.json()
archive_write('docs', daily)
# END

        return data["choices"][0]["message"]["content"].strip()
archive_write('docs', daily)
# END

    except Exception:
archive_write('docs', daily)
# END

        return None
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def main():
archive_write('docs', daily)
# END

    items = []
archive_write('docs', daily)
# END

    for f in FEEDS:
archive_write('docs', daily)
# END

        try:
archive_write('docs', daily)
# END

            d = feedparser.parse(f)
archive_write('docs', daily)
# END

            for e in d.entries:
archive_write('docs', daily)
# END

                it = norm(e, f)
archive_write('docs', daily)
# END

                ts = it.get("published_ts")
archive_write('docs', daily)
# END

                if ts and datetime.fromtimestamp(ts, tz=timezone.utc) < SINCE:
archive_write('docs', daily)
# END

                    continue
archive_write('docs', daily)
# END

                items.append(it)
archive_write('docs', daily)
# END

        except Exception:
archive_write('docs', daily)
# END

            pass
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # dedupe by (title_lower, domain) and by SHA if same link/title
archive_write('docs', daily)
# END

    seen, uniq = set(), []
archive_write('docs', daily)
# END

    for it in items:
archive_write('docs', daily)
# END

        key = (it["title"].strip().lower(), it.get("source_domain",""))
archive_write('docs', daily)
# END

        if key in seen: 
archive_write('docs', daily)
# END

            continue
archive_write('docs', daily)
# END

        seen.add(key)
archive_write('docs', daily)
# END

        uniq.append(it)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # enrich
archive_write('docs', daily)
# END

    for it in uniq:
archive_write('docs', daily)
# END

        text = f'{it["title"]} {it.get("summary_raw","")}'
archive_write('docs', daily)
# END

        it["tag"] = tag_category(text)
archive_write('docs', daily)
# END

        it["peer_reviewed"] = is_peer_reviewed(it.get("source_domain",""), it.get("link",""))
archive_write('docs', daily)
# END

        it["score"] = score(it)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

        # summaries
archive_write('docs', daily)
# END

        llm = summarize_llm(it["title"], it.get("summary_raw",""))
archive_write('docs', daily)
# END

        it["summary"] = llm if llm else summarize_extractive(it.get("summary_raw","") or it["title"])
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

        # bullets
archive_write('docs', daily)
# END

        t = text.lower()
archive_write('docs', daily)
# END

        it["why_new"]      = "New method/benchmark" if re.search(r"benchmark|sota|state[ -]?of", t) else "Fresh results/preprint"
archive_write('docs', daily)
# END

        it["why_matters"]  = "Practical impact likely" if re.search(r"chip|clinical|industry|deployment|production", t) else "Research significance"
archive_write('docs', daily)
# END

        it["caveats"]      = "Peer-reviewed" if it["peer_reviewed"] else ("Preprint â€” not peer reviewed" if "arxiv" in it.get("source_domain","") or re.search(r"biorxiv|medrxiv", t) else "Check replication/details")
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    uniq.sort(key=lambda x: (x["score"], x.get("published_ts") or 0), reverse=True)
archive_write('docs', daily)
# END

    top = uniq[:60]
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # group
archive_write('docs', daily)
# END

    groups = {}
archive_write('docs', daily)
# END

    for it in top:
archive_write('docs', daily)
# END

        groups.setdefault(it["tag"], []).append(it)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    os.makedirs("docs", exist_ok=True)
archive_write('docs', daily)
# END

    out = {
archive_write('docs', daily)
# END

        "generated_at": TODAY.isoformat(),
archive_write('docs', daily)
# END

        "count": sum(len(v) for v in groups.values()),
archive_write('docs', daily)
# END

        "groups": [{"category": k, "items": v} for k, v in groups.items()]
archive_write('docs', daily)
# END

    }
archive_write('docs', daily)
# END

    with open("docs/daily.json","w",encoding="utf-8") as f:
archive_write('docs', daily)
# END

        json.dump(out, f, indent=2, ensure_ascii=False)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # CSV export
archive_write('docs', daily)
# END

    csv_path = "docs/daily.csv"
archive_write('docs', daily)
# END

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
archive_write('docs', daily)
# END

        w = csv.writer(f)
archive_write('docs', daily)
# END

        w.writerow(["category","title","link","source","published_ts","score","peer_reviewed","summary"])
archive_write('docs', daily)
# END

        for g in out["groups"]:
archive_write('docs', daily)
# END

            for it in g["items"]:
archive_write('docs', daily)
# END

                w.writerow([g["category"], it["title"], it["link"], it["source_domain"], it.get("published_ts",""), it["score"], it["peer_reviewed"], it["summary"]])
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # RSS export
archive_write('docs', daily)
# END

    feed = []
archive_write('docs', daily)
# END

    feed.append('<?xml version="1.0" encoding="UTF-8"?>')
archive_write('docs', daily)
# END

    feed.append('<rss version="2.0"><channel>')
archive_write('docs', daily)
# END

    feed.append(f"<title>Science & AI Brief</title>")
archive_write('docs', daily)
# END

    feed.append(f"<link>https://{os.getenv('GITHUB_REPOSITORY','').split('/')[0]}.github.io/{os.getenv('GITHUB_REPOSITORY','').split('/')[-1]}/</link>")
archive_write('docs', daily)
# END

    feed.append(f"<description>Auto-curated daily brief</description>")
archive_write('docs', daily)
# END

    feed.append(f"<lastBuildDate>{TODAY.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>")
archive_write('docs', daily)
# END

    for g in out["groups"]:
archive_write('docs', daily)
# END

        for it in g["items"][:12]:
archive_write('docs', daily)
# END

            pub = ""
archive_write('docs', daily)
# END

            if it.get("published_ts"):
archive_write('docs', daily)
# END

                pub = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
archive_write('docs', daily)
# END

            desc = BeautifulSoup(it.get("summary",""), "html.parser").get_text(" ")
archive_write('docs', daily)
# END

            feed.append("<item>")
archive_write('docs', daily)
# END

            feed.append(f"<title><![CDATA[{it['title']}]]></title>")
archive_write('docs', daily)
# END

            feed.append(f"<link>{it['link']}</link>")
archive_write('docs', daily)
# END

            feed.append(f"<guid isPermaLink='false'>{it['id']}</guid>")
archive_write('docs', daily)
# END

            if pub: feed.append(f"<pubDate>{pub}</pubDate>")
archive_write('docs', daily)
# END

            feed.append(f"<category>{g['category']}</category>")
archive_write('docs', daily)
# END

            feed.append(f"<description><![CDATA[{desc}]]></description>")
archive_write('docs', daily)
# END

            feed.append("</item>")
archive_write('docs', daily)
# END

    feed.append("</channel></rss>")
archive_write('docs', daily)
# END

    with open("docs/feed.xml","w",encoding="utf-8") as f:
archive_write('docs', daily)
# END

        f.write("\n".join(feed))
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    print(f"âœ… Collected {out['count']} items in {len(out['groups'])} groups. CSV+RSS exported.")
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

if __name__ == "__main__":
archive_write('docs', daily)
# END

    main()
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

# ===== Archive helpers (added) =====
archive_write('docs', daily)
# END

def _safe_mkdir(path: str):
archive_write('docs', daily)
# END

    os.makedirs(path, exist_ok=True)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def _write_json(path: str, obj):
archive_write('docs', daily)
# END

    with open(path, 'w', encoding='utf-8') as f:
archive_write('docs', daily)
# END

        json.dump(obj, f, ensure_ascii=False, indent=2)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def _read_json(path: str, default):
archive_write('docs', daily)
# END

    try:
archive_write('docs', daily)
# END

        with open(path, 'r', encoding='utf-8') as f:
archive_write('docs', daily)
# END

            return json.load(f)
archive_write('docs', daily)
# END

    except Exception:
archive_write('docs', daily)
# END

        return default
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

def archive_write(docroot: str, daily_obj: dict):
archive_write('docs', daily)
# END

    # daily_obj is the final object you already assemble (with "generated_at", "groups", etc.)
archive_write('docs', daily)
# END

    # Derive YYYY-MM-DD in ET for clarity (matches your site design)
archive_write('docs', daily)
# END

    try:
archive_write('docs', daily)
# END

        # generated_at is ISO UTC: convert to date in America/New_York on render side if needed
archive_write('docs', daily)
# END

        # here we just use UTC date so itâ€™s deterministic in Actions
archive_write('docs', daily)
# END

        day = datetime.utcnow().strftime('%Y-%m-%d')
archive_write('docs', daily)
# END

    except Exception:
archive_write('docs', daily)
# END

        day = 'unknown'
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    rec_dir = os.path.join(docroot, 'records')
archive_write('docs', daily)
# END

    _safe_mkdir(rec_dir)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # 1) Write per-day snapshot
archive_write('docs', daily)
# END

    perday_path = os.path.join(rec_dir, f'{day}.json')
archive_write('docs', daily)
# END

    _write_json(perday_path, daily_obj)
archive_write('docs', daily)
# END


archive_write('docs', daily)
# END

    # 2) Maintain index.json: [{date, count}]
archive_write('docs', daily)
# END

    idx_path = os.path.join(rec_dir, 'index.json')
archive_write('docs', daily)
# END

    idx = _read_json(idx_path, [])
archive_write('docs', daily)
# END

    # update or insert
archive_write('docs', daily)
# END

    count = 0
archive_write('docs', daily)
# END

    try:
archive_write('docs', daily)
# END

        for g in daily_obj.get('groups', []):
archive_write('docs', daily)
# END

            count += len(g.get('items', []))
archive_write('docs', daily)
# END

    except Exception:
archive_write('docs', daily)
# END

        pass
archive_write('docs', daily)
# END

    # replace existing record for the day if present
archive_write('docs', daily)
# END

    idx = [r for r in idx if r.get('date') != day]
archive_write('docs', daily)
# END

    idx.append({'date': day, 'count': count})
archive_write('docs', daily)
# END

    # keep newest first
archive_write('docs', daily)
# END

    idx.sort(key=lambda r: r.get('date',''), reverse=True)
archive_write('docs', daily)
# END

    _write_json(idx_path, idx)
archive_write('docs', daily)
# END

# ===== End helpers =====
archive_write('docs', daily)
# END


# Post-pass hook to enhance all item summaries if enabled
def postprocess_enhance(daily):
    try:
        for g in daily.get("groups", []):
            for it in g.get("items", []):
                # Only enhance short/plain summaries (skip if already good)
                base = it.get("summary") or it.get("summary_raw") or ""
                if base:
                    it["summary"] = enhance_summary(it)
        return daily
    except Exception:
        return daily

daily = postprocess_enhance(daily)

# ===== LLM summary enhancement (OpenAI -> Anthropic -> Gemini) =====
import time, textwrap, requests

def _shorten(txt, limit=9000):
    if txt and len(txt) > limit:
        return txt[:limit] + " …"
    return txt

def _call_openai(prompt, api_key, model="gpt-4o-mini"):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [{"role": "system", "content": "You are a concise scientific editor."},
                     {"role": "user",   "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 280
    }
    r = requests.post(url, headers=headers, json=body, timeout=60); r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def _call_anthropic(prompt, api_key, model="claude-3-haiku-20240307"):
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type":"application/json"}
    body = {"model": model, "max_tokens": 280, "temperature": 0.2, "messages": [{"role":"user","content": prompt}]}
    r = requests.post(url, headers=headers, json=body, timeout=60); r.raise_for_status()
    return r.json()["content"][0]["text"].strip()

def _call_gemini(prompt, api_key, model="gemini-1.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type":"application/json"}
    body = {"contents":[{"parts":[{"text": prompt}]}], "generationConfig":{"temperature":0.2,"maxOutputTokens":280}}
    r = requests.post(url, headers=headers, json=body, timeout=60); r.raise_for_status()
    out = r.json()
    return out["candidates"][0]["content"]["parts"][0]["text"].strip()

def _compose_prompt(title, raw_sum, url, category):
    return textwrap.dedent(f"""
    You rewrite scientific news abstracts into crisp 2–3 sentence summaries for a daily brief.
    Keep it factual, neutral, and readable for a technical but busy audience.
    Include one short impact line starting with "Why it matters:".
    Do not use markdown headings or emojis.

    Title: {title}
    Category: {category}
    Source URL: {url}

    Raw abstract/summary:
    {raw_sum}
    """).strip()

def enhance_summary(item):
    if str(os.getenv("LLM_ENHANCE_SUMMARIES","0")).strip() not in ("1","true","yes"):
        return item.get("summary") or item.get("summary_raw") or ""
    title = item.get("title","")
    raw_sum = item.get("summary") or item.get("summary_raw") or ""
    url = item.get("link","")
    category = item.get("tag") or item.get("category") or ""
    prompt = _compose_prompt(title, _shorten(raw_sum), url, category)

    provider = (os.getenv("SUMMARY_PROVIDER","openai") or "openai").lower().strip()
    order = {"openai":["openai","anthropic","gemini"],
             "anthropic":["anthropic","openai","gemini"],
             "gemini":["gemini","openai","anthropic"]}.get(provider,["openai","anthropic","gemini"])

    for p in order:
        try:
            if p=="openai" and os.getenv("OPENAI_API_KEY"):    return _call_openai(prompt, os.getenv("OPENAI_API_KEY"))
            if p=="anthropic" and os.getenv("ANTHROPIC_API_KEY"): return _call_anthropic(prompt, os.getenv("ANTHROPIC_API_KEY"))
            if p=="gemini" and os.getenv("GEMINI_API_KEY"):    return _call_gemini(prompt, os.getenv("GEMINI_API_KEY"))
        except Exception:
            time.sleep(1.0)
    return raw_sum

def postprocess_enhance(daily):
    try:
        for g in daily.get("groups", []):
            for it in g.get("items", []):
                base = it.get("summary") or it.get("summary_raw") or ""
                if base:
                    it["summary"] = enhance_summary(it)
        return daily
    except Exception:
        return daily
# ===== End LLM enhancement =====
