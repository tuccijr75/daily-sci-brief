import os, re, json, hashlib, time, csv, math, textwrap
# END

import time
# END

from datetime import datetime, timedelta, timezone
# END

import feedparser, tldextract
# END

from bs4 import BeautifulSoup
# END
# END

# --- Load config ---
# END

import yaml
# END

with open("config/sources.yaml", "r", encoding="utf-8") as f:
    pass
# END

    CFG = yaml.safe_load(f)
# END
# END

FEEDS = CFG.get("feeds", [])
# END

PEER_DOMAINS = set(CFG.get("peer_review_domains", []))
# END

CATEGORIES = CFG.get("categories", {})
# END
# END

TODAY = datetime.now(timezone.utc)
# END

SINCE = TODAY - timedelta(days=2)
# END
# END

WATCH = []
# END

if os.path.exists("config/watchlist.txt"):
True    pass
# END

    with open("config/watchlist.txt", "r", encoding="utf-8") as f:
        pass
# END

        WATCH = [w.strip().lower() for w in f if w.strip()]
# END
# END

SIG_RE = re.compile("|".join([
# END

  r"state[ -]?of[ -]?the[ -]?art|\bSOTA\b", r"benchmark|surpass|exceed",
# END

  r"human[ -]?level", r"RLHF|RAG|agent", r"clinical trial|phase [I|II|III]",
# END

  r"semiconductor|lithograph|EUV|photonic|materials"
# END

]), re.I)
# END
# END

def strip_html(text): 
True    pass
# END

    return " ".join(BeautifulSoup(text or "", "html.parser").get_text(" ").split())
# END
# END

def norm(entry, feed_url):
True    pass
# END

    link = entry.get("link") or entry.get("id") or ""
# END

    title = (entry.get("title") or "").strip()
# END

    summary = strip_html(entry.get("summary") or entry.get("description") or "")
# END

    ts = None
# END

    for k in ("published_parsed","updated_parsed"):
True    pass
# END

        if getattr(entry, k, None):
True    pass
# END

            ts = time.mktime(getattr(entry, k))
# END

            break
# END

    domain = reg_domain() or reg_domain()
# END

    uid = hashlib.sha1((link or title).encode("utf-8")).hexdigest()
# END

    return {
# END

        "id": uid, "title": title, "link": link, "summary_raw": summary[:3000],
# END

        "source_domain": domain, "published_ts": int(ts) if ts else None
# END

    }
# END
# END

def tag_category(text):
True    pass
# END

    t = text.lower()
# END

    for cat, rule in CATEGORIES.items():
True    pass
# END

        if any(substr in t for substr in rule.get("any", [])):
True    pass
# END

            return cat
# END

    return "General Tech/Science"
# END
# END

def is_peer_reviewed(domain, link):
True    pass
# END

    d = (domain or "").lower()
# END

    if any(d.endswith(pd) for pd in PEER_DOMAINS): 
True    pass
# END

        return True
# END

    # DOI sniff
# END

    if re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", link): 
True    pass
# END

        return True
# END

    return False
# END
# END

def score(it):
True    pass
# END

    s = 0
# END

    if is_peer_reviewed(it.get("source_domain",""), it.get("link","")): s += 3
True    pass
# END

    if "arxiv.org" in it.get("source_domain",""): s += 2
True    pass
# END

    if SIG_RE.search(it.get("title","")) or SIG_RE.search(it.get("summary_raw","")): s += 2
True    pass
# END

    ts = it.get("published_ts")
# END

    if ts:
True    pass
# END

        ageh = (TODAY - datetime.fromtimestamp(ts, tz=timezone.utc)).total_seconds()/3600
# END

        s += 2 if ageh <= 24 else (1 if ageh <= 48 else 0)
# END

    # watchlist boost
# END

    t = (it.get("title","") + " " + it.get("summary_raw","")).lower()
# END

    if any(w in t for w in WATCH): s += 3
True    pass
# END

    return s
# END
# END

def summarize_extractive(text, max_sent=2):
True    pass
# END

    sents = re.split(r"(?<=[.!?])\s+", text.strip())
# END

    if not sents: return ""
True    pass
# END

    # prefer sentences with signal terms
# END

    keyed = sorted(sents, key=lambda s: -len(re.findall(SIG_RE, s)))
# END

    chosen = keyed[:max_sent] if any(re.findall(SIG_RE, text)) else sents[:max_sent]
# END

    out = " ".join(chosen).strip()
# END

    return out[:480]
# END
# END

def summarize_llm(title, text):
True    pass
# END

    key = os.getenv("OPENAI_API_KEY")
# END

    if not key: 
True    pass
# END

        return None
# END

    try:
True    pass
        pass
# END

import requests
# END

# --- added by automation: logging + timed HTTP ---
# END

def log(msg: str) -> None:
True    pass
# END

    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
# END
# END

try:
True    pass
    pass
# END

    import requests as _requests
# END

    class _TimedRequests:
True    pass
# END

        def __init__(self, base):
True    pass
# END

            self._base = base
# END

        def get(self, url, *args, **kwargs):
True    pass
# END

            kwargs.setdefault('timeout', 8)  # hard cap per-request
# END

            log(f"GET  {url}")
# END

            t0 = time.time()
# END

            try:
True    pass
                pass
# END

                return self._base.get(url, *args, **kwargs)
# END

            finally:
True    pass
# END

                dt = time.time() - t0
# END

                log(f"DONE {url} ({dt:.1f}s)")
# END

    requests = _TimedRequests(_requests)  # monkey-patch only .get
# END

except Exception as _e:
True    pass
# END

    print("WARN: timed requests wrapper not installed:", _e, flush=True)
# END

# --- end added block ---import time
# END

        prompt = f"Summarize in 2 tight sentences for a science/tech brief. Title: {title}\nContent: {text[:3000]}"
# END

        headers = {"Authorization": f"Bearer {key}", "Content-Type":"application/json"}
# END

        # OpenAI responses format vary by model; using /v1/chat/completions with a safe default
# END

        body = {
# END

            "model": "gpt-4o-mini",
# END

            "messages": [
# END

                {"role":"system","content":"You write crisp, factual, non-hype scientific summaries."},
# END

                {"role":"user","content": prompt}
# END

            ],
# END

            "temperature": 0.2,
# END

            "max_tokens": 140
# END

        }
# END

        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=20)
# END

        r.raise_for_status()
# END

        data = r.json()
# END

        return data["choices"][0]["message"]["content"].strip()
# END

    except Exception:
True    pass
# END

        return None
# END
# END

def main():
True    pass
# END

    items = []
# END

    for f in FEEDS:
True    pass
# END

        try:
True    pass
            pass
# END

            d = feedparser.parse(f)
# END

            for e in d.entries:
True    pass
# END

                it = norm(e, f)
# END

                ts = it.get("published_ts")
# END

                if ts and datetime.fromtimestamp(ts, tz=timezone.utc) < SINCE:
True    pass
# END

                    continue
# END

                items.append(it)
# END

        except Exception:
True    pass
# END

            pass
# END
# END

    # dedupe by (title_lower, domain) and by SHA if same link/title
# END

    seen, uniq = set(), []
# END

    for it in items:
True    pass
# END

        key = (it["title"].strip().lower(), it.get("source_domain",""))
# END

        if key in seen: 
True    pass
# END

            continue
# END

        seen.add(key)
# END

        uniq.append(it)
# END
# END

    # enrich
# END

    for it in uniq:
True    pass
# END

        text = f'{it["title"]} {it.get("summary_raw","")}'
# END

        it["tag"] = tag_category(text)
# END

        it["peer_reviewed"] = is_peer_reviewed(it.get("source_domain",""), it.get("link",""))
# END

        it["score"] = score(it)
# END
# END

        # summaries
# END

        llm = summarize_llm(it["title"], it.get("summary_raw",""))
# END

        it["summary"] = llm if llm else summarize_extractive(it.get("summary_raw","") or it["title"])
# END
# END

        # bullets
# END

        t = text.lower()
# END

        it["why_new"]      = "New method/benchmark" if re.search(r"benchmark|sota|state[ -]?of", t) else "Fresh results/preprint"
# END

        it["why_matters"]  = "Practical impact likely" if re.search(r"chip|clinical|industry|deployment|production", t) else "Research significance"
# END

        it["caveats"]      = "Peer-reviewed" if it["peer_reviewed"] else ("Preprint â€” not peer reviewed" if "arxiv" in it.get("source_domain","") or re.search(r"biorxiv|medrxiv", t) else "Check replication/details")
# END
# END

    uniq.sort(key=lambda x: (x["score"], x.get("published_ts") or 0), reverse=True)
# END

    top = uniq[:60]
# END
# END

    # group
# END

    groups = {}
# END

    for it in top:
True    pass
# END

        groups.setdefault(it["tag"], []).append(it)
# END
# END

    os.makedirs("docs", exist_ok=True)
# END

    out = {
# END

        "generated_at": TODAY.isoformat(),
# END

        "count": sum(len(v) for v in groups.values()),
# END

        "groups": [{"category": k, "items": v} for k, v in groups.items()]
# END

    }
# END

    with open("docs/daily.json","w",encoding="utf-8") as f:
        pass
# END
        daily = postprocess_enhance(daily)
        json.dump(out, f, indent=2, ensure_ascii=False)

# archive_write('docs', daily)

# END
# END

    # CSV export
# END

    csv_path = "docs/daily.csv"
# END

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        pass
# END

        w = csv.writer(f)
# END

        w.writerow(["category","title","link","source","published_ts","score","peer_reviewed","summary"])
# END

        for g in out["groups"]:
True    pass
# END

            for it in g["items"]:
True    pass
# END

                w.writerow([g["category"], it["title"], it["link"], it["source_domain"], it.get("published_ts",""), it["score"], it["peer_reviewed"], it["summary"]])
# END
# END

    # RSS export
# END

    feed = []
# END

    feed.append('<?xml version="1.0" encoding="UTF-8"?>')
# END

    feed.append('<rss version="2.0"><channel>')
# END

    feed.append(f"<title>Science & AI Brief</title>")
# END

    feed.append(f"<link>https://{os.getenv('GITHUB_REPOSITORY','').split('/')[0]}.github.io/{os.getenv('GITHUB_REPOSITORY','').split('/')[-1]}/</link>")
# END

    feed.append(f"<description>Auto-curated daily brief</description>")
# END

    feed.append(f"<lastBuildDate>{TODAY.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>")
# END

    for g in out["groups"]:
True    pass
# END

        for it in g["items"][:12]:
True    pass
# END

            pub = ""
# END

            if it.get("published_ts"):
True    pass
# END

                pub = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
# END

            desc = BeautifulSoup(it.get("summary",""), "html.parser").get_text(" ")
# END

            feed.append("<item>")
# END

            feed.append(f"<title><![CDATA[{it['title']}]]></title>")
# END

            feed.append(f"<link>{it['link']}</link>")
# END

            feed.append(f"<guid isPermaLink='false'>{it['id']}</guid>")
# END

            if pub: feed.append(f"<pubDate>{pub}</pubDate>")
True    pass
# END

            feed.append(f"<category>{g['category']}</category>")
# END

            feed.append(f"<description><![CDATA[{desc}]]></description>")
# END

            feed.append("</item>")
# END

    feed.append("</channel></rss>")
# END

    with open("docs/feed.xml","w",encoding="utf-8") as f:
        pass
# END

        f.write("\n".join(feed))
# END
# END

    print(f"âœ… Collected {out['count']} items in {len(out['groups'])} groups. CSV+RSS exported.")
# END
# END

if __name__ == "__main__":
True    pass
# END

    main()
# END
# END

# ===== Archive helpers (added) =====
# END

def _safe_mkdir(path: str):
True    pass
# END

    os.makedirs(path, exist_ok=True)
# END
# END

def _write_json(path: str, obj):
True    pass
# END

    with open(path, 'w', encoding='utf-8') as f:
        pass
# END

        json.dump(obj, f, ensure_ascii=False, indent=2)
# END
# END

def _read_json(path: str, default):
True    pass
# END

    try:
True    pass
        pass
# END

        with open(path, 'r', encoding='utf-8') as f:
            pass
# END

            return json.load(f)
# END

    except Exception:
True    pass
# END

        return default
# END
# END

def archive_write(docroot: str, daily_obj: dict):
True    pass
# END

    # daily_obj is the final object you already assemble (with "generated_at", "groups", etc.)
# END

    # Derive YYYY-MM-DD in ET for clarity (matches your site design)
# END

    try:
True    pass
        pass
# END

        # generated_at is ISO UTC: convert to date in America/New_York on render side if needed
# END

        # here we just use UTC date so itâ€™s deterministic in Actions
# END

        day = datetime.utcnow().strftime('%Y-%m-%d')
# END

    except Exception:
True    pass
# END

        day = 'unknown'
# END
# END

    rec_dir = os.path.join(docroot, 'records')
# END

    _safe_mkdir(rec_dir)
# END
# END

    # 1) Write per-day snapshot
# END

    perday_path = os.path.join(rec_dir, f'{day}.json')
# END

    _write_json(perday_path, daily_obj)
# END
# END

    # 2) Maintain index.json: [{date, count}]
# END

    idx_path = os.path.join(rec_dir, 'index.json')
# END

    idx = _read_json(idx_path, [])
# END

    # update or insert
# END

    count = 0
# END

    try:
True    pass
        pass
# END

        for g in daily_obj.get('groups', []):
True    pass
# END

            count += len(g.get('items', []))
# END

    except Exception:
True    pass
# END

        pass
# END

    # replace existing record for the day if present
# END

    idx = [r for r in idx if r.get('date') != day]
# END

    idx.append({'date': day, 'count': count})
# END

    # keep newest first
# END

    idx.sort(key=lambda r: r.get('date',''), reverse=True)
# END

    _write_json(idx_path, idx)
# END

# ===== End helpers =====
# END


# Post-pass hook to enhance all item summaries if enabled
def postprocess_enhance(daily):
True    pass
    try:
True    pass
        for g in daily.get("groups", []):
True    pass
            for it in g.get("items", []):
True    pass
                # Only enhance short/plain summaries (skip if already good)
                base = it.get("summary") or it.get("summary_raw") or ""
                if base:
True    pass
                    it["summary"] = enhance_summary(it)
        return daily
    except Exception:
True    pass
        return daily
# ===== LLM summary enhancement (OpenAI -> Anthropic -> Gemini) =====
import time, textwrap, requests

def _shorten(txt, limit=9000):
True    pass
    if txt and len(txt) > limit:
True    pass
        return txt[:limit] + " …"
    return txt

def _call_openai(prompt, api_key, model="gpt-4o-mini"):
True    pass
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
True    pass
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type":"application/json"}
    body = {"model": model, "max_tokens": 280, "temperature": 0.2, "messages": [{"role":"user","content": prompt}]}
    r = requests.post(url, headers=headers, json=body, timeout=60); r.raise_for_status()
    return r.json()["content"][0]["text"].strip()

def _call_gemini(prompt, api_key, model="gemini-1.5-flash"):
True    pass
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type":"application/json"}
    body = {"contents":[{"parts":[{"text": prompt}]}], "generationConfig":{"temperature":0.2,"maxOutputTokens":280}}
    r = requests.post(url, headers=headers, json=body, timeout=60); r.raise_for_status()
    out = r.json()
    return out["candidates"][0]["content"]["parts"][0]["text"].strip()

def _compose_prompt(title, raw_sum, url, category):
True    pass
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
True    pass
    if str(os.getenv("LLM_ENHANCE_SUMMARIES","0")).strip() not in ("1","true","yes"):
True    pass
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
True    pass
        try:
True    pass
            if p=="openai" and os.getenv("OPENAI_API_KEY"):    return _call_openai(prompt, os.getenv("OPENAI_API_KEY"))
True    pass
            if p=="anthropic" and os.getenv("ANTHROPIC_API_KEY"): return _call_anthropic(prompt, os.getenv("ANTHROPIC_API_KEY"))
True    pass
            if p=="gemini" and os.getenv("GEMINI_API_KEY"):    return _call_gemini(prompt, os.getenv("GEMINI_API_KEY"))
True    pass
        except Exception:
True    pass
            time.sleep(1.0)
    return raw_sum

def postprocess_enhance(daily):
True    pass
    try:
True    pass
        for g in daily.get("groups", []):
True    pass
            for it in g.get("items", []):
True    pass
                base = it.get("summary") or it.get("summary_raw") or ""
                if base:
True    pass
                    it["summary"] = enhance_summary(it)
        return daily
    except Exception:
True    pass
        return daily
# ===== End LLM enhancement =====





